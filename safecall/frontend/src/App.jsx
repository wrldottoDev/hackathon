import { Routes, Route } from "react-router-dom";
import BottomNav from "./components/BottomNav";
import Lookup from "./pages/Lookup";
import Report from "./pages/Report";
import Dashboard from "./pages/Dashboard";
import Users from "./pages/Users";

export default function App() {
  return (
    <div className="min-h-screen bg-sc-bg text-sc-text font-sans pb-20">
      <Routes>
        <Route path="/" element={<Lookup />} />
        <Route path="/report" element={<Report />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/users" element={<Users />} />
      </Routes>
      <BottomNav />
    </div>
  );
}
