import { useEffect, useRef } from "react";

const EXAMPLE_PROMPTS = [
  "Find doctors in Kolkata aged 28 to 32",
  "Show my favorites",
  "Help me write a first message",
];

export default function MessageList({ messages, isSending, onPrompt, onShowMore }) {
  const endOfMessagesRef = useRef(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ block: "end" });
  }, [messages, isSending]);

  return (
    <div className="message-list" aria-live="polite">
      {messages.length === 0 && (
        <article className="greeting">
          <div className="greeting-copy">
            Hi, I'm your matchmaking assistant. I can help you find profiles, save the ones you like, and message them. Not sure where to start? Try one of these.
          </div>
          <div className="prompt-list" aria-label="Example prompts">
            {EXAMPLE_PROMPTS.map((prompt) => (
              <button type="button" className="prompt" key={prompt} onClick={() => onPrompt(prompt)}>
                {prompt}
              </button>
            ))}
          </div>
        </article>
      )}
      {messages.map((message) => (
        <article
          className={`message ${message.role}${message.role === "assistant" && message.profiles?.length === 0 ? " no-results" : ""}`}
          key={message.id}
        >
          <div className="message-avatar">
            {message.role === "assistant" ? "AI" : "You"}
          </div>
          <div className="message-body">{message.content}</div>
          {message.profiles?.length > 0 && (
            <div className="profile-results" aria-label="Matching profiles" role="list">
              {message.profiles.map((profile) => {
                const firstName = profile.first_name || profile.name?.split(" ")[0] || "Profile";
                const summary = [profile.age, profile.city, profile.profession]
                  .filter((value) => value !== null && value !== undefined && value !== "")
                  .join(" · ");
                const accessibleName = [firstName, profile.age, profile.profession, profile.city]
                  .filter((value) => value !== null && value !== undefined && value !== "")
                  .join(", ");

                return (
                  <article
                    className="profile-card"
                    key={profile.profile_id || profile.id}
                    role="listitem"
                    aria-label={accessibleName}
                  >
                    {profile.photo_url ? (
                      <img
                        className="profile-photo"
                        src={profile.photo_url}
                        alt=""
                        width="64"
                        height="64"
                        loading="lazy"
                        decoding="async"
                      />
                    ) : (
                      <div className="profile-photo profile-photo-fallback" aria-hidden="true">
                        {firstName.charAt(0)}
                      </div>
                    )}
                    <div className="profile-card-copy">
                      <h3>{firstName}</h3>
                      <p className="profile-summary">{summary}</p>
                      <a
                        className="profile-link"
                        href={profile.profile_url || `/profile/${profile.profile_id || profile.id}`}
                      >
                        View profile
                      </a>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
          {message.has_more && (
            <button type="button" className="show-more-button" onClick={onShowMore}>
              Show 5 more
            </button>
          )}
        </article>
      ))}
      {isSending && (
        <article className="message assistant">
          <div className="message-avatar">AI</div>
          <div className="typing" role="status" aria-label="Assistant is typing">
            <span /><span /><span />
          </div>
        </article>
      )}
      <div ref={endOfMessagesRef} />
    </div>
  );
}
