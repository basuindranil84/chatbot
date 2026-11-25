export default function ChatInput({
  value,
  onChange,
  onSend,
  isDisabled,
  isSendDisabled,
  inputRef,
}) {
  const characterCount = value.length;
  const overLimit = characterCount - 500;

  function submit(event) {
    event.preventDefault();
    if (!value.trim() || isDisabled || isSendDisabled) return;
    onSend(value);
  }

  return (
    <form className="chat-input" onSubmit={submit}>
      <div className="chat-input-main">
        <input
          ref={inputRef}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Type what you're looking for"
          aria-label="Chat message"
          aria-describedby={characterCount >= 400 ? "chat-character-count" : undefined}
          disabled={isDisabled}
          autoFocus
        />
        {characterCount >= 400 && (
          <span
            id="chat-character-count"
            className={`character-count ${overLimit > 0 ? "over-limit" : ""}`}
            role={overLimit > 0 ? "alert" : undefined}
          >
            {overLimit > 0 ? `${overLimit} characters over the limit` : `${characterCount}/500`}
          </span>
        )}
      </div>
      <button type="submit" disabled={!value.trim() || isDisabled || isSendDisabled || characterCount > 500}>
        Send
      </button>
    </form>
  );
}
