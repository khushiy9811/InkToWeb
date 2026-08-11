import { useState, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";
import Layout from "../components/Layout";

const ACCEPTED_TYPES = ["image/jpeg", "image/png", "application/pdf"];

export default function Upload() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);
  const navigate = useNavigate();

  const handleFile = useCallback((f) => {
    if (!f) return;
    if (!ACCEPTED_TYPES.includes(f.type)) {
      setError("Please upload a JPG, PNG, or PDF file.");
      return;
    }
    setError("");
    setFile(f);
    if (f.type === "application/pdf") {
      setPreview(null);
    } else {
      setPreview(URL.createObjectURL(f));
    }
  }, []);

  function handleDrop(e) {
    e.preventDefault();
    setDragActive(false);
    handleFile(e.dataTransfer.files?.[0]);
  }

  async function handleExtract() {
    if (!file) return;
    setExtracting(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await client.post("/api/forms/extract", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      sessionStorage.setItem(
        "inktoweb_extraction",
        JSON.stringify({
          fields: res.data.fields,
          image_path: res.data.image_path,
          signature_image_path: res.data.signature_image_path,
        })
      );
      navigate("/review");
    } catch (err) {
      setError(err.response?.data?.detail || "Extraction failed. Please try again.");
    } finally {
      setExtracting(false);
    }
  }

  return (
    <Layout>
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-semibold text-navy-900 mb-1">Upload New Form</h1>
        <p className="text-sm text-slate-500 mb-6">
          Upload a photo or scan of a filled bank account opening form. We'll extract the
          fields automatically — you'll review and confirm everything before it's saved.
        </p>

        <div
          onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`rounded-xl border-2 border-dashed p-10 text-center cursor-pointer transition-colors ${
            dragActive ? "border-teal-500 bg-teal-50" : "border-slate-300 bg-white hover:border-teal-400"
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".jpg,.jpeg,.png,.pdf"
            className="hidden"
            onChange={(e) => handleFile(e.target.files?.[0])}
          />
          {preview ? (
            <img src={preview} alt="Preview" className="max-h-96 mx-auto rounded-lg shadow-sm" />
          ) : file ? (
            <div className="text-slate-600">
              <p className="font-medium">{file.name}</p>
              <p className="text-sm text-slate-400 mt-1">PDF selected — no preview available</p>
            </div>
          ) : (
            <div className="text-slate-500">
              <svg className="mx-auto h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
              </svg>
              <p className="mt-3 font-medium">Drag & drop a form image here</p>
              <p className="text-sm mt-1">or click to browse (JPG, PNG, PDF)</p>
            </div>
          )}
        </div>

        {error && (
          <div className="mt-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2">
            {error}
          </div>
        )}

        <div className="mt-6 flex items-center gap-3">
          <button
            onClick={handleExtract}
            disabled={!file || extracting}
            className="inline-flex items-center gap-2 rounded-md bg-teal-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-teal-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {extracting ? (
              <>
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                </svg>
                Extracting data...
              </>
            ) : (
              "Extract Data"
            )}
          </button>
          {file && !extracting && (
            <button
              onClick={() => { setFile(null); setPreview(null); }}
              className="text-sm font-medium text-slate-500 hover:text-slate-700"
            >
              Clear
            </button>
          )}
        </div>
      </div>
    </Layout>
  );
}
