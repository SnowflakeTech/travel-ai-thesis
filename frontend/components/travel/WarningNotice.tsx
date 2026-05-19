import { AlertTriangle } from "lucide-react";

type WarningNoticeProps = {
  title: string;
  message: string;
  suggestions?: string[];
};

export function WarningNotice({
  title,
  message,
  suggestions = [],
}: WarningNoticeProps) {
  return (
    <div className="rounded-2xl border border-amber-400/20 bg-amber-400/10 p-4 text-amber-100">
      <div className="mb-2 flex items-center gap-2">
        <AlertTriangle className="h-4 w-4" />
        <p className="font-medium">{title}</p>
      </div>

      <p className="text-sm leading-6 text-amber-100/80">{message}</p>

      {suggestions.length > 0 && (
        <ul className="mt-3 ml-5 list-disc space-y-1 text-sm text-amber-100/80">
          {suggestions.map((suggestion, index) => (
            <li key={index}>{suggestion}</li>
          ))}
        </ul>
      )}
    </div>
  );
}