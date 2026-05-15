"use client";

import dynamic from "next/dynamic";
import type { RetrievedContext } from "@/types/travel";
import { MapPinned } from "lucide-react";

const TravelMapInner = dynamic(() => import("./TravelMapInner"), {
  ssr: false,
});

type TravelMapProps = {
  places: RetrievedContext[];
};

export function TravelMap({ places }: TravelMapProps) {
  const hasMarker = places.some(
    (place) =>
      typeof place.latitude === "number" && typeof place.longitude === "number"
  );

  return (
    <div className="rounded-2xl border border-white/10 bg-white/10 p-5 text-white shadow-2xl shadow-black/20 backdrop-blur-xl">
      <div className="mb-4 flex items-center gap-2">
        <MapPinned className="h-5 w-5 text-cyan-300" />
        <div>
          <h2 className="text-xl font-semibold">Travel Map</h2>
          <p className="text-sm text-slate-400">
            {hasMarker
              ? "Hiển thị các địa điểm có tọa độ"
              : "Chưa có tọa độ để hiển thị marker"}
          </p>
        </div>
      </div>

      <TravelMapInner places={places} />
    </div>
  );
}