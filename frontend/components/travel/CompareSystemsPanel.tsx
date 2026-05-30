"use client";

import { useMemo, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  BrainCircuit,
  FileSearch,
  Loader2,
  RefreshCw,
  Sparkles,
} from "lucide-react";

import { comparePrompts } from "@/lib/api";
import type { ComparePromptsResponse } from "@/types/travel";
import { MarkdownMessage } from "@/components/chat/MarkdownMessage";
import { Button } from "@/components/ui/button";

type CompareSystemsPanelProps = {
  lastRequest: string;
};

export function CompareSystemsPanel({ lastRequest }: CompareSystemsPanelProps) {
  const [result, setResult] = useState<ComparePromptsResponse | null>(null);
  const [comparedRequest, setComparedRequest] = useState("");
  const [isComparing, setIsComparing] = useState(false);
  const [error, setError] = useState("");

  const hasPrompt = Boolean(lastRequest.trim());
  const hasCompared = Boolean(result && comparedRequest.trim());
  const promptChanged =
    hasCompared && lastRequest.trim() !== comparedRequest.trim();

  const buttonLabel = useMemo(() => {
    if (isComparing) return "Đang so sánh...";
    if (!hasCompared) return "Chạy so sánh";
    if (promptChanged) return "So sánh lại với prompt mới";
    return "Chạy lại so sánh";
  }, [hasCompared, isComparing, promptChanged]);

  async function handleCompare() {
    const currentRequest = lastRequest.trim();

    if (!currentRequest || isComparing) return;

    setIsComparing(true);
    setError("");

    try {
      const data = await comparePrompts(currentRequest);
      setResult(data);
      setComparedRequest(currentRequest);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Không thể so sánh 3 hệ thống."
      );
    } finally {
      setIsComparing(false);
    }
  }

  return (
    <section className="rounded-2xl border border-white/10 bg-white/10 p-5 text-white shadow-2xl shadow-black/20 backdrop-blur-xl">
      <div className="mb-5 flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-violet-300" />
            <h2 className="text-xl font-semibold">So sánh 3 hệ thống</h2>
          </div>

          <p className="max-w-3xl text-sm leading-6 text-slate-400">
            So sánh phản hồi giữa LLM thuần, Basic RAG và Agentic RAG trên cùng
            một yêu cầu. Kết quả so sánh sẽ được giữ lại khi bạn chuyển tab.
          </p>
        </div>

        <Button
          onClick={handleCompare}
          disabled={!hasPrompt || isComparing}
          className="rounded-xl bg-violet-400 px-5 font-semibold text-slate-950 hover:bg-violet-300 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isComparing ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : promptChanged ? (
            <RefreshCw className="mr-2 h-4 w-4" />
          ) : (
            <Sparkles className="mr-2 h-4 w-4" />
          )}
          {buttonLabel}
        </Button>
      </div>

      {!hasPrompt && (
        <div className="rounded-2xl border border-amber-400/20 bg-amber-400/10 p-4 text-sm leading-6 text-amber-100">
          Bạn cần gửi một yêu cầu ở tab AI Travel Agent trước, sau đó mới có thể
          chạy so sánh.
        </div>
      )}

      {hasPrompt && (
        <div className="mb-5 rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-4">
          <p className="mb-1 text-sm font-medium text-cyan-100">
            Prompt hiện tại ở AI Travel Agent
          </p>
          <p className="text-sm leading-6 text-slate-300">{lastRequest}</p>
        </div>
      )}

      {hasCompared && (
        <div className="mb-5 rounded-2xl border border-white/10 bg-slate-950/50 p-4">
          <p className="mb-1 text-sm font-medium text-slate-200">
            Prompt đã dùng cho kết quả so sánh hiện tại
          </p>
          <p className="text-sm leading-6 text-slate-400">{comparedRequest}</p>
        </div>
      )}

      {promptChanged && (
        <div className="mb-5 rounded-2xl border border-amber-400/20 bg-amber-400/10 p-4 text-sm leading-6 text-amber-100">
          Prompt ở tab AI Travel Agent đã thay đổi. Bấm{" "}
          <span className="font-semibold">“So sánh lại với prompt mới”</span> để
          cập nhật kết quả.
        </div>
      )}

      {error && (
        <div className="mb-5 rounded-2xl border border-red-400/20 bg-red-400/10 p-4 text-sm leading-6 text-red-100">
          {error}
        </div>
      )}

      {result && (
        <div className="grid gap-5">
          <div className="grid gap-5 xl:grid-cols-3">
            <CompareResultCard
              icon={<BrainCircuit className="h-5 w-5 text-cyan-300" />}
              title="LLM thuần"
              subtitle="Gemini trả lời trực tiếp, không dùng dữ liệu Qdrant"
              content={result.llm_only}
            />

            <CompareResultCard
              icon={<FileSearch className="h-5 w-5 text-emerald-300" />}
              title="Basic RAG"
              subtitle="Gemini trả lời dựa trên retrieved contexts từ Qdrant"
              content={result.rag_only}
            />

            <CompareResultCard
              icon={<Sparkles className="h-5 w-5 text-violet-300" />}
              title="Agentic RAG"
              subtitle="Planner, Retriever, Route, Budget, Guard, Critic và Memory"
              content={result.rag_agentic}
            />
          </div>

          <div className="overflow-hidden rounded-2xl border border-amber-400/20 bg-amber-400/10 shadow-xl shadow-black/20">
            <div className="border-b border-amber-400/20 bg-amber-400/10 px-5 py-4">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-amber-200" />
                <h3 className="text-lg font-semibold text-amber-100">
                  Điểm khác biệt / mâu thuẫn
                </h3>
              </div>
            </div>

            <div className="px-5 py-5">
              <div className="prose prose-invert max-w-none prose-headings:mb-3 prose-headings:mt-4 prose-p:leading-7 prose-li:leading-7 prose-strong:text-white">
                <MarkdownMessage content={result.differences} />
              </div>
            </div>
          </div>

          {result.rag_contexts && result.rag_contexts.length > 0 && (
            <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
              <div className="mb-4 flex items-center gap-2">
                <FileSearch className="h-5 w-5 text-cyan-300" />
                <h3 className="text-lg font-semibold text-white">
                  Retrieved contexts dùng trong Basic RAG
                </h3>
              </div>

              <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                {result.rag_contexts.slice(0, 6).map((item, index) => (
                  <div
                    key={`${item.title || "context"}-${index}`}
                    className="rounded-2xl border border-white/10 bg-white/[0.04] p-4"
                  >
                    <p className="line-clamp-2 font-medium text-white">
                      {item.title || `Context ${index + 1}`}
                    </p>

                    <div className="mt-3 flex flex-wrap gap-2">
                      <ContextBadge label="City" value={item.city || "N/A"} />
                      <ContextBadge
                        label="Category"
                        value={item.category || "N/A"}
                      />
                      <ContextBadge
                        label="Score"
                        value={
                          typeof item.score === "number"
                            ? item.score.toFixed(2)
                            : "N/A"
                        }
                      />
                    </div>

                    <p className="mt-3 line-clamp-2 text-xs leading-5 text-slate-500">
                      {item.source_file || item.source_url || "Nguồn nội bộ"}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}

function CompareResultCard({
  icon,
  title,
  subtitle,
  content,
}: {
  icon: React.ReactNode;
  title: string;
  subtitle: string;
  content: string;
}) {
  return (
    <div className="overflow-hidden rounded-2xl border border-white/10 bg-slate-950/70 shadow-xl shadow-black/20">
      <div className="border-b border-white/10 bg-white/[0.04] px-5 py-4">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/5">
            {icon}
          </div>

          <div>
            <h3 className="text-lg font-semibold text-white">{title}</h3>
            <p className="mt-1 text-sm leading-6 text-slate-400">
              {subtitle}
            </p>
          </div>
        </div>
      </div>

      <div className="max-h-[520px] overflow-y-auto px-5 py-5">
        <div className="prose prose-invert max-w-none prose-headings:mb-3 prose-headings:mt-4 prose-p:leading-7 prose-li:leading-7 prose-strong:text-white">
          <MarkdownMessage content={content || "Không có phản hồi."} />
        </div>
      </div>
    </div>
  );
}

function ContextBadge({ label, value }: { label: string; value: string }) {
  return (
    <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-2.5 py-1 text-[11px] text-cyan-100">
      {label}: {value}
    </span>
  );
}