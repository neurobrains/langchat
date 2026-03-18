import type { ChatResponse } from "./types";

export async function sendChat(params: {
  query: string;
  sessionKey: string; // passed as userId to backend (keeps sessions separate)
  image?: File | null;
}): Promise<ChatResponse> {
  const form = new FormData();
  form.append("query", params.query);
  form.append("userId", params.sessionKey);
  form.append("platform", "default");
  if (params.image) form.append("image", params.image);

  try {
    const res = await fetch("/chat", { method: "POST", body: form });
    
    if (!res.ok) {
      let errorMessage = `HTTP ${res.status}`;
      try {
        const errorJson = await res.json();
        errorMessage = errorJson?.error ?? errorJson?.response ?? errorMessage;
      } catch {
        // If JSON parsing fails, use status text
        errorMessage = res.statusText || errorMessage;
      }
      
      return {
        status: "error",
        response: "Sorry — the server returned an error. Please try again.",
        error: errorMessage
      };
    }

    const json = (await res.json()) as ChatResponse;
    
    // Ensure response field exists
    if (!json.response) {
      json.response = json.error ?? "No response received.";
    }
    
    return json;
  } catch (e) {
    // Network error or JSON parsing error
    return {
      status: "error",
      response: "Unable to reach the server. Please check your connection.",
      error: e instanceof Error ? e.message : "Unknown error"
    };
  }
}


