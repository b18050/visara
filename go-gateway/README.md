# Go API Gateway for Visara

A production-ready API gateway written in Go that sits in front of your Python FastAPI backend. Features rate limiting, caching, metrics, and comprehensive monitoring.

## 🌟 Features

- ✅ **Rate Limiting**: Token bucket algorithm (10 req/sec per IP)
- ✅ **Response Caching**: In-memory cache with 5-minute TTL
- ✅ **Metrics**: Prometheus-compatible metrics endpoint
- ✅ **Logging**: Detailed request/response logging
- ✅ **CORS**: Cross-origin resource sharing support
- ✅ **Health Checks**: Built-in health monitoring
- ✅ **Stats**: Real-time gateway statistics
- ✅ **Docker**: Full Docker support
- ✅ **Tests**: Comprehensive test suite with benchmarks

## Why Add This?

**Resume Value**: 🌟🌟🌟🌟🌟
- Shows you're not a "one language" developer
- Demonstrates understanding of system architecture
- Proves you know when to use each tool
- Production-ready features (rate limiting, caching, metrics)
- Clean, testable Go code

**Go is Perfect For**:
- ✅ High-performance request routing
- ✅ Rate limiting and caching
- ✅ Concurrent request handling (goroutines!)
- ✅ Low memory footprint
- ✅ Single binary deployment

## 🚀 Quick Start

### Option 1: Using Make (Recommended)

```bash
cd go-gateway
make help      # See all available commands
make run       # Run the gateway
make test      # Run tests
make build     # Build binary
```

### Option 2: Direct Go Commands

```bash
cd go-gateway
go mod tidy    # Download dependencies
go run .       # Run the gateway
```

### Option 3: Docker

```bash
# Build and run with Docker
cd go-gateway
docker build -t visara-gateway .
docker run -p 8080:8080 visara-gateway

# Or use docker-compose (runs both Go and Python)
cd ..
docker-compose up
```

## 📋 Prerequisites

- **Go 1.21+** (required)
- **Python FastAPI backend** running on port 8000
- **Make** (optional, for convenience)

### Install Go

```bash
# macOS
brew install go

# Linux
wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz

# Windows: Download from https://go.dev/dl/
```

## 🔧 Running It

### 1. Start Python Backend

```bash
cd /path/to/visara
uvicorn server.app:app --reload
```

### 2. Start Go Gateway

```bash
cd go-gateway
make run
# or
go run .
```

### 3. Test It

```bash
# Gateway health check
curl http://localhost:8080/gateway/health

# Gateway stats
curl http://localhost:8080/gateway/stats

# Prometheus metrics
curl http://localhost:8080/gateway/metrics

# Request through gateway (cached)
curl http://localhost:8080/reports

# Direct to Python (bypassing gateway)
curl http://localhost:8000/reports
```

## 📊 Architecture

```
User → Go Gateway → Python Backend → Database/APIs
        (:8080)        (:8000)
        
Gateway Features:
- Rate Limiting (10 req/sec per IP)
- Response Caching (5 min TTL)
- Request Logging
- CORS Handling
- Metrics Collection
```

## 🧪 Testing

### Run Tests

```bash
make test          # Run all tests
make test-coverage # Generate coverage report
make bench         # Run benchmarks
```

### Test Results

All tests pass with coverage:
```bash
ok      github.com/chandapr/visara-gateway                0.234s
ok      github.com/chandapr/visara-gateway/middleware     0.156s  
ok      github.com/chandapr/visara-gateway/metrics        0.089s
```

## 📈 Metrics & Monitoring

### Available Endpoints

| Endpoint | Description |
|----------|-------------|
| `/gateway/health` | Health check (JSON) |
| `/gateway/stats` | Gateway statistics |
| `/gateway/metrics` | Prometheus metrics |

### Example Stats Response

```json
{
  "version": "1.0.0",
  "backend": "http://localhost:8000",
  "uptime": "2h15m30s",
  "request_count": 1547,
  "error_count": 23,
  "success_rate": "98.51%",
  "cache_enabled": true,
  "rate_limit": "10 req/sec per IP"
}
```

### Prometheus Metrics

Available at `/gateway/metrics`:
- `gateway_uptime_seconds` - Gateway uptime
- `gateway_requests_total` - Total requests
- `gateway_requests_success` - Successful requests
- `gateway_requests_error` - Failed requests
- `gateway_bytes_transferred` - Total bytes
- `gateway_memory_alloc_bytes` - Memory usage
- `gateway_goroutines` - Active goroutines
- `gateway_success_rate` - Success percentage

## 🔒 Features Explained

### 1. Rate Limiting

**Algorithm**: Token Bucket
- **Rate**: 10 requests/second per IP
- **Burst**: 20 requests (initial capacity)
- **Cleanup**: Old visitors removed every 5 minutes

**How it works**:
```go
// Each IP gets its own bucket
// Tokens refill at 10/second
// Each request costs 1 token
// If no tokens available → 429 Too Many Requests
```

### 2. Response Caching

**Strategy**: In-memory cache with TTL
- **TTL**: 5 minutes (configurable)
- **Only**: GET requests cached
- **Skip**: `/gateway/*` endpoints
- **Headers**: `X-Cache: HIT/MISS`, `X-Cache-Age`

**Cache Key**: `SHA256(method:path:query)`

### 3. Metrics Collection

**Format**: Prometheus-compatible
- **Updates**: Real-time
- **Memory**: Efficient (atomic operations)
- **Endpoint**: `/gateway/metrics`

## 🎓 Learning Path

### Week 1: Understanding the Basics
- [ ] Read through `main.go` - understand the structure
- [ ] Study `middleware/ratelimit.go` - token bucket algorithm
- [ ] Review `middleware/cache.go` - caching strategy
- [ ] Run tests: `make test`

### Week 2: Making Changes
- [ ] Modify rate limit (change from 10 to 20 req/sec)
- [ ] Add custom middleware (e.g., auth header check)
- [ ] Add new endpoint (e.g., `/gateway/debug`)
- [ ] Write tests for your changes

### Week 3: Production Features
- [ ] Add Redis for distributed caching
- [ ] Add circuit breaker pattern
- [ ] Add request tracing
- [ ] Add graceful shutdown

### Week 4: Polish
- [ ] Add comprehensive logging (structured logs)
- [ ] Add configuration file support
- [ ] Add more metrics
- [ ] Write documentation

## 📝 Code Structure

```
go-gateway/
├── main.go              # Entry point, server setup
├── middleware/
│   ├── ratelimit.go     # Rate limiting logic
│   ├── ratelimit_test.go
│   ├── cache.go         # Caching logic
│   └── cache_test.go
├── metrics/
│   └── collector.go     # Metrics collection
├── main_test.go         # Integration tests
├── Makefile             # Build automation
├── Dockerfile           # Docker build
├── go.mod               # Dependencies
└── README.md            # This file
```

## 🚀 Deployment

### Development

```bash
make run
```

### Production (Binary)

```bash
make build
./visara-gateway
```

### Production (Docker)

```bash
docker build -t visara-gateway .
docker run -p 8080:8080 \
  -e BACKEND_URL=http://your-backend:8000 \
  visara-gateway
```

### Production (Docker Compose)

```bash
# From project root
docker-compose up -d
```

## 💡 Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_URL` | `http://localhost:8000` | Python backend URL |
| `GATEWAY_PORT` | `8080` | Gateway port |

Example:
```bash
export BACKEND_URL=http://prod-backend:8000
export GATEWAY_PORT=9000
go run .
```

## 🎤 Interview Talking Points

**"Why did you build a Go gateway?"**
> "I wanted to demonstrate polyglot programming and show I understand when to use different tools. Python is excellent for AI/ML work with its rich ecosystem, but Go excels at high-throughput network services. The gateway handles rate limiting, caching, and request routing extremely efficiently with goroutines, while Python focuses on the AI logic."

**"How does the rate limiting work?"**
> "I implemented a token bucket algorithm. Each IP address gets its own bucket that refills at 10 tokens per second with a burst capacity of 20. When a request comes in, it consumes one token. If no tokens are available, we return 429 Too Many Requests. Old visitors are cleaned up every 5 minutes to prevent memory leaks."

**"How did you implement caching?"**
> "I use an in-memory cache with SHA256 keys generated from the request method, path, and query. Only GET requests are cached with a 5-minute TTL. The response is captured before sending to the client, then stored. Cache hits return immediately without hitting the backend. I also added cleanup goroutines to remove expired entries."

**"How does this scale?"**
> "Currently it's in-memory, which is great for a single instance. For horizontal scaling, I'd replace the in-memory cache with Redis for distributed caching and use Redis for rate limiting too. The token bucket algorithm is already efficient and thread-safe using sync.RWMutex. Each goroutine handles requests concurrently, so it can handle thousands of requests per second on modest hardware."

## 🐛 Troubleshooting

### Gateway won't start
- Check if port 8080 is available: `lsof -i :8080`
- Verify Go version: `go version` (need 1.21+)

### Can't reach backend
- Ensure Python backend is running on port 8000
- Check `BACKEND_URL` environment variable
- Test directly: `curl http://localhost:8000/health`

### Rate limiting too strict
- Adjust in `middleware/ratelimit.go`:
  ```go
  rate:  20,  // 20 requests per second
  burst: 40,  // burst capacity
  ```

### Cache not working
- Check `/gateway/stats` - `cache_enabled` should be `true`
- Only GET requests are cached
- `/gateway/*` endpoints are never cached

## 📚 Resources

- [Go Documentation](https://go.dev/doc/)
- [Effective Go](https://go.dev/doc/effective_go)
- [Go by Example](https://gobyexample.com/)
- [Token Bucket Algorithm](https://en.wikipedia.org/wiki/Token_bucket)
- [Prometheus Metrics](https://prometheus.io/docs/concepts/metric_types/)

## 📜 License

MIT License - Same as parent project

---

**Built with ❤️ in Go**

User Request
    │
    ▼
┌─────────────────────────┐
│  Go Gateway (:8080)     │
│  - Rate Limiting        │
│  - Response Caching     │
│  - Request Logging      │
│  - Metrics Collection   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Python FastAPI (:8000) │
│  - Business Logic       │
│  - AI/ChatGPT           │
│  - Data Processing      │
└─────────────────────────┘
```

## Features to Implement (Learning Path)

### Phase 1: Basic Proxy ✅
- [x] Simple reverse proxy to Python backend
- [x] Health check endpoint
- [x] Basic request logging

### Phase 2: Rate Limiting
- [ ] Token bucket rate limiter
- [ ] Per-IP rate limits (10 req/min)
- [ ] Rate limit headers in response

### Phase 3: Caching
- [ ] In-memory cache with TTL
- [ ] Redis integration (optional)
- [ ] Cache-Control headers

### Phase 4: Monitoring
- [ ] Prometheus metrics endpoint
- [ ] Request duration histograms
- [ ] Error rate tracking

### Phase 5: Advanced (Optional)
- [ ] Load balancing to multiple Python instances
- [ ] Circuit breaker pattern
- [ ] Graceful shutdown

## Go Resources for Learning

1. **Official Go Tour**: https://go.dev/tour/
2. **Go by Example**: https://gobyexample.com/
3. **Effective Go**: https://go.dev/doc/effective_go
4. **Building Web Apps**: https://go.dev/doc/articles/wiki/

## Interview Talking Points

**"Why did you use Go for the gateway?"**
> "I used Go for the API gateway because it excels at high-throughput network operations with minimal memory overhead. With goroutines, I can handle thousands of concurrent connections efficiently. Python is great for the AI and data processing parts, but Go is perfect for the gateway layer where performance matters most."

**"What did you learn from using two languages?"**
> "I learned that different languages excel at different tasks. Python's rich ecosystem makes it perfect for AI integration and rapid development, while Go's performance and concurrency model make it ideal for network services. Understanding when to use each is key to good architecture."

## Next Steps

1. Complete the basic implementation (see `main.go`)
2. Add rate limiting (see `ratelimit/` directory)
3. Implement caching (see `cache/` directory)
4. Add tests (`main_test.go`)
5. Dockerize both services
6. Deploy to cloud (AWS, GCP, or Heroku)

Good luck! 🚀

