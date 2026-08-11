import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Layout({ children }) {
  const { employee, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  const navLinkClass = (path) =>
    `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
      location.pathname === path
        ? "bg-navy-800 text-white"
        : "text-navy-100 hover:bg-navy-800/60 hover:text-white"
    }`;

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <header className="bg-navy-900 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-8">
              <Link to="/dashboard" className="flex items-center gap-2 text-white font-semibold text-lg">
                <img src="/inktoweb-logo.png" alt="InkToWeb" className="h-9 w-9 rounded-md object-cover" />
                InkToWeb
              </Link>
              <nav className="hidden sm:flex items-center gap-1">
                <Link to="/dashboard" className={navLinkClass("/dashboard")}>Dashboard</Link>
                <Link to="/upload" className={navLinkClass("/upload")}>Upload New Form</Link>
              </nav>
            </div>
            <div className="flex items-center gap-4">
              <span className="hidden sm:block text-sm text-navy-200">
                {employee?.full_name}
              </span>
              <button
                onClick={handleLogout}
                className="text-sm font-medium text-navy-200 hover:text-white transition-colors"
              >
                Log out
              </button>
            </div>
          </div>
        </div>
      </header>
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
