import { useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

function formatDate(iso) {
  return new Date(iso).toLocaleString();
}

export default function App() {
  const [message, setMessage] = useState("");
  const [result, setResult] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [loadingTickets, setLoadingTickets] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const canSubmit = useMemo(() => message.trim().length >= 5, [message]);

  async function fetchTickets() {
    setLoadingTickets(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/tickets?limit=20`);
      if (!response.ok) {
        throw new Error("Failed to load ticket list.");
      }
      const data = await response.json();
      setTickets(data);
    } catch (err) {
      setError(err.message || "Could not fetch tickets.");
    } finally {
      setLoadingTickets(false);
    }
  }

  useEffect(() => {
    fetchTickets();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!canSubmit) return;
    setSubmitting(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/tickets/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message.trim() })
      });
      if (!response.ok) {
        const payload = await response.json();
        throw new Error(payload.detail || "Analysis failed.");
      }
      const data = await response.json();
      setResult(data);
      setMessage("");
      fetchTickets();
    } catch (err) {
      setError(err.message || "Unable to analyze ticket.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="page">
      <section className="card">
        <h1>AI-Powered Support Ticket Triage</h1>
        <p className="sub">Submit a ticket and get local NLP-based analysis.</p>

        <form onSubmit={handleSubmit} className="form">
          <textarea
            placeholder="Describe the support issue..."
            rows={6}
            value={message}
            onChange={(event) => setMessage(event.target.value)}
          />
          <button disabled={!canSubmit || submitting} type="submit">
            {submitting ? "Analyzing..." : "Analyze Ticket"}
          </button>
        </form>

        {error && <div className="error">{error}</div>}
      </section>

      {result && (
        <section className="card result">
          <h2>Latest Result</h2>
          <div className="grid">
            <p><strong>Category:</strong> {result.category}</p>
            <p><strong>Priority:</strong> {result.priority}</p>
            <p><strong>Urgency:</strong> {result.urgency}</p>
            <p><strong>Confidence:</strong> {(result.confidence * 100).toFixed(0)}%</p>
          </div>
          <p><strong>Signals:</strong> {result.signals.join(", ") || "None"}</p>
          <p><strong>Keywords:</strong> {result.keywords.join(", ") || "None"}</p>
        </section>
      )}

      <section className="card">
        <h2>Recent Tickets</h2>
        {loadingTickets ? (
          <p>Loading tickets...</p>
        ) : tickets.length === 0 ? (
          <p>No analyzed tickets yet.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Category</th>
                  <th>Priority</th>
                  <th>Urgency</th>
                  <th>Confidence</th>
                  <th>Keywords</th>
                </tr>
              </thead>
              <tbody>
                {tickets.map((ticket) => (
                  <tr key={ticket.id}>
                    <td>{formatDate(ticket.created_at)}</td>
                    <td>{ticket.category}</td>
                    <td>{ticket.priority}</td>
                    <td>{ticket.urgency}</td>
                    <td>{(ticket.confidence * 100).toFixed(0)}%</td>
                    <td>{ticket.keywords.join(", ")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}
