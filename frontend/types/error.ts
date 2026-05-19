export type AppErrorCode =
  | "BACKEND_OFFLINE"
  | "GEMINI_QUOTA_EXCEEDED"
  | "GEMINI_API_ERROR"
  | "QDRANT_NOT_RUNNING"
  | "NO_RETRIEVED_CONTEXT"
  | "MAP_MISSING_COORDINATES"
  | "MEMORY_SAVE_FAILED"
  | "AGENT_WORKFLOW_ERROR"
  | "NETWORK_ERROR"
  | "UNKNOWN_ERROR";

export type AppError = {
  code: AppErrorCode;
  title: string;
  message: string;
  suggestions: string[];
  raw?: string;
};