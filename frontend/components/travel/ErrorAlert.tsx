"use client";

import type { AppError } from "@/types/error";
import {
  AlertTriangle,
  Database,
  MapPinned,
  MemoryStick,
  RefreshCcw,
  ServerCrash,
  Sparkles,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";

type ErrorAlertProps = {
  error: AppError;
  onClose?: () => void;
  onRetry?: () => void;
};

export function ErrorAlert({ error, onClose, onRetry }: ErrorAlertProps) {
  const Icon = getErrorIcon(error.code);

  return (
    <div className="rounded-2xl border border-red-400/20 bg-red-950/30 p-5 text-white shadow-2xl shadow-red-950/20 backdrop-blur-xl">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div className="flex gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-red-400/10 text-red-300">
            <Icon className="h-5 w-5" />
          </div>

          <div>
            <h3 className="font-semibold text-red-100">{error.title}</h3>
            <p className="mt-1 text-sm leading-6 text-red-100/80">
              {error.message}
            </p>
          </div>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            className="rounded-full p-1 text-red-100/70 hover:bg-white/10 hover:text-white"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      <div className="rounded-xl border border-white/10 bg-black/20 p-4">
        <p className="mb-2 text-sm font-medium text-red-100">
          Gợi ý kiểm tra:
        </p>

        <ul className="ml-5 list-disc space-y-1 text-sm leading-6 text-red-100/80">
          {error.suggestions.map((suggestion, index) => (
            <li key={index}>{suggestion}</li>
          ))}
        </ul>
      </div>

      {error.raw && (
        <details className="mt-4 rounded-xl border border-white/10 bg-black/20 p-3">
          <summary className="cursor-pointer text-xs text-red-100/70">
            Xem lỗi kỹ thuật
          </summary>
          <pre className="mt-3 max-h-32 overflow-auto whitespace-pre-wrap text-xs text-red-100/70">
            {error.raw}
          </pre>
        </details>
      )}

      {onRetry && (
        <div className="mt-4 flex justify-end">
          <Button
            onClick={onRetry}
            size="sm"
            className="rounded-xl bg-red-300 text-red-950 hover:bg-red-200"
          >
            <RefreshCcw className="mr-2 h-4 w-4" />
            Thử lại
          </Button>
        </div>
      )}
    </div>
  );
}

function getErrorIcon(code: AppError["code"]) {
  switch (code) {
    case "BACKEND_OFFLINE":
      return ServerCrash;
    case "QDRANT_NOT_RUNNING":
      return Database;
    case "GEMINI_QUOTA_EXCEEDED":
    case "GEMINI_API_ERROR":
      return Sparkles;
    case "MAP_MISSING_COORDINATES":
      return MapPinned;
    case "MEMORY_SAVE_FAILED":
      return MemoryStick;
    default:
      return AlertTriangle;
  }
}