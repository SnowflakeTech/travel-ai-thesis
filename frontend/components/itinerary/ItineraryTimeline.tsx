import { Button } from "@/components/ui/button";
import type { RetrievedContext } from "@/types/travel";
import { RefreshCcw, Route } from "lucide-react";
import { PlaceCard } from "./PlaceCard";

type ItineraryTimelineProps = {
  places: RetrievedContext[];
  onRegenerateDay: (day: number) => void;
  onOptimizeRoute: () => void;
};

export function ItineraryTimeline({
  places,
  onRegenerateDay,
  onOptimizeRoute,
}: ItineraryTimelineProps) {
  const dayOne = places.slice(0, 3);
  const dayTwo = places.slice(3, 6);
  const dayThree = places.slice(6, 9);

  return (
    <div className="rounded-2xl border border-white/10 bg-white/10 p-5 text-white shadow-2xl shadow-black/20 backdrop-blur-xl">
      <div className="mb-5 flex items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">Itinerary Timeline</h2>
          <p className="text-sm text-slate-400">
            Dựa trên địa điểm RAG truy xuất được
          </p>
        </div>

        <Button
          onClick={onOptimizeRoute}
          variant="outline"
          size="sm"
          className="border-white/15 bg-white/5 text-white hover:bg-white/10 hover:text-white"
        >
          <Route className="mr-2 h-4 w-4" />
          Tối ưu tuyến
        </Button>
      </div>

      <div className="space-y-6">
        <TimelineDay
          day={1}
          places={dayOne}
          onRegenerateDay={onRegenerateDay}
        />

        {dayTwo.length > 0 && (
          <TimelineDay
            day={2}
            places={dayTwo}
            onRegenerateDay={onRegenerateDay}
          />
        )}

        {dayThree.length > 0 && (
          <TimelineDay
            day={3}
            places={dayThree}
            onRegenerateDay={onRegenerateDay}
          />
        )}
      </div>
    </div>
  );
}

function TimelineDay({
  day,
  places,
  onRegenerateDay,
}: {
  day: number;
  places: RetrievedContext[];
  onRegenerateDay: (day: number) => void;
}) {
  if (!places.length) return null;

  return (
    <div className="border-l border-cyan-400/30 pl-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-cyan-100">Ngày {day}</h3>
          <p className="text-xs text-slate-500">{places.length} địa điểm</p>
        </div>

        <Button
          onClick={() => onRegenerateDay(day)}
          variant="ghost"
          size="sm"
          className="text-slate-300 hover:bg-white/10 hover:text-white"
        >
          <RefreshCcw className="mr-2 h-4 w-4" />
          Tạo lại
        </Button>
      </div>

      <div className="space-y-3">
        {places.map((place, index) => (
          <PlaceCard key={`${place.title}-${day}-${index}`} place={place} />
        ))}
      </div>
    </div>
  );
}