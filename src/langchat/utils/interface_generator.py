"""
Auto-generate chat interface HTML file.
"""

import os
from pathlib import Path
from typing import Optional


def generate_chat_interface(
    output_path: str = "chat_interface.html",
    api_url: Optional[str] = None,
    title: str = "LangChat AI",
    subtitle: str = "Your intelligent AI assistant",
    default_user_id: str = "user123",
    default_domain: str = "default",
) -> str:
    """
    Generate chat interface HTML file.

    Args:
        output_path: Path to save the HTML file
        api_url: Default API URL (defaults to http://localhost:8000)
        title: Chat interface title
        subtitle: Chat interface subtitle
        default_user_id: Default user ID
        default_domain: Default domain

    Returns:
        Path to generated file
    """
    if api_url is None:
        api_url = os.getenv("LANGCHAT_API_URL", "http://localhost:8000")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}

        .chat-container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 800px;
            height: 600px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        .chat-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            position: relative;
        }}

        .chat-header h1 {{
            font-size: 1.8em;
            margin-bottom: 5px;
        }}

        .chat-header p {{
            opacity: 0.9;
            font-size: 0.9em;
        }}

        .settings-panel {{
            background: #f8f9fa;
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }}

        .settings-panel input, .settings-panel select {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 0.9em;
            flex: 1;
            min-width: 150px;
        }}

        .settings-panel label {{
            font-weight: 500;
            color: #555;
            font-size: 0.9em;
        }}

        .chat-messages {{
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #fafafa;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}

        .message {{
            max-width: 70%;
            padding: 15px 20px;
            border-radius: 18px;
            position: relative;
            word-wrap: break-word;
            animation: fadeIn 0.3s ease-in;
        }}

        .message.user {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 5px;
        }}

        .message.ai {{
            background: white;
            color: #333;
            align-self: flex-start;
            border-bottom-left-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .message-time {{
            font-size: 0.7em;
            opacity: 0.7;
            margin-top: 5px;
        }}

        .chat-input {{
            background: white;
            padding: 20px;
            border-top: 1px solid #e9ecef;
            display: flex;
            gap: 15px;
            align-items: flex-end;
        }}

        .input-container {{
            flex: 1;
            position: relative;
        }}

        .chat-input textarea {{
            width: 100%;
            padding: 12px 45px 12px 15px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            font-size: 1em;
            resize: none;
            font-family: inherit;
            min-height: 50px;
            max-height: 100px;
            transition: border-color 0.3s;
        }}

        .chat-input textarea:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .send-button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 25px;
            font-size: 1em;
            cursor: pointer;
            transition: transform 0.2s;
            min-width: 80px;
        }}

        .send-button:hover {{
            transform: translateY(-2px);
        }}

        .send-button:disabled {{
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }}

        .typing-indicator {{
            display: none;
            align-self: flex-start;
            background: white;
            padding: 15px 20px;
            border-radius: 18px;
            border-bottom-left-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-width: 70%;
        }}

        .typing-dots {{
            display: flex;
            gap: 4px;
        }}

        .typing-dots span {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #667eea;
            animation: typing 1.4s infinite;
        }}

        .typing-dots span:nth-child(2) {{
            animation-delay: 0.2s;
        }}

        .typing-dots span:nth-child(3) {{
            animation-delay: 0.4s;
        }}

        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes typing {{
            0%, 60%, 100% {{
                transform: translateY(0);
            }}
            30% {{
                transform: translateY(-10px);
            }}
        }}

        @media (max-width: 768px) {{
            .chat-container {{
                height: 100vh;
                border-radius: 0;
                max-width: 100%;
            }}

            .settings-panel {{
                flex-direction: column;
                gap: 10px;
            }}

            .settings-panel input, .settings-panel select {{
                min-width: 100%;
            }}

            .message {{
                max-width: 85%;
            }}

            .chat-input {{
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤖 {title}</h1>
            <p>{subtitle}</p>
        </div>

        <div class="settings-panel">
            <label for="userId">User ID:</label>
            <input type="text" id="userId" placeholder="Enter your user ID" value="{default_user_id}">

            <label for="domain">Domain:</label>
            <select id="domain">
                <option value="{default_domain}" selected>{default_domain.title()}</option>
                <option value="general">General</option>
                <option value="education">Education</option>
                <option value="travel">Travel</option>
            </select>

            <label for="apiUrl">API URL:</label>
            <input type="text" id="apiUrl" placeholder="Enter API URL" value="{api_url}">
        </div>

        <div class="chat-messages" id="chatMessages">
            <div class="message ai">
                <div>👋 Hello! I'm your {title} assistant. How can I help you today?</div>
                <div class="message-time">Just now</div>
            </div>
        </div>

        <div class="typing-indicator" id="typingIndicator">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>

        <div class="chat-input">
            <div class="input-container">
                <textarea
                    id="messageInput"
                    placeholder="Type your message here..."
                    rows="1"
                    onkeypress="handleKeyPress(event)"
                    oninput="autoResize(this)">
                </textarea>
            </div>
            <button class="send-button" onclick="sendMessage()" id="sendButton">
                Send
            </button>
        </div>
    </div>

    <script>
        function autoResize(textarea) {{
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        }}

        function handleKeyPress(event) {{
            if (event.key === 'Enter' && !event.shiftKey) {{
                event.preventDefault();
                sendMessage();
            }}
        }}

        async function sendMessage() {{
            const messageInput = document.getElementById('messageInput');
            const userId = document.getElementById('userId').value;
            const domain = document.getElementById('domain').value;
            const apiUrl = document.getElementById('apiUrl').value;
            const message = messageInput.value.trim();

            if (!message) {{
                return;
            }}

            if (!userId) {{
                alert('Please enter a User ID');
                return;
            }}

            if (!apiUrl) {{
                alert('Please enter API URL');
                return;
            }}

            // Add user message to chat
            addMessage(message, 'user');

            // Clear input
            messageInput.value = '';
            messageInput.style.height = 'auto';

            // Show typing indicator
            showTypingIndicator();

            // Disable send button
            const sendButton = document.getElementById('sendButton');
            sendButton.disabled = true;
            sendButton.textContent = 'Sending...';

            try {{
                // Prepare form data
                const formData = new FormData();
                formData.append('query', message);
                formData.append('userId', userId);
                formData.append('domain', domain);

                // Make API call
                const response = await fetch(`${{apiUrl}}/chat`, {{
                    method: 'POST',
                    body: formData
                }});

                if (!response.ok) {{
                    throw new Error(`HTTP error! status: ${{response.status}}`);
                }}

                const data = await response.json();

                // Hide typing indicator
                hideTypingIndicator();

                // Add AI response to chat
                if (data.status === 'success') {{
                    addMessage(data.response, 'ai');
                }} else {{
                    addMessage('Sorry, I encountered an error while processing your request. Please try again.', 'ai');
                }}

            }} catch (error) {{
                console.error('Error:', error);
                hideTypingIndicator();
                addMessage('Unable to connect to the AI service. Please check your API URL and server status.', 'ai');
            }} finally {{
                // Re-enable send button
                sendButton.disabled = false;
                sendButton.textContent = 'Send';
            }}
        }}

        function addMessage(text, sender) {{
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${{sender}}`;

            const now = new Date();
            const timeStr = now.toLocaleTimeString([], {{ hour: '2-digit', minute: '2-digit' }});

            messageDiv.innerHTML = `<div>${{text}}</div><div class="message-time">${{timeStr}}</div>`;

            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }}

        function showTypingIndicator() {{
            const typingIndicator = document.getElementById('typingIndicator');
            const chatMessages = document.getElementById('chatMessages');

            typingIndicator.style.display = 'block';
            chatMessages.appendChild(typingIndicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }}

        function hideTypingIndicator() {{
            const typingIndicator = document.getElementById('typingIndicator');
            typingIndicator.style.display = 'none';
        }}

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            const messageInput = document.getElementById('messageInput');
            messageInput.focus();

            // Generate random user ID if not set
            if (!document.getElementById('userId').value) {{
                const randomId = 'user_' + Math.random().toString(36).substr(2, 9);
                document.getElementById('userId').value = randomId;
            }}
        }});
    </script>
</body>
</html>"""

    Path(output_path).write_text(html_content, encoding="utf-8")

    return output_path
