export default function LogsTable({ logs }) {
  if (!logs || logs.length === 0) {
    return (
      <div className="empty-state">
        <span className="empty-icon">📋</span>
        <p>No audit logs yet. Ask the agent a question to get started!</p>
      </div>
    );
  }

  const formatDate = (iso) => {
    const d = new Date(iso);
    return d.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const actionColors = {
    answer_question: "#6c63ff",
    generate_report: "#00c9a7",
    flag_issue: "#ff6b6b",
    no_action: "#8b8b8b",
  };

  return (
    <div className="logs-table-wrapper">
      <table className="logs-table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Query</th>
            <th>Action</th>
            <th>Explanation</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id} className="log-row animate-in">
              <td className="log-time">{formatDate(log.created_at)}</td>
              <td className="log-query">{log.query}</td>
              <td>
                <span
                  className="action-chip"
                  style={{
                    "--chip-color":
                      actionColors[log.chosen_action] || "#8b8b8b",
                  }}
                >
                  {log.chosen_action?.replace("_", " ") || "—"}
                </span>
              </td>
              <td className="log-explanation">
                {log.explanation?.slice(0, 120) || "—"}
                {log.explanation?.length > 120 ? "…" : ""}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
