import { useState, useEffect } from "react";
import { useLocation, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, PenLine } from "lucide-react";
import client from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function VerifyOtp() {
  const location = useLocation();
  const navigate = useNavigate();
  const { verifyOtp } = useAuth();

  const email = location.state?.email;
  const [devOtp, setDevOtp] = useState(location.state?.devOtp || null);
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    if (!email) navigate("/signup", { replace: true });
  }, [email, navigate]);

  useEffect(() => {
    if (cooldown <= 0) return;
    const t = setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [cooldown]);

  async function handleVerify(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await verifyOtp(email, otp);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Verification failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleResend() {
    setError("");
    setInfo("");
    setResending(true);
    try {
      const res = await client.post("/api/auth/resend-otp", { email });
      setDevOtp(res.data.dev_otp || null);
      setInfo("A new code has been sent.");
      setCooldown(30);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not resend the code.");
    } finally {
      setResending(false);
    }
  }

  if (!email) return null;

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
        <div className="text-center mb-6">
          <Link to="/" className="inline-flex items-center gap-2.5">
            <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-navy-900 text-white shadow-sm">
              <PenLine className="h-5 w-5" strokeWidth={2} />
            </span>
            <span className="font-semibold text-navy-900 text-2xl tracking-tight">InkToWeb</span>
          </Link>
          <p className="mt-3 text-sm text-slate-500">Verify your email</p>
        </div>

        <form onSubmit={handleVerify} className="bg-white rounded-xl shadow-xl p-8 space-y-5">
          <p className="text-sm text-slate-600">
            We sent a 6-digit verification code to <span className="font-medium text-slate-800">{email}</span>.
          </p>

          {devOtp && (
            <div className="text-sm text-amber-800 bg-amber-50 border border-amber-200 rounded-md px-3 py-2">
              <p className="font-medium">Dev mode — no email service is configured yet</p>
              <p className="mt-1">
                Your code: <span className="font-mono text-base tracking-widest">{devOtp}</span>
              </p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Verification Code</label>
            <input
              type="text"
              inputMode="numeric"
              autoFocus
              maxLength={6}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-center text-lg tracking-[0.5em] font-mono shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
              required
            />
          </div>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2">
              {error}
            </div>
          )}
          {info && !error && (
            <div className="text-sm text-teal-700 bg-teal-50 border border-teal-200 rounded-md px-3 py-2">
              {info}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || otp.length !== 6}
            className="w-full rounded-md bg-navy-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-navy-800 transition-colors disabled:opacity-60"
          >
            {loading ? "Verifying..." : "Verify & Continue"}
          </button>

          <div className="text-sm text-center text-slate-500">
            Didn't get a code?{" "}
            <button
              type="button"
              onClick={handleResend}
              disabled={resending || cooldown > 0}
              className="font-medium text-teal-700 hover:text-teal-800 disabled:text-slate-400 disabled:cursor-not-allowed"
            >
              {cooldown > 0 ? `Resend in ${cooldown}s` : resending ? "Sending..." : "Resend code"}
            </button>
          </div>

          <p className="text-sm text-center text-slate-400">
            <Link to="/signup" className="hover:text-slate-600">← Back to sign up</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
