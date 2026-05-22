import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

function App() {
  return (
    <main className="shell">
      <section className="intro">
        <p className="eyebrow">AI Financial Intelligence Platform</p>
        <h1>Finance Engine</h1>
        <p>
          A backend-heavy distributed AI data platform for ingestion, enrichment,
          semantic search, narrative detection, and research workflows.
        </p>
      </section>

      <section className="status-grid" aria-label="System modules">
        <article>
          <span>01</span>
          <h2>Ingestion</h2>
          <p>Financial documents enter as traceable raw source records.</p>
        </article>
        <article>
          <span>02</span>
          <h2>Workers</h2>
          <p>Queued jobs enrich events outside the request path.</p>
        </article>
        <article>
          <span>03</span>
          <h2>Search</h2>
          <p>Keyword and semantic retrieval expose indexed intelligence.</p>
        </article>
        <article>
          <span>04</span>
          <h2>Narratives</h2>
          <p>Related events become explainable market themes.</p>
        </article>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
