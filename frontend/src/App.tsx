import { useState } from "react";

const areas = ["Chat", "Knowledge", "Sources", "My Learning"] as const;

export default function App() {
  const [area, setArea] = useState<(typeof areas)[number]>("Chat");
  return (
    <main>
      <p className="eyebrow">无限引擎 / INFINITE ENGINE</p>
      <h1>From Zero to Infinite Possibilities.</h1>
      <p>
        A local-first workspace for curiosity, knowledge, and personal
        understanding.
      </p>
      <nav aria-label="Workspace">
        {areas.map((name) => (
          <button
            key={name}
            aria-pressed={area === name}
            onClick={() => setArea(name)}
          >
            {name}
          </button>
        ))}
      </nav>
      <section aria-labelledby="area-title">
        <h2 id="area-title">{area}</h2>
        <p role="status">Not implemented — repository foundation only.</p>
        <p>
          Conversation and structured exploration will share source-grounded
          knowledge. Personal interpretations will remain distinct from reviewed
          knowledge.
        </p>
      </section>
      <footer>
        No domain seeds, AI answers, or learning scores are available yet.
      </footer>
    </main>
  );
}
