<div align="center">
<img src="https://raw.githubusercontent.com/neurobrains/langchat/main/docs/public/logo-sidebar.png" alt="LangChat logo">

<h2>Ship production-grade AI chatbots in minutes</h2>

<p>
  <strong>LangChat</strong> is a high-performance Python library designed to bridge the gap between "prototype" and "production." It unifies LLMs, vector databases, and session management into a single, modular interface.
</p>

<p>
  <a href="https://langchat.neurobrains.co/"><strong>Explore the Docs</strong></a>
</p>

</div>

---

## Why LangChat?

Most AI frameworks are great for experiments but require massive boilerplate for production. LangChat handles the "hard parts" out of the box so you can focus on building features.

<table>
  <thead>
    <tr>
      <th>Feature</th>
      <th>LangChat</th>
      <th>Other Libraries</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Setup Time</strong></td>
      <td>Minutes</td>
      <td>Days / Weeks</td>
    </tr>
    <tr>
      <td><strong>API Key Rotation</strong></td>
      <td>Built-in</td>
      <td>Manual</td>
    </tr>
    <tr>
      <td><strong>Chat History</strong></td>
      <td>Automatic</td>
      <td>Manual</td>
    </tr>
    <tr>
      <td><strong>Vector Search</strong></td>
      <td>Integrated</td>
      <td>Separate</td>
    </tr>
    <tr>
      <td><strong>Reranking</strong></td>
      <td>Built-in</td>
      <td>Manual</td>
    </tr>
    <tr>
      <td><strong>Production Ready</strong></td>
      <td>Yes</td>
      <td>Depends</td>
    </tr>
  </tbody>
</table>

---

## Installation

```bash
pip install langchat
```

---

## Quick Start

### 1 — Set your environment variables

```bash
# .env
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=pc-...
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_KEY=your-key
```

### 2 — Build and chat

```python
from langchat import LangChat
from langchat.providers import OpenAI, Pinecone, Supabase

lc = LangChat(
    llm=OpenAI("gpt-4o"),
    vector_db=Pinecone("my-index"),
    db=Supabase(),
)

# Async
response = await lc.chat("What is RAG?", user_id="alice")
print(response.text)           # typed response — no dict["response"] needed

# Sync (no asyncio boilerplate)
response = lc.chat_sync("Hello!", user_id="alice")
print(response.text)
```

All providers read credentials from the environment automatically. No need to pass keys explicitly unless you want to override them.

---

## Providers

### LLM providers

Every LLM provider follows the same pattern: model as the first argument, everything else keyword-only.

```python
from langchat.providers import OpenAI, Anthropic, Gemini, Mistral, Cohere, Ollama

# Reads OPENAI_API_KEY from environment
OpenAI()
OpenAI("gpt-4o")
OpenAI("gpt-4o", temperature=0.2)
OpenAI(api_keys=["sk-1", "sk-2"])   # automatic key rotation

# Reads ANTHROPIC_API_KEY
Anthropic()
Anthropic("claude-opus-4-6")

# Reads GEMINI_API_KEY or GOOGLE_API_KEY
Gemini()
Gemini("gemini-1.5-pro")

# Reads MISTRAL_API_KEY
Mistral()
Mistral("mistral-large-latest")

# Reads COHERE_API_KEY
Cohere()
Cohere("command-r")

# No API key required — connects to a local Ollama server
Ollama()
Ollama("mistral")
Ollama("codellama", base_url="http://gpu-server:11434")
```

### Vector database

```python
from langchat.providers import Pinecone

# Reads PINECONE_API_KEY and OPENAI_API_KEY (for embeddings)
Pinecone("my-index")
Pinecone("my-index", embedding_model="text-embedding-3-small")
Pinecone("my-index", api_key="pc-...", embedding_api_key="sk-...")
```

### History database

```python
from langchat.providers import Supabase

# Reads SUPABASE_URL and SUPABASE_KEY
Supabase()
Supabase(url="https://yourproject.supabase.co", key="your-key")
```

---

## Typed responses

`chat()` returns a `ChatResponse` dataclass — no more `result["response"]` key lookups.

```python
response = await lc.chat("Summarise the docs", user_id="alice", platform="docs")

response.text           # str   — the answer
response.status         # "success" | "error"
response.response_time  # float — wall-clock seconds
response.timestamp      # str   — ISO-8601
response.user_id        # str
response.platform       # str
response.error          # str | None — set when status == "error"

# Boolean protocol
if response:
    print("OK:", response.text)
else:
    print("Error:", response.error)

# Works directly with print / f-strings
print(response)          # same as print(response.text)
print(f"Answer: {response}")
```

---

## Document indexing

```python
# Single file
lc.index("docs/guide.pdf")

# Multiple files at once
lc.index(["docs/guide.pdf", "docs/api.pdf", "data/faq.csv"])

# With options
lc.index(
    "docs/guide.pdf",
    chunk_size=500,
    chunk_overlap=50,
    namespace="v2",
    prevent_duplicates=True,   # default — safe to call multiple times
)
```

---

## Custom prompt

```python
PROMPT = """You are a helpful assistant for {platform}.
Use only the provided context to answer questions.

Context:
{context}

Chat history:
{chat_history}

Question: {question}
Answer:"""

lc = LangChat(
    llm=OpenAI("gpt-4o"),
    vector_db=Pinecone("my-index"),
    db=Supabase(),
    prompt_template=PROMPT,
)
```

---

## As a FastAPI server

```python
from langchat.api.app import create_app
from langchat.providers import OpenAI, Pinecone, Supabase
import uvicorn

app = create_app(
    llm=OpenAI("gpt-4o"),
    vector_db=Pinecone("my-index"),
    db=Supabase(),
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Endpoints exposed automatically:

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/chat` | Send a message |
| `GET`  | `/health` | Health check |
| `GET`  | `/frontend` | Serves the built-in UI |

---

## Use Cases

| Education | E-commerce | Enterprise |
|-----------|------------|------------|
| Intelligent tutoring and course Q&A | Customer support and product discovery | Internal knowledge base search |

---

## Roadmap & Contributing

We are building the future of conversational AI infrastructure.

- Contributing: We welcome PRs! Please check [CONTRIBUTING.md](CONTRIBUTING.md).

---

<div align="center" style="margin-top: 40px; padding: 20px; background-color: #f5f5f5; border-radius: 10px;">

<p style="font-size: 20px; margin: 0;">
  <strong>Built with ❤️ by <a href="https://neurobrain.co">NeuroBrain</a></strong>
</p>

<p style="margin-top: 15px;">
  <a href="https://github.com/neurobrains/langchat">GitHub</a> •
  <a href="https://pypi.org/project/langchat/">PyPI</a> •
  <a href="https://langchat.neurobrains.co/">Documentation</a>
</p>

</div>
