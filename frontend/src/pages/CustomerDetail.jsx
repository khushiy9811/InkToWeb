import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { Trash2 } from "lucide-react";
import client, { API_ORIGIN } from "../api/client";
import Layout from "../components/Layout";
import FieldInput from "../components/FieldInput";
import { FIELD_SECTIONS } from "../fieldConfig";

function AccountTypeBadge({ type }) {
  if (!type) return null;
  const isSavings = type === "savings";
  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${
        isSavings ? "bg-teal-100 text-teal-800" : "bg-navy-100 text-navy-800"
      }`}
    >
      {type.charAt(0).toUpperCase() + type.slice(1)} Account
    </span>
  );
}

export default function CustomerDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [customer, setCustomer] = useState(null);
  const [fields, setFields] = useState({});
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [imageZoomed, setImageZoomed] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [confirmingDelete, setConfirmingDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    load();
  }, [id]);

  async function load() {
    setLoading(true);
    try {
      const res = await client.get(`/api/customers/${id}`);
      setCustomer(res.data);
      setFields(res.data);
    } catch (err) {
      setError("Failed to load customer.");
    } finally {
      setLoading(false);
    }
  }

  function handleChange(name, value) {
    setFields((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSave() {
    setSaving(true);
    setError("");
    try {
      const payload = { ...fields };
      delete payload.id;
      delete payload.form_image_path;
      delete payload.signature_image_path;
      delete payload.added_by_employee_id;
      delete payload.added_by_name;
      delete payload.created_at;
      delete payload.updated_at;
      delete payload.extraction_confidence;
      const res = await client.put(`/api/customers/${id}`, payload);
      setCustomer(res.data);
      setFields(res.data);
      setEditing(false);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save changes.");
    } finally {
      setSaving(false);
    }
  }

  function handleCancelEdit() {
    setFields(customer);
    setEditing(false);
  }

  async function handleDelete() {
    setDeleting(true);
    setError("");
    try {
      await client.delete(`/api/customers/${id}`);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete customer record.");
      setDeleting(false);
      setConfirmingDelete(false);
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-200 rounded w-64" />
          <div className="h-64 bg-slate-200 rounded" />
        </div>
      </Layout>
    );
  }

  if (!customer) {
    return (
      <Layout>
        <p className="text-slate-500">Customer not found.</p>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="mb-6">
        <Link to="/dashboard" className="text-sm text-slate-500 hover:text-navy-700">
          ← Back to Dashboard
        </Link>
        <div className="flex items-start justify-between mt-2 flex-wrap gap-3">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-semibold text-navy-900">
                {customer.full_name || "(unnamed customer)"}
              </h1>
              <AccountTypeBadge type={customer.account_type} />
            </div>
            <p className="text-sm text-slate-500 mt-1">
              Added by {customer.added_by_name || "unknown"} on{" "}
              {customer.created_at ? new Date(customer.created_at).toLocaleString() : "—"}
              {customer.updated_at &&
                customer.updated_at !== customer.created_at &&
                ` · Last edited ${new Date(customer.updated_at).toLocaleString()}`}
            </p>
          </div>
          {confirmingDelete ? (
            <div className="flex items-center gap-2 rounded-md border border-red-200 bg-red-50 px-3 py-2">
              <span className="text-sm text-red-700">Delete this record permanently?</span>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="rounded-md bg-red-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                {deleting ? "Deleting..." : "Confirm"}
              </button>
              <button
                onClick={() => setConfirmingDelete(false)}
                disabled={deleting}
                className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          ) : !editing ? (
            <div className="flex gap-2">
              <button
                onClick={() => setEditing(true)}
                className="rounded-md bg-navy-900 px-4 py-2 text-sm font-semibold text-white hover:bg-navy-800 transition-colors"
              >
                Edit
              </button>
              <button
                onClick={() => setConfirmingDelete(true)}
                className="inline-flex items-center gap-1.5 rounded-md border border-red-200 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
              >
                <Trash2 className="h-4 w-4" strokeWidth={1.8} />
                Delete
              </button>
            </div>
          ) : (
            <div className="flex gap-2">
              <button
                onClick={handleSave}
                disabled={saving}
                className="rounded-md bg-teal-600 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-700 transition-colors disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save Changes"}
              </button>
              <button
                onClick={handleCancelEdit}
                className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="mb-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2">
          {error}
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        <div>
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-4 py-2 border-b border-slate-200 bg-slate-50">
              <span className="text-sm font-medium text-slate-600">Hard Copy — Scanned Form</span>
            </div>
            {customer.form_image_path ? (
              <img
                src={`${API_ORIGIN}${customer.form_image_path}`}
                alt="Scanned form"
                onClick={() => setImageZoomed(true)}
                className="w-full cursor-zoom-in hover:opacity-95 transition-opacity"
              />
            ) : (
              <div className="p-8 text-center text-slate-400 text-sm">No image attached.</div>
            )}
          </div>

          <div className="mt-4 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-4 py-2 border-b border-slate-200 bg-slate-50">
              <span className="text-sm font-medium text-slate-600">Applicant Signature</span>
            </div>
            <div className="p-4">
              {customer.signature_image_path ? (
                <img
                  src={`${API_ORIGIN}${customer.signature_image_path}`}
                  alt="Captured applicant signature"
                  className="h-20 rounded-md border border-slate-200 bg-white"
                />
              ) : (
                <p className="text-sm text-slate-400">No signature captured.</p>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          {FIELD_SECTIONS.map((section) => (
            <div key={section.title} className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <h2 className="text-sm font-semibold text-navy-900 uppercase tracking-wide mb-4">
                {section.title}
              </h2>
              {editing ? (
                <div className="grid sm:grid-cols-2 gap-4">
                  {section.fields.map((field) => (
                    <FieldInput
                      key={field.name}
                      field={field}
                      value={fields[field.name]}
                      onChange={handleChange}
                    />
                  ))}
                </div>
              ) : (
                <dl className="grid sm:grid-cols-2 gap-4">
                  {section.fields.map((field) => (
                    <div key={field.name}>
                      <dt className="text-xs font-medium text-slate-400 uppercase tracking-wide">
                        {field.label}
                      </dt>
                      <dd className="text-sm text-slate-800 mt-0.5">
                        {customer[field.name] || <span className="text-slate-300">—</span>}
                      </dd>
                    </div>
                  ))}
                </dl>
              )}
            </div>
          ))}
        </div>
      </div>

      {imageZoomed && customer.form_image_path && (
        <div
          className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-6 cursor-zoom-out"
          onClick={() => setImageZoomed(false)}
        >
          <img
            src={`${API_ORIGIN}${customer.form_image_path}`}
            alt="Scanned form enlarged"
            className="max-h-full max-w-full rounded-lg shadow-2xl"
          />
        </div>
      )}
    </Layout>
  );
}
