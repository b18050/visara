package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"sync"
	"time"

	"github.com/chandapr/visara-gateway/middleware"
	"github.com/chandapr/visara-gateway/metrics"
)

const (
	// Python FastAPI backend (can be overridden by env var)
	defaultBackendURL = "http://localhost:8000"
	// Gateway port (can be overridden by env var)
	defaultGatewayPort = "8080"
)

var (
	startTime = time.Now()
	stats     = &Stats{
		RequestCount: 0,
		ErrorCount:   0,
	}
	statsMutex sync.RWMutex
)

// Stats holds gateway statistics
type Stats struct {
	RequestCount int64
	ErrorCount   int64
}

// Config holds gateway configuration
type Config struct {
	BackendURL  string
	GatewayPort string
}

func loadConfig() Config {
	backendURL := os.Getenv("BACKEND_URL")
	if backendURL == "" {
		backendURL = defaultBackendURL
	}

	gatewayPort := os.Getenv("GATEWAY_PORT")
	if gatewayPort == "" {
		gatewayPort = defaultGatewayPort
	}

	return Config{
		BackendURL:  backendURL,
		GatewayPort: gatewayPort,
	}
}

// ResponseWriter wrapper to capture status code
type responseWriter struct {
	http.ResponseWriter
	statusCode int
	written    int64
}

func (rw *responseWriter) WriteHeader(code int) {
	rw.statusCode = code
	rw.ResponseWriter.WriteHeader(code)
}

func (rw *responseWriter) Write(b []byte) (int, error) {
	n, err := rw.ResponseWriter.Write(b)
	rw.written += int64(n)
	return n, err
}

// LoggingMiddleware logs all requests with detailed information
func LoggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()

		// Wrap response writer to capture status code
		wrapped := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}

		// Log incoming request
		log.Printf("→ [%s] %s %s from %s",
			r.Method, r.URL.Path, r.Proto, r.RemoteAddr)

		// Increment request counter
		statsMutex.Lock()
		stats.RequestCount++
		statsMutex.Unlock()

		// Call next handler
		next.ServeHTTP(wrapped, r)

		// Calculate duration
		duration := time.Since(start)

		// Log response
		log.Printf("← [%s] %s → %d (%v, %d bytes)",
			r.Method, r.URL.Path, wrapped.statusCode, duration, wrapped.written)

		// Track errors
		if wrapped.statusCode >= 400 {
			statsMutex.Lock()
			stats.ErrorCount++
			statsMutex.Unlock()
		}
	})
}

// CORSMiddleware adds CORS headers
func CORSMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}

// HealthCheckHandler handles health check requests
func HealthCheckHandler(w http.ResponseWriter, r *http.Request) {
	response := map[string]interface{}{
		"status":    "healthy",
		"service":   "visara-gateway",
		"version":   "1.0.0",
		"timestamp": time.Now().Format(time.RFC3339),
		"uptime":    time.Since(startTime).String(),
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

// StatsHandler returns gateway statistics
func StatsHandler(backendURL string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		statsMutex.RLock()
		defer statsMutex.RUnlock()

		response := map[string]interface{}{
			"version":        "1.0.0",
			"backend":        backendURL,
			"uptime":         time.Since(startTime).String(),
			"request_count":  stats.RequestCount,
			"error_count":    stats.ErrorCount,
			"success_rate":   calculateSuccessRate(),
			"cache_enabled":  middleware.IsCacheEnabled(),
			"rate_limit":     "10 req/sec per IP",
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(response)
	}
}

func calculateSuccessRate() string {
	if stats.RequestCount == 0 {
		return "N/A"
	}
	successCount := stats.RequestCount - stats.ErrorCount
	rate := float64(successCount) / float64(stats.RequestCount) * 100
	return fmt.Sprintf("%.2f%%", rate)
}

func main() {
	// Load configuration
	config := loadConfig()

	log.Println("=" + string(make([]byte, 58)) + "=")
	log.Println("🚀 Visara API Gateway Starting...")
	log.Println("=" + string(make([]byte, 58)) + "=")

	// Parse backend URL
	backend, err := url.Parse(config.BackendURL)
	if err != nil {
		log.Fatalf("❌ Failed to parse backend URL: %v", err)
	}

	// Initialize metrics
	metricsCollector := metrics.NewCollector()
	metricsCollector.Start()

	// Create reverse proxy
	proxy := httputil.NewSingleHostReverseProxy(backend)

	// Customize proxy error handler
	proxy.ErrorHandler = func(w http.ResponseWriter, r *http.Request, err error) {
		log.Printf("❌ Proxy error for %s: %v", r.URL.Path, err)

		statsMutex.Lock()
		stats.ErrorCount++
		statsMutex.Unlock()

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadGateway)

		response := map[string]string{
			"error":   "Backend unavailable",
			"message": "The Python backend service is not responding. Please ensure it's running on " + config.BackendURL,
		}
		json.NewEncoder(w).Encode(response)
	}

	// Gateway-specific routes (don't proxy these)
	http.HandleFunc("/gateway/health", HealthCheckHandler)
	http.HandleFunc("/gateway/stats", StatsHandler(config.BackendURL))
	http.HandleFunc("/gateway/metrics", metricsCollector.MetricsHandler())

	// Main handler with all middleware
	handler := LoggingMiddleware(
		CORSMiddleware(
			middleware.RateLimitMiddleware(
				middleware.CacheMiddleware(proxy),
			),
		),
	)

	http.Handle("/", handler)

	// Start server
	addr := ":" + config.GatewayPort
	log.Printf("✅ Backend: %s", config.BackendURL)
	log.Printf("✅ Gateway: http://localhost:%s", config.GatewayPort)
	log.Printf("✅ Health: http://localhost:%s/gateway/health", config.GatewayPort)
	log.Printf("✅ Stats: http://localhost:%s/gateway/stats", config.GatewayPort)
	log.Printf("✅ Metrics: http://localhost:%s/gateway/metrics", config.GatewayPort)
	log.Println("")
	log.Printf("🔧 Features enabled:")
	log.Printf("   - Rate limiting: 10 req/sec per IP")
	log.Printf("   - Response caching: 5 min TTL")
	log.Printf("   - Request logging: Enabled")
	log.Printf("   - CORS: Enabled")
	log.Printf("   - Metrics: Prometheus format")
	log.Println("")
	log.Printf("📡 Waiting for requests...")
	log.Println("=" + string(make([]byte, 58)) + "=")

	if err := http.ListenAndServe(addr, nil); err != nil {
		log.Fatalf("❌ Server failed to start: %v", err)
	}
}

