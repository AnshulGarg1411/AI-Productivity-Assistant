import Sidebar from "../components/layout/Sidebar";
import Navbar from "../components/layout/Navbar";
import { Outlet } from "react-router-dom";

const DashboardLayout = () => {
  return (
    <div className="flex min-h-screen bg-canvas">

      <Sidebar />

      <div className="flex-1 flex flex-col ml-64">

        <Navbar />

        {/* No max-width or padding here on purpose: pages like Emails need
            a full-bleed 3-pane layout. Document-style pages (Dashboard,
            Tasks, etc.) apply their own "max-w-5xl mx-auto px-10 py-8"
            wrapper internally instead. */}
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>

      </div>

    </div>
  );
};

export default DashboardLayout;