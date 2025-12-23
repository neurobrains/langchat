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
};


