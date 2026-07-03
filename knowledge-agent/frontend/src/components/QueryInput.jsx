import { useState } from "react";

export default function QueryInput({ onSubmit, isLoading }) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;
    onSubmit(query.trim());
    setQuery("");
  };

  return (
    <form className="query-input" onSubmit={handleSubmit}>
      <div className="input-wrapper">
        <div className="input-glow"></div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask the Knowledge Agent anything..."
          disabled={isLoading}
          autoFocus
        />
        <button type="submit" disabled={isLoading || !query.trim()}>
          {isLoading ? (
            <span className="spinner"></span>
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 2L11 13" />
              <path d="M22 2L15 22L11 13L2 9L22 2Z" />
            </svg>
          )}
        </button>
      </div>
    </form>
  );
}
