# 🚀 Quick Installation Guide

Get your Personal Knowledge Assistant running in 5 minutes!

## 📋 Prerequisites Checklist

Before you start, make sure you have:

- [ ] Python 3.10 or higher installed
- [ ] Node.js 18 or higher installed
- [ ] A Cohere API key (free tier available)
- [ ] Your PDF documents ready

---

## 🎯 Step-by-Step Installation

### 1️⃣ Download the Project

```bash
# Clone the repository
git clone https://github.com/gaurav-163/Personal-Knowledge-Assistant.git

# Navigate to project directory
cd Personal-Knowledge-Assistant
```

### 2️⃣ Get Your API Key

1. Go to https://dashboard.cohere.com/api-keys
2. Sign up for a free account
3. Copy your API key (starts with something like: `8gkslUhj2z...`)
4. Keep it safe - you'll need it in the next step!

### 3️⃣ Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Open .env in your favorite editor
nano .env
# or
code .env
# or
vim .env
```

**Edit the `.env` file:**

```bash
# Change this line:
COHERE_API_KEY=your-cohere-api-key-here

# To your actual key:
COHERE_API_KEY=8gkslUhj2zcmmVolGkN1pgcp0grbr69xfBI7Af0d

# Save and close the file
```

### 4️⃣ Install Dependencies

```bash
# Install Python packages (this may take 2-3 minutes)
pip install -r requirements.txt

# Install frontend packages
cd frontend
npm install
cd ..
```

**Troubleshooting:**
- If `pip` doesn't work, try `pip3`
- If `npm` is slow, try: `npm install --legacy-peer-deps`

### 5️⃣ Add Your Documents

```bash
# Your PDFs should go here:
# data/knowledge_base/

# Copy your documents
cp /path/to/your/documents/*.pdf data/knowledge_base/

# Example:
cp ~/Downloads/research-paper.pdf data/knowledge_base/
cp ~/Documents/book.pdf data/knowledge_base/
```

**Supported formats:**
- ✅ PDF (digital)
- ✅ PDF (scanned - uses OCR)
- ❌ Word documents (convert to PDF first)
- ❌ Images (convert to PDF first)

### 6️⃣ Start the Application

```bash
# Start backend (this will also start frontend if needed)
./start.sh

# Wait for this message:
# ✓ Personal Knowledge Assistant is ready!
# ✓ Access points:
#   • API Backend: http://localhost:8000
#   • Frontend: http://localhost:3000
```

**First time setup:**
- Backend starts: ~5 seconds
- Processing PDFs: ~10-30 seconds (depends on size)
- Frontend starts: ~10 seconds

### 7️⃣ Open in Browser

```bash
# Manually open:
http://localhost:3000

# Or use command line:
# macOS
open http://localhost:3000

# Linux
xdg-open http://localhost:3000

# Windows
start http://localhost:3000
```

### 8️⃣ Start Chatting!

1. Wait for the green "Ready" indicator in the top right
2. Type your question in the input box
3. Press Enter or click Send
4. Get your answer in 2-3 seconds!

**Try these example questions:**
- "What is [topic from your PDF]?"
- "Summarize the main points"
- "Explain [concept from your documents]"
- "What is Python?" (general knowledge)

---

## 🛑 Stopping the Application

```bash
# Stop all services
./stop.sh
```

---

## ⚠️ Common Issues & Fixes

### Issue: "Port 8000 already in use"

```bash
# Find and kill the process
lsof -i :8000
kill -9 <PID>

# Restart
./start.sh
```

### Issue: "Module not found" errors

```bash
# Reinstall Python dependencies
pip install -r requirements.txt --force-reinstall

# Or create a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Issue: "API key invalid"

```bash
# Check your .env file
cat .env | grep COHERE_API_KEY

# Make sure:
# 1. No extra spaces
# 2. No quotes around the key
# 3. Key is correct from Cohere dashboard

# Correct format:
COHERE_API_KEY=8gkslUhj2zcmmVolGkN1pgcp0grbr69xfBI7Af0d

# Wrong format:
COHERE_API_KEY = "8gkslUhj2zcmmVolGkN1pgcp0grbr69xfBI7Af0d"
```

### Issue: "No documents found"

```bash
# Check if PDFs are in the right location
ls -la data/knowledge_base/

# Make sure:
# 1. Files are .pdf extension
# 2. Directory path is correct
# 3. Files are readable

# Restart to reindex
./stop.sh
./start.sh
```

### Issue: Frontend won't load

```bash
# Check if it's running
curl http://localhost:3000

# If not, start it manually
cd frontend
npm run dev

# In a new terminal, keep frontend running
```

### Issue: Slow responses

```bash
# Option 1: Disable self-reflection (in .env)
ENABLE_REFLECTION=false

# Option 2: Use Groq (faster, needs valid key)
LLM_PROVIDER=groq
GROQ_API_KEY=your-groq-key

# Restart
./stop.sh && ./start.sh
```

---

## 🎓 What's Next?

### Learn More
- Read the full [README.md](README.md)
- Check the [Self-Reflection Guide](Docs/SELF_REFLECTION.md)
- Explore [API Documentation](http://localhost:8000/docs)

### Customize
- Adjust performance settings in `config.py`
- Change UI colors in `frontend/app/page.tsx`
- Add more LLM providers

### Advanced Features
- Enable self-reflection for better answers
- Add more documents dynamically
- Export conversations
- Monitor logs for debugging

---

## 💡 Tips for Best Results

1. **Quality Documents**: Use clear, well-formatted PDFs
2. **Specific Questions**: Ask focused questions for better answers
3. **Check Sources**: Review the source citations for accuracy
4. **Clear History**: Use "Clear all history" button to start fresh
5. **Monitor Logs**: Check `logs/app.log` if something seems off

---

## 📞 Need Help?

- **Logs**: `tail -f logs/app.log`
- **Errors**: `tail -f logs/error.log`
- **Issues**: https://github.com/gaurav-163/Personal-Knowledge-Assistant/issues

---

**Happy chatting! 🎉**
