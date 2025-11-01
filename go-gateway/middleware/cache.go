package middleware

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"io"
	"net/http"
	"sync"
	"time"
)

const (
	defaultTTL = 5 * time.Minute
)

// CacheEntry represents a cached response
type CacheEntry struct {
	StatusCode  int
	Headers     http.Header
	Body        []byte
	CachedAt    time.Time
	TTL         time.Duration
}

// IsExpired checks if the cache entry has expired
func (ce *CacheEntry) IsExpired() bool {
	return time.Since(ce.CachedAt) > ce.TTL
}

// Cache implements a simple in-memory cache
type Cache struct {
	entries map[string]*CacheEntry
	mu      sync.RWMutex
	enabled bool
}

var cache = &Cache{
	entries: make(map[string]*CacheEntry),
	enabled: true,
}

func init() {
	// Start cleanup goroutine
	go cache.cleanup()
}

// IsCacheEnabled returns whether caching is enabled
func IsCacheEnabled() bool {
	return cache.enabled
}

// generateCacheKey creates a cache key from the request
func generateCacheKey(r *http.Request) string {
	// Only cache GET requests
	if r.Method != http.MethodGet {
		return ""
	}

	// Create key from method, path, and query
	key := r.Method + ":" + r.URL.Path + ":" + r.URL.RawQuery
	hash := sha256.Sum256([]byte(key))
	return hex.EncodeToString(hash[:])
}

// get retrieves an entry from the cache
func (c *Cache) get(key string) (*CacheEntry, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	entry, exists := c.entries[key]
	if !exists || entry.IsExpired() {
		return nil, false
	}

	return entry, true
}

// set stores an entry in the cache
func (c *Cache) set(key string, entry *CacheEntry) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.entries[key] = entry
}

// cleanup removes expired entries periodically
func (c *Cache) cleanup() {
	ticker := time.NewTicker(time.Minute)
	defer ticker.Stop()

	for range ticker.C {
		c.mu.Lock()
		for key, entry := range c.entries {
			if entry.IsExpired() {
				delete(c.entries, key)
			}
		}
		c.mu.Unlock()
	}
}

// responseCapture captures the response for caching
type responseCapture struct {
	http.ResponseWriter
	statusCode int
	body       *bytes.Buffer
	headers    http.Header
}

func newResponseCapture(w http.ResponseWriter) *responseCapture {
	return &responseCapture{
		ResponseWriter: w,
		statusCode:     http.StatusOK,
		body:           new(bytes.Buffer),
		headers:        make(http.Header),
	}
}

func (rc *responseCapture) WriteHeader(code int) {
	rc.statusCode = code
	// Don't call underlying WriteHeader yet
}

func (rc *responseCapture) Write(b []byte) (int, error) {
	// Capture the body
	rc.body.Write(b)
	return len(b), nil
}

func (rc *responseCapture) Header() http.Header {
	// Capture headers
	return rc.ResponseWriter.Header()
}

// CacheMiddleware implements response caching for GET requests
func CacheMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Only cache GET requests
		if r.Method != http.MethodGet {
			next.ServeHTTP(w, r)
			return
		}

		// Skip caching for gateway endpoints
		if len(r.URL.Path) >= 8 && r.URL.Path[:8] == "/gateway" {
			next.ServeHTTP(w, r)
			return
		}

		// Generate cache key
		cacheKey := generateCacheKey(r)
		if cacheKey == "" {
			next.ServeHTTP(w, r)
			return
		}

		// Check cache
		if entry, found := cache.get(cacheKey); found {
			// Cache hit!
			w.Header().Set("X-Cache", "HIT")
			w.Header().Set("X-Cache-Age", time.Since(entry.CachedAt).String())

			// Copy cached headers
			for key, values := range entry.Headers {
				for _, value := range values {
					w.Header().Add(key, value)
				}
			}

			w.WriteHeader(entry.StatusCode)
			w.Write(entry.Body)
			return
		}

		// Cache miss - capture the response
		w.Header().Set("X-Cache", "MISS")
		capture := newResponseCapture(w)

		// Call next handler
		next.ServeHTTP(capture, r)

		// Cache successful responses (2xx and 3xx)
		if capture.statusCode >= 200 && capture.statusCode < 400 {
			entry := &CacheEntry{
				StatusCode: capture.statusCode,
				Headers:    capture.Header(),
				Body:       capture.body.Bytes(),
				CachedAt:   time.Now(),
				TTL:        defaultTTL,
			}
			cache.set(cacheKey, entry)
		}

		// Write the captured response to the actual response writer
		for key, values := range capture.Header() {
			for _, value := range values {
				w.Header().Add(key, value)
			}
		}
		w.WriteHeader(capture.statusCode)
		io.Copy(w, capture.body)
	})
}

