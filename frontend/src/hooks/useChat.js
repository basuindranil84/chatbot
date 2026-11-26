import { useEffect, useRef, useState } from "react";
import { fetchConversation, sendChatMessage } from "../api/chatApi";

const CONVERSATION_KEY = "matchmaking-assistant-conversation-id";
const DRAFT_KEY = "matchmaking-assistant-draft";

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(
    () => localStorage.getItem(CONVERSATION_KEY) || null,
  );
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [sendError, setSendError] = useState("");
  const [draft, setDraft] = useState(() => sessionStorage.getItem(DRAFT_KEY) || "");
  const [lastSentMessage, setLastSentMessage] = useState("");
  const loadRequestRef = useRef(0);
  const loadAbortRef = useRef(null);

  useEffect(() => {
    return () => loadAbortRef.current?.abort();
  }, []);

  useEffect(() => {
    if (conversationId) localStorage.setItem(CONVERSATION_KEY, conversationId);
  }, [conversationId]);

  useEffect(() => {
    sessionStorage.setItem(DRAFT_KEY, draft);
  }, [draft]);

  async function loadConversation() {
    const requestId = ++loadRequestRef.current;
    loadAbortRef.current?.abort();
    const controller = new AbortController();
    loadAbortRef.current = controller;

    setIsLoading(true);
    setLoadError("");

    try {
      if (!conversationId) {
        if (requestId === loadRequestRef.current) setMessages([]);
        return;
      }
      const conversation = await fetchConversation(conversationId, { signal: controller.signal });
      if (requestId === loadRequestRef.current) {
        setMessages(conversation.messages || []);
      }
    } catch (requestError) {
      if (requestError.name === "AbortError") return;
      if (requestId === loadRequestRef.current) {
        setMessages([]);
        setLoadError("I couldn't load our chat just now. Please try again.");
      }
    } finally {
      if (requestId === loadRequestRef.current) setIsLoading(false);
    }
  }

  async function sendMessage(text) {
    const trimmed = text.trim();
    if (!trimmed || isSending || trimmed.length > 500) return;

    setSendError("");
    setMessages((current) => [
      ...current,
      { id: `user-${Date.now()}`, role: "user", content: trimmed },
    ]);
    setIsSending(true);
    setDraft("");
    setLastSentMessage(trimmed);

    try {
      const result = await sendChatMessage(trimmed, conversationId);
      setConversationId(result.conversation_id);
      setMessages((current) => [...current, result.message]);
    } catch (requestError) {
      setSendError(requestError.message);
    } finally {
      setIsSending(false);
    }
  }

  return {
    messages,
    isLoading,
    isSending,
    loadError,
    sendError,
    draft,
    setDraft,
    loadConversation,
    sendMessage,
    retryLastMessage: () => sendMessage(lastSentMessage),
  };
}
