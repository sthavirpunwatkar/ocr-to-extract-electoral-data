const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchCandidates() {
  const response = await fetch(`${API_BASE_URL}/candidates`, {
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!response.ok) throw new Error("Failed to fetch candidates");
  return response.json();
}

export async function createCandidate(data: { name: string; party_name?: string; constituency_code: string }) {
  const response = await fetch(`${API_BASE_URL}/candidates`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Failed to create candidate");
  return response.json();
}

export async function uploadCandidateAssets(candidateId: number, logo?: File, profileImage?: File) {
  const formData = new FormData();
  if (logo) formData.append("logo", logo);
  if (profileImage) formData.append("profile_image", profileImage);

  const response = await fetch(`${API_BASE_URL}/candidates/${candidateId}/assets`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
    body: formData,
  });
  if (!response.ok) throw new Error("Failed to upload assets");
  return response.json();
}
