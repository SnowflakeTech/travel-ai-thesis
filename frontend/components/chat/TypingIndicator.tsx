export function TypingIndicator() {
  return (
    <div className="flex w-fit items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
      <span>Travel Agent đang lập kế hoạch</span>

      <span className="flex gap-1">
        <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-300" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-300 [animation-delay:0.15s]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-300 [animation-delay:0.3s]" />
      </span>
    </div>
  );
}