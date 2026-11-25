import { useEffect, useRef, useState } from "react";
import ChatInput from "./components/ChatInput";
import MessageList from "./components/MessageList";
import { useChat } from "./hooks/useChat";

export default function App({ isAuthenticated = true }) {
  const [isOpen, setIsOpen] = useState(false);
  const launcherRef = useRef(null);
  const inputRef = useRef(null);
  const panelRef = useRef(null);
  const {
    messages,
    isLoading,
    isSending,
    loadError,
    sendError,
    draft,
    setDraft,
    loadConversation,
    sendMessage,
    retryLastMessage,
  } = useChat();

  const assistantEnabled =
    isAuthenticated && import.meta.env.VITE_ASSISTANT_FEATURE_FLAG !== "false";

  useEffect(() => {
    if (!isAuthenticated) setIsOpen(false);
  }, [isAuthenticated]);

  useEffect(() => {
    if (isOpen) {
      loadConversation();
      window.requestAnimationFrame(() => inputRef.current?.focus());
    }
  }, [isOpen]);

  useEffect(() => {
    function handleEscape(event) {
      if (event.key === "Escape" && isOpen) closePanel();
    }
    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [isOpen]);

  useEffect(() => {
    function trapFocus(event) {
      if (!isOpen || window.innerWidth >= 768 || event.key !== "Tab") return;
      const controls = panelRef.current?.querySelectorAll(
        "button:not(:disabled), input:not(:disabled), [tabindex='0']",
      );
      if (!controls?.length) return;
      const first = controls[0];
      const last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
    window.addEventListener("keydown", trapFocus);
    return () => window.removeEventListener("keydown", trapFocus);
  }, [isOpen]);

  function closePanel() {
    setIsOpen(false);
    window.requestAnimationFrame(() => launcherRef.current?.focus());
  }

  function togglePanel() {
    setIsOpen((current) => !current);
  }

  function choosePrompt(prompt) {
    setDraft(prompt);
    window.requestAnimationFrame(() => inputRef.current?.focus());
  }

  function showMore() {
    sendMessage("show more");
  }

  return (
    <main className="app-shell">
      <section className="demo-page">
        <div className="demo-card">
          <span className="demo-kicker">Member home</span>
          <h1>Find someone who fits your life.</h1>
          <p>Explore profiles and get help with your next conversation.</p>
        </div>
      </section>

      {assistantEnabled && isOpen && (
        <section className="chat-panel" ref={panelRef} aria-label="Matchmaking assistant">
          <header className="chat-header">
            <h2>Matchmaking assistant</h2>
            <button type="button" className="close-button" onClick={closePanel} aria-label="Close assistant">
              <span aria-hidden="true">×</span>
            </button>
          </header>
          <div className="chat-body">
            {isLoading ? (
              <div className="loading-skeleton" aria-label="Loading conversation">
                <span /><span /><span />
              </div>
            ) : loadError ? (
              <div className="load-error" role="alert">
                <p>{loadError}</p>
                <button type="button" onClick={loadConversation}>Try again</button>
              </div>
            ) : (
              <MessageList
                messages={messages}
                isSending={isSending}
                onPrompt={choosePrompt}
                onShowMore={showMore}
              />
            )}
            {sendError && (
              <div className="send-error" role="alert">
                <p>{sendError}</p>
                <button type="button" onClick={retryLastMessage}>Try again</button>
              </div>
            )}
          </div>
          <ChatInput
            value={draft}
            onChange={setDraft}
            onSend={sendMessage}
            isDisabled={Boolean(loadError) || isSending}
            isSendDisabled={isLoading || Boolean(loadError) || isSending || draft.length > 500}
            inputRef={inputRef}
          />
        </section>
      )}

      {assistantEnabled && <button
        ref={launcherRef}
        type="button"
        className="chat-launcher"
        onClick={togglePanel}
        aria-label="Chat with the assistant"
        aria-expanded={isOpen}
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M5 4h14a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H9l-5 4v-4.2A2 2 0 0 1 3 15V6a2 2 0 0 1 2-2Z" />
        </svg>
        <span className="launcher-tooltip" role="tooltip">Chat with the assistant</span>
      </button>}
    </main>
  );
}
