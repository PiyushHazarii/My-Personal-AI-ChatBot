import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Trash2 } from 'lucide-react';
import './App.css';

const API_BASE = 'http://localhost:8000';

function formatMessageText(text) {
  if (!text) return null;

  const lines = text.split('\n');
  return lines.map((line, idx) => {
    // Render bold **text**
    const parts = line.split(/(\*\*.*?\*\*)/g);
    const formattedLine = parts.map((part, pIdx) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={pIdx}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });

    if (line.startsWith('• ') || line.startsWith('- ')) {
      return (
        <li key={idx} className="list-item">
          {formattedLine}
        </li>
      );
    }

    if (line.trim() === '') {
      return <div key={idx} className="line-break" />;
    }

    return (
      <p key={idx} className="text-paragraph">
        {formattedLine}
      </p>
    );
  });
}

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'ai',
      text: "Hello! I am **Piyush AI**, the personal chatbot for **Piyush Hazari**. How can I help you today?",
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async () => {
    const query = input.trim();
    if (!query || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: query,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: query,
          history: messages.map(m => ({
            role: m.sender === 'user' ? 'user' : 'assistant',
            content: m.text
          }))
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();

      const aiMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: data.answer,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      console.error(err);
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: "Sorry, I couldn't connect to the backend server. Please make sure it is running on port 8000.",
        isError: true,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 'welcome-reset',
        sender: 'ai',
        text: "Hello! I am **Piyush AI**, the personal chatbot for **Piyush Hazari**. How can I help you today?",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-brand">
          <div className="avatar-badge">
            <Bot size={22} className="bot-icon" />
          </div>
          <div className="brand-info">
            <h1 className="brand-title">Piyush AI</h1>
            <p className="brand-subtitle">Personal Chatbot of Piyush Hazari</p>
          </div>
        </div>

        <button className="clear-btn" onClick={clearChat} title="Clear Chat">
          <Trash2 size={16} />
          <span className="btn-label">Clear</span>
        </button>
      </header>

      {/* Chat Messages */}
      <main className="chat-area">
        <div className="messages-wrapper">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`message-row ${msg.sender === 'user' ? 'message-user' : 'message-ai'}`}
            >
              <div className="message-avatar">
                {msg.sender === 'user' ? <User size={18} /> : <Bot size={18} />}
              </div>

              <div className="message-content">
                <div className={`message-bubble ${msg.isError ? 'bubble-error' : ''}`}>
                  {formatMessageText(msg.text)}
                </div>
                <span className="message-time">{msg.time}</span>
              </div>
            </div>
          ))}

          {/* Loading Indicator */}
          {isLoading && (
            <div className="message-row message-ai">
              <div className="message-avatar">
                <Bot size={18} />
              </div>
              <div className="message-content">
                <div className="message-bubble loading-bubble">
                  <span className="loading-dot"></span>
                  <span className="loading-dot"></span>
                  <span className="loading-dot"></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input Field */}
      <footer className="input-area">
        <div className="input-container">
          <input
            type="text"
            className="chat-input"
            placeholder="Ask a question about Piyush Hazari..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            autoFocus
          />
          <button
            className="send-button"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            title="Send"
          >
            <Send size={18} />
          </button>
        </div>
      </footer>
    </div>
  );
}
