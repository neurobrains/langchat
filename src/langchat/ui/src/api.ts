import type { ChatResponse } from "./types";

export async function sendChat(params: {
  query: string;
  userId: string;
  domain: string;
  image?: File | null;
}): Promise<ChatResponse> {
  const form = new FormData();
  form.append("query", params.query);
  form.append("userId", params.userId);
  form.append("domain", params.domain);
  if (params.image) form.append("image", params.image);

  const res = await fetch("/chat", { method: "POST", body: form });
  const json = (await res.json()) as ChatResponse;

  if (!res.ok) {
    return {
      status: "error",
      response:
        json?.response ??
        "Sorry — the server returned an error. Please try again.",
      error: json?.error ?? `HTTP ${res.status}`
    };
  }

  return json;
}


