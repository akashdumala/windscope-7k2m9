
const API_BASE_URL = "https://windscope-7k2m9.onrender.com/api";

export async function getDashboardSummary() {
  const response = await fetch(
    `${API_BASE_URL}/analysis/january-2026`
  );

  if (!response.ok) {
    throw new Error(`API request failed (${response.status})`);
  }

  return response.json();
}
