import type { ChatMessage } from "@/types/travel";
import { Bot, UserRound } from "lucide-react";
import { MarkdownMessage } from "./MarkdownMessage";

type ChatBubbleProps = {
  message: ChatMessage;
};

export function ChatBubble({ message }: ChatBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-cyan-400/10 text-cyan-300">
          <Bot className="h-4 w-4" />
        </div>
      )}

      <div
        className={
          isUser
            ? "max-w-[82%] rounded-2xl bg-cyan-400 px-4 py-3 text-sm leading-6 text-slate-950 shadow-lg shadow-cyan-500/20"
            : "max-w-[88%] rounded-2xl border border-white/10 bg-white/5 px-4 py-3 shadow-lg shadow-black/20"
        }
      >
        {isUser ? (
          <p className="whitespace-pre-wrap font-medium">{message.content}</p>
        ) : (
          <MarkdownMessage content={message.content} />
        )}
      </div>

      {isUser && (
        <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-violet-400/10 text-violet-300">
          <UserRound className="h-4 w-4" />
        </div>
      )}
    </div>
  );
}