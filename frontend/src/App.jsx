import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import ComparePage from "./pages/ComparePage";
import PricingPage from "./pages/PricingPage";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-950 font-['Inter',sans-serif]">
        <Navbar />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/compare" element={<ComparePage />} />
          <Route path="/pricing" element={<PricingPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;