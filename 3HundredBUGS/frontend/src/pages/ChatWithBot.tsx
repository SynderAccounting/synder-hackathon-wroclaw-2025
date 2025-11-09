import React, { useState, useRef, useEffect } from 'react';
import Markdown from 'marked-react';

function generateSessionId() {
  return Math.random().toString(36).substr(2, 9) + Date.now();
}

type ChatMessage = {
  sender: 'user' | 'bot';
  text?: string; // plain text
  markdown?: string; // markdown content from backend
  image?: string; // base64 image string
  sessionId?: string;
};

const ChatWithBot: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const chatBoxRef = useRef<HTMLDivElement>(null);
  const sessionId = useRef<string>(generateSessionId());
  const [expandedImage, setExpandedImage] = useState<{src: string, mime: string} | null>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:8000/ws/chat');

    ws.current.onmessage = (event) => {
      setIsLoading(false);
      let parsed: any = null;
      try {
        parsed = JSON.parse(event.data);
      } catch (e) {
        const md = String(event.data);
        setMessages((prev) => [...prev, { sender: 'bot', markdown: md }]);
        return;
      }

      // If parsed JSON, support several shapes:
      // 1) { sender: 'bot'|'user', text: '...', markdown: '...' }
      // 2) { type: 'markdown', content: '...' }
      // 3) { content: '...', role: 'assistant' }

      if (parsed === null) return;

      // If image key is present, treat as base64 image
      if (parsed.image) {
        // Try to auto-detect MIME type from base64 header
        let mime = 'image/png';
        if (parsed.image.startsWith('/9j/')) mime = 'image/jpeg';
        if (parsed.image.startsWith('R0lGOD')) mime = 'image/gif';
        setMessages((prev) => [...prev, {
          sender: parsed.sender === 'user' ? 'user' : 'bot',
          image: parsed.image,
          sessionId: parsed.sessionId,
          // @ts-ignore
          mime,
        }]);
        // Debug log
        console.log('Received image base64:', parsed.image.slice(0, 40), '...');
        return;
      }

      // Prefer explicit markdown field
      if (parsed.markdown) {
        setMessages((prev) => [...prev, { sender: parsed.sender === 'user' ? 'user' : 'bot', markdown: parsed.markdown, sessionId: parsed.sessionId }]);
        return;
      }

      // If the server uses a type/content shape
      if (parsed.type === 'markdown' && parsed.content) {
        setMessages((prev) => [...prev, { sender: 'bot', markdown: parsed.content, sessionId: parsed.sessionId }]);
        return;
      }

      // If plain text field exists
      if (parsed.text) {
        setMessages((prev) => [...prev, { sender: parsed.sender === 'user' ? 'user' : 'bot', text: parsed.text, sessionId: parsed.sessionId }]);
        return;
      }

      // Fallback: if object has a 'content' field, treat as markdown
      if (parsed.content) {
        setMessages((prev) => [...prev, { sender: parsed.sender === 'user' ? 'user' : 'bot', markdown: String(parsed.content), sessionId: parsed.sessionId }]);
        return;
      }

      // Unknown shape - push as textified JSON for debugging
      setMessages((prev) => [...prev, { sender: 'bot', text: JSON.stringify(parsed) }]);
    };

    ws.current.onopen = () => {
      console.log('WebSocket connected');
    };
    ws.current.onclose = () => {
      console.log('WebSocket closed');
    };
    ws.current.onerror = (ev) => {
      console.warn('WebSocket error', ev);
    };

    return () => {
      ws.current?.close();
    };
  }, []);

  const sendMessage = () => {
    if (input.trim() && ws.current?.readyState === 1) {
      const msg: ChatMessage = {
        text: input,
        sender: 'user',
        sessionId: sessionId.current,
      };
      ws.current.send(JSON.stringify(msg));
      setMessages((prev) => [...prev, msg]);
      setInput('');
      setIsLoading(true);
    }
  };

  return (
    <div className="page-container">
      <div className="chat-box" ref={chatBoxRef} style={{display:'flex',flexDirection:'column',gap:12}}>
        {messages.map((msg, idx) => {
          const isUser = msg.sender === 'user';
          return (
            <div
              key={idx}
              className={isUser ? 'chat-message user-message' : 'chat-message bot-message'}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: isUser ? 'flex-end' : 'flex-start',
              }}
            >
              <span className="chat-sender" style={{fontWeight:'bold',marginBottom:2}}>{isUser ? 'You' : 'Bot'}:</span>
              <div style={{
                marginTop: 6,
                background: isUser ? '#e6f7ff' : '#f5f5f5',
                color: '#222',
                borderRadius: 8,
                padding: '8px 12px',
                maxWidth: '70%',
                boxShadow: isUser ? '0 2px 8px #b3e5fc' : '0 2px 8px #eee',
                wordBreak: 'break-word',
                textAlign: 'left',
              }}>
                {msg.image ? (
                  <img
                    src={`data:${(msg as any).mime || 'image/png'};base64,${msg.image}`}
                    alt="chat image"
                    style={{maxWidth:'300px',borderRadius:8,cursor:'pointer'}}
                    onClick={() => setExpandedImage({src: `data:${(msg as any).mime || 'image/png'};base64,${msg.image}`, mime: (msg as any).mime || 'image/png'})}
                  />
                ) : msg.markdown ? (
                  <Markdown>{msg.markdown}</Markdown>
                ) : (
                  <Markdown>{msg.text}</Markdown>
                )}
              </div>
            </div>
          );
        })}
        {isLoading && (
          <div className="loading-container">
            <div className="loading-spinner" />
          </div>
        )}
      </div>
      <div style={{ display: 'flex', gap: 8, width: '100%', marginTop: 12 }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' ? sendMessage() : undefined}
          placeholder="Type your message..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>

      {expandedImage && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            background: 'rgba(0,0,0,0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
          }}
          onClick={() => setExpandedImage(null)}
        >
          <img
            src={expandedImage.src}
            alt="Expanded chat image"
            style={{maxWidth:'90vw',maxHeight:'90vh',borderRadius:12,boxShadow:'0 0 24px #000'}}
            onClick={e => e.stopPropagation()}
          />
        </div>
      )}
    </div>
  );
};

export default ChatWithBot;
