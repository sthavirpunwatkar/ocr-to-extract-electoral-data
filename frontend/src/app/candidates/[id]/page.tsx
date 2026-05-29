"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";

export default function CandidateDetailPage() {
  const { id } = useParams();
  const [file, setFile] = useState<File | null>(null);
  const [jobs, setJobs] = useState<any[]>([]);
  const [voters, setVoters] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadJobs();
    loadVoters();
  }, [id]);

  async function loadJobs() {
    const res = await fetch(`http://localhost:8000/extraction-jobs?candidate_id=${id}`, {
        headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
    });
    const data = await res.json();
    setJobs(data);
  }

  async function loadVoters() {
    const res = await fetch(`http://localhost:8000/voters?candidate_id=${id}&limit=100`, {
        headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
    });
    const data = await res.json();
    setVoters(data);
  }

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`http://localhost:8000/upload?candidate_id=${id}`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` },
        body: formData
      });
      if (res.ok) {
        alert("Upload successful! OCR processing started.");
        loadJobs();
      }
    } catch (e) {
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleApprove(jobId: string) {
    await fetch(`http://localhost:8000/extraction-jobs/${jobId}/approve`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
    });
    loadJobs();
    loadVoters();
  }

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Candidate Data Management (ID: {id})</h1>
      
      <section style={{ marginBottom: "2rem" }}>
        <h2>Upload Voter PDF</h2>
        <form onSubmit={handleUpload} style={{ display: "flex", gap: "1rem" }}>
          <input type="file" accept=".pdf" onChange={e => setFile(e.target.files?.[0] || null)} required />
          <button type="submit" disabled={loading}>{loading ? "Uploading..." : "Upload & Process OCR"}</button>
        </form>
      </section>

      <section style={{ marginBottom: "2rem" }}>
        <h2>Extraction Jobs</h2>
        <table border={1} cellPadding={10} style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th>Job ID</th>
              <th>File Name</th>
              <th>Status</th>
              <th>Confidence</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map(j => (
              <tr key={j.id}>
                <td>{j.id}</td>
                <td>{j.file_name}</td>
                <td>{j.status}</td>
                <td>{j.confidence_score ? (j.confidence_score * 100).toFixed(1) + "%" : "N/A"}</td>
                <td>
                  {j.status === "pending_review" && (
                    <button onClick={() => handleApprove(j.id)}>Verify & Approve</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section>
        <h2>Extracted Voters (OCR Values)</h2>
        <div style={{ overflowX: "auto" }}>
          <table border={1} cellPadding={10} style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th>Voter ID</th>
                <th>Full Name</th>
                <th>Confidence</th>
                <th>Structured Data</th>
              </tr>
            </thead>
            <tbody>
              {voters.map(v => (
                <tr key={v.id}>
                  <td>{v.voter_id}</td>
                  <td>{v.full_name}</td>
                  <td>{(v.confidence * 100).toFixed(1)}%</td>
                  <td><pre style={{ fontSize: "0.8rem" }}>{JSON.stringify(v.structured_data, null, 2)}</pre></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <div style={{ marginTop: "2rem" }}>
          <button style={{ backgroundColor: "green", color: "white", padding: "1rem", borderRadius: "8px", cursor: "pointer" }} onClick={() => alert("Triggering automated build pipeline for Candidate APK...")}>
              Generate Customized Mobile App (APK)
          </button>
      </div>
    </div>
  );
}
