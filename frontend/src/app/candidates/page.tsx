"use client";

import { useState, useEffect } from "react";
import { fetchCandidates, createCandidate, uploadCandidateAssets } from "@/lib/api";

export default function CandidatesPage() {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [name, setName] = useState("");
  const [party, setParty] = useState("");
  const [constituency, setConstituency] = useState("");
  const [logo, setLogo] = useState<File | null>(null);
  const [image, setImage] = useState<File | null>(null);

  useEffect(() => {
    loadCandidates();
  }, []);

  async function loadCandidates() {
    try {
      const data = await fetchCandidates();
      setCandidates(data);
    } catch (e) {
      console.error(e);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      const candidate = await createCandidate({ name, party_name: party, constituency_code: constituency });
      if (logo || image) {
        await uploadCandidateAssets(candidate.id, logo || undefined, image || undefined);
      }
      setName("");
      setParty("");
      setConstituency("");
      setLogo(null);
      setImage(null);
      loadCandidates();
    } catch (e) {
      alert("Error creating candidate");
    }
  }

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Candidate Management</h1>
      
      <form onSubmit={handleSubmit} style={{ marginBottom: "2rem", display: "flex", flexDirection: "column", gap: "1rem", maxWidth: "400px" }}>
        <input type="text" placeholder="Candidate Name" value={name} onChange={e => setName(e.target.value)} required />
        <input type="text" placeholder="Party Name" value={party} onChange={e => setParty(e.target.value)} />
        <input type="text" placeholder="Constituency Code" value={constituency} onChange={e => setConstituency(e.target.value)} required />
        <div>
          <label>Party Logo:</label>
          <input type="file" onChange={e => setLogo(e.target.files?.[0] || null)} />
        </div>
        <div>
          <label>Profile Image:</label>
          <input type="file" onChange={e => setImage(e.target.files?.[0] || null)} />
        </div>
        <button type="submit" style={{ padding: "0.5rem", cursor: "pointer" }}>Add Candidate</button>
      </form>

      <table border={1} cellPadding={10} style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>Name</th>
            <th>Party</th>
            <th>Constituency</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {candidates.map(c => (
            <tr key={c.id}>
              <td>{c.name}</td>
              <td>{c.party_name}</td>
              <td>{c.constituency_code}</td>
              <td>
                <button onClick={() => window.location.href=`/candidates/${c.id}`}>View / Upload Data</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
