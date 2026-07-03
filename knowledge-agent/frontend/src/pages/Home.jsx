import { useState, useEffect } from "react";
import QueryInput from "../components/QueryInput";
import AnswerCard from "../components/AnswerCard";
import { askAgent } from "../api/agentApi";

export default function Home() {
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState(() => {
    const saved = localStorage.getItem("akea-history");
    return saved ? JSON.parse(saved) : [];
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentQuery, setCurrentQuery] = useState("");
  const [inputValue, setInputValue] = useState("");

  useEffect(() => {
    localStorage.setItem("akea-history", JSON.stringify(history));
  }, [history]);

  const handleSubmit = async (query, isApproved = false) => {
    if (!isApproved) setResult(null); // Clear previous result on new query
    setIsLoading(true);
    setError(null);
    setCurrentQuery(query);

    try {
      const data = await askAgent(query, isApproved);
      setResult(data);
      setHistory((prev) => [{ query, ...data, time: new Date().toISOString() }, ...prev]);
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

  const handleReject = () => {
    setResult(null);
    setCurrentQuery("");
  };

  const handleHistoryClick = (item) => {
    setCurrentQuery(item.query);
    setResult(item);
    setIsLoading(false);
    setError(null);
  };

  const handleSuggestion = (query) => {
    setInputValue(query);
    handleSubmit(query);
  };

  const runDemo = () => {
    if (isLoading) return;
    setResult(null);
    setCurrentQuery("");
    setInputValue("");
    const demoText = "Can you flag a security issue for James Wilson?";
    let i = 0;
    const interval = setInterval(() => {
      setInputValue((prev) => {
        const nextVal = demoText.slice(0, i + 1);
        i++;
        if (i >= demoText.length) {
          clearInterval(interval);
          setTimeout(() => {
            handleSubmit(demoText);
            setInputValue("");
          }, 600);
        }
        return nextVal;
      });
    }, 40);
  };

  return (
    <div className="home-layout">
      {/* Sidebar for History */}
      <aside className="chat-sidebar">
        <div className="sidebar-header">
          <h3>Chat History</h3>
          <button className="clear-btn" onClick={() => setHistory([])}>Clear All</button>
        </div>
        <div className="history-list">
          {history.map((item, i) => (
            <div key={i} className="history-item" onClick={() => handleHistoryClick(item)}>
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
          {history.length === 0 && (
            <p className="no-history">No past conversations.</p>
          )}
        </div>
      </aside>

      <div className="page home-page chat-main">
      <div className="hero-section">
        <div className="hero-glow"></div>
        <h1>
          <span className="gradient-text">Knowledge Agent</span>
        </h1>
        <p className="hero-subtitle">
          Ask anything — I'll retrieve, reason, decide, act, and explain.
        </p>
      </div>

      <QueryInput 
        query={inputValue} 
        setQuery={setInputValue} 
        onSubmit={handleSubmit} 
        isLoading={isLoading} 
      />

      {error && (
        <div className="error-card animate-in">
          <span>⚠️</span> {error}
        </div>
      )}

      {/* Onboarding Section */}
      {!result && !isLoading && !currentQuery && (
        <div className="onboarding-section animate-in">
          <h2>Welcome to AKEA</h2>
          <div className="onboarding-copy">
            <div className="problem-statement">
              <h4>⚠️ The Problem</h4>
              <p>Company knowledge and operations are often scattered across databases, documents, and APIs. When you need an answer or want to execute a workflow, you are forced to jump between tools manually.</p>
            </div>
            <div className="solution-statement">
              <h4>✨ The Solution</h4>
              <p>AKEA connects directly to your data stores. It uses LLMs to autonomously retrieve relevant knowledge, reason through the facts, and execute complex backend actions based on your intent.</p>
            </div>
          </div>
          
          <h3 className="how-it-works-title">How it works:</h3>
          <div className="features-grid">
            <div className="feature-card">
              <h3>🔍 Retrieve</h3>
              <p>Searches through structured Postgres data and vector embeddings to find exactly what you need.</p>
            </div>
            <div className="feature-card">
              <h3>🧠 Reason</h3>
              <p>Analyzes retrieved context to determine the best course of action.</p>
            </div>
            <div className="feature-card">
              <h3>⚡ Execute</h3>
              <p>Safely executes backend actions (like generating reports) with your explicit approval.</p>
            </div>
          </div>
          <div className="suggestion-chips">
            <p>Try asking:</p>
            <button onClick={() => handleSuggestion("Who is John Doe?")} className="suggestion-chip">"Who is John Doe?"</button>
            <button onClick={() => handleSuggestion("Generate a system report")} className="suggestion-chip">"Generate a system report"</button>
            <button onClick={() => handleSuggestion("Wait, block the user account for john.doe.")} className="suggestion-chip">"Wait, block the user account for john.doe."</button>
            <button onClick={runDemo} className="suggestion-chip demo-chip">▶️ Watch Demo</button>
          </div>
        </div>
      )}

      {/* User Query Message */}
      {(result || isLoading) && currentQuery && (
        <div className="user-query-message animate-in">
          <span className="user-query-icon">👤</span>
          <span>{currentQuery}</span>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="loading-state animate-in">
          <span className="spinner large"></span>
          <p>🧠 AI is reasoning and retrieving context...</p>
        </div>
      )}

      <AnswerCard data={result} onApprove={handleApprove} onReject={handleReject} />
      </div>
    </div>
  );
}
