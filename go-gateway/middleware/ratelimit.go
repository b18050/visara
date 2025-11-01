package middleware

import (
	"net/http"
	"sync"
	"time"
)

// RateLimiter implements a token bucket rate limiter per IP
type RateLimiter struct {
	visitors map[string]*Visitor
	mu       sync.RWMutex
	rate     int           // requests per second
	burst    int           // bucket size
	cleanup  time.Duration // cleanup interval
}

// Visitor represents a single visitor's rate limit state
type Visitor struct {
	limiter  *TokenBucket
	lastSeen time.Time
}

// TokenBucket implements the token bucket algorithm
type TokenBucket struct {
	tokens    float64
	capacity  float64
	rate      float64 // tokens per second
	lastCheck time.Time
	mu        sync.Mutex
}

// NewTokenBucket creates a new token bucket
func NewTokenBucket(rate, capacity int) *TokenBucket {
	return &TokenBucket{
		tokens:    float64(capacity),
		capacity:  float64(capacity),
		rate:      float64(rate),
		lastCheck: time.Now(),
	}
}

// Allow checks if a request should be allowed
func (tb *TokenBucket) Allow() bool {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	now := time.Now()
	elapsed := now.Sub(tb.lastCheck).Seconds()

	// Add new tokens based on time passed
	tb.tokens = min(tb.capacity, tb.tokens+elapsed*tb.rate)
	tb.lastCheck = now

	if tb.tokens >= 1.0 {
		tb.tokens -= 1.0
		return true
	}

	return false
}

func min(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}

var rateLimiter = &RateLimiter{
	visitors: make(map[string]*Visitor),
	rate:     10,  // 10 requests per second
	burst:    20,  // burst capacity
	cleanup:  time.Minute * 5,
}

func init() {
	// Start cleanup goroutine
	go rateLimiter.cleanupVisitors()
}

// getVisitor returns the rate limiter for a specific IP
func (rl *RateLimiter) getVisitor(ip string) *TokenBucket {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	visitor, exists := rl.visitors[ip]
	if !exists {
		visitor = &Visitor{
			limiter:  NewTokenBucket(rl.rate, rl.burst),
			lastSeen: time.Now(),
		}
		rl.visitors[ip] = visitor
	} else {
		visitor.lastSeen = time.Now()
	}

	return visitor.limiter
}

// cleanupVisitors removes old visitors periodically
func (rl *RateLimiter) cleanupVisitors() {
	ticker := time.NewTicker(rl.cleanup)
	defer ticker.Stop()

	for range ticker.C {
		rl.mu.Lock()
		for ip, visitor := range rl.visitors {
			if time.Since(visitor.lastSeen) > rl.cleanup {
				delete(rl.visitors, ip)
			}
		}
		rl.mu.Unlock()
	}
}

// RateLimitMiddleware applies rate limiting per IP address
func RateLimitMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Get client IP
		ip := r.RemoteAddr
		if forwarded := r.Header.Get("X-Forwarded-For"); forwarded != "" {
			ip = forwarded
		}

		// Get rate limiter for this IP
		limiter := rateLimiter.getVisitor(ip)

		// Check if request is allowed
		if !limiter.Allow() {
			w.Header().Set("Content-Type", "application/json")
			w.Header().Set("X-RateLimit-Limit", "10")
			w.Header().Set("X-RateLimit-Remaining", "0")
			w.WriteHeader(http.StatusTooManyRequests)
			w.Write([]byte(`{"error":"Rate limit exceeded","message":"Too many requests. Please slow down."}`))
			return
		}

		// Add rate limit headers
		w.Header().Set("X-RateLimit-Limit", "10")

		next.ServeHTTP(w, r)
	})
}

