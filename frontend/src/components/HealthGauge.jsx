import { motion } from "framer-motion";

export default function HealthGauge({ score = 0, grade = "N/A", size = "lg" }) {
  const radius = size === "lg" ? 72 : 52;
  const strokeWidth = size === "lg" ? 10 : 8;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const color = score >= 80 ? "#10b981" : score >= 65 ? "#06b6d4" : score >= 50 ? "#f59e0b" : "#ef4444";

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: (radius + strokeWidth) * 2, height: (radius + strokeWidth) * 2 }}>
        <svg width="100%" height="100%" viewBox={`0 0 ${(radius + strokeWidth) * 2} ${(radius + strokeWidth) * 2}`}>
          <circle cx={radius + strokeWidth} cy={radius + strokeWidth} r={radius}
            fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={strokeWidth} />
          <motion.circle cx={radius + strokeWidth} cy={radius + strokeWidth} r={radius}
            fill="none" stroke={color} strokeWidth={strokeWidth} strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            transform={`rotate(-90 ${radius + strokeWidth} ${radius + strokeWidth})`} />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span className={`font-bold ${size === "lg" ? "text-4xl" : "text-2xl"}`}
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            style={{ color }}>
            {score}
          </motion.span>
          <span className={`text-slate-500 ${size === "lg" ? "text-sm" : "text-xs"}`}>/ 100</span>
        </div>
      </div>
      <div className="mt-2 flex items-center gap-2">
        <span className={`font-bold ${size === "lg" ? "text-lg" : "text-base"}`} style={{ color }}>{grade}</span>
      </div>
    </div>
  );
}
