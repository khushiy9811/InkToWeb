import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import client, { API_ORIGIN } from "../api/client";
import Layout from "../components/Layout";
import FieldInput from "../components/FieldInput";
import { FIELD_SECTIONS, LOW_CONFIDENCE_THRESHOLD } from "../fieldConfig";

export default function Review() {
  const [fields, setFields] = useState({});
  const [confidences, setConfidences] = useState({});
  const [imagePath, setImagePath] = useState(null);
  const [signaturePath, setSignaturePath] = useState(null);
  const [zoom, setZoom] = useState(1);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const raw = sessionStorage.getItem("inktoweb_extraction");
    if (!raw) {
      navigate("/upload");
      return;
    }
    const parsed = JSON.parse(raw);
    const values = {};
    const confs = {};
    for (const [key, { value, confidence }] of Object.entries(parsed.fields)) {
      values[key] = value;
      confs[key] = confidence;
    }
    setFields(values);
    setConfidences(confs);
    setImagePath(parsed.image_path);
    setSignaturePath(parsed.signature_image_path || null);
  }, [navigate]);

  const lowConfidenceCount = Object.values(confidences).filter(
    (c) => c < LOW_CONFIDENCE_THRESHOLD
  ).length;

  function handleChange(name, value) {
    setFields((prev) => ({ ...prev, [name]: value }));
    // Employee has reviewed/edited this field manually — treat as confirmed.
    setConfidences((prev) => ({ ...prev, [name]: 100 }));
  }

  async function handleConfirm() {
    setSaving(true);
    setError("");
    try {
      const payload = {
        ...fields,
        form_image_path: imagePath,
        signature_image_path: signaturePath,
        extraction_confidence: confidences,
      };
      const res = await client.post("/api/customers", payload);
      sessionStorage.removeItem("inktoweb_extraction");
      navigate(`/customers/${res.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save customer record.");
    } finally {
      setSaving(false);
    }
  }

  if (!imagePath) return null;

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-navy-900">Review Extracted Data</h1>
        <p className="text-sm text-slate-500 mt-1">
          Verify and correct the fields below against the scanned form. Nothing is saved
          until you confirm.
        </p>
        {lowConfidenceCount > 0 && (
          <div className="mt-3 inline-flex items-center gap-2 rounded-md bg-amber-50 border border-amber-200 px-3 py-2 text-sm text-amber-800">
            ⚠ {lowConfidenceCount} field{lowConfidenceCount > 1 ? "s" : ""} flagged for review — low OCR confidence.
          </div>
        )}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="lg:sticky lg:top-6 h-fit">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-slate-200 bg-slate-50">
              <span className="text-sm font-medium text-slate-600">Uploaded Form</span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setZoom((z) => Math.max(0.5, z - 0.25))}
                  className="text-slate-500 hover:text-navy-700 px-2 py-1 rounded hover:bg-slate-200"
                >
                  −
                </button>
                <span className="text-xs text-slate-500 w-10 text-center">{Math.round(zoom * 100)}%</span>
                <button
                  onClick={() => setZoom((z) => Math.min(3, z + 0.25))}
                  className="text-slate-500 hover:text-navy-700 px-2 py-1 rounded hover:bg-slate-200"
                >
                  +
                </button>
              </div>
            </div>
            <div className="overflow-auto max-h-[80vh] p-4 bg-slate-100">
              <img
                src={`${API_ORIGIN}${imagePath}`}
                alt="Uploaded form"
                style={{ width: `${zoom * 100}%`, maxWidth: "none" }}
                className="mx-auto shadow-md"
              />
            </div>
          </div>
        </div>

        <div className="space-y-6">
          {FIELD_SECTIONS.map((section) => (
            <div key={section.title} className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <h2 className="text-sm font-semibold text-navy-900 uppercase tracking-wide mb-4">
                {section.title}
              </h2>
              <div className="grid sm:grid-cols-2 gap-4">
                {section.fields.map((field) => (
                  <FieldInput
                    key={field.name}
                    field={field}
                    value={fields[field.name]}
                    confidence={confidences[field.name]}
                    onChange={handleChange}
                  />
                ))}
              </div>
            </div>
          ))}

          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
            <h2 className="text-sm font-semibold text-navy-900 uppercase tracking-wide mb-4">
              Applicant Signature
            </h2>
            {signaturePath ? (
              <img
                src={`${API_ORIGIN}${signaturePath}`}
                alt="Captured applicant signature"
                className="h-20 rounded-md border border-slate-200 bg-white"
              />
            ) : (
              <p className="text-sm text-slate-400">No signature captured from the form.</p>
            )}
          </div>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2">
              {error}
            </div>
          )}

          <div className="flex items-center gap-3 pb-6">
            <button
              onClick={handleConfirm}
              disabled={saving}
              className="inline-flex items-center gap-2 rounded-md bg-navy-900 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-navy-800 transition-colors disabled:opacity-50"
            >
              {saving ? "Saving..." : "Confirm & Save"}
            </button>
            <button
              onClick={() => navigate("/upload")}
              className="text-sm font-medium text-slate-500 hover:text-slate-700"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
}
