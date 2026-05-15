import { Badge } from "@/components/ui/badge";
import type { RetrievedContext } from "@/types/travel";
import { Clock, MapPin, WalletCards } from "lucide-react";

type PlaceCardProps = {
  place: RetrievedContext;
};

export function PlaceCard({ place }: PlaceCardProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
      <div className="mb-3 flex items-start justify-between gap-3">
        <div>
          <h3 className="font-semibold text-white">
            {place.title || "Địa điểm"}
          </h3>
          <p className="text-sm text-slate-400">{place.city}</p>
        </div>

        {place.category && (
          <Badge className="bg-cyan-400/10 text-cyan-200 hover:bg-cyan-400/10">
            {place.category}
          </Badge>
        )}
      </div>

      <div className="space-y-2">
        {place.address && (
          <div className="flex gap-2 text-sm text-slate-400">
            <MapPin className="mt-0.5 h-4 w-4 text-cyan-300" />
            <span>{place.address}</span>
          </div>
        )}

        {place.best_time && (
          <div className="flex gap-2 text-sm text-slate-400">
            <Clock className="mt-0.5 h-4 w-4 text-violet-300" />
            <span>{place.best_time}</span>
          </div>
        )}

        {place.budget && (
          <div className="flex gap-2 text-sm text-slate-400">
            <WalletCards className="mt-0.5 h-4 w-4 text-emerald-300" />
            <span>{place.budget}</span>
          </div>
        )}
      </div>

      {place.tips && (
        <p className="mt-3 text-sm leading-6 text-slate-300">{place.tips}</p>
      )}
    </div>
  );
}