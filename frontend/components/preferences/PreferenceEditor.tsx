"use client";

import { useState } from "react";
import { savePreferences } from "@/lib/api";
import { classifyAppError } from "@/lib/error-handler";
import type { AppError } from "@/types/error";
import type { UserPreferences } from "@/types/travel";
import { ErrorAlert } from "@/components/travel/ErrorAlert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SlidersHorizontal } from "lucide-react";

export function PreferenceEditor() {
  const [preferences, setPreferences] = useState<UserPreferences>({
    travelStyle: "",
    budgetLevel: "",
    walkingLevel: "",
    favoritePlaces: "",
    avoidPlaces: "",
  });

  const [status, setStatus] = useState("");
  const [error, setError] = useState<AppError | null>(null);

  function updateField(key: keyof UserPreferences, value: string) {
    setPreferences((prev) => ({
      ...prev,
      [key]: value,
    }));
  }

  async function handleSave() {
    setStatus("Đang lưu...");
    setError(null);

    try {
      await savePreferences(preferences);
      setStatus("Đã lưu sở thích vào memory.");
    } catch (err) {
      const classifiedError = classifyAppError(err);

      setError({
        ...classifiedError,
        code: "MEMORY_SAVE_FAILED",
        title: "Không lưu được sở thích",
        message:
          "Hệ thống chưa lưu được sở thích vào memory. Có thể database hoặc memory API đang gặp lỗi.",
      });

      setStatus("");
    }
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-slate-900/80 p-5 text-white shadow-2xl shadow-black/20 backdrop-blur-xl">
      <div className="mb-5 flex items-center gap-2">
        <SlidersHorizontal className="h-5 w-5 text-violet-300" />
        <div>
          <h2 className="text-xl font-semibold">Personal Preferences</h2>
          <p className="text-sm text-slate-400">
            Lưu sở thích vào memory của người dùng
          </p>
        </div>
      </div>

      <div className="space-y-3">
        <PreferenceInput
          label="Phong cách du lịch"
          placeholder="Ví dụ: chill, nghỉ dưỡng, khám phá nhẹ nhàng"
          value={preferences.travelStyle}
          onChange={(value) => updateField("travelStyle", value)}
        />

        <PreferenceInput
          label="Mức ngân sách"
          placeholder="Ví dụ: tiết kiệm, trung bình, cao cấp"
          value={preferences.budgetLevel}
          onChange={(value) => updateField("budgetLevel", value)}
        />

        <PreferenceInput
          label="Mức độ đi bộ"
          placeholder="Ví dụ: ít đi bộ, đi bộ vừa phải"
          value={preferences.walkingLevel}
          onChange={(value) => updateField("walkingLevel", value)}
        />

        <PreferenceInput
          label="Địa điểm yêu thích"
          placeholder="Ví dụ: cafe chill, biển, phố cổ"
          value={preferences.favoritePlaces}
          onChange={(value) => updateField("favoritePlaces", value)}
        />

        <PreferenceInput
          label="Muốn tránh"
          placeholder="Ví dụ: nơi quá đông, leo núi, đi bộ nhiều"
          value={preferences.avoidPlaces}
          onChange={(value) => updateField("avoidPlaces", value)}
        />

        <Button
          onClick={handleSave}
          className="w-full rounded-xl bg-violet-400 text-slate-950 hover:bg-violet-300"
        >
          Lưu sở thích
        </Button>

        {status && (
          <p className="rounded-xl border border-emerald-400/20 bg-emerald-400/10 px-3 py-2 text-sm text-emerald-200">
            {status}
          </p>
        )}

        {error && (
          <ErrorAlert
            error={error}
            onClose={() => setError(null)}
            onRetry={handleSave}
          />
        )}
      </div>
    </div>
  );
}

function PreferenceInput({
  label,
  placeholder,
  value,
  onChange,
}: {
  label: string;
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="space-y-2">
      <label className="text-sm text-slate-300">{label}</label>
      <Input
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
        className="border-white/10 bg-slate-950/70 text-white placeholder:text-slate-500"
      />
    </div>
  );
}