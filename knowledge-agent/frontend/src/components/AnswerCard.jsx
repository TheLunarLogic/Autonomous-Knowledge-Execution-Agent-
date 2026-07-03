export default function AnswerCard({ data, onApprove, onReject }) {
  if (!data) return null;

  const { answer, action_taken, explanation, require_approval } = data;

  const actionLabels = {
    answer_question: { label: "Answered", icon: "💡", color: "#6c63ff" },
    generate_report: { label: "Report Generated", icon: "📊", color: "#00c9a7" },
    flag_issue: { label: "Issue Flagged", icon: "⚠️", color: "#ff6b6b" },
    no_action: { label: "No Action", icon: "ℹ️", color: "#8b8b8b" },
  };

  const actionInfo = actionLabels[action_taken] || actionLabels.no_action;

  return (
    <div className="answer-card animate-in">
      {/* Action Badge */}
      <div className="action-badge" style={{ "--badge-color": actionInfo.color }}>
        <span className="action-icon">{actionInfo.icon}</span>
        <span className="action-label">{actionInfo.label}</span>
      </div>

      {/* Approval Warning */}
      {require_approval && !data.isHistory && (
        <div className="approval-banner">
          <span>🔒 This action requires your approval before execution.</span>
          <div className="approval-actions">
            <button className="approve-btn" onClick={onApprove}>
              ✓ Approve &amp; Execute
            </button>
            <button className="reject-btn" onClick={onReject}>
              ✕ Reject
            </button>
          </div>
        </div>
      )}

      {/* Answer Content */}
      <div className="answer-section">
        <h3>Answer</h3>
        <div className="answer-text">{answer}</div>
      </div>

      {/* Explanation */}
      <div className="explanation-section">
        <h3>Behind the Scenes (Backend Reasoning)</h3>
        <p>{explanation}</p>
        <div className="backend-activity">
          <strong>Tool Called:</strong> <code>{action_taken}</code>
        </div>
      </div>
    </div>
  );
}
