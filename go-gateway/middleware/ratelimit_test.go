package middleware

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestTokenBucket(t *testing.T) {
	bucket := NewTokenBucket(10, 10)

	// Should allow first 10 requests immediately
	for i := 0; i < 10; i++ {
		if !bucket.Allow() {
			t.Errorf("Request %d should be allowed", i)
		}
	}

	// 11th request should be denied
	if bucket.Allow() {
		t.Error("Request should be rate limited")
	}

	// Wait a bit and try again
	time.Sleep(200 * time.Millisecond)
	if !bucket.Allow() {
		t.Error("Request should be allowed after waiting")
	}
}

func TestRateLimitMiddleware(t *testing.T) {
	handler := RateLimitMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))

	// Make requests
	for i := 0; i < 21; i++ { // More than burst capacity
		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		req.RemoteAddr = "127.0.0.1:1234"
		w := httptest.NewRecorder()
		handler.ServeHTTP(w, req)

		if i < 20 {
			// First 20 should succeed (burst capacity)
			if w.Code != http.StatusOK {
				t.Errorf("Request %d: expected 200, got %d", i, w.Code)
			}
		} else {
			// 21st should be rate limited
			if w.Code != http.StatusTooManyRequests {
				t.Errorf("Request %d: expected 429, got %d", i, w.Code)
			}
		}
	}
}

func TestRateLimiter_DifferentIPs(t *testing.T) {
	handler := RateLimitMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))

	// Requests from different IPs should not affect each other
	ips := []string{"192.168.1.1:1234", "192.168.1.2:1234", "192.168.1.3:1234"}

	for _, ip := range ips {
		for i := 0; i < 20; i++ {
			req := httptest.NewRequest(http.MethodGet, "/test", nil)
			req.RemoteAddr = ip
			w := httptest.NewRecorder()
			handler.ServeHTTP(w, req)

			if w.Code != http.StatusOK {
				t.Errorf("Request from %s should succeed, got status %d", ip, w.Code)
			}
		}
	}
}

func BenchmarkRateLimitMiddleware(b *testing.B) {
	handler := RateLimitMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))

	req := httptest.NewRequest(http.MethodGet, "/test", nil)
	req.RemoteAddr = "127.0.0.1:1234"

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		handler.ServeHTTP(w, req)
	}
}

