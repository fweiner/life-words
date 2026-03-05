"use client";

import { PhoneMockup } from "./PhoneMockup";
import { useInView } from "./useInView";

const stats = [
  { label: "Accuracy", value: "85%", fill: 85, color: "bg-blue-500" },
  { label: "Sessions", value: "24", fill: 72, color: "bg-green-500" },
  { label: "Streak", value: "5 days", fill: 60, color: "bg-purple-500" },
  { label: "Items Learned", value: "18", fill: 90, color: "bg-amber-500" },
];

export function MockProgress() {
  const { ref, isVisible } = useInView();

  return (
    <div ref={ref}>
      <PhoneMockup>
        <div className="space-y-3">
          <p className="font-bold text-gray-900 text-lg">Your Progress</p>

          {stats.map((s) => (
            <div
              key={s.label}
              className="bg-gray-50 rounded-xl p-3 border-l-4"
              style={{ borderColor: `var(--tw-${s.color})` }}
            >
              <div className="flex justify-between items-center mb-2">
                <p className="text-sm font-medium text-gray-700">{s.label}</p>
                <p className="text-sm font-bold text-gray-900">{s.value}</p>
              </div>
              <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${s.color} rounded-full ${isVisible ? "promo-fill-bar" : ""}`}
                  style={
                    { "--fill-width": `${s.fill}%` } as React.CSSProperties
                  }
                />
              </div>
            </div>
          ))}
        </div>
      </PhoneMockup>
    </div>
  );
}
