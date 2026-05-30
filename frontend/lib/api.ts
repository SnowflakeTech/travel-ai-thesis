import type {
  AgentResponse,
  ComparePromptsResponse,
  UserPreferences,
} from "@/types/travel";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const DEMO_API_KEY = process.env.NEXT_PUBLIC_DEMO_API_KEY || "";

function demoAuthHeaders() {
  return {
    "Content-Type": "application/json",
    "x-demo-api-key": DEMO_API_KEY,
  };
}

function demoAuthOnlyHeaders() {
  return {
    "x-demo-api-key": DEMO_API_KEY,
  };
}

async function parseApiError(response: Response, fallbackMessage: string) {
  let detail = fallbackMessage;

  try {
    const data = await response.json();

    if (typeof data.detail === "string") {
      detail = data.detail;
    } else if (data.detail) {
      detail = JSON.stringify(data.detail);
    } else if (data.message) {
      detail = data.message;
    }
  } catch {
    detail = fallbackMessage;
  }

  throw new Error(`${response.status} ${response.statusText}: ${detail}`);
}

export async function checkBackendHealth() {
  const response = await fetch(`${API_BASE_URL}/api/health`);

  if (!response.ok) {
    await parseApiError(response, "Backend health check failed");
  }

  return response.json();
}

export async function checkDatabaseHealth() {
  const response = await fetch(`${API_BASE_URL}/api/db-health`);

  if (!response.ok) {
    await parseApiError(response, "Database health check failed");
  }

  return response.json();
}

export async function sendAgentMessage(
  message: string
): Promise<AgentResponse> {
  const response = await fetch(`${API_BASE_URL}/api/agent/travel`, {
    method: "POST",
    headers: demoAuthHeaders(),
    body: JSON.stringify({
      user_id: "demo_user",
      message,
    }),
  });

  if (!response.ok) {
    await parseApiError(response, "Agent request failed");
  }

  return response.json();
}

export async function regenerateDay(day: number, originalRequest: string) {
  const response = await fetch(`${API_BASE_URL}/api/agent/regenerate-day`, {
    method: "POST",
    headers: demoAuthHeaders(),
    body: JSON.stringify({
      user_id: "demo_user",
      day,
      original_request: originalRequest,
    }),
  });

  if (!response.ok) {
    await parseApiError(response, "Regenerate day failed");
  }

  return response.json();
}

export async function optimizeRoute(originalRequest: string) {
  const response = await fetch(`${API_BASE_URL}/api/agent/optimize-route`, {
    method: "POST",
    headers: demoAuthHeaders(),
    body: JSON.stringify({
      user_id: "demo_user",
      original_request: originalRequest,
    }),
  });

  if (!response.ok) {
    await parseApiError(response, "Optimize route failed");
  }

  return response.json();
}

export async function savePreferences(preferences: UserPreferences) {
  const response = await fetch(`${API_BASE_URL}/api/preferences/demo_user`, {
    method: "POST",
    headers: demoAuthHeaders(),
    body: JSON.stringify(preferences),
  });

  if (!response.ok) {
    await parseApiError(response, "Save preferences failed");
  }

  return response.json();
}

export async function getUserMemories(userId: string = "demo_user") {
  const response = await fetch(`${API_BASE_URL}/api/memory/${userId}`, {
    headers: demoAuthOnlyHeaders(),
  });

  if (!response.ok) {
    await parseApiError(response, "Get memory failed");
  }

  return response.json();
}

export async function comparePrompts(
  message: string,
  userId: string = "demo_user"
): Promise<ComparePromptsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/agent/compare-prompts`, {
    method: "POST",
    headers: demoAuthHeaders(),
    body: JSON.stringify({
      user_id: userId,
      message,
    }),
  });

  if (!response.ok) {
    await parseApiError(response, "Compare prompts failed");
  }

  return response.json();
}
