package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestHealthCheckHandler(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/gateway/health", nil)
	w := httptest.NewRecorder()

	HealthCheckHandler(w, req)

	resp := w.Result()
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected status 200, got %d", resp.StatusCode)
	}

	var response map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		t.Fatalf("Failed to decode response: %v", err)
	}

	if response["status"] != "healthy" {
		t.Errorf("Expected status 'healthy', got %v", response["status"])
	}

	if response["service"] != "visara-gateway" {
		t.Errorf("Expected service 'visara-gateway', got %v", response["service"])
	}
}

func TestStatsHandler(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/gateway/stats", nil)
	w := httptest.NewRecorder()

	handler := StatsHandler("http://localhost:8000")
	handler(w, req)

	resp := w.Result()
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected status 200, got %d", resp.StatusCode)
	}

	var response map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		t.Fatalf("Failed to decode response: %v", err)
	}

	if response["version"] != "1.0.0" {
		t.Errorf("Expected version '1.0.0', got %v", response["version"])
	}

	if response["backend"] != "http://localhost:8000" {
		t.Errorf("Expected backend 'http://localhost:8000', got %v", response["backend"])
	}
}

func TestCalculateSuccessRate(t *testing.T) {
	tests := []struct {
		name     string
		total    int64
		errors   int64
		expected string
	}{
		{"All success", 100, 0, "100.00%"},
		{"Half success", 100, 50, "50.00%"},
		{"No requests", 0, 0, "N/A"},
		{"Some errors", 1000, 100, "90.00%"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Temporarily set stats
			oldStats := stats
			stats = &Stats{
				RequestCount: tt.total,
				ErrorCount:   tt.errors,
			}
			defer func() { stats = oldStats }()

			result := calculateSuccessRate()
			if result != tt.expected {
				t.Errorf("Expected %s, got %s", tt.expected, result)
			}
		})
	}
}

func TestCORSMiddleware(t *testing.T) {
	handler := CORSMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))

	// Test OPTIONS request
	req := httptest.NewRequest(http.MethodOptions, "/test", nil)
	w := httptest.NewRecorder()
	handler.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status 200 for OPTIONS, got %d", w.Code)
	}

	// Check CORS headers
	if w.Header().Get("Access-Control-Allow-Origin") != "*" {
		t.Error("CORS origin header not set correctly")
	}
}

func TestLoggingMiddleware(t *testing.T) {
	callCount := 0
	handler := LoggingMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		callCount++
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("test response"))
	}))

	req := httptest.NewRequest(http.MethodGet, "/test", nil)
	w := httptest.NewRecorder()
	handler.ServeHTTP(w, req)

	if callCount != 1 {
		t.Errorf("Handler should be called once, got %d", callCount)
	}

	if w.Code != http.StatusOK {
		t.Errorf("Expected status 200, got %d", w.Code)
	}
}

func TestResponseWriter(t *testing.T) {
	w := httptest.NewRecorder()
	rw := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}

	// Test WriteHeader
	rw.WriteHeader(http.StatusCreated)
	if rw.statusCode != http.StatusCreated {
		t.Errorf("Expected status 201, got %d", rw.statusCode)
	}

	// Test Write
	data := []byte("test data")
	n, err := rw.Write(data)
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}
	if n != len(data) {
		t.Errorf("Expected to write %d bytes, wrote %d", len(data), n)
	}
	if rw.written != int64(len(data)) {
		t.Errorf("Expected written %d, got %d", len(data), rw.written)
	}
}

func TestLoadConfig(t *testing.T) {
	// Test default values
	config := loadConfig()
	if config.BackendURL != defaultBackendURL {
		t.Errorf("Expected default backend URL, got %s", config.BackendURL)
	}
	if config.GatewayPort != defaultGatewayPort {
		t.Errorf("Expected default gateway port, got %s", config.GatewayPort)
	}
}

// Benchmark tests
func BenchmarkHealthCheckHandler(b *testing.B) {
	req := httptest.NewRequest(http.MethodGet, "/gateway/health", nil)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		HealthCheckHandler(w, req)
	}
}

func BenchmarkCalculateSuccessRate(b *testing.B) {
	stats = &Stats{
		RequestCount: 1000,
		ErrorCount:   100,
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		calculateSuccessRate()
	}
}

