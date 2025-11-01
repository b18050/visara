.PHONY: build run test clean docker-build docker-run help

# Variables
BINARY_NAME=visara-gateway
GO=go
GOFLAGS=-v
DOCKER_IMAGE=visara-gateway
DOCKER_TAG=latest

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build the Go binary
	@echo "🔨 Building $(BINARY_NAME)..."
	$(GO) build $(GOFLAGS) -o $(BINARY_NAME) .
	@echo "✅ Build complete!"

run: ## Run the gateway
	@echo "🚀 Starting $(BINARY_NAME)..."
	$(GO) run .

test: ## Run tests
	@echo "🧪 Running tests..."
	$(GO) test $(GOFLAGS) ./...

test-coverage: ## Run tests with coverage
	@echo "🧪 Running tests with coverage..."
	$(GO) test -coverprofile=coverage.out ./...
	$(GO) tool cover -html=coverage.out -o coverage.html
	@echo "✅ Coverage report: coverage.html"

bench: ## Run benchmarks
	@echo "⚡ Running benchmarks..."
	$(GO) test -bench=. -benchmem ./...

lint: ## Run linter
	@echo "🔍 Running linter..."
	@if command -v golangci-lint > /dev/null; then \
		golangci-lint run; \
	else \
		echo "golangci-lint not installed. Install: go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest"; \
	fi

fmt: ## Format code
	@echo "📝 Formatting code..."
	$(GO) fmt ./...

vet: ## Run go vet
	@echo "🔍 Running go vet..."
	$(GO) vet ./...

clean: ## Clean build artifacts
	@echo "🧹 Cleaning..."
	rm -f $(BINARY_NAME)
	rm -f coverage.out coverage.html
	$(GO) clean
	@echo "✅ Clean complete!"

docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "✅ Docker image built: $(DOCKER_IMAGE):$(DOCKER_TAG)"

docker-run: ## Run Docker container
	@echo "🐳 Running Docker container..."
	docker run -p 8080:8080 --name $(BINARY_NAME) $(DOCKER_IMAGE):$(DOCKER_TAG)

docker-stop: ## Stop Docker container
	@echo "🛑 Stopping Docker container..."
	docker stop $(BINARY_NAME) || true
	docker rm $(BINARY_NAME) || true

deps: ## Download dependencies
	@echo "📦 Downloading dependencies..."
	$(GO) mod download
	$(GO) mod tidy

upgrade-deps: ## Upgrade dependencies
	@echo "⬆️  Upgrading dependencies..."
	$(GO) get -u ./...
	$(GO) mod tidy

install: build ## Install the binary
	@echo "📦 Installing $(BINARY_NAME)..."
	$(GO) install

all: clean fmt vet test build ## Run all checks and build

ci: fmt vet test ## Run CI pipeline

dev: ## Run in development mode with auto-reload
	@echo "🔧 Running in dev mode..."
	@if command -v air > /dev/null; then \
		air; \
	else \
		echo "air not installed. Install: go install github.com/cosmtrek/air@latest"; \
		echo "Running without auto-reload..."; \
		$(GO) run .; \
	fi

