export default function ChatInput({
  value,
  onChange,
  onSend,
  isDisabled,
  isSendDisabled,
  inputRef,
}) {
  function submit(event) {
    event.preventDefault();
    if (!value.trim() || isDisabled || isSendDisabled) return;
    onSend(value);
  }

  return (
    <form className="chat-input" onSubmit={submit}>
      <input
        ref={inputRef}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Type what you're looking for"
        aria-label="Chat message"
        disabled={isDisabled}
        autoFocus
      />
      <button type="submit" disabled={!value.trim() || isDisabled || isSendDisabled}>
        Send
      </button>
    </form>
  );
}
