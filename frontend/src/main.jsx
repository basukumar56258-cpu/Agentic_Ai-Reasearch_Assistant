import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [query, setQuery] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function runResearch(e) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setData(null);

    try {
      const res = await fetch(`${API}/api/research`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({query})
      });
      const json = await res.json();
      if (!res.ok) {
        const detail = String(json.detail || "");
        const isApiKeyError = res.status === 401 || /api.?key|invalid_api_key|credentials/i.test(detail);
        throw new Error(
          isApiKeyError
            ? "API keys are missing or invalid. Update backend/.env with valid OPENAI_API_KEY and TAVILY_API_KEY, then retry."
            : detail || "Research failed."
        );
      }
      setData(json);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header>
        <div className="badge">AGENTIC AI</div>
        <h1>Research Assistant</h1>
        <p>Ask a question. Agents plan, research, and synthesize a cited report.</p>
      </header>

      <main>
        <form onSubmit={runResearch} className="search-box">
          <textarea
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Example: Research the latest trends in AI agents..."
            rows="4"
          />
          <button disabled={loading}>
            {loading ? "Researching..." : "Start Research"}
          </button>
        </form>

        {error && <div className="error">{error}</div>}

        {loading && (
          <div className="card">
            <h2>Agent workflow running</h2>
            <div className="steps">
              <span>1. Planning</span>
              <span>2. Web Research</span>
              <span>3. Synthesis</span>
            </div>
          </div>
        )}

        {data && (
          <>
            <section className="card">
              <h2>Research Plan</h2>
              <ol>{data.plan.map((x, i) => <li key={i}>{x}</li>)}</ol>
            </section>

            <section className="card report">
              <h2>Research Report</h2>
              <pre>{data.report}</pre>
            </section>

            <section className="card">
              <h2>Sources</h2>
              {data.sources.map(s => (
                <a className="source" href={s.url} target="_blank" rel="noreferrer" key={s.id}>
                  <b>[{s.id}] {s.title}</b>
                  <small>{s.url}</small>
                </a>
              ))}
            </section>
          </>
        )}
      </main>

      <footer>Agentic AI Research Assistant • MVP</footer>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
