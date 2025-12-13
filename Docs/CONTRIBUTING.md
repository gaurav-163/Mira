# 🤝 Contributing to Personal Knowledge Assistant

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Pull Requests](#submitting-pull-requests)
- [Coding Standards](#coding-standards)
- [Testing](#testing)

## 📜 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the issue, not the person
- Help others learn and grow

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git
- A code editor (VS Code recommended)

### Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/Personal-Knowledge-Assistant.git
cd Personal-Knowledge-Assistant

# Add upstream remote
git remote add upstream https://github.com/gaurav-163/Personal-Knowledge-Assistant.git
```

## 🛠️ Development Setup

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black pylint mypy
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Environment Configuration

```bash
# Copy example env
cp .env.example .env

# Add your API keys
# See INSTALLATION.md for details
```

## 🔧 Making Changes

### Branch Naming

Use descriptive branch names:

```bash
# Features
git checkout -b feature/add-export-functionality

# Bug fixes
git checkout -b fix/resolve-ocr-issue

# Documentation
git checkout -b docs/update-readme
```

### Commit Messages

Follow conventional commits:

```bash
# Feature
git commit -m "feat: add export conversation feature"

# Bug fix
git commit -m "fix: resolve PDF processing error"

# Documentation
git commit -m "docs: update installation guide"

# Refactor
git commit -m "refactor: improve vector store performance"

# Test
git commit -m "test: add unit tests for assistant service"
```

## 🧪 Testing

### Python Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=backend tests/

# Run specific test file
pytest tests/test_assistant.py
```

### Frontend Tests

```bash
cd frontend
npm test
npm run lint
```

## 📝 Coding Standards

### Python

```python
# Use type hints
def process_document(file_path: str) -> List[Document]:
    """Process a PDF document and return chunks."""
    pass

# Follow PEP 8
# Use descriptive variable names
document_chunks = []  # Good
dc = []  # Bad

# Add docstrings
def calculate_similarity(query: str, doc: str) -> float:
    """
    Calculate similarity score between query and document.
    
    Args:
        query: Search query string
        doc: Document content
        
    Returns:
        Similarity score between 0 and 1
    """
    pass
```

### TypeScript

```typescript
// Use proper types
interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

// Use descriptive names
const handleSendMessage = () => {  // Good
  // ...
};

const handle = () => {  // Bad
  // ...
};

// Add JSDoc for complex functions
/**
 * Fetches chat response from the API
 * @param message - User message
 * @returns Promise with API response
 */
async function fetchResponse(message: string): Promise<Response> {
  // ...
}
```

## 🔍 Code Review Checklist

Before submitting a PR:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Added tests for new features
- [ ] Documentation updated
- [ ] No console.log or print statements
- [ ] No commented-out code
- [ ] Type hints added (Python)
- [ ] Proper types used (TypeScript)
- [ ] Commit messages are clear

## 📬 Submitting Pull Requests

### PR Title Format

```
feat: Add export conversation feature
fix: Resolve OCR processing error
docs: Update README with new examples
refactor: Improve vector search performance
```

### PR Description Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Manually tested

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No breaking changes
```

### Submission Process

```bash
# 1. Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# 2. Create feature branch
git checkout -b feature/your-feature

# 3. Make changes and commit
git add .
git commit -m "feat: your feature description"

# 4. Push to your fork
git push origin feature/your-feature

# 5. Create Pull Request on GitHub
# Go to your fork on GitHub and click "New Pull Request"
```

## 🎯 Areas to Contribute

### High Priority

- [ ] Add unit tests
- [ ] Improve error handling
- [ ] Add more LLM providers
- [ ] Performance optimizations
- [ ] Mobile responsive design

### Documentation

- [ ] API documentation
- [ ] Code examples
- [ ] Deployment guides
- [ ] Troubleshooting guides

### Features

- [ ] Document upload via UI
- [ ] User authentication
- [ ] Export conversations
- [ ] Advanced search filters
- [ ] Multiple knowledge bases

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Screenshots**
If applicable

**Environment**
- OS: [e.g. Ubuntu 22.04]
- Python version: [e.g. 3.10.5]
- Node version: [e.g. 18.17.0]
- Browser: [e.g. Chrome 120]

**Logs**
```
Paste relevant logs
```
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
Clear description of the feature

**Problem It Solves**
What problem does this solve?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other solutions you've thought about

**Additional Context**
Any other information
```

## 📚 Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [LangChain Docs](https://python.langchain.com/)
- [ChromaDB Docs](https://docs.trychroma.com/)

### Style Guides
- [PEP 8](https://pep8.org/)
- [TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- [Conventional Commits](https://www.conventionalcommits.org/)

## ❓ Questions?

- Open an issue for questions
- Check existing issues first
- Join discussions on GitHub

## 🎉 Thank You!

Every contribution helps make this project better. Thank you for taking the time to contribute!

---

**Happy Coding! 🚀**
