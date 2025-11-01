package metrics

import (
	"fmt"
	"net/http"
	"runtime"
	"sync/atomic"
	"time"
)

// Collector collects and exposes metrics
type Collector struct {
	requestsTotal   uint64
	requestsSuccess uint64
	requestsError   uint64
	bytesTransferred uint64
	startTime       time.Time
}

// NewCollector creates a new metrics collector
func NewCollector() *Collector {
	return &Collector{
		startTime: time.Now(),
	}
}

// Start initializes the metrics collector
func (c *Collector) Start() {
	// Nothing to initialize for now
	// In a real system, you might start background tasks here
}

// IncrementRequests increments the total request counter
func (c *Collector) IncrementRequests() {
	atomic.AddUint64(&c.requestsTotal, 1)
}

// IncrementSuccess increments the success counter
func (c *Collector) IncrementSuccess() {
	atomic.AddUint64(&c.requestsSuccess, 1)
}

// IncrementError increments the error counter
func (c *Collector) IncrementError() {
	atomic.AddUint64(&c.requestsError, 1)
}

// AddBytes adds to the bytes transferred counter
func (c *Collector) AddBytes(n uint64) {
	atomic.AddUint64(&c.bytesTransferred, n)
}

// MetricsHandler returns an HTTP handler for the /metrics endpoint
func (c *Collector) MetricsHandler() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var m runtime.MemStats
		runtime.ReadMemStats(&m)

		uptime := time.Since(c.startTime)
		requestsTotal := atomic.LoadUint64(&c.requestsTotal)
		requestsSuccess := atomic.LoadUint64(&c.requestsSuccess)
		requestsError := atomic.LoadUint64(&c.requestsError)
		bytesTransferred := atomic.LoadUint64(&c.bytesTransferred)

		// Prometheus-style metrics format
		metrics := fmt.Sprintf(`# HELP gateway_uptime_seconds Gateway uptime in seconds
# TYPE gateway_uptime_seconds gauge
gateway_uptime_seconds %f

# HELP gateway_requests_total Total number of requests
# TYPE gateway_requests_total counter
gateway_requests_total %d

# HELP gateway_requests_success Total number of successful requests
# TYPE gateway_requests_success counter
gateway_requests_success %d

# HELP gateway_requests_error Total number of failed requests
# TYPE gateway_requests_error counter
gateway_requests_error %d

# HELP gateway_bytes_transferred Total bytes transferred
# TYPE gateway_bytes_transferred counter
gateway_bytes_transferred %d

# HELP gateway_memory_alloc_bytes Current memory allocated in bytes
# TYPE gateway_memory_alloc_bytes gauge
gateway_memory_alloc_bytes %d

# HELP gateway_memory_sys_bytes Total memory obtained from OS in bytes
# TYPE gateway_memory_sys_bytes gauge
gateway_memory_sys_bytes %d

# HELP gateway_goroutines Number of goroutines
# TYPE gateway_goroutines gauge
gateway_goroutines %d

# HELP gateway_success_rate Success rate percentage
# TYPE gateway_success_rate gauge
gateway_success_rate %f
`,
			uptime.Seconds(),
			requestsTotal,
			requestsSuccess,
			requestsError,
			bytesTransferred,
			m.Alloc,
			m.Sys,
			runtime.NumGoroutine(),
			calculateSuccessRate(requestsTotal, requestsError),
		)

		w.Header().Set("Content-Type", "text/plain; version=0.0.4")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(metrics))
	}
}

func calculateSuccessRate(total, errors uint64) float64 {
	if total == 0 {
		return 100.0
	}
	success := total - errors
	return (float64(success) / float64(total)) * 100.0
}

