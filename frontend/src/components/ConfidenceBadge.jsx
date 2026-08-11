import { LOW_CONFIDENCE_THRESHOLD } from "../fieldConfig";

export default function ConfidenceBadge({ confidence }) {
  if (confidence == null) return null;
  const isLow = confidence < LOW_CONFIDENCE_THRESHOLD;
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
        isLow
          ? "bg-amber-100 text-amber-800"
          : "bg-teal-100 text-teal-800"
      }`}
      title={`OCR confidence: ${confidence}%`}
    >
      {isLow ? "⚠ Check" : "✓"} {confidence}%
    </span>
  );
}
