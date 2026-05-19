"use client";

import { useEffect, useRef, useState } from "react";
import {
  Bot,
  Loader2,
  MessageSquareText,
  Send,
  Sparkles,
  UserRound,
} from "lucide-react";

import { sendAgentMessage } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

const suggestedPrompts = [
  "Lập lịch trình Đà Lạt 3 ngày 2 đêm, ngân sách 5 triệu.",
  "Gợi ý chuyến đi Đà Nẵng cho nhóm bạn thích biển và cafe chill.",
  "Tạo lịch trình Hội An 1 ngày, ít đi bộ, chi phí tiết kiệm.",
];

export function AiChatPanel() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesContainerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = messagesContainerRef.current;

    if (!container) return;

    container.scrollTop = container.scrollHeight;
  }, [messages, isLoading]);

  async function handleSend(customInput?: string) {
    const trimmedInput = (customInput ?? input).trim();

    if (!trimmedInput || isLoading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: trimmedInput,
    };

    const assistantMessage: ChatMessage = {
      role: "assistant",
      content: "",
    };

    const assistantIndex = messages.length + 1;

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const data = await sendAgentMessage(trimmedInput);

      setMessages((prev) =>
        prev.map((msg, index) =>
          index === assistantIndex
            ? {
                ...msg,
                content:
                  data.answer ||
                  "Agent đã phản hồi nhưng không có trường answer trong dữ liệu trả về.",
              }
            : msg
        )
      );
    } catch {
      setMessages((prev) =>
        prev.map((msg, index) =>
          index === assistantIndex
            ? {
                ...msg,
                content:
                  "Có lỗi khi gọi Agent API. Bạn hãy kiểm tra backend, endpoint /api/agent/travel hoặc log server nhé.",
              }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  }

  return (
    <section className="relative mt-0">
      <Card className="flex h-[760px] flex-col overflow-hidden rounded-[2rem] border border-white/10 bg-slate-900/70 text-white shadow-2xl shadow-cyan-950/30 backdrop-blur-xl">
        <div className="shrink-0 border-b border-white/5 bg-white/5 px-6 py-5">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border border-cyan-400/30 bg-cyan-400/10 text-cyan-300 shadow-lg shadow-cyan-500/10">
                <Bot className="h-5 w-5" />
              </div>

              <div>
                <h2 className="bg-gradient-to-r from-cyan-200 via-sky-200 to-violet-200 bg-clip-text text-lg font-semibold leading-none text-transparent">
                  Gemini Travel Assistant
                </h2>
                <p className="mt-1 text-xs font-medium text-cyan-100/60">
                  Trợ lý AI lập lịch trình du lịch cá nhân hóa theo ngân sách,
                  sở thích và thời gian.
                </p>
              </div>
            </div>

            <div className="w-fit rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-300">
              AI Ready
            </div>
          </div>
        </div>

        <CardContent className="flex min-h-0 flex-1 flex-col gap-4 p-5">
          <div
            ref={messagesContainerRef}
            className="min-h-0 flex-1 space-y-5 overflow-y-auto rounded-[1.5rem] border border-white/10 bg-slate-950/80 p-5"
          >
            {messages.length === 0 && (
              <div className="space-y-4">
                <div className="rounded-3xl border border-cyan-400/20 bg-gradient-to-br from-cyan-400/10 via-blue-400/5 to-violet-400/10 p-5">
                  <div className="mb-3 flex items-center gap-2 text-cyan-200">
                    <Sparkles className="h-4 w-4" />
                    <p className="text-sm font-semibold">Gợi ý bắt đầu</p>
                  </div>

                  <p className="text-sm leading-6 text-slate-300">
                    Hãy nhập yêu cầu du lịch thật tự nhiên. Ví dụ: địa điểm muốn
                    đi, số ngày, ngân sách, sở thích, người đi cùng và điều bạn
                    không thích.
                  </p>
                </div>

                <div className="grid gap-3 md:grid-cols-3">
                  {suggestedPrompts.map((prompt) => (
                    <button
                      key={prompt}
                      type="button"
                      onClick={() => handleSend(prompt)}
                      className="group min-h-[96px] rounded-3xl border border-white/10 bg-white/[0.04] p-4 text-left text-sm text-slate-300 transition hover:border-cyan-400/30 hover:bg-cyan-400/10 hover:text-cyan-100"
                    >
                      <div className="flex items-start gap-3">
                        <MessageSquareText className="mt-0.5 h-4 w-4 shrink-0 text-cyan-300" />
                        <span className="leading-6">{prompt}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex gap-3 ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {msg.role === "assistant" && (
                  <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-cyan-400/20 bg-cyan-400/10 text-cyan-300">
                    <Bot className="h-4 w-4" />
                  </div>
                )}

                <div
                  className={`max-w-[78%] overflow-hidden rounded-3xl px-5 py-4 text-sm leading-7 shadow-xl ${
                    msg.role === "user"
                      ? "bg-cyan-400 text-slate-950 shadow-cyan-950/40"
                      : "border border-white/10 bg-slate-900/90 text-slate-100 shadow-black/30"
                  }`}
                >
                  {msg.content ? (
                    <p className="whitespace-pre-wrap break-words">
                      {msg.content}
                    </p>
                  ) : (
                    <div className="flex items-center gap-2 text-slate-400">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Đang tạo phản hồi...</span>
                    </div>
                  )}
                </div>

                {msg.role === "user" && (
                  <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-violet-400/20 bg-violet-400/10 text-violet-300">
                    <UserRound className="h-4 w-4" />
                  </div>
                )}
              </div>
            ))}

            {isLoading && messages.length > 0 && (
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />
                Agent đang xử lý yêu cầu...
              </div>
            )}
          </div>

          <div className="shrink-0 rounded-[1.5rem] border border-white/10 bg-slate-950/70 p-4">
            <Textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ví dụ: Tôi muốn đi Đà Lạt 3 ngày 2 đêm, ngân sách 5 triệu, thích cafe chill, không thích lịch trình quá dày..."
              rows={3}
              maxLength={1200}
              className="resize-none rounded-2xl border-white/10 bg-slate-950/90 text-white placeholder:text-slate-500 focus-visible:ring-cyan-400"
            />

            <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-xs text-slate-500">
                Nhấn Enter để gửi, Shift + Enter để xuống dòng. Tối đa 1200 ký
                tự.
              </p>

              <Button
                onClick={() => handleSend()}
                disabled={isLoading || !input.trim()}
                className="h-11 rounded-xl bg-cyan-400 px-5 font-semibold text-slate-950 hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Send className="mr-2 h-4 w-4" />
                )}
                {isLoading ? "Đang gửi..." : "Gửi yêu cầu"}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </section>
  );
}