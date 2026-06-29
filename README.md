# LAB: Prompt Engineering & Agents avec LangChain
## Master SDIA - Prof. RETAL SARA

Complete guide for setting up and running the Prompt Engineering and LangChain Agents labs.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Prerequisites](#-prerequisites)
- [Quick Start (5 minutes)](#-quick-start-5-minutes)
- [Detailed Installation](#-detailed-installation)
- [Download Ollama Models](#-download-ollama-models)
- [Run the Notebooks](#-run-the-notebooks)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)

---

## 🎯 Project Overview

This project contains two comprehensive lab notebooks:

1. **TP_Prompt_Engineering.ipynb** - Prompt Engineering fundamentals
   - Tokenization with Tiktoken
   - Working with Ollama, Groq, and OpenAI LLMs
   - Multi-modal LLMs (image generation & description)

2. **TP_Agents_Langchain.ipynb** - Building Intelligent Agents
   - Creating agents with LangChain
   - System messages and few-shot learning
   - Structured responses with Pydantic
   - Custom tools and web search
   - Memory management
   - Practical TP: Personal Chef Agent

---

## ✅ Prerequisites

Before starting, ensure you have:

- **Python** 3.10 or higher
- **UV** (modern Python package manager)
- **Ollama** (for local LLM models)
- **Git** (optional, for cloning)

### Check what you have:

```bash
python --version      # Should be 3.10+
uv --version          # Should be installed
ollama --version      # Should be installed
```

---

## 🚀 Quick Start (5 minutes)

### 1️⃣ Clone or Download the Project

```bash
# If you have git
git clone <your-repo-url>
cd langchainPrompt

# Or just create a new folder
mkdir langchainPrompt
cd langchainPrompt
```

### 2️⃣ Install UV (if not already installed)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3️⃣ Create Virtual Environment

```bash
# Initialize and create virtual environment
uv venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 4️⃣ Install Python Dependencies

```bash
uv add langchain langchain-ollama langchain-core langchain-groq langchain-openai \
        python-dotenv pydantic tiktoken tavily-python langgraph ipkernel
```

### 5️⃣ Start Ollama (in a separate terminal)

```bash
ollama serve
```

### 6️⃣ Download a Model (in another terminal)

```bash
# Recommended model (2GB, fast)
ollama pull llama3.2:3b

# Or choose an alternative:
ollama pull mistral      # Very fast
ollama pull gemma        # Great quality
ollama pull phi          # Ultra-lightweight
```

### 7️⃣ Run Jupyter

```bash
# In the original terminal (with venv activated)
jupyter notebook

# Or use VSCode with Python extension
code .
```

Open `TP_Agents_Langchain.ipynb` or `TP_Prompt_Engineering.ipynb`

---

## 📦 Detailed Installation

### Step 1: System Setup

#### macOS/Linux

```bash
# Update package manager
# macOS with Homebrew:
brew update

# Linux (Ubuntu/Debian):
sudo apt update && sudo apt upgrade -y
```

#### Windows

```powershell
# Update Windows (via Settings > Update & Security)
# Or use Windows Package Manager:
winget install Python.Python.3.12
```

### Step 2: Install UV

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
uv --version
```

**Windows (PowerShell as Administrator):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv --version
```

Verify installation:
```bash
uv --version    # Should show version number
```

### Step 3: Create Project Folder

```bash
mkdir langchainPrompt
cd langchainPrompt
```

### Step 4: Initialize with UV

```bash
# Create virtual environment
uv venv

# Activate it
# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

You should see `(.venv)` in your terminal prompt.

### Step 5: Install Dependencies

```bash
# Install all required packages in one command
uv add \
    langchain \
    langchain-ollama \
    langchain-core \
    langchain-groq \
    langchain-openai \
    python-dotenv \
    pydantic \
    tiktoken \
    tavily-python \
    langgraph \
    ipkernel \
    jupyter \
    notebook

# For RAG labs (PDF, Embeddings, Vector Stores)
uv add \
    langchain-community \
    langchain-text-splitters \
    langchain-huggingface \
    sentence-transformers \
    pypdf \
    faiss-cpu
```

This creates `pyproject.toml` and `uv.lock` files automatically.

### Step 6: Verify Installation

```bash
python --version
pip list | grep langchain
```

---

## 🦙 Download Ollama Models

### Install Ollama

Visit https://ollama.ai and download the installer for your OS.

### Start Ollama Server

**Terminal 1** (Keep this open while working):

```bash
ollama serve
```

You should see:
```
Loaded weights...
Model loaded successfully
```

### Download Models

**Terminal 2** (New terminal, venv activated):

#### Recommended Model (2GB - Best for this lab)

```bash
ollama pull llama3.2:3b
```

Wait for completion. You'll see:
```
pulling manifest
pulling layer [=====>] 100%
verifying sha256 digest
writing manifest
success
```

#### Alternative Models

```bash
# Fast and lightweight
ollama pull mistral

# Google's model - Great quality
ollama pull gemma

# Ultra-lightweight (if low resources)
ollama pull phi

# Best for conversations
ollama pull neural-chat
```

### Verify Models

```bash
# List all downloaded models
ollama list

# Test a model quickly
ollama run llama3.2:3b "Bonjour, comment ça va?"
```

You should get a response in French.

---

## 📊 Download Chinook Database (for SQL Agent Lab)

The SQL Agent lab uses the Chinook sample database. Here's how to get it:

### Option 1: Direct Download (Recommended)

```bash
# macOS/Linux:
curl -o Chinook.db https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite

# Windows (PowerShell):
Invoke-WebRequest -Uri "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite" -OutFile "Chinook.db"
```

### Option 2: Manual Download

1. Visit: https://github.com/lerocha/chinook-database
2. Go to: `ChinookDatabase/DataSources/Chinook_Sqlite.sqlite`
3. Click "Download raw file"
4. Save as `Chinook.db` in your project folder

### Option 3: Create Your Own SQLite Database

```bash
# Create an empty SQLite database
sqlite3 my_database.db

# Or use Python:
python -c "import sqlite3; conn = sqlite3.connect('my_database.db'); conn.close()"
```

### Verify Database

```bash
# Check if Chinook.db exists
ls -la Chinook.db      # macOS/Linux
dir Chinook.db         # Windows

# Check tables (optional)
sqlite3 Chinook.db ".tables"
```

---

## 📓 Run the Notebooks

### Option 1: Jupyter Notebook (Recommended for beginners)

```bash
# Make sure (.venv) is activated
# Terminal should show: (.venv) $ or (.venv) >

jupyter notebook
```

A browser window will open. Click on:
- `TP_Agents_Langchain.ipynb` - For the agents lab
- `TP_Prompt_Engineering.ipynb` - For prompt engineering

### Option 2: Jupyter Lab (More features)

```bash
uv add jupyterlab
jupyter lab
```

### Option 3: VSCode (Best IDE experience)

```bash
# Install VSCode if not done:
# Visit: https://code.visualstudio.com

# Open current folder in VSCode
code .

# In VSCode:
# 1. Install Python extension
# 2. Click "Run" on cells
# 3. Select kernel: .venv/bin/python
```

### Option 4: Command Line (Python directly)

```bash
# Run a specific notebook programmatically
python -m nbconvert --to notebook --execute TP_Agents_Langchain.ipynb
```

---

## 🔧 Troubleshooting

### ❌ Error: `Connection refused` / `[Errno 111]`

**Cause**: Ollama is not running

**Solution**:
```bash
# Terminal 1: Start Ollama
ollama serve

# Wait for "Loaded weights..." message
# Keep this terminal open
```

### ❌ Error: `ModuleNotFoundError: No module named 'langchain'`

**Cause**: Virtual environment not activated or packages not installed

**Solution**:
```bash
# Check if (.venv) is in your prompt
# If not, activate it:

# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

# Then reinstall:
uv add langchain langchain-ollama langchain-core
```

### ❌ Error: `Model 'llama3.2:3b' not found`

**Cause**: Model not downloaded

**Solution**:
```bash
# List what you have
ollama list

# Download the model
ollama pull llama3.2:3b

# Try an alternative if that fails:
ollama pull mistral
```

### ❌ Error: `Port 11434 already in use`

**Cause**: Ollama already running

**Solution**:
```bash
# Check if Ollama is running elsewhere
# Kill the process and restart:

# macOS/Linux:
pkill -f "ollama serve"
ollama serve

# Windows:
taskkill /IM ollama.exe /F
ollama serve
```

### ❌ Error: `Permission denied` on `.venv/Scripts/activate`

**Cause**: Permission issue on Windows

**Solution**:
```powershell
# Run PowerShell as Administrator:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate:
.venv\Scripts\activate
```

---

## 📁 Project Structure

```
langchainPrompt/
├── README.md                              # This file
├── .env                                   # Environment variables (create manually)
├── pyproject.toml                         # UV project config (auto-generated)
├── uv.lock                                # Dependency lock file (auto-generated)
├── .venv/                                 # Virtual environment (created by UV)
│
├── TP_Prompt_Engineering.ipynb            # Lab 1: Prompt Engineering
│   ├── Setup section
│   ├── Tokenization with Tiktoken
│   ├── Ollama LLMs
│   ├── Groq LLMs
│   ├── OpenAI LLMs
│   └── Multi-modal LLMs
│
├── TP_Agents_Langchain.ipynb              # Lab 2: Agents with LangChain
│   ├── Setup & Troubleshooting
│   ├── Basic agents
│   ├── System messages & Few-shot learning
│   ├── Structured responses
│   ├── Custom tools
│   ├── Web search tools
│   ├── Memory management
│   └── Practical TP: Personal Chef Agent
│
└── TP_RAG_Agent.ipynb                     # Lab 3: RAG & SQL Agents
    ├── Part 1: PDF RAG
    │   ├── PDF Loading with PyPDFLoader
    │   ├── Text Segmentation
    │   ├── Embedding Generation
    │   ├── Vector Store Indexing
    │   ├── Semantic Search
    │   └── RAG Agent Creation
    │
    └── Part 2: SQL Agent
        ├── SQLite Connection
        ├── Custom SQL Tools
        ├── SQL Agent Creation
        └── Natural Language Querying

# Data Files (Optional - Place in project root)
├── your_document.pdf                      # Your PDF for RAG (optional)
└── Chinook.db                             # SQLite database for SQL Agent (optional)
```

---

## 🔑 Environment Variables (Optional)

Create a `.env` file in the project root for API keys:

```bash
# .env file
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
TAVILY_API_KEY=tvly_...
```

Load in Python:
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

---

## 📊 Quick Reference Commands

### Virtual Environment

```bash
# Activate
source .venv/bin/activate          # macOS/Linux
.venv\Scripts\activate              # Windows

# Deactivate
deactivate
```

### UV Package Manager

```bash
# Add packages
uv add package_name

# Remove packages
uv remove package_name

# List installed packages
uv pip list

# Update all packages
uv pip install --upgrade -r requirements.txt
```

### Ollama Commands

```bash
# Start server
ollama serve

# Download model
ollama pull model_name

# List models
ollama list

# Test model
ollama run model_name "Your prompt"

# Remove model
ollama rm model_name
```

### Jupyter

```bash
# Start notebook
jupyter notebook

# Start lab
jupyter lab

# Run specific notebook
jupyter notebook TP_Agents_Langchain.ipynb

# Convert to different format
jupyter nbconvert --to pdf TP_Agents_Langchain.ipynb
```

---

## 🎓 Learning Path

### For Beginners:

1. Start with `TP_Prompt_Engineering.ipynb`
   - Understand tokenization
   - Learn how LLMs work
   - Simple prompt examples

2. Then move to `TP_Agents_Langchain.ipynb`
   - Start with "Basic agent creation"
   - Progress through system messages
   - Try the "Personal Chef" exercise

3. Finally `TP_RAG_Agent.ipynb`
   - Start with PDF RAG (Part 1)
   - Understand vector stores and embeddings
   - Then explore SQL agents (Part 2)

### For Advanced:

1. Combine all three notebooks
2. Create custom agents with multiple tools
3. Build hybrid RAG systems (PDF + SQL)
4. Integrate with production databases
5. Implement persistent vector stores (FAISS)

---

## 📚 Additional Resources

- **LangChain Documentation**: https://python.langchain.com
- **Ollama Models**: https://ollama.ai/library
- **Python UV Guide**: https://docs.astral.sh/uv/
- **Jupyter Tips**: https://jupyter.org/documentation

---

## 💡 Tips & Best Practices

1. **Keep Ollama Running**: Always have `ollama serve` in a separate terminal

2. **Use Virtual Environments**: Never skip this step
   ```bash
   source .venv/bin/activate
   ```

3. **Monitor Memory**: Some models are large (2-5GB)
   ```bash
   # Check available disk space
   df -h              # macOS/Linux
   dir                # Windows
   ```

4. **Test Models First**: Before using in notebooks
   ```bash
   ollama run llama3.2:3b "test"
   ```

5. **Save Your Work**: Notebooks auto-save, but also commit to git
   ```bash
   git add .
   git commit -m "Lab progress"
   git push
   ```

---

## 🐛 Report Issues

If you encounter problems:

1. Check the **Troubleshooting** section above
2. Verify Ollama is running: `ollama list`
3. Check virtual environment is active: `(.venv)` in prompt
4. Review the **Setup** section in the notebooks

---

## 📝 Notes

- **Ollama must be running** while using the notebooks
- **First model download takes time** (5-15 minutes depending on internet)
- **Some models need 2-5GB** of free disk space
- **Memory usage**: Running models uses RAM (typical: 2-4GB)

---

## ✨ Quick Setup Script (All-in-One)

Save as `setup.sh` (macOS/Linux) and run:

```bash
#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Setting up LangChain Lab...${NC}\n"

# 1. Create virtual environment
echo -e "${BLUE}📦 Creating virtual environment...${NC}"
uv venv

# 2. Activate virtual environment
echo -e "${BLUE}✅ Activating virtual environment...${NC}"
source .venv/bin/activate

# 3. Install dependencies
echo -e "${BLUE}📚 Installing dependencies...${NC}"
uv add langchain langchain-ollama langchain-core langchain-groq langchain-openai \
        python-dotenv pydantic tiktoken tavily-python langgraph ipkernel jupyter

# 4. Verify installation
echo -e "${BLUE}✔️ Verifying installation...${NC}"
python --version
pip list | grep langchain

echo -e "${GREEN}✨ Setup complete!${NC}"
echo -e "\nNext steps:"
echo -e "1. Start Ollama: ${BLUE}ollama serve${NC}"
echo -e "2. Download model: ${BLUE}ollama pull llama3.2:3b${NC}"
echo -e "3. Run notebook: ${BLUE}jupyter notebook${NC}"
```

Run it:
```bash
chmod +x setup.sh
./setup.sh
```

---

## 📞 Support

For questions or issues:
- Review the Troubleshooting section
- Check notebook's built-in help cells
- Consult LangChain documentation
- Check Ollama documentation

---

**Happy Learning! 🎓**

Last updated: June 2026