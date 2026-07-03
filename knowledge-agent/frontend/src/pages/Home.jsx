import { useState } from "react";
import QueryInput from "../components/QueryInput";
import AnswerCard from "../components/AnswerCard";
import { askAgent } from "../api/agentApi";

export default function Home() {
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentQuery, setCurrentQuery] = useState("");

  const handleSubmit = async (query, isApproved = false) => {
    setIsLoading(true);
    setError(null);
    setCurrentQuery(query);

    try {
      const data = await askAgent(query, isApproved);
      setResult(data);
      setHistory((prev) => [{ query, ...data, time: new Date() }, ...prev]);
    } catch (err) {
      setError(
        err.response?.data?.detail || err.message || "Something went wrong"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = () => {
    if (currentQuery) {
      handleSubmit(currentQuery, true);
    }
  };

  return (
    <div className="page home-page">
      <div className="hero-section">
        <div className="hero-glow"></div>
        <h1>
          <span className="gradient-text">Knowledge Agent</span>
        </h1>
        <p className="hero-subtitle">
          Ask anything — I'll retrieve, reason, decide, act, and explain.
        </p>
      </div>

      <QueryInput onSubmit={handleSubmit} isLoading={isLoading} />

      {error && (
        <div className="error-card animate-in">
          <span>⚠️</span> {error}
        </div>
      )}

      <AnswerCard data={result} onApprove={handleApprove} />

      {/* Chat History */}
      {history.length > 1 && (
        <div className="history-section">
          <h3>Recent Queries</h3>
          <div className="history-list">
            {history.slice(1).map((item, i) => (
              <div key={i} className="history-item">
                <span className="history-query">{item.query}</span>
                <span
                  className="action-chip"
                  style={{
                    "--chip-color":
                      item.action_taken === "answer_question"
                        ? "#6c63ff"
                        : item.action_taken === "generate_report"
                        ? "#00c9a7"
                        : item.action_taken === "flag_issue"
                        ? "#ff6b6b"
                        : "#8b8b8b",
                  }}
                >
                  {item.action_taken?.replace("_", " ")}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
