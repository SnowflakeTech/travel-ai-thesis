import type { RetrievedContext } from "@/types/travel";
import { Database } from "lucide-react";

type RetrievedPlacesPanelProps = {
  places: RetrievedContext[];
};

export function RetrievedPlacesPanel({ places }: RetrievedPlacesPanelProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/10 p-5 text-white shadow-2xl shadow-black/20 backdrop-blur-xl">
      <div className="mb-4 flex items-center gap-2">
        <Database className="h-5 w-5 text-cyan-300" />
        <div>
          <h2 className="text-xl font-semibold">Retrieved Contexts</h2>
          <p className="text-sm text-slate-400">
            Dữ liệu được lấy từ Qdrant/RAG
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {places.slice(0, 5).map((place, index) => (
          <div
            key={`${place.title}-${index}`}
            className="rounded-xl border border-white/10 bg-slate-950/60 p-3"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-medium text-white">
                  {place.title || "Không có tên"}
                </p>
                <p className="text-xs text-slate-400">
                  {place.city} · {place.category}
                </p>
              </div>

              {typeof place.score === "number" && (
                <span className="rounded-full bg-cyan-400/10 px-2 py-1 text-xs text-cyan-200">
                  {place.score}
                </span>
              )}
            </div>

            {place.search_mode && (
              <p className="mt-2 text-xs text-slate-500">
                mode: {place.search_mode}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}