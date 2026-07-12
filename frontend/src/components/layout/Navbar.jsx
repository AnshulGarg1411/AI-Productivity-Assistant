import { LogOut, Star } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

const PAGE_META = {
  "/dashboard": { title: "Dashboard", icon: "🏠" },
  "/emails": { title: "Emails", icon: "📧" },
  "/meetings": { title: "Meetings", icon: "🗓️" },
  "/tasks": { title: "Tasks", icon: "✅" },
  "/analytics": { title: "Analytics", icon: "📊" },
  "/assistant": { title: "AI Assistant", icon: "🤖" },
  "/calendar": { title: "Calendar", icon: "📅" },
};

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const meta = PAGE_META[location.pathname] || { title: "Dashboard", icon: "🏠" };

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  const initials = user?.name
    ? user.name.split(" ").map((p) => p[0]).slice(0, 2).join("").toUpperCase()
    : "?";

  return (
    <div className="h-12 bg-canvas border-b border-border flex justify-between items-center px-5">
      <div className="flex items-center gap-2 text-sm text-ink-muted">
        <span>{meta.icon}</span>
        <span className="font-medium text-ink">{meta.title}</span>
      </div>

      <div className="flex items-center gap-1">
        <button
          title="Add to favorites"
          className="p-1.5 rounded-md text-ink-faint hover:bg-surface-hover hover:text-ink transition-colors"
        >
          <Star size={16} />
        </button>

        <div className="w-px h-5 bg-border mx-1.5" />

        {user && (
          <div className="flex items-center gap-2 pl-1 pr-2">
            <div className="w-6 h-6 rounded-full bg-accent text-white flex items-center justify-center text-[11px] font-semibold">
              {initials}
            </div>
            <span className="text-sm text-ink hidden sm:inline">{user.name}</span>
          </div>
        )}

        <button
          onClick={handleLogout}
          title="Log out"
          className="p-1.5 rounded-md text-ink-faint hover:bg-surface-hover hover:text-ink transition-colors"
        >
          <LogOut size={16} />
        </button>
      </div>
    </div>
  );
};

export default Navbar;
