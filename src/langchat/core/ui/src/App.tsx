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
      .map((s) => {
        const session = s as ChatSession;
        // Restore full text for messages that have fullText but incomplete text
        if (Array.isArray(session.messages)) {
          session.messages = session.messages.map((m) => {
            // If message has fullText but text is incomplete, restore full text
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
  // Backend session key is `${userId}_${platform}`. We keep platform constant and encode
  // conversation id into userId so each conversation becomes a separate backend session.
  return `${baseUserId}:${sessionId}`;
}

function summarizeTitle(messages: ChatMessage[]) {
  // Find first user message (not AI response)
  const firstUser = messages.find((m) => m.role === "user" && m.text.trim().length > 0);
  const t = firstUser?.text.trim() ?? "New conversation";
  return t.length > 34 ? `${t.slice(0, 34)}…` : t;
}

function previewText(messages: ChatMessage[]) {
  // Show first user message as preview, not AI response
  const firstUser = messages.find((m) => m.role === "user" && m.text.trim().length > 0);
  if (!firstUser) return "";
  const t = firstUser.text.replace(/\s+/g, " ").trim();
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

function IconMore(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true" {...props}>
      <circle cx="12" cy="6" r="1.5" fill="currentColor" />
      <circle cx="12" cy="12" r="1.5" fill="currentColor" />
      <circle cx="12" cy="18" r="1.5" fill="currentColor" />
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
  const typingControllerRef = useRef<{ sessionId: string; messageId: string; timer: number } | null>(
    null
  );
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    // Always scroll to bottom when active session changes
    requestAnimationFrame(() => {
      el.scrollTop = el.scrollHeight;
    });
  }, [activeId]);

  // Auto-scroll when new message is added or typing updates
  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    const active = sessions.find((s) => s.id === activeId);
    if (!active) return;
    
    // Scroll to bottom when messages change (new message or typing update)
    const scrollToBottom = () => {
      if (el) {
        el.scrollTop = el.scrollHeight;
      }
    };
    
    // Use requestAnimationFrame for smooth scrolling
    requestAnimationFrame(() => {
      scrollToBottom();
      // Also scroll after a short delay to catch typewriter updates
      setTimeout(scrollToBottom, 50);
    });
  }, [sessions.find((s) => s.id === activeId)?.messages.length, sessions.find((s) => s.id === activeId)?.messages]);

  useEffect(() => {
    if (!toast) return;
    const t = window.setTimeout(() => setToast(null), 1100);
    return () => window.clearTimeout(t);
  }, [toast]);

  // Close session menu when clicking outside
  useEffect(() => {
    if (!sessionMenuOpen) return;
    
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('.sessionMenu') && !target.closest('.sessionActions')) {
        setSessionMenuOpen(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [sessionMenuOpen]);

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
    if (!full || full.length === 0) {
      // If no fullText, mark as done immediately
      setSessionState((st) => {
        const nextSessions = st.sessions.map((s) => {
          if (s.id !== active.id) return s;
          const nextMessages = s.messages.map((m) => {
            if (m.id !== typingMsg.id) return m;
            return { ...m, text: m.text || "", isTyping: false, fullText: m.text || "" };
          });
          return { ...s, messages: nextMessages, updatedAt: Date.now() };
        });
        saveSessions(nextSessions, st.activeId);
        return { ...st, sessions: nextSessions };
      });
      return;
    }

    // Start from current text length if already partially typed, otherwise start from 0
    let idx = typingMsg.text?.length || 0;
    // Ensure we don't start beyond the full text length
    idx = Math.min(idx, full.length);
    
    // Calculate step size - type faster for shorter messages
    const step = Math.max(1, Math.ceil(full.length / 100));
    // Adaptive interval delay - faster for shorter messages (10-30ms range)
    const intervalDelay = Math.max(10, Math.min(30, 500 / Math.max(1, full.length / 5)));

    const timer = window.setInterval(() => {
      idx = Math.min(full.length, idx + step);
      
      setSessionState((st) => {
        const nextSessions = st.sessions.map((s) => {
          if (s.id !== active.id) return s;
          const nextMessages = s.messages.map((m) => {
            if (m.id !== typingMsg.id) return m;
            const nextText = full.slice(0, idx);
            const done = idx >= full.length;
            
            if (done) {
              // Complete - ensure full text is set
              return { 
                ...m, 
                text: full, 
                isTyping: false, 
                fullText: full 
              };
            } else {
              // Still typing - keep isTyping true
              return { 
                ...m, 
                text: nextText, 
                fullText: full,
                isTyping: true 
              };
            }
          });
          return { ...s, messages: nextMessages, updatedAt: Date.now() };
        });
        saveSessions(nextSessions, st.activeId);
        return { ...st, sessions: nextSessions };
      });

      // Auto-scroll during typing
      requestAnimationFrame(() => {
        const el = scrollerRef.current;
        if (el) {
          el.scrollTop = el.scrollHeight;
        }
      });

      if (idx >= full.length) {
        window.clearInterval(timer);
        typingControllerRef.current = null;
        // Final scroll to bottom when typing completes
        requestAnimationFrame(() => {
          const el = scrollerRef.current;
          if (el) {
            el.scrollTop = el.scrollHeight;
          }
        });
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

  const activeSession = useMemo(() => sessions.find((s) => s.id === activeId) ?? sessions[0], [
    sessions,
    activeId,
  ]);

  const canSend = useMemo(() => !busy && text.trim().length > 0, [busy, text]);

  async function onSend() {
    const query = text.trim();
    // Prevent sending if query is too short or busy
    if (!query || query.length < 1 || busy) return;

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
    
    // Immediately scroll to bottom when user sends message
    requestAnimationFrame(() => {
      const el = scrollerRef.current;
      if (el) {
        el.scrollTop = el.scrollHeight;
      }
    });

    try {
      const sessionKey = buildSessionKey(baseUserId, sessionId);
      const res = await sendChat({ query, sessionKey });
      
      // Ensure we have a valid response - don't trim here, preserve full response
      const fullResponse = res?.response || res?.error || "No response received.";
      
      // Check if there was an error
      if (res.status === "error") {
        setError(res.error ?? "Server returned an error.");
        // Still show the error message in the chat
        setSessionState((st) => {
          const nextSessions = st.sessions.map((s) => {
            if (s.id !== sessionId) return s;
            const nextMessages = s.messages.map((m) => {
              if (m.id !== pendingId) return m;
              return {
                ...m,
                pending: false,
                isTyping: true,
                fullText: fullResponse, // Store full response
                text: "", // Start with empty text for typewriter effect
                ts: Date.now(),
              };
            });
            return { ...s, messages: nextMessages, updatedAt: Date.now() };
          });
          saveSessions(nextSessions, st.activeId);
          return { ...st, sessions: nextSessions };
        });
      } else {
        // Success - update message with response
        setSessionState((st) => {
          const nextSessions = st.sessions.map((s) => {
            if (s.id !== sessionId) return s;
            const nextMessages = s.messages.map((m) => {
              if (m.id !== pendingId) return m;
              return {
                ...m,
                pending: false,
                isTyping: true,
                fullText: fullResponse, // Store full response
                text: "", // Start with empty text for typewriter effect
                ts: Date.now(),
              };
            });
            return { ...s, messages: nextMessages, updatedAt: Date.now() };
          });
          saveSessions(nextSessions, st.activeId);
          return { ...st, sessions: nextSessions };
        });
      }
      
      // Auto-scroll to bottom after response is received
      requestAnimationFrame(() => {
        const el = scrollerRef.current;
        if (el) {
          el.scrollTop = el.scrollHeight;
        }
        // Also scroll after a delay to ensure it happens
        setTimeout(() => {
          if (el) {
            el.scrollTop = el.scrollHeight;
          }
        }, 100);
      });
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
            <img src="/frontend/logo-sidebar.png" alt="LangChat" className="brandLogo" onError={(e) => {
              // Fallback if logo fails to load - try alternative path
              const target = e.target as HTMLImageElement;
              if (target.src.includes('/frontend/')) {
                target.src = '/logo-sidebar.png';
              } else {
                target.style.display = 'none';
              }
            }} />
          </div>

          <button className="btnPrimary" onClick={onNewConversation}>
            <IconPlus />
            New conversation
          </button>
        </div>

        <div className="sessionList" role="list" aria-label="Conversations">
          {sessions.map((s) => {
            const active = s.id === activeId;
            const menuOpen = sessionMenuOpen === s.id;
            return (
              <div key={s.id} className={`sessionItem ${active ? "active" : ""}`} role="listitem">
                <button className="sessionMain" onClick={() => onSelectSession(s.id)}>
                  <div className="sessionTitle">{s.title || "Conversation"}</div>
                  <div className="sessionPreview">{previewText(s.messages)}</div>
                </button>
                <div className="sessionActions">
                  <button
                    className="iconBtn"
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
                        className="sessionMenuBackdrop"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSessionMenuOpen(null);
                        }}
                      />
                      <div className="sessionMenu">
                        <div className="sessionMenuHeader">Session Details</div>
                        <div className="sessionMenuInfo">
                          <div className="sessionMenuLabel">Session ID:</div>
                          <div className="sessionMenuValue">{s.id}</div>
                        </div>
                        <button
                          className="sessionMenuDelete"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSessionMenuOpen(null);
                            onDeleteSession(s.id);
                          }}
                        >
                          <IconTrash />
                          Delete Conversation
                        </button>
                      </div>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="main">
        <button className="iconBtn mobileOnly mobileMenuBtn" onClick={() => setMobileSidebarOpen((v) => !v)}>
          <span className="hamburger" aria-hidden="true" />
          <span className="srOnly">Toggle conversations</span>
        </button>

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
        </div>

        <div className="composerWrap">
          <form
            className="composer"
            onSubmit={(e) => {
              e.preventDefault();
              if (canSend) {
                void onSend();
              }
            }}
          >
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
                  if (canSend) {
                    void onSend();
                  }
                }
              }}
              disabled={busy}
              rows={1}
            />
            <button type="submit" className="btnPrimary" disabled={!canSend}>
              {busy ? "Sending…" : "Send"}
            </button>
          </form>
        </div>
      </div>

      <div 
        className={`backdrop ${mobileSidebarOpen || sessionMenuOpen ? "show" : ""}`} 
        onClick={() => {
          setMobileSidebarOpen(false);
          setSessionMenuOpen(null);
        }}
        onMouseDown={(e) => {
          // Close menu when clicking outside
          if (sessionMenuOpen) {
            setSessionMenuOpen(null);
          }
        }}
      />
      {toast ? <div className="toast">{toast}</div> : null}
    </div>
  );
}



