import type { GroundingGuard, PostProcessingGuard } from "@/types/travel";
import {
  AlertTriangle,
  CheckCircle2,
  ShieldCheck,
  ShieldAlert,
} from "lucide-react";

type HallucinationControlPanelProps = {
  guard?: GroundingGuard;
  postGuard?: PostProcessingGuard;
};

export function HallucinationControlPanel({
  guard,
  postGuard,
}: HallucinationControlPanelProps) {
  if (!guard && !postGuard) return null;

  const isRouteEstimate = Boolean(guard?.is_route_estimate_only);
  const hasContexts = guard?.has_retrieved_contexts !== false;
  const warnings = [...(guard?.warnings || []), ...(postGuard?.warnings || [])];
  const wasModified = Boolean(postGuard?.was_modified);

  return (
    <div className="rounded-2xl border border-white/10 bg-slate-900/80 p-5 text-white shadow-2xl shadow-black/20 backdrop-blur-xl">
      <div className="mb-4 flex items-center gap-2">
        <ShieldCheck className="h-5 w-5 text-emerald-300" />

        <div>
          <h2 className="text-xl font-semibold">Hallucination Control</h2>
          <p className="text-sm text-slate-400">
            Kiểm soát độ tin cậy của câu trả lời
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {guard && (
          <>
            <StatusRow
              ok={hasContexts}
              label={
                hasContexts
                  ? "RAG context available"
                  : "Missing reliable RAG context"
              }
            />

            <StatusRow
              ok={Boolean(guard.policy?.only_use_retrieved_places)}
              label="Only retrieved places allowed"
            />

            <StatusRow
              ok={Boolean(guard.policy?.no_realtime_claims)}
              label="No real-time claims"
            />
          </>
        )}

        {postGuard && (
          <StatusRow
            ok={Boolean(postGuard.guard_applied)}
            label={
              wasModified
                ? "Post-processing guard modified answer"
                : "Post-processing guard applied"
            }
            warning={wasModified}
          />
        )}

        {isRouteEstimate && (
          <div className="rounded-xl border border-amber-400/20 bg-amber-400/10 px-4 py-3 text-sm text-amber-200">
            <div className="mb-1 flex items-center gap-2 font-medium">
              <AlertTriangle className="h-4 w-4" />
              Route estimate only
            </div>

            <p className="text-amber-100/80">
              Khoảng cách chỉ là ước lượng theo dữ liệu hiện có, chưa phải tuyến
              đường thực tế.
            </p>
          </div>
        )}

        {wasModified && (
          <div className="rounded-xl border border-violet-400/20 bg-violet-400/10 px-4 py-3 text-sm text-violet-200">
            <div className="mb-1 flex items-center gap-2 font-medium">
              <ShieldAlert className="h-4 w-4" />
              Guard intervention
            </div>

            <p className="text-violet-100/80">
              Câu trả lời cuối đã được hậu kiểm để giảm nguy cơ hallucination.
            </p>
          </div>
        )}

        {warnings.length > 0 && (
          <div className="rounded-xl border border-white/10 bg-white/5 p-3">
            <p className="mb-2 text-sm font-medium text-slate-200">
              System warnings
            </p>

            <ul className="ml-4 list-disc space-y-1 text-sm text-slate-400">
              {warnings.map((warning, index) => (
                <li key={index}>{warning}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

function StatusRow({
  ok,
  label,
  warning = false,
}: {
  ok: boolean;
  label: string;
  warning?: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-xl border border-white/10 bg-white/5 px-4 py-3">
      <span className="text-sm text-slate-300">{label}</span>

      <span
        className={`inline-flex shrink-0 items-center gap-1 rounded-full px-2 py-1 text-xs ${
          warning
            ? "bg-amber-400/10 text-amber-300"
            : ok
              ? "bg-emerald-400/10 text-emerald-300"
              : "bg-red-400/10 text-red-300"
        }`}
      >
        {warning ? (
          <AlertTriangle className="h-3 w-3" />
        ) : (
          <CheckCircle2 className="h-3 w-3" />
        )}

        {warning ? "Modified" : ok ? "Active" : "Check"}
      </span>
    </div>
  );
}