import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";
import Layout from "../components/Layout";

function StatCard({ label, value }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-navy-900">{value}</p>
    </div>
  );
}

function AccountTypeBadge({ type }) {
  if (!type) return <span className="text-slate-400 text-sm">—</span>;
  const isSavings = type === "savings";
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
        isSavings ? "bg-teal-100 text-teal-800" : "bg-navy-100 text-navy-800"
      }`}
    >
      {type.charAt(0).toUpperCase() + type.slice(1)}
    </span>
  );
}

export default function Dashboard() {
  const [items, setItems] = useState([]);
  const [stats, setStats] = useState({});
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("created_at");
  const [sortDir, setSortDir] = useState("desc");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchCustomers = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await client.get("/api/customers", {
        params: { search, sort_by: sortBy, sort_dir: sortDir },
      });
      setItems(res.data.items);
      setStats(res.data.stats);
    } catch (err) {
      setError("Failed to load customers.");
    } finally {
      setLoading(false);
    }
  }, [search, sortBy, sortDir]);

  useEffect(() => {
    const timer = setTimeout(fetchCustomers, 250);
    return () => clearTimeout(timer);
  }, [fetchCustomers]);

  function toggleSort(col) {
    if (sortBy === col) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortBy(col);
      setSortDir("asc");
    }
  }

  const columns = [
    { key: "full_name", label: "Name" },
    { key: "account_type", label: "Account Type" },
    { key: "mobile_number", label: "Mobile" },
    { key: "city", label: "City" },
    { key: "created_at", label: "Date Added" },
  ];

  return (
    <Layout>
      <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-navy-900">Customers</h1>
          <p className="text-sm text-slate-500 mt-1">
            Browse and manage digitized account opening forms.
          </p>
        </div>
        <Link
          to="/upload"
          className="inline-flex items-center gap-2 rounded-md bg-teal-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-teal-700 transition-colors"
        >
          + Upload New Form
        </Link>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Customers" value={stats.total_customers ?? "—"} />
        <StatCard label="Added Today" value={stats.added_today ?? "—"} />
        <StatCard label="Savings Accounts" value={stats.savings_accounts ?? "—"} />
        <StatCard label="Current Accounts" value={stats.current_accounts ?? "—"} />
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200">
          <input
            type="text"
            placeholder="Search by name, mobile, email, or city..."
            className="w-full sm:w-96 rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {error && <div className="p-4 text-sm text-red-600">{error}</div>}

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                {columns.map((col) => (
                  <th
                    key={col.key}
                    onClick={() => toggleSort(col.key)}
                    className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider cursor-pointer select-none hover:text-navy-700"
                  >
                    {col.label}
                    {sortBy === col.key && (sortDir === "asc" ? " ↑" : " ↓")}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i}>
                    {columns.map((col) => (
                      <td key={col.key} className="px-4 py-4">
                        <div className="h-4 bg-slate-100 rounded animate-pulse w-24" />
                      </td>
                    ))}
                  </tr>
                ))
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={columns.length} className="px-4 py-12 text-center text-slate-400">
                    No customers found. {search && "Try a different search."}
                  </td>
                </tr>
              ) : (
                items.map((c) => (
                  <tr
                    key={c.id}
                    className="hover:bg-slate-50 cursor-pointer transition-colors"
                    onClick={() => (window.location.href = `/customers/${c.id}`)}
                  >
                    <td className="px-4 py-3 text-sm font-medium text-navy-900">
                      <Link to={`/customers/${c.id}`} className="hover:text-teal-700">
                        {c.full_name || "(unnamed)"}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <AccountTypeBadge type={c.account_type} />
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-600">{c.mobile_number || "—"}</td>
                    <td className="px-4 py-3 text-sm text-slate-600">{c.city || "—"}</td>
                    <td className="px-4 py-3 text-sm text-slate-500">
                      {c.created_at ? new Date(c.created_at).toLocaleDateString() : "—"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  );
}
