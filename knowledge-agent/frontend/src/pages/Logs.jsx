import { useEffect, useState } from "react";
import LogsTable from "../components/LogsTable";
import { getLogs } from "../api/agentApi";

export default function Logs() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await getLogs(50);
      setLogs(data.logs || []);
      setTotal(data.total || 0);
      setError(null);
    } catch (err) {
      setError(err.message || "Failed to fetch logs");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <div className="page logs-page">
      <div className="page-header">
        <div>
          <h1>Audit Logs</h1>
          <p className="page-subtitle">
            {total} total agent execution{total !== 1 ? "s" : ""} recorded
          </p>
        </div>
        <button className="refresh-btn" onClick={fetchLogs} disabled={loading}>
          {loading ? "Loading..." : "↻ Refresh"}
        </button>
      </div>

      {error && (
        <div className="error-card animate-in">
          <span>⚠️</span> {error}
        </div>
      )}

      {loading ? (
        <div className="loading-state">
          <div className="spinner large"></div>
          <p>Loading audit logs...</p>
        </div>
      ) : (
        <LogsTable logs={logs} />
      )}
    </div>
  );
}
