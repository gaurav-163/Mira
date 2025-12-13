# Mira

AI-powered knowledge base assistant with RAG (Retrieval-Augmented Generation). Ask questions about your documents or get answers from general knowledge - all in a beautiful ChatGPT-style interface.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Next.js](https://img.shields.io/badge/next.js-14.2.0-black)
![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ Features

### 🎨 **Modern & Eye-Catching UI**
- **Triple-Gradient Animations**: Flowing color gradients across the interface
- **Glassmorphism Effects**: Sophisticated frosted glass design elements
- **Smooth Typing Animation**: "Mira" branding with elegant cursor effect
- **Pulsing Glow Effects**: Dynamic lighting on interactive elements
- **Floating Animations**: Subtle motion on key components
- **Custom Scrollbars**: Styled with cyan-blue gradients

### 🤖 **AI & Intelligence**
- 🎯 **Hybrid Intelligence**: Automatically routes questions to knowledge base OR general AI
- 📚 **Enhanced Semantic RAG**: Advanced retrieval with hybrid search and query expansion
- 🚀 **Reciprocal Rank Fusion (RRF)**: Merges multiple search results for best accuracy
- 💡 **Query Caching**: Smart caching for faster repeated queries
- 🔍 **Multi-Query Search**: Expands queries with variations for comprehensive results
- 📄 **OCR Support**: Process both digital and scanned PDFs (Tesseract/EasyOCR)
- 🔄 **Self-Reflection**: Optional AI quality checking for improved answers

### 💬 **User Experience**
- 💾 **Persistent Chat History**: Conversations saved in browser localStorage
- 📊 **Source Citations**: See exactly which documents were used
- ⚡ **Lightning Fast**: Optimized for 2-3 second response times
- 🎭 **Interactive Elements**: Hover effects, scale animations, and smooth transitions
- 📱 **Responsive Design**: Works beautifully on all screen sizes

## 🚀 Quick Start

### Prerequisites

Make sure you have the following installed:

```bash
# Python 3.10 or higher
python --version

# Node.js 18 or higher
node --version

# npm or yarn
npm --version
```

### Step 1: Clone the Repository

```bash
git clone https://github.com/gaurav-163/Mira.git
cd Personal-Knowledge-Assistant
```

### Step 2: Set Up Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Required: Get your API keys**

1. **Cohere** (Recommended - Free tier available)
   - Visit: https://dashboard.cohere.com/api-keys
   - Sign up and copy your API key
   - Paste in `.env`: `COHERE_API_KEY=your-key-here`

2. **Groq** (Optional - 10x faster but needs valid key)
   - Visit: https://console.groq.com/keys
   - Sign up and copy your API key
   - Paste in `.env`: `GROQ_API_KEY=your-key-here`

### Step 3: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Step 4: Add Your Documents

```bash
# Create knowledge base directory if it doesn't exist
mkdir -p data/knowledge_base

# Copy your PDF files
cp /path/to/your/documents/*.pdf data/knowledge_base/

# Example: Copy research papers, books, documentation, etc.
```

### Step 5: Start the Application

**Option 1: Start Both Backend and Frontend (Recommended)**

```bash
# Terminal 1: Start the backend
./start.sh

# Terminal 2: Start the frontend
cd frontend
./start-frontend.sh
```

**Option 2: Manual Start with Uvicorn**

```bash
# Start backend with uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Or with uv (faster)
uv run uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# In another terminal, start frontend
cd frontend
npm run dev
```

**Option 3: Backend Only**

```bash
./start.sh
# Backend will run at http://localhost:8000
```

**Access the application:**
- 🌐 **Frontend**: http://localhost:3000
- 🔧 **API**: http://localhost:8000
- 📖 **API Docs**: http://localhost:8000/docs

### Step 6: Use the Assistant

1. Open http://localhost:3000 in your browser
2. Wait for "Ready" status (green dot in top right)
3. Start asking questions!

**Example questions:**
- "What is data warehousing?" (from your docs)
- "Explain the main concepts" (from your docs)
- "What is Python?" (general knowledge)

### Stop the Application

```bash
./stop.sh
```

## 🎨 UI/UX Highlights

**Mira features a stunning, modern interface with:**

- **Animated Background**: Multi-layered gradient orbs with smooth floating animations
- **Glassmorphism**: Frosted glass effects on sidebar and panels for depth
- **Typography Animation**: "Mira" brand name types out with a blinking cursor
- **Triple Gradients**: Blue → Cyan → Purple color flows throughout
- **Pulsing Glow**: Dynamic lighting effects on the logo and active elements
- **Hover Interactions**: Cards scale, rotate icons, and show enhanced shadows
- **Smooth Transitions**: 300ms duration with easing for all interactive elements
- **Custom Scrollbars**: Cyan-blue gradient scrollbars matching the theme
- **Feature Cards**: 4 animated cards with color-coded gradients (blue, cyan, green, purple)
- **Enhanced Input**: Gradient-filled textarea with cyan focus ring
- **Gradient Buttons**: Animated blue-to-cyan gradient on primary actions

## 📁 Project Structure

```
Personal-Knowledge-Assistant/
├── backend/                    # Backend application
│   ├── core/                  # Core business logic
│   │   ├── llm/              # LLM providers and factory
│   │   ├── vector_store/     # Vector database management
│   │   └── document_processing/  # PDF and text processing
│   ├── services/             # Business services
│   ├── api/                  # API routes and endpoints
│   ├── models/               # Data models
│   ├── utils/                # Utility functions
│   ├── config.py             # Configuration management
│   └── main.py               # Application entry point
│
├── frontend/                  # Next.js frontend application
│   ├── app/                  # Next.js app directory
│   ├── src/                  # Source code
│   │   ├── components/       # React components
│   │   ├── lib/             # Utility libraries
│   │   ├── types/           # TypeScript types
│   │   └── hooks/           # Custom React hooks
│   └── public/               # Static assets
│
├── data/                      # Data directory
│   ├── knowledge_base/       # PDF documents
│   └── vector_db/            # Vector database storage
│
├── docs/                      # Documentation
├── scripts/                   # Utility scripts
├── tests/                     # Test files
│
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Python project configuration
└── README.md                 # This file
```

## Technology Stack

### Backend
- **Framework**: FastAPI
- **LLM Provider**: Cohere (command-r-plus-08-2024)
- **Vector Database**: ChromaDB
- **Embeddings**: HuggingFace (sentence-transformers/all-MiniLM-L6-v2)
- **Document Processing**: PyPDF, Tesseract OCR, EasyOCR
- **Language**: Python 3.10+

### Frontend
- **Framework**: Next.js 14.2.0
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **HTTP Client**: Axios

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI - Modern, fast web framework
- **LLM Provider**: Cohere (command-r-plus-08-2024) - Powerful language model
- **Vector Database**: ChromaDB - Efficient similarity search
- **Embeddings**: HuggingFace (sentence-transformers/all-MiniLM-L6-v2)
- **Document Processing**: PyPDF, Tesseract OCR, EasyOCR
- **Language**: Python 3.10+

### Frontend
- **Framework**: Next.js 14.2.0 - React framework
- **Language**: TypeScript - Type-safe JavaScript
- **Styling**: Tailwind CSS - Utility-first CSS
- **Animations**: Framer Motion - Smooth UI animations
- **HTTP Client**: Axios - Promise-based HTTP client
- **Markdown**: react-markdown - Render formatted responses

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Choose your LLM provider
LLM_PROVIDER=cohere          # Options: cohere, groq, openai

# API Keys (get from respective platforms)
COHERE_API_KEY=your-key-here
GROQ_API_KEY=your-key-here   # Optional, for faster responses

# Self-Reflection (improves quality but adds 2-3 seconds)
ENABLE_REFLECTION=false      # Set to 'true' for better answers

# OCR Path (optional, if tesseract not in system PATH)
# TESSERACT_PATH=/usr/bin/tesseract
```

### Performance Tuning

Edit `config.py` to adjust performance:

```python
# Vector Search Settings
CHUNK_SIZE = 500              # Smaller = faster, larger = more context
CHUNK_OVERLAP = 50            # Overlap between chunks
TOP_K_RESULTS = 1             # Number of docs to retrieve (1 = fastest)
SIMILARITY_THRESHOLD = 0.15   # Lower = more results, higher = more selective

# LLM Settings
temperature = 0.1             # Lower = focused, higher = creative
max_tokens = 256              # Shorter = faster responses
```

## 📚 Usage Guide

### Adding Documents

```bash
# Add PDFs to knowledge base
cp your-file.pdf data/knowledge_base/

# Restart backend to index new documents
./stop.sh
./start.sh
```

### Using Self-Reflection

Self-reflection improves answer quality by validating responses:

```bash
# Enable in .env
ENABLE_REFLECTION=true

# Restart services
./stop.sh && ./start.sh
```

**Trade-offs:**
- ✅ Better, more accurate answers
- ✅ Catches incomplete responses
- ⚠️ Adds 2-3 seconds to response time
- ⚠️ Doubles LLM API usage

### Switching LLM Providers

```bash
# Edit .env
LLM_PROVIDER=groq  # Change to groq for 10x faster responses

# Restart backend
./stop.sh && ./start.sh
```

**Provider Comparison:**
- **Cohere**: Best balance, reliable, good free tier
- **Groq**: 10x faster, requires valid API key
- **OpenAI**: Most capable, costs more

## 🔧 API Reference

### Initialize Assistant
```bash
POST /api/initialize
```
Loads the knowledge base and prepares the assistant.

**Response:**
```json
{
  "status": "initialized",
  "stats": {
    "documents": 1819,
    "pdfs": 3
  }
}
```

### Send Message
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "What is a data warehouse?"
}
```

**Response:**
```json
{
  "answer": "A data warehouse is...",
  "source_type": "knowledge_base",
  "sources": [
    {
      "title": "Source: document.pdf",
      "page": "Page 38",
      "content": "...",
      "relevance_score": "53.78%",
      "extraction_method": "DIRECT"
    }
  ]
}
```

### Clear Chat History
```bash
POST /api/clear
```

### Get Status
```bash
GET /api/status
```

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill existing process
kill -9 <PID>

# Restart
./start.sh
```

### Frontend won't start

```bash
# Check if port 3000 is in use
lsof -i :3000

# Kill and restart
cd frontend
npm run dev
```

### No documents found

```bash
# Verify PDFs are in correct location
ls data/knowledge_base/

# Check logs
tail -f logs/app.log
```

### OCR not working

```bash
# Install Tesseract (Ubuntu/Debian)
sudo apt-get install tesseract-ocr

# Install Tesseract (macOS)
brew install tesseract

# Install Tesseract (Windows)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### API key errors

```bash
# Verify .env file exists
ls -la .env

# Check API key is set correctly
grep COHERE_API_KEY .env

# Make sure no extra spaces or quotes
# Correct: COHERE_API_KEY=abc123
# Wrong: COHERE_API_KEY = "abc123"
```

## 📊 Logs

View application logs:

```bash
# All logs
tail -f logs/app.log

# Errors only
tail -f logs/error.log

# API logs
tail -f api.log

# Follow logs in real-time
tail -f logs/app.log | grep -E "(ERROR|WARNING|Question)"
```

## 🎯 Development

### Running Tests

```bash
# Run Python tests
pytest tests/

# Run with coverage
pytest --cov=backend tests/
```

### Code Quality

```bash
# Format Python code
black backend/

# Lint Python code
pylint backend/

# Type check
mypy backend/

# Format frontend code
cd frontend
npm run lint
```

### Project Architecture

```
┌─────────────┐
│  Frontend   │  Next.js + React
│   (Port     │  
│   3000)     │
└──────┬──────┘
       │ HTTP/REST
       ↓
┌─────────────┐
│  Backend    │  FastAPI
│   (Port     │  
│   8000)     │
└──────┬──────┘
       │
   ┌───┴────┬────────┬─────────┐
   ↓        ↓        ↓         ↓
┌──────┐ ┌─────┐ ┌──────┐ ┌────────┐
│ LLM  │ │Vector│ │ OCR  │ │  PDF   │
│Cohere│ │ DB   │ │Tess. │ │Process │
└──────┘ └─────┘ └──────┘ └────────┘
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Cohere** - For the powerful LLM API
- **LangChain** - For the RAG framework
- **ChromaDB** - For vector storage
- **Vercel** - For Next.js framework

## 📞 Support

- **Issues**: https://github.com/gaurav-163/Personal-Knowledge-Assistant/issues
- **Documentation**: See `/Docs` folder
- **Logs**: Check `logs/app.log` for debugging

## 🗺️ Roadmap

- [ ] Multi-user support with authentication
- [ ] Document upload via web interface
- [ ] Support for more file types (DOCX, TXT, MD)
- [ ] Advanced filtering and search
- [ ] Export conversations
- [ ] Mobile-responsive design improvements
- [ ] Docker containerization
- [ ] Cloud deployment guides

---

**Made with ❤️ by [Gaurav](https://github.com/gaurav-163)**

*Star ⭐ this repo if you find it helpful!*
