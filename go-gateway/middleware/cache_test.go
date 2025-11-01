package middleware

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestCacheMiddleware_CacheHit(t *testing.T) {
	callCount := 0
	handler := CacheMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		callCount++
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("response body"))
	}))

	// First request - cache miss
	req1 := httptest.NewRequest(http.MethodGet, "/test", nil)
	w1 := httptest.NewRecorder()
	handler.ServeHTTP(w1, req1)

	if w1.Header().Get("X-Cache") != "MISS" {
		t.Error("First request should be a cache miss")
	}
	if callCount != 1 {
		t.Errorf("Handler should be called once, got %d", callCount)
	}

	// Second request - cache hit
	req2 := httptest.NewRequest(http.MethodGet, "/test", nil)
	w2 := httptest.NewRecorder()
	handler.ServeHTTP(w2, req2)

	if w2.Header().Get("X-Cache") != "HIT" {
		t.Error("Second request should be a cache hit")
	}
	if callCount != 1 {
		t.Errorf("Handler should still be called once, got %d", callCount)
	}
	if w2.Body.String() != "response body" {
		t.Error("Cached response body doesn't match")
	}
}

func TestCacheMiddleware_OnlyGET(t *testing.T) {
	callCount := 0
	handler := CacheMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		callCount++
		w.WriteHeader(http.StatusOK)
	}))

	// POST request should not be cached
	methods := []string{http.MethodPost, http.MethodPut, http.MethodDelete}
	for _, method := range methods {
		req := httptest.NewRequest(method, "/test", nil)
		w := httptest.NewRecorder()
		handler.ServeHTTP(w, req)

		if w.Header().Get("X-Cache") != "" {
			t.Errorf("%s request should not be cached", method)
		}
	}
}

func TestCacheMiddleware_SkipGatewayEndpoints(t *testing.T) {
	callCount := 0
	handler := CacheMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		callCount++
		w.WriteHeader(http.StatusOK)
	}))

	// Gateway endpoints should not be cached
	req := httptest.NewRequest(http.MethodGet, "/gateway/health", nil)
	w := httptest.NewRecorder()
	handler.ServeHTTP(w, req)

	if w.Header().Get("X-Cache") != "" {
		t.Error("Gateway endpoints should not be cached")
	}
}

func TestCacheEntry_IsExpired(t *testing.T) {
	// Fresh entry
	entry := &CacheEntry{
		CachedAt: time.Now(),
		TTL:      5 * time.Minute,
	}
	if entry.IsExpired() {
		t.Error("Fresh entry should not be expired")
	}

	// Expired entry
	expiredEntry := &CacheEntry{
		CachedAt: time.Now().Add(-10 * time.Minute),
		TTL:      5 * time.Minute,
	}
	if !expiredEntry.IsExpired() {
		t.Error("Old entry should be expired")
	}
}

func TestGenerateCacheKey(t *testing.T) {
	tests := []struct {
		name   string
		method string
		path   string
		query  string
		want   string
	}{
		{
			name:   "Simple GET",
			method: http.MethodGet,
			path:   "/test",
			query:  "",
			want:   "not empty",
		},
		{
			name:   "POST returns empty",
			method: http.MethodPost,
			path:   "/test",
			query:  "",
			want:   "",
		},
		{
			name:   "GET with query",
			method: http.MethodGet,
			path:   "/test",
			query:  "foo=bar",
			want:   "not empty",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest(tt.method, tt.path+"?"+tt.query, nil)
			key := generateCacheKey(req)

			if tt.want == "" && key != "" {
				t.Errorf("Expected empty key, got %s", key)
			}
			if tt.want == "not empty" && key == "" {
				t.Error("Expected non-empty key, got empty")
			}
		})
	}
}

func BenchmarkCacheMiddleware_Hit(b *testing.B) {
	handler := CacheMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("response"))
	}))

	// Prime the cache
	req := httptest.NewRequest(http.MethodGet, "/test", nil)
	w := httptest.NewRecorder()
	handler.ServeHTTP(w, req)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		w := httptest.NewRecorder()
		handler.ServeHTTP(w, req)
	}
}

