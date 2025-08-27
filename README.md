# Innotrat Chatbot

An AI-powered electronics requirements assistant that helps collect and structure hardware project requirements through natural conversation.

## Features

- Interactive chat interface for requirements gathering
- Persistent conversation history with SQLite
- Structured data collection for electronics projects
- RESTful API backend with FastAPI
- Streamlit web frontend

## Prerequisites

- Python 3.11+
- Ollama (for local LLM)

## Quick Start

### 1. Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Start Ollama and Install Model

```bash
# Start Ollama service
ollama serve

# In another terminal, pull the model
ollama pull tinyllama
```

### 3. Setup Project

```bash
# Clone and navigate to project
cd innotrat-chatbot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
uvicorn backend.app:app --reload
```

**Terminal 2 - Frontend:**
```bash
streamlit run frontend/streamlit_app.py
```

Access the application at `http://localhost:8501`

## API Endpoints

- `GET /` - Health check
- `POST /session/new` - Create new chat session
- `POST /chat` - Send message and get response

## Project Structure

```
innotrat-chatbot/
├── backend/
│   ├── __init__.py
│   ├── app.py              # FastAPI application
│   ├── conversation_engine.py  # LLM conversation logic
│   └── memory.py           # SQLite database operations
├── frontend/
│   └── streamlit_app.py    # Streamlit web interface
├── data/                   # SQLite database (auto-created)
├── requirements.txt
└── README.md
```

## Production Deployment

### Environment Variables

Create `.env` file:
```env
# Database
DATABASE_URL=sqlite:///./data/chat.db

# LLM Configuration
OLLAMA_HOST=http://localhost:11434
MODEL_NAME=tinyllama
MODEL_TEMPERATURE=0.2

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000","https://yourdomain.com"]

# Frontend
BACKEND_URL=http://localhost:8000
```

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - OLLAMA_HOST=http://ollama:11434
    depends_on:
      - ollama
  
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "8501:8501"
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      - backend

volumes:
  ollama_data:
```

### Production Checklist

- [ ] Use PostgreSQL instead of SQLite
- [ ] Add authentication and authorization
- [ ] Implement rate limiting
- [ ] Add logging and monitoring
- [ ] Use HTTPS with SSL certificates
- [ ] Set up backup strategy
- [ ] Configure environment-specific settings
- [ ] Add health checks and graceful shutdown
- [ ] Implement caching (Redis)
- [ ] Add API documentation with OpenAPI

## Troubleshooting

**"No module named 'backend'" error:**
- Ensure you're running uvicorn from the project root directory
- Check that `backend/__init__.py` exists

**"Connection refused" to Ollama:**
- Start Ollama service: `ollama serve`
- Verify model is installed: `ollama list`

**500 Internal Server Error:**
- Check backend logs for detailed error messages
- Ensure all dependencies are installed
- Verify database permissions

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black backend/ frontend/
isort backend/ frontend/
```

### API Documentation
Visit `http://localhost:8000/docs` when backend is running.

## License

MIT License