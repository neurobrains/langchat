import React, { useEffect, useMemo, useRef, useState } from "react";
import { sendChat } from "./api";
import type { ChatMessage, ChatSession } from "./types";

function nowId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function newSessionId() {
  return `s_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

function formatTime(ts: number) {
  const d = new Date(ts);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function initialGreeting(): ChatMessage {
  return {
    id: nowId(),
    role: "assistant",
    text: "Hi — I’m LangChat. Ask me anything.",
    ts: Date.now(),
  };
}

function loadSessions(): { sessions: ChatSession[]; activeId: string | null } {
  try {
    const raw = localStorage.getItem("langchat.sessions.v1");
    const rawActive = localStorage.getItem("langchat.activeSessionId.v1");
    if (!raw) return { sessions: [], activeId: rawActive };
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return { sessions: [], activeId: rawActive };

    const sessions: ChatSession[] = parsed
      .filter((s) => s && typeof s === "object")
      .map((s) => s as ChatSession)
      .filter((s) => typeof s.id === "string" && Array.isArray(s.messages));

    return { sessions, activeId: rawActive };
  } catch {
    return { sessions: [], activeId: null };
  }
}

function saveSessions(sessions: ChatSession[], activeId: string) {
  localStorage.setItem("langchat.sessions.v1", JSON.stringify(sessions));
  localStorage.setItem("langchat.activeSessionId.v1", activeId);
}

function buildSessionKey(baseUserId: string, sessionId: string) {
  // Backend session key is `${userId}_${domain}`. We keep domain constant and encode
  // conversation id into userId so each conversation becomes a separate backend session.
  return `${baseUserId}:${sessionId}`;
}

function summarizeTitle(messages: ChatMessage[]) {
  const firstUser = messages.find((m) => m.role === "user" && m.text.trim().length > 0);
  const t = firstUser?.text.trim() ?? "New conversation";
  return t.length > 34 ? `${t.slice(0, 34)}…` : t;
}

function previewText(messages: ChatMessage[]) {
  const last = [...messages].reverse().find((m) => m.text.trim().length > 0);
  if (!last) return "";
  const t = last.text.replace(/\s+/g, " ").trim();
  return t.length > 44 ? `${t.slice(0, 44)}…` : t;
}

function IconPlus(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true" {...props}>
      <path
        d="M12 5v14M5 12h14"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function IconCopy(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true" {...props}>
      <path
        d="M8 8h10v12H8V8Z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      <path
        d="M6 16H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function IconTrash(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true" {...props}>
      <path
        d="M4 7h16"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M10 11v7M14 11v7"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M6 7l1 14a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-14"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      <path
        d="M9 7V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v3"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function ThinkingDots() {
  return (
    <span className="thinking" aria-label="Thinking">
      <span className="thinkingDot" />
      <span className="thinkingDot" />
      <span className="thinkingDot" />
    </span>
  );
}

export function App() {
  const [text, setText] = useState<string>("");
  const [busy, setBusy] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState<boolean>(false);

  const baseUserId = useMemo(() => {
    const existing = localStorage.getItem("langchat.baseUserId.v1");
    if (existing) return existing;
    const id = `u_${Math.random().toString(36).slice(2, 10)}`;
    localStorage.setItem("langchat.baseUserId.v1", id);
    return id;
  }, []);

  const [{ sessions, activeId }, setSessionState] = useState<{
    sessions: ChatSession[];
    activeId: string;
  }>(() => {
    const loaded = loadSessions();
    let nextSessions = loaded.sessions;
    let nextActive = loaded.activeId ?? (nextSessions[0]?.id ?? "");

    if (!nextSessions.length) {
      const id = newSessionId();
      nextSessions = [
        {
          id,
          title: "New conversation",
          createdAt: Date.now(),
          updatedAt: Date.now(),
          messages: [initialGreeting()],
        },
      ];
      nextActive = id;
    } else if (!nextActive || !nextSessions.some((s) => s.id === nextActive)) {
      nextActive = nextSessions[0].id;
    }

    saveSessions(nextSessions, nextActive);
    return { sessions: nextSessions, activeId: nextActive };
  });

  const scrollerRef = useRef<HTMLDivElement | null>(null);
  const typingControllerRef = useRef<{ sessionId: string; messageId: string; timer: number } | null>(
    null
  );
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [sessions, activeId]);

  useEffect(() => {
    if (!toast) return;
    const t = window.setTimeout(() => setToast(null), 1100);
    return () => window.clearTimeout(t);
  }, [toast]);

  useEffect(() => {
    const active = sessions.find((s) => s.id === activeId);
    if (!active) return;

    const typingMsg = active.messages.find((m) => m.role === "assistant" && m.isTyping && m.fullText);
    if (!typingMsg) {
      if (typingControllerRef.current) {
        window.clearInterval(typingControllerRef.current.timer);
        typingControllerRef.current = null;
      }
      return;
    }

    // Only start a new typewriter loop if we haven't already started one for this msg.
    if (
      typingControllerRef.current &&
      typingControllerRef.current.sessionId === active.id &&
      typingControllerRef.current.messageId === typingMsg.id
    ) {
      return;
    }

    if (typingControllerRef.current) {
      window.clearInterval(typingControllerRef.current.timer);
      typingControllerRef.current = null;
    }

    const full = typingMsg.fullText ?? typingMsg.text;
    let idx = 0;
    const step = Math.max(1, Math.ceil(full.length / 140));

    const timer = window.setInterval(() => {
      idx = Math.min(full.length, idx + step);
      setSessionState((st) => {
        const nextSessions = st.sessions.map((s) => {
          if (s.id !== active.id) return s;
          const nextMessages = s.messages.map((m) => {
            if (m.id !== typingMsg.id) return m;
            const nextText = full.slice(0, idx);
            const done = idx >= full.length;
            return done
              ? { ...m, text: full, isTyping: false, fullText: undefined }
              : { ...m, text: nextText };
          });
          return { ...s, messages: nextMessages, updatedAt: Date.now() };
        });
        saveSessions(nextSessions, st.activeId);
        return { ...st, sessions: nextSessions };
      });

      if (idx >= full.length) {
        if (typingControllerRef.current) {
          window.clearInterval(typingControllerRef.current.timer);
          typingControllerRef.current = null;
        }
      }
    }, 16);

    typingControllerRef.current = { sessionId: active.id, messageId: typingMsg.id, timer };

    return () => {
      if (typingControllerRef.current?.timer === timer) {
        window.clearInterval(timer);
        typingControllerRef.current = null;
      }
    };
  }, [sessions, activeId]);

  const activeSession = useMemo(() => sessions.find((s) => s.id === activeId) ?? sessions[0], [
    sessions,
    activeId,
  ]);

  const canSend = useMemo(() => !busy && text.trim().length > 0, [busy, text]);

  async function onSend() {
    const query = text.trim();
    if (!query || busy) return;

    setError(null);
    setBusy(true);
    setText("");

    const sessionId = activeSession?.id ?? activeId;
    const userMsg: ChatMessage = { id: nowId(), role: "user", text: query, ts: Date.now() };
    const pendingId = nowId();
    const pending: ChatMessage = {
      id: pendingId,
      role: "assistant",
      text: "",
      ts: Date.now(),
      pending: true,
    };

    setSessionState((st) => {
      const nextSessions = st.sessions.map((s) => {
        if (s.id !== sessionId) return s;
        const nextMessages = [...s.messages, userMsg, pending];
        const nextTitle = s.title === "New conversation" ? summarizeTitle(nextMessages) : s.title;
        return { ...s, title: nextTitle, messages: nextMessages, updatedAt: Date.now() };
      });
      saveSessions(nextSessions, st.activeId);
      return { ...st, sessions: nextSessions };
    });

    try {
      const sessionKey = buildSessionKey(baseUserId, sessionId);
      const res = await sendChat({ query, sessionKey });
      const fullResponse = res.response || "No response received.";

      setSessionState((st) => {
        const nextSessions = st.sessions.map((s) => {
          if (s.id !== sessionId) return s;
          const nextMessages = s.messages.map((m) => {
            if (m.id !== pendingId) return m;
            return {
              ...m,
              pending: false,
              isTyping: true,
              fullText: fullResponse,
              text: "",
              ts: Date.now(),
            };
          });
          return { ...s, messages: nextMessages, updatedAt: Date.now() };
        });
        saveSessions(nextSessions, st.activeId);
        return { ...st, sessions: nextSessions };
      });

      if (res.status === "error") {
        setError(res.error ?? "Server returned an error.");
      }
    } catch (e) {
      setSessionState((st) => {
        const nextSessions = st.sessions.map((s) => {
          if (s.id !== sessionId) return s;
          const nextMessages = s.messages.map((m) =>
            m.id === pendingId
              ? {
                  ...m,
                  pending: false,
                  text: "Unable to reach the server. Is FastAPI running?",
                  ts: Date.now(),
                }
              : m
          );
          return { ...s, messages: nextMessages, updatedAt: Date.now() };
        });
        saveSessions(nextSessions, st.activeId);
        return { ...st, sessions: nextSessions };
      });
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setBusy(false);
    }
  }

  function autoGrow(el: HTMLTextAreaElement) {
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 140)}px`;
  }

  function onNewConversation() {
    const id = newSessionId();
    const s: ChatSession = {
      id,
      title: "New conversation",
      createdAt: Date.now(),
      updatedAt: Date.now(),
      messages: [initialGreeting()],
    };
    setSessionState((st) => {
      const nextSessions = [s, ...st.sessions];
      saveSessions(nextSessions, id);
      return { sessions: nextSessions, activeId: id };
    });
    setMobileSidebarOpen(false);
    setError(null);
  }

  function onSelectSession(id: string) {
    setSessionState((st) => {
      saveSessions(st.sessions, id);
      return { ...st, activeId: id };
    });
    setMobileSidebarOpen(false);
    setError(null);
  }

  function onDeleteSession(id: string) {
    setSessionState((st) => {
      const nextSessions = st.sessions.filter((s) => s.id !== id);
      const nextActive =
        st.activeId === id ? (nextSessions[0]?.id ?? newSessionId()) : st.activeId;

      // If we deleted the last session, create a new one automatically.
      let finalSessions = nextSessions;
      if (!finalSessions.length) {
        finalSessions = [
          {
            id: nextActive,
            title: "New conversation",
            createdAt: Date.now(),
            updatedAt: Date.now(),
            messages: [initialGreeting()],
          },
        ];
      }

      saveSessions(finalSessions, nextActive);
      return { sessions: finalSessions, activeId: nextActive };
    });
    setToast("Deleted");
    setError(null);
  }

  async function copyToClipboard(value: string) {
    try {
      await navigator.clipboard.writeText(value);
      setToast("Copied");
    } catch {
      // Best effort: no extra colors / modals
      setToast("Copy failed");
    }
  }

  return (
    <div className="app">
      <div className={`sidebar ${mobileSidebarOpen ? "open" : ""}`}>
        <div className="sidebarTop">
          <div className="brand">
            <div className="brandMark" aria-hidden="true" />
            <div className="brandText">
              <div className="brandName">LangChat</div>
              <div className="brandSub">Teal UI • Clean chat</div>
            </div>
          </div>

          <button className="btnPrimary" onClick={onNewConversation}>
            <IconPlus />
            New conversation
          </button>
        </div>

        <div className="sessionList" role="list" aria-label="Conversations">
          {sessions.map((s) => {
            const active = s.id === activeId;
            return (
              <div key={s.id} className={`sessionItem ${active ? "active" : ""}`} role="listitem">
                <button className="sessionMain" onClick={() => onSelectSession(s.id)}>
                  <div className="sessionTitle">{s.title || "Conversation"}</div>
                  <div className="sessionPreview">{previewText(s.messages)}</div>
                </button>
                <button
                  className="iconBtn"
                  onClick={() => onDeleteSession(s.id)}
                  aria-label="Delete conversation"
                  title="Delete"
                >
                  <IconTrash />
                </button>
              </div>
            );
          })}
        </div>
      </div>

      <div className="main">
        <div className="topbar">
          <button className="iconBtn mobileOnly" onClick={() => setMobileSidebarOpen((v) => !v)}>
            <span className="hamburger" aria-hidden="true" />
            <span className="srOnly">Toggle conversations</span>
          </button>
          <div className="topbarTitle">
            <div className="topbarTitleMain">{activeSession?.title ?? "Conversation"}</div>
            <div className="topbarTitleSub">
              Session: {activeSession?.id ?? "—"} • {busy ? "Thinking…" : "Ready"}
            </div>
          </div>
        </div>

        <div className="content">
          <div className="messages" ref={scrollerRef} aria-label="Messages">
            {(activeSession?.messages ?? []).map((m) => (
              <div key={m.id} className={`bubble ${m.role}`}>
                <div className="bubbleBody">
                  {m.pending ? (
                    <div className="pendingRow">
                      <span className="pendingText">Thinking</span>
                      <ThinkingDots />
                    </div>
                  ) : (
                    m.text
                  )}
                </div>

                <div className="bubbleMeta">
                  <span className="metaTime">{formatTime(m.ts)}</span>
                  {m.role === "assistant" && !m.pending && m.text.trim().length > 0 ? (
                    <button
                      className="metaAction"
                      onClick={() => void copyToClipboard(m.text)}
                      aria-label="Copy response"
                      title="Copy"
                    >
                      <IconCopy />
                      Copy
                    </button>
                  ) : null}
                </div>
              </div>
            ))}
          </div>

          {error ? <div className="notice">{error}</div> : null}

          <div className="composerWrap">
            <div className="composer">
              <textarea
                value={text}
                placeholder="Write a message… (Enter to send, Shift+Enter for newline)"
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
              <button className="btnPrimary" onClick={() => void onSend()} disabled={!canSend}>
                {busy ? "Sending…" : "Send"}
              </button>
            </div>

            <div className="composerHint">No user_id/domain fields — sessions are handled automatically.</div>
          </div>
        </div>
      </div>

      <div className={`backdrop ${mobileSidebarOpen ? "show" : ""}`} onClick={() => setMobileSidebarOpen(false)} />
      {toast ? <div className="toast">{toast}</div> : null}
    </div>
  );
}


