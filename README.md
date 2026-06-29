# 1. Create and navigate to your project folder
mkdir TP_Prompt_Engineering
cd TP_Prompt_Engineering

# 2. Initialize the project with uv
uv init
uv venv

# 3. Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# 4. Install ipkernel for Jupyter
uv add ipkernel

# 5. Install required dependencies
uv add tiktoken langchain langchain-ollama langchain-groq langchain-openai python-dotenv