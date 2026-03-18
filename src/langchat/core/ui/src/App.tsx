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
  return new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function initialGreeting(): ChatMessage {
  return {
    id: nowId(),
    role: "assistant",
    text: "Hi — I'm LangChat. Ask me anything.",
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
      .map((s) => {
        const session = s as ChatSession;
        if (Array.isArray(session.messages)) {
          session.messages = session.messages.map((m) => {
            if (m.fullText && m.text !== m.fullText) {
              return { ...m, text: m.fullText, isTyping: false };
            }
            return m;
          });
        }
        return session;
      })
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
  return `${baseUserId}:${sessionId}`;
}

function summarizeTitle(messages: ChatMessage[]) {
  const firstUser = messages.find((m) => m.role === "user" && m.text.trim().length > 0);
  const t = firstUser?.text.trim() ?? "New conversation";
  return t.length > 34 ? `${t.slice(0, 34)}…` : t;
}

function previewText(messages: ChatMessage[]) {
  const firstUser = messages.find((m) => m.role === "user" && m.text.trim().length > 0);
  if (!firstUser) return "";
  const t = firstUser.text.replace(/\s+/g, " ").trim();
  return t.length > 44 ? `${t.slice(0, 44)}…` : t;
}

function userInitials(userId: string) {
  return userId.slice(0, 2).toUpperCase();
}

// ── Icons ─────────────────────────────────────────────────────────────────

function IconPlus(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true" {...props}>
      <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function IconCopy(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true" {...props}>
      <path d="M8 8h10v12H8V8Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
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
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true" {...props}>
      <path d="M4 7h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <path d="M10 11v7M14 11v7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
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

function IconMore(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true" {...props}>
      <circle cx="12" cy="6" r="1.5" fill="currentColor" />
      <circle cx="12" cy="12" r="1.5" fill="currentColor" />
      <circle cx="12" cy="18" r="1.5" fill="currentColor" />
    </svg>
  );
}

function IconSend(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true" {...props}>
      <path
        d="M22 2L11 13"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M22 2L15 22L11 13L2 9L22 2Z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function IconBot(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true" {...props}>
      <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" strokeWidth="2" />
      <path d="M12 2v4M8 2v2M16 2v2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <circle cx="9" cy="16" r="1.5" fill="currentColor" />
      <circle cx="15" cy="16" r="1.5" fill="currentColor" />
    </svg>
  );
}

function ThinkingDots() {
  return (
    <span className="thinking" aria-label="Thinking">
      <span className="thinking-dot" />
      <span className="thinking-dot" />
      <span className="thinking-dot" />
    </span>
  );
}

// ── Welcome screen ────────────────────────────────────────────────────────

const HINT_PROMPTS = [
  "What can you help me with?",
  "Summarize recent documents",
  "Explain how RAG works",
  "What data do you have access to?",
];

function WelcomeScreen({ onHint }: { onHint: (text: string) => void }) {
  return (
    <div className="welcome">
      <div className="welcome-icon">
        <IconBot />
      </div>
      <div className="welcome-title">How can I help you today?</div>
      <div className="welcome-sub">
        I'm powered by retrieval-augmented generation. Ask me anything about your data.
      </div>
      <div className="welcome-hints">
        {HINT_PROMPTS.map((p) => (
          <button key={p} className="welcome-hint" onClick={() => onHint(p)}>
            {p}
          </button>
        ))}
      </div>
    </div>
  );
}

// ── App ───────────────────────────────────────────────────────────────────

export function App() {
  const [text, setText] = useState<string>("");
  const [busy, setBusy] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState<boolean>(false);
  const [sessionMenuOpen, setSessionMenuOpen] = useState<string | null>(null);

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
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const typingControllerRef = useRef<{
    sessionId: string;
    messageId: string;
    timer: number;
  } | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  // Scroll to bottom when session changes
  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    requestAnimationFrame(() => {
      el.scrollTop = el.scrollHeight;
    });
  }, [activeId]);

  // Auto-scroll on message changes
  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    requestAnimationFrame(() => {
      el.scrollTop = el.scrollHeight;
      setTimeout(() => {
        if (el) el.scrollTop = el.scrollHeight;
      }, 50);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    // eslint-disable-next-line react-hooks/exhaustive-deps
    sessions.find((s) => s.id === activeId)?.messages.length,
    // eslint-disable-next-line react-hooks/exhaustive-deps
    sessions.find((s) => s.id === activeId)?.messages,
  ]);

  // Toast auto-dismiss
  useEffect(() => {
    if (!toast) return;
    const t = window.setTimeout(() => setToast(null), 1100);
    return () => window.clearTimeout(t);
  }, [toast]);

  // Close session menu on outside click
  useEffect(() => {
    if (!sessionMenuOpen) return;
    const handler = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest(".session-menu") && !target.closest(".session-menu-wrap")) {
        setSessionMenuOpen(null);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [sessionMenuOpen]);

  // Typewriter effect
  useEffect(() => {
    const active = sessions.find((s) => s.id === activeId);
    if (!active) return;

    const typingMsg = active.messages.find(
      (m) => m.role === "assistant" && m.isTyping && m.fullText,
    );
    if (!typingMsg) {
      if (typingControllerRef.current) {
        window.clearInterval(typingControllerRef.current.timer);
        typingControllerRef.current = null;
      }
      return;
    }

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
    if (!full || full.length === 0) {
      setSessionState((st) => {
        const nextSessions = st.sessions.map((s) => {
          if (s.id !== active.id) return s;
          return {
            ...s,
            messages: s.messages.map((m) =>
              m.id !== typingMsg.id
                ? m
                : { ...m, text: m.text || "", isTyping: false, fullText: m.text || "" },
            ),
            updatedAt: Date.now(),
          };
        });
        saveSessions(nextSessions, st.activeId);
        return { ...st, sessions: nextSessions };
      });
      return;
    }

    let idx = Math.min(typingMsg.text?.length || 0, full.length);
    const step = Math.max(1, Math.ceil(full.length / 100));
    const intervalDelay = Math.max(10, Math.min(30, 500 / Math.max(1, full.length / 5)));

    const timer = window.setInterval(() => {
      idx = Math.min(full.length, idx + step);

      setSessionState((st) => {
        const nextSessions = st.sessions.map((s) => {
          if (s.id !== active.id) return s;
          return {
            ...s,
            messages: s.messages.map((m) => {
              if (m.id !== typingMsg.id) return m;
              const done = idx >= full.length;
              return done
                ? { ...m, text: full, isTyping: false, fullText: full }
                : { ...m, text: full.slice(0, idx), fullText: full, isTyping: true };
            }),
            updatedAt: Date.now(),
          };
        });
        saveSessions(nextSessions, st.activeId);
        return { ...st, sessions: nextSessions };
      });

      requestAnimationFrame(() => {
        const el = scrollerRef.current;
        if (el) el.scrollTop = el.scrollHeight;
      });

      if (idx >= full.length) {
        window.clearInterval(timer);
        typingControllerRef.current = null;
      }
    }, intervalDelay);

    typingControllerRef.current = { sessionId: active.id, messageId: typingMsg.id, timer };

    return () => {
      if (typingControllerRef.current?.timer === timer) {
        window.clearInterval(timer);
        typingControllerRef.current = null;
      }
    };
  }, [sessions, activeId]);

  const activeSession = useMemo(
    () => sessions.find((s) => s.id === activeId) ?? sessions[0],
    [sessions, activeId],
  );

  // Show welcome screen if only the greeting message is present (no user messages yet)
  const showWelcome = useMemo(() => {
    const msgs = activeSession?.messages ?? [];
    return msgs.length === 1 && msgs[0].role === "assistant";
  }, [activeSession]);

  const canSend = useMemo(() => !busy && text.trim().length > 0, [busy, text]);

  async function onSend(overrideText?: string) {
    const query = (overrideText ?? text).trim();
    if (!query || busy) return;

    setError(null);
    setBusy(true);
    setText("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }

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
        const nextTitle =
          s.title === "New conversation" ? summarizeTitle(nextMessages) : s.title;
        return { ...s, title: nextTitle, messages: nextMessages, updatedAt: Date.now() };
      });
      saveSessions(nextSessions, st.activeId);
      return { ...st, sessions: nextSessions };
    });

    requestAnimationFrame(() => {
      const el = scrollerRef.current;
      if (el) el.scrollTop = el.scrollHeight;
    });

    try {
      const sessionKey = buildSessionKey(baseUserId, sessionId);
      const res = await sendChat({ query, sessionKey });
      const fullResponse = res?.response || res?.error || "No response received.";

      if (res.status === "error") {
        setError(res.error ?? "Server returned an error.");
      }

      setSessionState((st) => {
        const nextSessions = st.sessions.map((s) => {
          if (s.id !== sessionId) return s;
          return {
            ...s,
            messages: s.messages.map((m) =>
              m.id !== pendingId
                ? m
                : { ...m, pending: false, isTyping: true, fullText: fullResponse, text: "", ts: Date.now() },
            ),
            updatedAt: Date.now(),
          };
        });
        saveSessions(nextSessions, st.activeId);
        return { ...st, sessions: nextSessions };
      });
    } catch (e) {
      setSessionState((st) => {
        const nextSessions = st.sessions.map((s) => {
          if (s.id !== sessionId) return s;
          return {
            ...s,
            messages: s.messages.map((m) =>
              m.id !== pendingId
                ? m
                : {
                    ...m,
                    pending: false,
                    text: "Unable to reach the server. Is FastAPI running?",
                    ts: Date.now(),
                  },
            ),
            updatedAt: Date.now(),
          };
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
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
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
      const next = [s, ...st.sessions];
      saveSessions(next, id);
      return { sessions: next, activeId: id };
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
      const next = st.sessions.filter((s) => s.id !== id);
      const nextActive = st.activeId === id ? (next[0]?.id ?? newSessionId()) : st.activeId;
      const finalSessions = next.length
        ? next
        : [
            {
              id: nextActive,
              title: "New conversation",
              createdAt: Date.now(),
              updatedAt: Date.now(),
              messages: [initialGreeting()],
            },
          ];
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
      setToast("Copy failed");
    }
  }

  const activeMessages = activeSession?.messages ?? [];

  return (
    <div className="app">
      {/* ── Sidebar ─────────────────────────────────────────────────── */}
      <div className={`sidebar${mobileSidebarOpen ? " open" : ""}`}>
        <div className="sidebar-top">
          {/* Brand */}
          <div className="brand">
            <div className="brand-icon">
              <IconBot />
            </div>
            <div className="brand-text">
              <span className="brand-name">LangChat</span>
              <span className="brand-tagline">Powered by RAG</span>
            </div>
          </div>

          {/* New conversation */}
          <button className="btn-new-chat" onClick={onNewConversation}>
            <IconPlus />
            New conversation
          </button>
        </div>

        {/* Session list */}
        <div className="session-list" role="list" aria-label="Conversations">
          {sessions.length > 0 && (
            <div className="session-list-label">Recent</div>
          )}
          {sessions.map((s) => {
            const isActive = s.id === activeId;
            const menuOpen = sessionMenuOpen === s.id;
            return (
              <div
                key={s.id}
                className={`session-item${isActive ? " active" : ""}`}
                role="listitem"
              >
                <button className="session-btn" onClick={() => onSelectSession(s.id)}>
                  <div className="session-title">{s.title || "Conversation"}</div>
                  <div className="session-meta">{previewText(s.messages)}</div>
                </button>
                <div className="session-menu-wrap">
                  <button
                    className="session-opts-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSessionMenuOpen(menuOpen ? null : s.id);
                    }}
                    aria-label="Session options"
                    title="Options"
                  >
                    <IconMore />
                  </button>
                  {menuOpen && (
                    <>
                      <div
                        className="session-menu-backdrop"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSessionMenuOpen(null);
                        }}
                      />
                      <div className="session-menu">
                        <div className="session-menu-header">Session Details</div>
                        <div className="session-menu-id">
                          <div className="session-menu-id-label">Session ID</div>
                          <div className="session-menu-id-value">{s.id}</div>
                        </div>
                        <button
                          className="session-menu-delete"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSessionMenuOpen(null);
                            onDeleteSession(s.id);
                          }}
                        >
                          <IconTrash />
                          Delete conversation
                        </button>
                      </div>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Sidebar footer — status dot */}
        <div className="sidebar-footer">
          <div className="sidebar-status">
            <span className="status-dot" />
            LangChat is ready
          </div>
        </div>
      </div>

      {/* ── Main area ─────────────────────────────────────────────────── */}
      <div className="main">
        {/* Mobile topbar */}
        <div className="topbar mobile-only">
          <button
            className="icon-btn"
            onClick={() => setMobileSidebarOpen((v) => !v)}
            aria-label="Toggle conversations"
          >
            <span
              className={`hamburger${mobileSidebarOpen ? " is-open" : ""}`}
              aria-hidden="true"
            >
              <span />
              <span />
              <span />
            </span>
          </button>
          <div className="topbar-title">
            <div className="topbar-title-main">
              {activeSession?.title || "LangChat"}
            </div>
          </div>
        </div>

        {/* Messages / Welcome */}
        {showWelcome ? (
          <WelcomeScreen
            onHint={(hint) => {
              setText(hint);
              textareaRef.current?.focus();
            }}
          />
        ) : (
          <div className="messages" ref={scrollerRef} aria-label="Messages">
            {activeMessages.map((m) => (
              <div key={m.id} className={`msg-row ${m.role}`}>
                {/* Avatar */}
                <div className="msg-avatar" aria-hidden="true">
                  {m.role === "assistant" ? <IconBot /> : userInitials(baseUserId)}
                </div>

                {/* Body */}
                <div className="msg-body">
                  {m.pending ? (
                    <div className="bubble-pending">
                      <span>Thinking</span>
                      <ThinkingDots />
                    </div>
                  ) : (
                    <div className="bubble">{m.text}</div>
                  )}

                  {!m.pending && (
                    <div className="msg-meta">
                      <span className="meta-time">{formatTime(m.ts)}</span>
                      {m.role === "assistant" && m.text.trim().length > 0 && (
                        <button
                          className="meta-copy"
                          onClick={() => void copyToClipboard(m.text)}
                          aria-label="Copy response"
                          title="Copy"
                        >
                          <IconCopy />
                          Copy
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Error notice */}
        {error && <div className="notice">{error}</div>}

        {/* Composer */}
        <div className="composer-wrap">
          <form
            className="composer"
            onSubmit={(e) => {
              e.preventDefault();
              if (canSend) void onSend();
            }}
          >
            <textarea
              ref={textareaRef}
              className="composer-textarea"
              value={text}
              placeholder="Message LangChat… (Enter to send)"
              onChange={(e) => {
                setText(e.target.value);
                autoGrow(e.target);
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  if (canSend) void onSend();
                }
              }}
              disabled={busy}
              rows={1}
            />
            <button
              type="submit"
              className="btn-send"
              disabled={!canSend}
              aria-label="Send message"
            >
              <IconSend />
            </button>
          </form>
          <div className="composer-hint">Shift+Enter for new line</div>
        </div>
      </div>

      {/* ── Backdrop (mobile) ─────────────────────────────────────────── */}
      <div
        className={`backdrop${mobileSidebarOpen || !!sessionMenuOpen ? " show" : ""}`}
        onClick={() => {
          setMobileSidebarOpen(false);
          setSessionMenuOpen(null);
        }}
      />

      {/* ── Toast ─────────────────────────────────────────────────────── */}
      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}
