import {
  LayoutDashboard,
  Mail,
  CalendarRange,
  CheckSquare,
  BarChart3,
  Bot,
  CalendarDays,
  ChevronsUpDown,
  Search,
} from "lucide-react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

const Sidebar = () => {
  const { user } = useAuth();

  const menus = [
    { title: "Dashboard", icon: LayoutDashboard, path: "/dashboard" },
    { title: "Emails", icon: Mail, path: "/emails" },
    { title: "Meetings", icon: CalendarRange, path: "/meetings" },
    { title: "Tasks", icon: CheckSquare, path: "/tasks" },
    { title: "Analytics", icon: BarChart3, path: "/analytics" },
    { title: "AI Assistant", icon: Bot, path: "/assistant" },
    { title: "Calendar", icon: CalendarDays, path: "/calendar" },
  ];

  const initials = user?.name
    ? user.name.split(" ").map((p) => p[0]).slice(0, 2).join("").toUpperCase()
    : "?";

  return (
    <div className="fixed left-0 top-0 w-64 h-screen bg-surface border-r border-border flex flex-col">
      {/* Workspace switcher */}
      <button className="flex items-center gap-2 px-3 py-3 mx-2 mt-2 rounded-md hover:bg-surface-hover transition-colors text-left">
        <div className="w-6 h-6 rounded bg-accent text-white flex items-center justify-center text-xs font-semibold shrink-0">
          {initials}
        </div>
        <span className="text-sm font-medium text-ink truncate flex-1">
          {user?.name ? `${user.name.split(" ")[0]}'s workspace` : "Workspace"}
        </span>
        <ChevronsUpDown size={14} className="text-ink-faint shrink-0" />
      </button>

      {/* Fake search affordance */}
      <div className="px-2 mt-1">
        <button className="w-full flex items-center gap-2 px-3 py-1.5 rounded-md text-ink-muted hover:bg-surface-hover transition-colors text-sm">
          <Search size={14} />
          Search
        </button>
      </div>

      <div className="px-4 mt-5 mb-1.5">
        <span className="text-xs font-medium text-ink-faint tracking-wide uppercase">
          Workspace
        </span>
      </div>

      <nav className="flex flex-col gap-0.5 px-2">
        {menus.map((menu) => {
          const Icon = menu.icon;
          return (
            <NavLink
              key={menu.path}
              to={menu.path}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-1.5 rounded-md text-sm transition-colors ${
                  isActive
                    ? "bg-surface-hover text-ink font-medium"
                    : "text-ink-muted hover:bg-surface-hover hover:text-ink"
                }`
              }
            >
              <Icon size={16} strokeWidth={2} />
              {menu.title}
            </NavLink>
          );
        })}
      </nav>
    </div>
  );
};

export default Sidebar;
