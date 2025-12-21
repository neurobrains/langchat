<div align="center">
<img src="docs/public/logo-sidebar.png" alt="Lagchat-logo">

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

<p>
  Most AI frameworks are great for experiments but require massive boilerplate for production. LangChat handles the "hard parts" out of the box so you can focus on building features.
</p>


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
      <td>Days/Weeks</td>
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

<pre><code>pip install langchat</code></pre>


---

## 🚀 Quick Start

### Step 1: Set Environment Variables

```bash
export OPENAI_API_KEYS="sk-...,sk-..."
export PINECONE_API_KEY="your-key"
export PINECONE_INDEX_NAME="your-index"
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_KEY="your-key"
```

### Step 2: Build and run a production-ready agent in just a few lines of code

```python
import asyncio
from langchat import LangChat, LangChatConfig

async def main():
    # Load configuration from environment variables
    config = LangChatConfig.from_env()
    
    # Initialize LangChat
    ai = LangChat(config=config)
    
    # Chat with the AI
    # Note: Response is automatically displayed in a Rich panel
    result = await ai.chat(
        query="Hello! What can you help me with?",
        user_id="user123",
        domain="general"
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### As API Server

```python
from langchat.api.app import create_app
from langchat.config import LangChatConfig
import uvicorn

config = LangChatConfig.from_env()

app = create_app(
    config=config,
    auto_generate_interface=True,
    auto_generate_docker=True
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config.server_port)
```

---

## Use Cases

| Education            | E-commerce | E-commerce |
|----------------------|----------------------|----------------------|
| Intelligent tutoring and course Q&A | Customer support and product discovery | Internal knowledge base search |

---

## Roadmap & Contributing

<p> We are building the future of conversational AI infrastructure. </p>

 - <p>Contributing: We welcome PRs! Please check <a href="CONTRIBUTING.md">CONTRIBUTING.md</a>.</p>

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
