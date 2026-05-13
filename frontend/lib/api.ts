const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function checkBackendHealth() {
  const response = await fetch(`${API_BASE_URL}/api/health`);

  if (!response.ok) {
    throw new Error("Backend health check failed");
  }

  return response.json();
}

export async function checkDatabaseHealth() {
  const response = await fetch(`${API_BASE_URL}/api/db-health`);

  if (!response.ok) {
    throw new Error("Database health check failed");
  }

  return response.json();
}