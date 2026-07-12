import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import DashboardLayout from "../layouts/DashboardLayout";
import ProtectedRoute from "../components/auth/ProtectedRoute";

import Dashboard from "../pages/Dashboard";
import Emails from "../pages/Emails";
import Meetings from "../pages/Meetings";
import Tasks from "../pages/Tasks";
import Analytics from "../pages/Analytics";
import AIAssistant from "../pages/AIAssistant";
import Login from "../pages/Login";
import Calendar from "../pages/Calendar";
import OAuthCallback from "../pages/OAuthCallback";

const AppRoutes = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" />} />

        <Route path="/login" element={<Login />} />
        <Route path="/oauth/callback" element={<OAuthCallback />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/emails" element={<Emails />} />
            <Route path="/meetings" element={<Meetings />} />
            <Route path="/tasks" element={<Tasks />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/assistant" element={<AIAssistant />} />
            <Route path="/calendar" element={<Calendar />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default AppRoutes;
