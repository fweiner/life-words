import { PhoneMockup } from "./PhoneMockup";

export function MockDashboard() {
  return (
    <PhoneMockup>
      <div className="space-y-4">
        {/* Welcome card */}
        <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4">
          <p className="text-2xl mb-1">👋</p>
          <p className="font-bold text-gray-900 text-lg">Welcome back!</p>
          <p className="text-sm text-gray-600">
            Ready for today&apos;s practice?
          </p>
        </div>

        {/* Quick action pills */}
        <div className="flex gap-2">
          <div className="flex-1 bg-blue-600 text-white text-center text-sm font-semibold py-3 rounded-lg">
            Start Practice
          </div>
          <div className="flex-1 bg-gray-100 text-gray-700 text-center text-sm font-semibold py-3 rounded-lg">
            View Progress
          </div>
        </div>

        {/* Recent activity */}
        <div className="space-y-2">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
            Recent
          </p>
          <div className="bg-gray-50 rounded-lg p-3 flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-sm">
              ✓
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">
                Naming Practice
              </p>
              <p className="text-xs text-gray-500">85% accuracy</p>
            </div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3 flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-sm">
              📊
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">
                Word Finding
              </p>
              <p className="text-xs text-gray-500">12 items completed</p>
            </div>
          </div>
        </div>
      </div>
    </PhoneMockup>
  );
}
