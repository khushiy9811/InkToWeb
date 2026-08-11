import ConfidenceBadge from "./ConfidenceBadge";
import { LOW_CONFIDENCE_THRESHOLD } from "../fieldConfig";

export default function FieldInput({ field, value, confidence, onChange, readOnly }) {
  const isLow = confidence != null && confidence < LOW_CONFIDENCE_THRESHOLD;

  const inputClass = `w-full rounded-md border px-3 py-2 text-sm shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 ${
    isLow ? "border-amber-400 bg-amber-50" : "border-slate-300 bg-white"
  } ${readOnly ? "bg-slate-100 text-slate-600 cursor-not-allowed" : ""}`;

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <label className="text-sm font-medium text-slate-700">{field.label}</label>
        {confidence != null && <ConfidenceBadge confidence={confidence} />}
      </div>
      {field.type === "select" ? (
        <select
          className={inputClass}
          value={value || ""}
          disabled={readOnly}
          onChange={(e) => onChange(field.name, e.target.value)}
        >
          <option value="">Select...</option>
          {field.options.map((opt) => (
            <option key={opt} value={opt}>
              {opt.charAt(0).toUpperCase() + opt.slice(1)}
            </option>
          ))}
        </select>
      ) : (
        <input
          type="text"
          className={inputClass}
          value={value || ""}
          readOnly={readOnly}
          onChange={(e) => onChange(field.name, e.target.value)}
        />
      )}
    </div>
  );
}
