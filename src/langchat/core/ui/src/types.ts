export type ChatStatus = "success" | "error";

export type ChatResponse = {
  response: string;
  status?: ChatStatus;
  error?: string;
  timestamp?: string;
  userId?: string;
  context?: unknown[];
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  text: string;
  ts: number;
  pending?: boolean;
  isTyping?: boolean;
  fullText?: string;
};

export type ChatSession = {
  id: string; // frontend session id (used as part of backend userId)
  title: string;
  createdAt: number;
  updatedAt: number;
  messages: ChatMessage[];
};


