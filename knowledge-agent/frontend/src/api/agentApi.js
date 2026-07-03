import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  headers: { "Content-Type": "application/json" },
  timeout: 60000, // 60s — agent may take time to reason
});

/**
 * Send a query to the knowledge agent.
 * @param {string} query — user's natural language question
 * @returns {Promise<{answer: string, action_taken: string, explanation: string, require_approval: boolean}>}
 */
export async function askAgent(query) {
  const response = await api.post("/ask", { query });
  return response.data;
}

/**
 * Fetch recent audit logs.
 * @param {number} limit — max entries
 * @returns {Promise<{logs: Array, total: number}>}
 */
export async function getLogs(limit = 20) {
  const response = await api.get("/logs", { params: { limit } });
  return response.data;
}

/**
 * Load sample knowledge data into the backend.
 */
export async function loadKnowledge() {
  const response = await api.post(
    "/load-knowledge",
    {},
    { baseURL: "http://localhost:8000/api/v1/../.." }
  );
  return response.data;
}
