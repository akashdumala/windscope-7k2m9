
const API_BASE_URL = "https://windscope-7k2m9.onrender.com/api";

export async function getDashboardSummary() {
  const response = await fetch(
    `${API_BASE_URL}/analysis/january-2026`
  );

  if (!response.ok) {
    const details = await response.text();
    throw new Error(
      `API request failed (${response.status}): ${details.slice(0, 150)}`
    );
  }

  return response.json();
}
