import { useEffect, useRef, useState } from "react";
import { fetchConversation, sendChatMessage } from "../api/chatApi";

const CONVERSATION_KEY = "matchmaking-assistant-conversation-id";
const DRAFT_KEY = "matchmaking-assistant-draft";

function readStorage(storageName, key) {
  try {
    return window[storageName].getItem(key);
  } catch {
    return null;
  }
}

function writeStorage(storageName, key, value) {
  try {
    window[storageName].setItem(key, value);
  } catch {
    // Keep the in-memory chat usable when browser storage is unavailable.
  }
}

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(
    () => readStorage("localStorage", CONVERSATION_KEY) || null,
  );
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [sendError, setSendError] = useState("");
  const [draft, setDraft] = useState(() => readStorage("sessionStorage", DRAFT_KEY) || "");
  const [lastSentMessage, setLastSentMessage] = useState("");
  const sendInProgressRef = useRef(false);

  useEffect(() => {
    if (conversationId) writeStorage("localStorage", CONVERSATION_KEY, conversationId);
  }, [conversationId]);

  useEffect(() => {
    writeStorage("sessionStorage", DRAFT_KEY, draft);
  }, [draft]);

  async function loadConversation() {
    setIsLoading(true);
    setLoadError("");

    try {
      if (!conversationId) {
        setMessages([]);
        return;
      }
      const conversation = await fetchConversation(conversationId);
      setMessages(conversation.messages || []);
    } catch {
      setMessages([]);
      setLoadError("I couldn't load our chat just now. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  async function sendMessage(text, { isRetry = false } = {}) {
    const trimmed = text.trim();
    if (!trimmed || sendInProgressRef.current || trimmed.length > 500) return;

    sendInProgressRef.current = true;
    setSendError("");
    if (!isRetry) {
      setMessages((current) => [
        ...current,
        { id: `user-${Date.now()}`, role: "user", content: trimmed },
      ]);
    }
    setIsSending(true);
    if (!isRetry) setDraft("");
    setLastSentMessage(trimmed);

    try {
      const result = await sendChatMessage(trimmed, conversationId);
      setConversationId(result.conversation_id);
      setMessages((current) => [...current, result.message]);
    } catch (requestError) {
      setSendError(requestError.message);
    } finally {
      sendInProgressRef.current = false;
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
    retryLastMessage: () => sendMessage(lastSentMessage, { isRetry: true }),
  };
}
