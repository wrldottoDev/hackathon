import { Routes, Route } from "react-router-dom";
import BottomNav from "./components/BottomNav";
import Feed from "./pages/Feed";
import Profile from "./pages/Profile";
import Inbox from "./pages/Inbox";
import Conversation from "./pages/Conversation";
import Maliciosa1 from "./pages/Maliciosa1";
import Maliciosa2 from "./pages/Maliciosa2";
import AnalyticsDashboard from "./pages/AnalyticsDashboard";

export default function App() {
  return (
    <div className="min-h-screen bg-finsta-bg text-finsta-text font-sans">
      <Routes>
        <Route path="/" element={<Feed />} />
        <Route path="/profile/:userId" element={<Profile />} />
        <Route path="/inbox" element={<Inbox />} />
        <Route path="/conversation/:otherId" element={<Conversation />} />
        <Route path="/maliciosa1" element={<Maliciosa1 />} />
        <Route path="/maliciosa2" element={<Maliciosa2 />} />
        <Route path="/analytics" element={<AnalyticsDashboard />} />
      </Routes>
      <BottomNav />
    </div>
  );
}
