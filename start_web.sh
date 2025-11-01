#!/bin/bash
# Start both backend API and frontend for web demo

set -e

echo "🚀 Starting Visara Web Interface"
echo "================================="
echo ""

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8000 is already in use"
    echo "   Attempting to kill existing process..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Check if port 5173 is already in use
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 5173 is already in use"
    echo "   Attempting to kill existing process..."
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Check Python dependencies
if ! python3 -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "❌ Missing Python dependencies. Installing..."
    pip install -r requirements.txt
fi

# Check Node dependencies
if [ ! -d "web/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd web && npm install && cd ..
fi

echo "🔧 Starting backend API on http://localhost:8000..."
cd /Users/chandapr/visara
uvicorn server.app:app --reload --host 0.0.0.0 --port 8000 > /tmp/visara-backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start. Check /tmp/visara-backend.log"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

echo "🎨 Starting frontend on http://localhost:5173..."
cd web
npm run dev > /tmp/visara-frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to start..."
for i in {1..30}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo "✅ Frontend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Frontend failed to start. Check /tmp/visara-frontend.log"
        kill $BACKEND_PID 2>/dev/null || true
        kill $FRONTEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

echo ""
echo "🎉 All systems ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   🌐 Open your browser to:"
echo "   👉 http://localhost:5173"
echo ""
echo "   📡 API running at: http://localhost:8000"
echo "   📊 API docs: http://localhost:8000/docs"
echo ""
echo "   💡 For your video demo:"
echo "      1. Upload an outage image (PNG/JPEG)"
echo "      2. Enter location (e.g., 'Sanaa, Yemen')"
echo "      3. Click 'Fetch Latest News'"
echo "      4. Select relevant articles"
echo "      5. Click 'Generate Report'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Keep script running and show logs
tail -f /tmp/visara-backend.log /tmp/visara-frontend.log &
TAIL_PID=$!

# Wait for interrupt
wait $BACKEND_PID $FRONTEND_PID

