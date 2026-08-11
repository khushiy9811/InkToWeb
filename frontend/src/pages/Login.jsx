import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { ArrowLeft, PenLine } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { employee, login } = useAuth();
  const navigate = useNavigate();

  if (employee) return <Navigate to="/dashboard" replace />;

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(username, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden bg-gradient-to-b from-white via-slate-50 to-slate-100 px-4">
      <div className="pointer-events-none absolute -top-32 -left-32 h-80 w-80 rounded-full bg-teal-200/40 blur-3xl" />
      <div className="pointer-events-none absolute top-1/4 -right-32 h-80 w-80 rounded-full bg-blue-200/40 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 left-1/3 h-64 w-64 rounded-full bg-navy-200/30 blur-3xl" />

      <Link
        to="/"
        className="relative z-10 inline-flex items-center gap-1.5 mb-6 text-sm font-medium text-slate-500 hover:text-navy-900 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" strokeWidth={1.8} />
        Back to Home
      </Link>

      <div className="relative z-10 w-full max-w-sm">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2.5">
            <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-navy-900 text-white shadow-sm">
              <PenLine className="h-5 w-5" strokeWidth={2} />
            </span>
            <span className="font-semibold text-navy-900 text-2xl tracking-tight">InkToWeb</span>
          </Link>
          <p className="mt-3 text-sm text-slate-500">Bank Form Digitization System</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-xl p-8 space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Username</label>
            <input
              type="text"
              autoFocus
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
            <input
              type="password"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-navy-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-navy-800 transition-colors disabled:opacity-60"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>

          <p className="text-sm text-center text-slate-500">
            Don't have an account?{" "}
            <Link to="/signup" className="font-medium text-teal-700 hover:text-teal-800">
              Create one
            </Link>
          </p>

          <p className="text-xs text-center text-slate-400">
            Demo credentials: admin / admin123
          </p>
        </form>
      </div>
    </div>
  );
}
