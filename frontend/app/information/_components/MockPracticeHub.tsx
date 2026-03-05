import { PhoneMockup } from "./PhoneMockup";

const practiceTypes = [
  { label: "Name Practice", color: "bg-blue-500", icon: "🗣️" },
  { label: "Question Practice", color: "bg-purple-500", icon: "❓" },
  { label: "Information Practice", color: "bg-green-500", icon: "ℹ️" },
];

const gridItems = [
  { label: "Quick Add", icon: "📷" },
  { label: "Instructions", icon: "❓" },
  { label: "Progress", icon: "📊" },
  { label: "Messages", icon: "💬" },
  { label: "My People", icon: "👥" },
  { label: "My Info", icon: "ℹ️" },
  { label: "My Stuff", icon: "📦" },
  { label: "Settings", icon: "⚙️" },
];

export function MockPracticeHub() {
  return (
    <PhoneMockup>
      <div className="space-y-4">
        <p className="font-bold text-gray-900 text-lg">Practice</p>

        {/* Practice type buttons */}
        <div className="space-y-2 promo-stagger">
          {practiceTypes.map((t) => (
            <div
              key={t.label}
              className={`${t.color} text-white rounded-xl p-3 flex items-center gap-3`}
            >
              <span className="text-xl">{t.icon}</span>
              <span className="font-semibold text-sm">{t.label}</span>
            </div>
          ))}
        </div>

        {/* Dashboard icon grid */}
        <div className="grid grid-cols-4 gap-2 promo-stagger">
          {gridItems.map((item) => (
            <div
              key={item.label}
              className="bg-green-50 rounded-lg p-2 flex flex-col items-center justify-center gap-1"
            >
              <span className="text-lg">{item.icon}</span>
              <span className="text-[10px] font-medium text-gray-600 text-center leading-tight">
                {item.label}
              </span>
            </div>
          ))}
        </div>
      </div>
    </PhoneMockup>
  );
}
