const API_ROOT = "/api/chat";

export async function fetchConversation(id) {
  const response = await fetch(`${API_ROOT}/conversations/${id}`);
  if (!response.ok) throw new Error("Could not load conversation");
  return response.json();
}

export async function sendChatMessage(message, conversationId) {
  const response = await fetch(`${API_ROOT}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
    }),
  });
  if (!response.ok) throw new Error("Could not send message");
  return response.json();
}
