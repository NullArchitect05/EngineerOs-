import { Link, useLocation } from "react-router-dom";
import { Cpu, GitCompare, DollarSign, Github } from "lucide-react";

const navLinks = [
  { to: "/", label: "Analyze", icon: Cpu },
  { to: "/compare", label: "Compare", icon: GitCompare },
  { to: "/pricing", label: "Pricing", icon: DollarSign },
];

export default function Navbar() {
  const location = useLocation();

  return (
    <nav className="border-b border-slate-800/60 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500 to-emerald-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-slate-100 tracking-tight">
            Engineer<span className="text-cyan-400">OS</span>
          </span>
        </Link>

        <div className="flex items-center gap-2">
          {navLinks.map(({ to, label, icon: Icon }) => {
            const isActive = location.pathname === to;
            return (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-slate-800 text-slate-100 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </Link>
            );
          })}

          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 transition-all duration-200"
          >
            <Github className="w-4 h-4" />
            GitHub
          </a>
        </div>
      </div>
    </nav>
  );
}
