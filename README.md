# SolvIQ - AI-Powered RAG System for Solution Engineers

SolvIQ is an intelligent RAG (Retrieval-Augmented Generation) system specifically designed for Solution Engineers and M&A teams. It provides AI-powered assistance for creating compelling technical proposals, responding to complex RFPs, and delivering enterprise-grade solutions.

## 🚀 Features

- **Multi-Agent RAG System**: Standard, Advanced, and Conservative retrieval methods
- **M&A Focused**: Specialized for Solution Engineers and M&A integration scenarios
- **Web Search Integration**: Combines document retrieval with real-time web search
- **RAGAS Evaluation**: Built-in evaluation framework for performance assessment
- **Production Ready**: Docker support, logging, and configuration management

## 📋 Requirements

- Python 3.11+
- OpenAI API Key
- Tavily API Key (for web search)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vijaya-tirumala/AIE8-cert-challenge.git
   cd AIE8-cert-challenge
   ```

2. **Install dependencies using uv:**
   ```bash
   uv sync
   ```

3. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. **Verify installation:**
   ```bash
   uv run python test_app.py
   ```

## 🚀 Quick Start

### Development Mode

1. **Set your API keys:**
   ```bash
   export OPENAI_API_KEY="your_openai_api_key"
   export TAVILY_API_KEY="your_tavily_api_key"
   ```

2. **Start the application:**
   ```bash
   ./start.sh
   ```

3. **Access the application:**
   - Backend API: http://localhost:8000
   - Frontend UI: http://localhost:8501

### Production Mode

```bash
./start.sh
```

### Docker Deployment

```bash
docker-compose up -d
```

## 📁 Project Structure

```
AIE8-cert-challenge/
├── app.py                 # FastAPI backend
├── frontend.py            # Streamlit frontend
├── rag_components.py      # RAG system components
├── config.py              # Configuration management
├── data/                  # Document data
├── metrics/               # RAGAS evaluation results and metrics
├── notebooks/             # Jupyter notebooks
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Orchestration
└── README.md              # This file
```

## 🔧 Configuration

The application uses environment variables for configuration:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `TAVILY_API_KEY`: Your Tavily API key (required)
- `DATA_PATH`: Path to data directory (default: "data")
- `CHUNK_SIZE`: Document chunk size (default: 800)
- `CHUNK_OVERLAP`: Chunk overlap (default: 100)
- `MODEL_NAME`: OpenAI model (default: "gpt-4o-mini")

## 📊 API Endpoints

- `GET /`: Health check and API information
- `GET /agents`: List available RAG agents
- `POST /query`: Query the RAG system
- `GET /evaluation/golden-dataset`: Get evaluation test cases
- `POST /evaluation/run`: Run RAGAS evaluation

## 🧪 Testing

Run the test suite:
```bash
uv run python test_app.py
```

## 📈 Evaluation

The system includes RAGAS evaluation framework for assessing:
- **Faithfulness**: How well the answer is grounded in retrieved context
- **Answer Relevancy**: How relevant the answer is to the question
- **Context Precision**: How precise the retrieved context is
- **Context Recall**: How well the context covers the answer

## 🐳 Docker

Build and run with Docker:
```bash
docker build -t solviq .
docker run -p 8000:8000 -p 8501:8501 \
  -e OPENAI_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  solviq
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For questions or issues, please open a GitHub issue or contact the development team.