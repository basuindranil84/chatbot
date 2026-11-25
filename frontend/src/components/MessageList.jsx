import { useEffect, useRef } from "react";

const EXAMPLE_PROMPTS = [
  "Find doctors in Kolkata aged 28 to 32",
  "Show my favorites",
  "Help me write a first message",
];

export default function MessageList({ messages, isSending, onPrompt }) {
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
            <div className="profile-results" aria-label="Matching profiles">
              {message.profiles.map((profile) => (
                <article className="profile-card" key={profile.id}>
                  <h3>{profile.name}</h3>
                  <p className="profile-summary">
                    {profile.age} · {profile.gender} · {profile.profession}
                  </p>
                  <p>{profile.city}, {profile.region} · {profile.culture_community}</p>
                  <p>Education: {profile.education}</p>
                  <p>Languages: {profile.languages.join(", ")}</p>
                  <p>Interests: {profile.interests.join(", ")}</p>
                  <p>
                    Looking for: {profile.relationship_preferences.relationship_goal} · ages{" "}
                    {profile.relationship_preferences.preferred_age_range.min}–{profile.relationship_preferences.preferred_age_range.max}
                  </p>
                  <p className="profile-bio">{profile.short_bio}</p>
                </article>
              ))}
            </div>
          )}
        </article>
      ))}
      {isSending && (
        <article className="message assistant">
          <div className="message-avatar">AI</div>
          <div className="typing"><span /><span /><span /></div>
        </article>
      )}
      <div ref={endOfMessagesRef} />
    </div>
  );
}
