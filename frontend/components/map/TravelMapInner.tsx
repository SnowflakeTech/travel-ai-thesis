"use client";

import type { RetrievedContext } from "@/types/travel";
import L from "leaflet";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";

const markerIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

type TravelMapInnerProps = {
  places: RetrievedContext[];
};

export default function TravelMapInner({ places }: TravelMapInnerProps) {
  const validPlaces = places.filter(
    (place) =>
      typeof place.latitude === "number" && typeof place.longitude === "number"
  );

  const center: [number, number] =
    validPlaces.length > 0
      ? [validPlaces[0].latitude as number, validPlaces[0].longitude as number]
      : [16.047079, 108.20623];

  return (
    <MapContainer
      center={center}
      zoom={13}
      className="h-[360px] w-full rounded-2xl"
      scrollWheelZoom={false}
    >
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {validPlaces.map((place, index) => (
        <Marker
          key={`${place.title}-${index}`}
          position={[place.latitude as number, place.longitude as number]}
          icon={markerIcon}
        >
          <Popup>
            <div className="space-y-1">
              <strong>{place.title}</strong>
              <p>{place.address}</p>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}