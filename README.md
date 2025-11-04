# LangChat

<div align="center">

<h2>🚀 Production-ready AI chatbots in minutes, not months</h2>

<p>
  <a href="https://pypi.org/project/langchat/">
    <img src="https://badge.fury.io/py/langchat.svg" alt="PyPI version" />
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+" />
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" />
  </a>
</p>

<p>
  <strong>A powerful, modular conversational AI library</strong> with vector search capabilities, designed to help developers build production-ready AI chatbots with minimal effort.
</p>

<p>
  <a href="https://langchat.neurobrains.co/"><strong>📖 Full Documentation →</strong></a> • 
  <a href="https://github.com/neurobrains/langchat"><strong>⭐ GitHub</strong></a> • 
  <a href="https://pypi.org/project/langchat/"><strong>📦 PyPI</strong></a>
</p>

</div>

---

## 🎯 What is LangChat?

<p>
  <strong>LangChat</strong> is a production-ready conversational AI library that simplifies building intelligent chatbots with vector search capabilities. Instead of juggling multiple libraries, API integrations, vector databases, and chat history management, LangChat provides a unified, modular architecture that handles all these concerns out of the box.
</p>

<div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; border-left: 4px solid #2196F3;">
<strong>💡 Key Insight:</strong> LangChat combines the power of LLMs (Large Language Models), vector search, and conversation management into one easy-to-use library.
</div>

---

## 🎯 Why LangChat?

<p>Building production-ready conversational AI systems is complex. You need to:</p>

<ul>
  <li><strong>Integrate LLM APIs</strong> (OpenAI, Anthropic, etc.)</li>
  <li><strong>Manage Vector Databases</strong> (Pinecone, Weaviate, etc.)</li>
  <li><strong>Handle Chat History</strong> (conversation context and memory)</li>
  <li><strong>Implement Reranking</strong> (improve search result relevance)</li>
  <li><strong>Track Metrics</strong> (response times, errors, feedback)</li>
  <li><strong>Rotate API Keys</strong> (handle rate limits and failures)</li>
</ul>

<p><strong>LangChat simplifies all of this</strong> by providing a complete solution out of the box.</p>

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
      <td>⚡ Minutes</td>
      <td>⏳ Days/Weeks</td>
    </tr>
    <tr>
      <td><strong>API Key Rotation</strong></td>
      <td>✅ Built-in</td>
      <td>❌ Manual</td>
    </tr>
    <tr>
      <td><strong>Chat History</strong></td>
      <td>✅ Automatic</td>
      <td>⚠️ Manual</td>
    </tr>
    <tr>
      <td><strong>Vector Search</strong></td>
      <td>✅ Integrated</td>
      <td>⚠️ Separate</td>
    </tr>
    <tr>
      <td><strong>Reranking</strong></td>
      <td>✅ Built-in</td>
      <td>❌ Manual</td>
    </tr>
    <tr>
      <td><strong>Production Ready</strong></td>
      <td>✅ Yes</td>
      <td>⚠️ Depends</td>
    </tr>
  </tbody>
</table>

---

## ✨ Key Features

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 20px 0;">

<div style="background-color: #f5f5f5; padding: 15px; border-radius: 8px;">
<h3>🤖 LLM Integration</h3>
<ul>
  <li>OpenAI with automatic key rotation</li>
  <li>Fault-tolerant retry logic</li>
  <li>Production-ready error handling</li>
</ul>
</div>

<div style="background-color: #f5f5f5; padding: 15px; border-radius: 8px;">
<h3>🔍 Vector Search</h3>
<ul>
  <li>Pinecone integration</li>
  <li>Flashrank reranking</li>
  <li>Configurable retrieval</li>
</ul>
</div>

<div style="background-color: #f5f5f5; padding: 15px; border-radius: 8px;">
<h3>💾 Database Management</h3>
<ul>
  <li>Supabase integration</li>
  <li>Automatic ID management</li>
  <li>User session management</li>
</ul>
</div>

<div style="background-color: #f5f5f5; padding: 15px; border-radius: 8px;">
<h3>🎨 Customization</h3>
<ul>
  <li>Custom prompts</li>
  <li>Flexible configuration</li>
  <li>Modular architecture</li>
</ul>
</div>

</div>

---

## 📦 Installation

<pre><code>pip install langchat</code></pre>

<p><strong>Requirements:</strong> Python 3.8+, OpenAI API key(s), Pinecone account, Supabase project</p>

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

### Step 2: Write Your First Chatbot

```python
import asyncio
from langchat import LangChat, LangChatConfig

async def main():
    # Load configuration from environment variables
    config = LangChatConfig.from_env()
    
    # Initialize LangChat
    langchat = LangChat(config=config)
    
    # Chat with the AI
    # Note: Response is automatically displayed in a Rich panel
    result = await langchat.chat(
        query="Hello! What can you help me with?",
        user_id="user123",
        domain="general"
    )

asyncio.run(main())
```

---

## 📚 Examples

### Basic Usage

```python
import asyncio
from langchat import LangChat, LangChatConfig

async def main():
    config = LangChatConfig.from_env()
    langchat = LangChat(config=config)
    
    result = await langchat.chat(
        query="What are the best universities in Europe?",
        user_id="user123",
        domain="education"
    )
    

asyncio.run(main())
```

### Custom Configuration

```python
from langchat import LangChat, LangChatConfig

config = LangChatConfig(
    openai_api_keys=["sk-...", "sk-..."],  # Multiple keys for rotation
    openai_model="gpt-4o-mini",
    pinecone_api_key="pcsk-...",
    pinecone_index_name="my-index",
    supabase_url="https://xxxxx.supabase.co",
    supabase_key="eyJhbGc...",
    system_prompt_template="""You are a helpful assistant.
    
    Context: {context}
    Chat History: {chat_history}
    Question: {question}
    Answer:"""
)

langchat = LangChat(config=config)
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

## 🌐 API Endpoints

<p>When running as an API server:</p>

<ul>
  <li><code>POST /chat</code> - Send a chat message</li>
  <li><code>GET /frontend</code> - Access the chat interface</li>
  <li><code>GET /health</code> - Health check endpoint</li>
</ul>

---

## 💡 Use Cases

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin: 20px 0;">

<div>📚 <strong>Education Chatbots</strong><br/>Help students find universities</div>
<div>✈️ <strong>Travel Assistants</strong><br/>Travel recommendations</div>
<div>🛒 <strong>Customer Support</strong><br/>Answer product questions</div>
<div>💼 <strong>Business Assistants</strong><br/>Knowledge base queries</div>
<div>🎓 <strong>Learning Platforms</strong><br/>Course material Q&A</div>
<div>🏥 <strong>Healthcare</strong><br/>Medical information</div>

</div>

---

## 📖 Documentation

<p>
  For complete documentation, examples, guides, and API reference, visit:
</p>

<div align="center" style="margin: 30px 0;">
  <a href="https://langchat.neurobrains.co/" style="font-size: 18px; font-weight: bold; color: #2196F3; text-decoration: none;">
    📖 https://langchat.neurobrains.co/
  </a>
</div>

<p>The documentation includes:</p>

<ul>
  <li>📘 <a href="https://langchat.neurobrains.co/getting-started">Getting Started Guide</a></li>
  <li>⚙️ <a href="https://langchat.neurobrains.co/guides/configuration">Configuration Guide</a></li>
  <li>📝 <a href="https://langchat.neurobrains.co/api-reference/langchat">API Reference</a></li>
  <li>💡 <a href="https://langchat.neurobrains.co/examples/basic-usage">Examples</a></li>
  <li>🔧 <a href="https://langchat.neurobrains.co/advanced/customization">Advanced Topics</a></li>
</ul>

---

## 🤝 Contributing

<p>We welcome contributions! Please see <a href="CONTRIBUTING.md">CONTRIBUTING.md</a> for guidelines.</p>

<div style="background-color: #fff3cd; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107;">
<strong>⚠️ Important:</strong> All contributions require a <a href="DCO.md">Developer Certificate of Origin (DCO)</a> sign-off.
</div>

---

## 📄 License

<p>This project is licensed under the MIT License - see the <a href="LICENSE">LICENSE</a> file for details.</p>

---

<div align="center" style="margin-top: 40px; padding: 20px; background-color: #f5f5f5; border-radius: 10px;">

<p style="font-size: 20px; margin: 0;">
  <strong>Built with ❤️ by <a href="https://neurobrain.co">NeuroBrain</a></strong>
</p>

<p style="margin-top: 15px;">
  <a href="https://github.com/neurobrains/langchat">⭐ Star us on GitHub</a> • 
  <a href="https://langchat.neurobrains.co/">📖 Read the Docs</a> • 
  <a href="https://github.com/neurobrains/langchat/issues">🐛 Report Issues</a>
</p>

</div>
