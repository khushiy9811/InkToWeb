import { useState } from "react";
import { Link, Navigate } from "react-router-dom";
import {
  LogIn,
  UserPlus,
  PenLine,
  UploadCloud,
  ScanText,
  CheckCircle2,
  DatabaseZap,
  Send,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

const steps = [
  {
    icon: UploadCloud,
    title: "Upload",
    description: "Snap a photo or scan of the filled paper form.",
  },
  {
    icon: ScanText,
    title: "AI Extraction",
    description: "OCR and checkbox detection read every field automatically.",
  },
  {
    icon: CheckCircle2,
    title: "Review & Verify",
    description: "Low-confidence fields are flagged for a quick human check.",
  },
  {
    icon: DatabaseZap,
    title: "Confirm & Save",
    description: "Nothing is saved until an employee explicitly confirms it.",
  },
];

export default function Landing() {
  const { employee } = useAuth();
  const [comment, setComment] = useState("");
  const [submitted, setSubmitted] = useState(false);

  if (employee) return <Navigate to="/dashboard" replace />;

  function handleFeedbackSubmit(e) {
    e.preventDefault();
    if (!comment.trim()) return;
    setSubmitted(true);
    setComment("");
  }

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden bg-gradient-to-b from-white via-slate-50 to-slate-100">
      {/* Subtle background accents */}
      <div className="pointer-events-none absolute -top-32 -left-32 h-80 w-80 rounded-full bg-teal-200/40 blur-3xl" />
      <div className="pointer-events-none absolute top-1/4 -right-32 h-80 w-80 rounded-full bg-blue-200/40 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 left-1/3 h-64 w-64 rounded-full bg-navy-200/30 blur-3xl" />

      {/* Navbar — the only place the logo mark and auth CTAs appear */}
      <header className="relative z-10">
        <div className="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-navy-900 text-white shadow-sm">
              <PenLine className="h-4 w-4" strokeWidth={2} />
            </span>
            <span className="font-semibold text-navy-900 text-lg tracking-tight">InkToWeb</span>
          </Link>

          <div className="flex items-center gap-1.5">
            <Link
              to="/login"
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full text-sm font-medium text-slate-600 hover:text-navy-900 hover:bg-white transition-colors"
            >
              <LogIn className="h-4 w-4" strokeWidth={1.8} />
              Sign In
            </Link>
            <Link
              to="/signup"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-navy-900 text-white text-sm font-medium shadow-sm hover:bg-navy-800 transition-colors"
            >
              <UserPlus className="h-4 w-4" strokeWidth={1.8} />
              Create Account
            </Link>
          </div>
        </div>
      </header>

      {/* Hero — logo is the visual focus, no repeated CTAs */}
      <main className="relative z-10 px-6">
        <div className="max-w-xl w-full mx-auto text-center pt-10 pb-16">
          <div className="inline-block rounded-3xl bg-white p-3 shadow-xl shadow-slate-200/70 ring-1 ring-slate-100">
            <img
              src="/inktoweb-logo.png"
              alt="InkToWeb"
              className="w-40 sm:w-48 rounded-2xl"
            />
          </div>

          <h1 className="mt-8 text-3xl sm:text-4xl font-semibold text-navy-900 tracking-tight leading-tight">
            Let AI Read. Let InkToWeb Digitize.
          </h1>
          <p className="mt-3 text-base text-slate-500">
            From Ink to Web, Automatically.
          </p>
        </div>

        {/* How It Works */}
        <section className="max-w-5xl mx-auto pb-16">
          <div className="text-center mb-10">
            <h2 className="text-xl font-semibold text-navy-900 tracking-tight">How It Works</h2>
            <p className="mt-1.5 text-sm text-slate-500">From paper to database in four steps.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {steps.map(({ icon: Icon, title, description }, i) => (
              <div
                key={title}
                className="relative rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-100 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center gap-2 mb-3">
                  <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-navy-800 to-teal-600 text-white shrink-0">
                    <Icon className="h-4.5 w-4.5" strokeWidth={1.8} />
                  </span>
                  <span className="text-xs font-medium text-slate-400">Step {i + 1}</span>
                </div>
                <h3 className="text-sm font-semibold text-navy-900">{title}</h3>
                <p className="mt-1 text-sm text-slate-500 leading-relaxed">{description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Feedback */}
        <section className="max-w-lg mx-auto pb-16">
          <div className="text-center mb-6">
            <h2 className="text-xl font-semibold text-navy-900 tracking-tight">Have Feedback?</h2>
            <p className="mt-1.5 text-sm text-slate-500">
              Tell us what you think — we read every comment.
            </p>
          </div>

          <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-100">
            {submitted ? (
              <p className="text-sm text-center text-teal-700 py-4">
                Thanks for your feedback! We appreciate you taking the time.
              </p>
            ) : (
              <form onSubmit={handleFeedbackSubmit} className="space-y-3">
                <textarea
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="Share a comment or suggestion..."
                  rows={3}
                  required
                  className="w-full rounded-lg border border-slate-200 px-3.5 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 shadow-sm resize-none focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                />
                <button
                  type="submit"
                  className="w-full inline-flex items-center justify-center gap-1.5 rounded-lg bg-navy-900 px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-navy-800 transition-colors"
                >
                  <Send className="h-3.5 w-3.5" strokeWidth={1.8} />
                  Send Feedback
                </button>
              </form>
            )}
          </div>
        </section>
      </main>

      <footer className="relative z-10 text-center text-xs text-slate-400 pb-6">
        InkToWeb — AI-powered form digitization
      </footer>
    </div>
  );
}
