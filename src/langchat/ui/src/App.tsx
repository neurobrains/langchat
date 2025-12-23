import React, { useEffect, useMemo, useRef, useState } from "react";
import { sendChat } from "./api";
import type { ChatMessage } from "./types";

function nowId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function formatTime(ts: number) {
  const d = new Date(ts);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function App() {
  const [userId, setUserId] = useState<string>(() => {
    const existing = localStorage.getItem("langchat.userId");
    if (existing) return existing;
    const id = `user_${Math.random().toString(36).slice(2, 10)}`;
    localStorage.setItem("langchat.userId", id);
    return id;
  });
  const [domain, setDomain] = useState<string>("default");
  const [text, setText] = useState<string>("");
  const [busy, setBusy] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const [messages, setMessages] = useState<ChatMessage[]>(() => [
    {
      id: nowId(),
      role: "assistant",
      text: "Hi — I’m LangChat. Ask me anything.",
      ts: Date.now()
    }
  ]);

  const scrollerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    localStorage.setItem("langchat.userId", userId);
  }, [userId]);

  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [messages.length]);

  const canSend = useMemo(() => !busy && text.trim().length > 0, [busy, text]);

  async function onSend() {
    const query = text.trim();
    if (!query || busy) return;

    setError(null);
    setBusy(true);
    setText("");

    const userMsg: ChatMessage = { id: nowId(), role: "user", text: query, ts: Date.now() };
    const pendingId = nowId();
    const pending: ChatMessage = {
      id: pendingId,
      role: "assistant",
      text: "Thinking…",
      ts: Date.now()
    };

    setMessages((m) => [...m, userMsg, pending]);

    try {
      const res = await sendChat({ query, userId, domain });
      setMessages((m) =>
        m.map((msg) =>
          msg.id === pendingId
            ? {
                ...msg,
                text: res.response || "No response received.",
                ts: Date.now()
              }
            : msg
        )
      );

      if (res.status === "error") {
        setError(res.error ?? "Server returned an error.");
      }
    } catch (e) {
      setMessages((m) =>
        m.map((msg) =>
          msg.id === pendingId
            ? { ...msg, text: "Unable to reach the server. Is FastAPI running?", ts: Date.now() }
            : msg
        )
      );
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setBusy(false);
    }
  }

  function autoGrow(el: HTMLTextAreaElement) {
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 140)}px`;
  }

  return (
    <div className="page">
      <div className="shell">
        <div className="topbar">
          <div className="brand">
            <h1>LangChat</h1>
            <span>FastAPI + Vite</span>
          </div>
          <div className="settings">
            <input
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="User ID"
              aria-label="User ID"
            />
            <select value={domain} onChange={(e) => setDomain(e.target.value)} aria-label="Domain">
              <option value="default">default</option>
              <option value="general">general</option>
              <option value="education">education</option>
              <option value="travel">travel</option>
            </select>
          </div>
        </div>

        <div className="content">
          <div className="messages" ref={scrollerRef}>
            {messages.map((m) => (
              <div key={m.id} className={`bubble ${m.role}`}>
                {m.text}
                <div className="meta">{formatTime(m.ts)}</div>
              </div>
            ))}
          </div>

          {error ? <div className="error">{error}</div> : null}

          <div className="composer">
            <textarea
              value={text}
              placeholder="Type a message… (Enter to send, Shift+Enter for newline)"
              onChange={(e) => {
                setText(e.target.value);
                autoGrow(e.target);
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  void onSend();
                }
              }}
              disabled={busy}
            />
            <button onClick={() => void onSend()} disabled={!canSend}>
              {busy ? "Sending…" : "Send"}
            </button>
          </div>

          <div className="hint">Backend endpoint: POST /chat • Frontend served at /frontend/</div>
        </div>
      </div>
    </div>
  );
}


