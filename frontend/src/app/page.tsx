export default function Home() {
  return (
    <main style={{ padding: "4rem", textAlign: "center" }}>
      <h1>Campaign Admin Control Plane</h1>
      <p style={{ margin: "2rem 0", color: "#666" }}>
        Manage candidates, process voter lists via OCR, and provision white-labeled mobile apps.
      </p>
      <div style={{ display: "flex", gap: "2rem", justifyContent: "center" }}>
        <a href="/candidates" style={{ padding: "1rem 2rem", backgroundColor: "#0070f3", color: "white", borderRadius: "8px", textDecoration: "none" }}>
          Manage Candidates
        </a>
      </div>
    </main>
  );
}
