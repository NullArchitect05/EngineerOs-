import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
const COLORS = ["#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6"];
export default function LanguageChart({ extensionCounts = {} }) {
  const data = Object.entries(extensionCounts).map(([ext, count]) => ({ name: ext || "unknown", value: count })).sort((a, b) => b.value - a.value).slice(0, 8);
  if (data.length === 0) return null;
  const total = data.reduce((sum, item) => sum + item.value, 0);
  return (
    <div className="p-6 md:p-8 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl">
      <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-6">Language Distribution</h3>
      <div className="flex items-center gap-6">
        <div className="w-40 h-40 flex-shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data} cx="50%" cy="50%" innerRadius={35} outerRadius={65} dataKey="value" paddingAngle={2}>
                {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip formatter={(value) => [value, "files"]} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="flex-1 space-y-2">
          {data.map((item, i) => (
            <div key={item.name} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                <span className="text-sm text-slate-300">{item.name}</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-20 h-1.5 rounded-full bg-slate-800 overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: (item.value / total * 100) + "%", backgroundColor: COLORS[i % COLORS.length] }} />
                </div>
                <span className="text-xs font-medium text-slate-400 w-10 text-right">{item.value}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
