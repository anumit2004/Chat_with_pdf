# TOME

TOME is a Streamlit application for uploading PDF documents, generating summaries, and chatting with PDF content.

## Features

- Landing page with sign-in and sign-up
- Password-protected local accounts using SQLite
- PDF upload and text extraction
- Automatic PDF summaries
- PDF chat with relevant context retrieval
- Saved PDF library
- Extracted summary view
- Configurable AI providers and models
- Support for OpenRouter, OpenAI, Claude, Grok, NVIDIA, DeepSeek, Kimi, MiniMax, and custom providers
- Dark TOME interface

## Project Structure

```text
Chat_with_pdf/
|-- app.py                 # Landing page and authentication
|-- auth.py                # SQLite account and document storage
|-- pages/
|   `-- home.py            # Authenticated PDF workspace
|-- .streamlit/
|   `-- config.toml        # Streamlit configuration
|-- .gitignore
`-- README.md
```

## Requirements

- Python 3.10 or newer
- Streamlit
- PyPDF
- Requests
- OpenAI Python package

## Installation

From the project directory:

```bash
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install streamlit pypdf requests openai
```

For Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install streamlit pypdf requests openai
```

## Run the Application

Using Git Bash:

```bash
./venv/Scripts/python.exe -m streamlit run app.py --server.port 8502
```

Using Windows Command Prompt:

```bat
venv\Scripts\python.exe -m streamlit run app.py --server.port 8502
```

Open:

```text
http://localhost:8502
```

After signing in, open the workspace at:

```text
http://localhost:8502/home
```

## AI Provider Setup

1. Sign in to TOME.
2. Open **Configure intelligence** in the sidebar.
3. Choose a provider.
4. Paste the API key. API-key fields are masked.
5. Choose or enter a model.
6. Verify and save the provider configuration.

The provider configuration is kept in the current Streamlit session. TOME can also use local PDF context without a verified provider.

For OpenRouter, TOME retrieves available models using the API key and verifies the selected model with a small chat request.

## Local Storage

TOME uses `tome_users.db` for:

- User accounts
- Password hashes and salts
- Saved PDF text
- Generated summaries
- PDF metadata

The database file is local and is excluded from Git. Do not commit passwords, API keys, PDF uploads, or the local database.

## Files to Commit

```text
app.py
auth.py
pages/home.py
.streamlit/config.toml
.gitignore
README.md
```

Do not commit:

```text
venv/
__pycache__/
*.pyc
.env
.env.*
tome_users.db
uploads/
```

## Git Setup

```bash
git add app.py auth.py pages/home.py .streamlit/config.toml .gitignore README.md
git diff --cached --name-only
git commit -m "Create TOME PDF assistant"
git push -u origin main
```
