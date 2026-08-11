import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, PenLine } from "lucide-react";
import client from "../api/client";

export default function Signup() {
  const [fullName, setFullName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await client.post("/api/auth/signup", {
        full_name: fullName,
        username,
        email,
        password,
      });
      navigate("/verify-otp", {
        state: { email, devOtp: res.data.dev_otp },
      });
    } catch (err) {
      setError(err.response?.data?.detail || "Could not create account. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden bg-gradient-to-b from-white via-slate-50 to-slate-100 px-4 py-10">
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
        <div className="text-center mb-6">
          <Link to="/" className="inline-flex items-center gap-2.5">
            <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-navy-900 text-white shadow-sm">
              <PenLine className="h-5 w-5" strokeWidth={2} />
            </span>
            <span className="font-semibold text-navy-900 text-2xl tracking-tight">InkToWeb</span>
          </Link>
          <p className="mt-3 text-sm text-slate-500">Create your employee account</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-xl p-8 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
            <input
              type="text"
              autoFocus
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Username</label>
            <input
              type="text"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              minLength={3}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
            <input
              type="email"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
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
              minLength={6}
              required
            />
            <p className="mt-1 text-xs text-slate-400">At least 6 characters.</p>
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
            {loading ? "Creating account..." : "Create Account"}
          </button>

          <p className="text-sm text-center text-slate-500">
            Already have an account?{" "}
            <Link to="/login" className="font-medium text-teal-700 hover:text-teal-800">
              Sign in
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
