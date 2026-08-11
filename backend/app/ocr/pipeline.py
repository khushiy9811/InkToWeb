"""
OCR extraction pipeline for the bank account opening form.

Steps (per PROJECT.md):
  1. Preprocess: deskew and normalize the uploaded image.
  2. Map the fixed, known form layout onto the normalized image using
     app.ocr.template (bounding boxes in PDF points -> pixels).
  3. For each text field, crop just that region and run Tesseract on the
     crop rather than the whole page.
  4. For each checkbox group, crop the option regions and pick the one
     with the highest ink density above a threshold.
  5. Return { field_name: { value, confidence } }.
"""
import difflib
import io
import re
from pathlib import Path

import cv2
import numpy as np
import pytesseract
from PIL import Image

from ..config import TESSERACT_CMD
from . import trocr_engine
from .template import (
    TEXT_FIELDS, CHAR_BOX_FIELDS, CHECKBOX_GROUPS, SIGNATURE_BOX, PT_TO_PX,
    TEMPLATE_WIDTH_PX, TEMPLATE_HEIGHT_PX,
)

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

_TESS_CONFIG = {
    "text": "--oem 3 --psm 7",
    "digits": "--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789",
    "digits_date": "--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789/",
    "alnum": "--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    "email": "--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@._-",
}

# Single-character whitelists for CHAR_BOX_FIELDS. PSM 10 ("treat as a
# single character") is the documented choice for this, but empirically
# it misreads plenty of real handwritten capitals that PSM 8 ("single
# word") reads correctly on the exact same crop — e.g. a handwritten K
# came back as PSM10→'L'@0% vs PSM8→'K'@91%. So every char box tries both
# PSMs (see _CHAR_PSMS) and keeps whichever scores higher, the same
# best-of-N pattern used for line-mode fields above. Kept to just these
# two (not also 7, and not also the adaptive-threshold candidate below) —
# each candidate is a separate Tesseract call per character box, and with
# ~230 boxes on this form, every extra candidate adds real per-request
# latency; 7 rarely won over 10 in testing where 10 already lost to 8.
_CHAR_PSMS = [10, 8]

# NOT used as a Tesseract -c tessedit_char_whitelist. Whitelisting looked
# like the obvious approach, but it backfires on handwriting: Tesseract's
# classifier often recognizes a digit-mode "0" as looking most like the
# *letter* O (correctly, at 60-80% confidence — they're nearly identical
# shapes) and a hard whitelist then REJECTS that entirely rather than
# falling back to the nearest allowed character, returning nothing. So
# instead every box runs with NO whitelist and the raw result is mapped
# through the classic OCR confusable-character tables below; unmappable
# results are treated as unrecognized rather than force-fit.
_DIGIT_LOOKALIKES = {
    "O": "0", "D": "0", "Q": "0", "o": "0", "U": "0",
    "I": "1", "L": "1", "l": "1", "i": "1", "j": "1",
    "Z": "2", "z": "2",
    "S": "5", "s": "5",
    "G": "6", "b": "6",
    "T": "7",
    "B": "8",
    "g": "9", "q": "9",
}
_LETTER_LOOKALIKES = {
    "0": "O", "1": "I", "2": "Z", "5": "S", "6": "G", "8": "B",
}
_VALID_CHARS = {
    "text_char": set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    "digit_char": set("0123456789"),
    "alnum_char": set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
}


def _resolve_char(raw: str, ocr_mode: str) -> str:
    """Coerce Tesseract's unconstrained guess into the character set the
    field actually allows, via the confusable-character tables, instead of
    a hard whitelist rejecting a correct-but-differently-classified read."""
    if not raw:
        return ""
    ch = raw[0].upper()
    valid = _VALID_CHARS[ocr_mode]
    if ch in valid:
        return ch
    if ocr_mode == "digit_char" and raw[0] in _DIGIT_LOOKALIKES:
        return _DIGIT_LOOKALIKES[raw[0]]
    if ocr_mode == "text_char" and ch in _LETTER_LOOKALIKES:
        return _LETTER_LOOKALIKES[ch]
    return ""

# For free-text fields, also try PSM 8 (single word) alongside the default
# PSM 7 (single line) — short one-word fields (city, nationality...) are
# sometimes read more accurately as a single word than as a line. Whichever
# candidate scores higher confidence wins; multi-word fields naturally keep
# picking the PSM 7 result since PSM 8 only returns one word for those.
_TEXT_CONFIG_CANDIDATES = ["--oem 3 --psm 7", "--oem 3 --psm 8"]

# Fields whose valid values are a small known set. Noisy OCR output is
# snapped to the closest option (by string similarity) rather than trusted
# verbatim — this sidesteps most handwriting misreads for these fields
# entirely, since the answer space is already constrained. Options for
# id_proof_type come directly from the form's own printed hint text
# ("ID Proof Type (Passport / Voter ID / DL):").
FIELD_VOCABULARY = {
    "marital_status": ["Single", "Married", "Unmarried", "Divorced", "Widowed"],
    "id_proof_type": ["Passport", "Voter ID", "Driving License"],
}

# TrOCR has no character whitelist like Tesseract's -c tessedit_char_whitelist,
# so its raw output is filtered to the characters valid for the field's mode
# after the fact.
_MODE_FILTERS = {
    "digits": lambda s: re.sub(r"[^0-9]", "", s),
    "digits_date": lambda s: re.sub(r"[^0-9/]", "", s),
    "alnum": lambda s: re.sub(r"[^A-Za-z0-9]", "", s),
    "email": lambda s: re.sub(r"[^A-Za-z0-9@._-]", "", s),
}


def load_as_image(file_bytes: bytes, filename: str) -> np.ndarray:
    """Load an uploaded JPG/PNG/PDF into a BGR OpenCV image (first page if PDF)."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        page = doc[0]
        zoom = 200 / 72.0
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    else:
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    arr = np.array(img)
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def _estimate_skew_angle(gray: np.ndarray) -> float:
    """Estimate small rotation using the minAreaRect of ink pixels. Returns
    0.0 when there isn't enough ink to estimate from, or the angle looks
    like a bad estimate rather than an actually rotated page."""
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    if coords.shape[0] < 50:
        return 0.0
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    if abs(angle) < 0.5 or abs(angle) > 15:
        return 0.0
    return angle


def _rotate(img: np.ndarray, angle: float) -> np.ndarray:
    if angle == 0.0:
        return img
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    m = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        img, m, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )


def normalize_form_image(img_bgr: np.ndarray):
    """Deskew and resize the uploaded form photo/scan to the template's
    standard pixel dimensions so template field boxes line up. Returns both
    the grayscale version (used for OCR/checkbox detection) and a color
    version aligned the same way (used for the signature snapshot crop)."""
    gray_raw = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    angle = _estimate_skew_angle(gray_raw)
    gray_rot = _rotate(gray_raw, angle)
    color_rot = _rotate(img_bgr, angle)
    size = (TEMPLATE_WIDTH_PX, TEMPLATE_HEIGHT_PX)
    gray_norm = cv2.resize(gray_rot, size, interpolation=cv2.INTER_CUBIC)
    color_norm = cv2.resize(color_rot, size, interpolation=cv2.INTER_CUBIC)
    return gray_norm, color_norm


def _pt_box_to_px(box_pt):
    x0, y0, x1, y1 = box_pt
    return (
        int(x0 * PT_TO_PX), int(y0 * PT_TO_PX),
        int(x1 * PT_TO_PX), int(y1 * PT_TO_PX),
    )


def _remove_ruled_line(crop: np.ndarray) -> np.ndarray:
    """Blank out the field's printed underline so it doesn't get fused with
    handwritten strokes during thresholding. The ruled line is a thin,
    near-uniformly dark row spanning most of the crop's width, sitting in
    the lower part of the field box — unlike handwriting, which is uneven."""
    h, w = crop.shape
    if h < 10:
        return crop
    out = crop.copy()
    search_start = int(h * 0.55)
    for y in range(search_start, h):
        row = out[y]
        dark_ratio = np.count_nonzero(row < 140) / w
        if dark_ratio > 0.55:
            out[max(0, y - 1):min(h, y + 2), :] = 255
    return out


def _run_tesseract(binary: np.ndarray, config: str):
    data = pytesseract.image_to_data(
        binary, config=config, output_type=pytesseract.Output.DICT
    )
    words, confs = [], []
    for text, conf in zip(data["text"], data["conf"]):
        text = text.strip()
        conf = float(conf)
        if text and conf >= 0:
            words.append(text)
            confs.append(conf)
    value = " ".join(words).strip()
    confidence = round(sum(confs) / len(confs), 1) if confs else 0.0
    return value, confidence


def _prepare_crop(gray: np.ndarray, box_pt):
    """Crop the field region and enhance it for OCR. Returns the enhanced
    grayscale crop (pre-binarization — this is what TrOCR reads), or None
    if the box falls outside the image."""
    x0, y0, x1, y1 = _pt_box_to_px(box_pt)
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, gray.shape[1]), min(y1, gray.shape[0])
    crop = gray[y0:y1, x0:x1]
    if crop.size == 0:
        return None

    crop = _remove_ruled_line(crop)

    # Scale each crop up to a consistent target height — both OCR engines
    # read small-field crops far more reliably around ~100-120px tall than
    # at native scan resolution.
    target_h = 110
    scale = max(2.5, min(6.0, target_h / max(crop.shape[0], 1)))
    big = cv2.resize(crop, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    big = clahe.apply(big)
    big = cv2.GaussianBlur(big, (3, 3), 0)
    return big


def _tesseract_candidates(big: np.ndarray, ocr_mode: str):
    _, otsu = cv2.threshold(big, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    adaptive = cv2.adaptiveThreshold(
        big, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )

    configs = _TEXT_CONFIG_CANDIDATES if ocr_mode == "text" else [_TESS_CONFIG.get(ocr_mode, _TESS_CONFIG["text"])]
    best_value, best_confidence = "", 0.0
    for candidate in (otsu, adaptive):
        for config in configs:
            value, confidence = _run_tesseract(candidate, config)
            if confidence > best_confidence or (
                confidence == best_confidence and len(value) > len(best_value)
            ):
                best_value, best_confidence = value, confidence

    return best_value, best_confidence


def _snap_to_vocabulary(value: str, options: list[str]) -> tuple[str, float]:
    """Match noisy OCR output against a small set of known valid values.
    Returns (best_option, similarity 0-1) — caller decides the threshold."""
    best_option, best_ratio = "", 0.0
    for option in options:
        ratio = difflib.SequenceMatcher(None, value.lower(), option.lower()).ratio()
        if ratio > best_ratio:
            best_option, best_ratio = option, ratio
    return best_option, best_ratio


def _checkbox_ink_ratio(gray: np.ndarray, box_pt) -> float:
    x0, y0, x1, y1 = _pt_box_to_px(box_pt)
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, gray.shape[1]), min(y1, gray.shape[0])
    crop = gray[y0:y1, x0:x1]
    if crop.size == 0:
        return 0.0
    # Shrink inward slightly to avoid counting the box's own printed border.
    h, w = crop.shape
    margin_y, margin_x = max(1, int(h * 0.18)), max(1, int(w * 0.18))
    inner = crop[margin_y:h - margin_y, margin_x:w - margin_x]
    if inner.size == 0:
        inner = crop
    _, binary = cv2.threshold(inner, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    return float(np.count_nonzero(binary)) / float(binary.size)


def _detect_checkbox_group(gray: np.ndarray, group: dict):
    options = group["options"]
    ratios = {name: _checkbox_ink_ratio(gray, box) for name, box in options.items()}
    sorted_opts = sorted(ratios.items(), key=lambda kv: kv[1], reverse=True)
    top_name, top_ratio = sorted_opts[0]
    second_ratio = sorted_opts[1][1] if len(sorted_opts) > 1 else 0.0

    MIN_INK_RATIO = 0.12
    if top_ratio < MIN_INK_RATIO:
        return "", 20.0

    margin = top_ratio - second_ratio
    confidence = min(95.0, 50.0 + margin * 400)
    confidence = max(confidence, 30.0)
    return top_name, round(confidence, 1)


def _ocr_single_char(gray: np.ndarray, box_pt, ocr_mode: str):
    """OCR one character-grid cell. Returns ("", 100.0) for a confidently
    blank box (below the ink threshold) rather than guessing at noise."""
    # A fixed ink-ratio threshold doesn't generalize across box sizes: a
    # character is a roughly fixed absolute ink area, so the same digit
    # registers a much lower ratio in a wide box (e.g. initial_deposit,
    # 22pt) than a narrow one (e.g. aadhaar, 5.5pt). 0.008 is well below
    # any real character's ratio even in the widest boxes, while still
    # well above stray noise/border artifacts in a genuinely empty box.
    ink_ratio = _checkbox_ink_ratio(gray, box_pt)
    if ink_ratio < 0.008:
        return "", 100.0

    x0, y0, x1, y1 = _pt_box_to_px(box_pt)
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, gray.shape[1]), min(y1, gray.shape[0])
    crop = gray[y0:y1, x0:x1]
    if crop.size == 0:
        return "", 0.0

    h, w = crop.shape
    margin_y, margin_x = max(1, int(h * 0.12)), max(1, int(w * 0.12))
    inner = crop[margin_y:h - margin_y, margin_x:w - margin_x]
    if inner.size == 0:
        inner = crop

    target_h = 100
    scale = max(3.0, min(8.0, target_h / max(inner.shape[0], 1)))
    big = cv2.resize(inner, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    big = clahe.apply(big)
    _, otsu = cv2.threshold(big, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    def try_candidates(candidate):
        best_value, best_confidence = "", 0.0
        for psm in _CHAR_PSMS:
            config = f"--oem 3 --psm {psm}"
            raw_value, confidence = _run_tesseract(candidate, config)
            value = _resolve_char(raw_value, ocr_mode)
            if confidence > best_confidence or (
                confidence == best_confidence and value and not best_value
            ):
                best_value, best_confidence = value, confidence
        return best_value, best_confidence

    # OTSU alone resolves the large majority of boxes — with ~230 boxes on
    # this form, only paying for a second (adaptive) threshold candidate
    # when OTSU came up completely empty keeps per-request latency down
    # without giving up the accuracy adaptive occasionally adds.
    best_value, best_confidence = try_candidates(otsu)
    if not best_value:
        adaptive = cv2.adaptiveThreshold(
            big, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
        )
        best_value, best_confidence = try_candidates(adaptive)

    return best_value, best_confidence


def _ocr_char_boxes(gray: np.ndarray, spec: dict):
    """OCR every cell in a character grid and stitch the result together.
    text_char fields turn a run of blank cells into a single space;
    digit/alnum fields just skip blanks (fields shorter than the max box
    count, e.g. a 5-digit deposit in a 9-box field, are normal)."""
    insert_spaces = spec["ocr_mode"] == "text_char"
    chars, confs = [], []
    pending_space = False
    for box in spec["boxes"]:
        ch, confidence = _ocr_single_char(gray, box, spec["ocr_mode"])
        if ch:
            if insert_spaces and pending_space and chars:
                chars.append(" ")
            chars.append(ch)
            confs.append(confidence)
            pending_space = False
        else:
            pending_space = True

    value = "".join(chars).strip()
    confidence = round(sum(confs) / len(confs), 1) if confs else 0.0
    return value, confidence


def _crop_signature(color_bgr: np.ndarray) -> np.ndarray:
    """Crop the signature strip from the color-normalized image, in color
    (not binarized) since this is stored as a visual snapshot, not OCR'd."""
    x0, y0, x1, y1 = _pt_box_to_px(SIGNATURE_BOX)
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, color_bgr.shape[1]), min(y1, color_bgr.shape[0])
    return color_bgr[y0:y1, x0:x1]


def extract_form_fields(img_bgr: np.ndarray):
    """Returns (fields_dict, signature_crop) — signature_crop is a BGR
    numpy array ready to be encoded/saved by the caller."""
    gray, color = normalize_form_image(img_bgr)

    # Pass 1: crop + enhance every field, and run Tesseract on each (cheap,
    # per-field). Fields whose box falls outside the image are skipped.
    field_names, crops, tess_results = [], [], []
    for field_name, spec in TEXT_FIELDS.items():
        big = _prepare_crop(gray, spec["box"])
        if big is None:
            field_names.append(field_name)
            crops.append(None)
            tess_results.append(("", 0.0))
            continue
        field_names.append(field_name)
        crops.append(big)
        tess_results.append(_tesseract_candidates(big, spec["ocr_mode"]))

    # Pass 2: run TrOCR (handwriting-trained transformer) only for fields
    # Tesseract wasn't already confident about, batched into a single
    # forward pass. TrOCR inference is the slow part of this pipeline on
    # CPU, so fields Tesseract already read well (printed-ish handwriting,
    # short values) skip it entirely instead of paying that cost for no
    # benefit. If TrOCR is unavailable (deps missing, offline on first run,
    # runtime error) this just falls back to Tesseract-only results.
    TROCR_ESCALATION_THRESHOLD = 75.0
    escalate_indices = [
        i for i, (big, (_, tess_confidence)) in enumerate(zip(crops, tess_results))
        if big is not None and tess_confidence < TROCR_ESCALATION_THRESHOLD
    ]
    try:
        rgb_crops = [cv2.cvtColor(crops[i], cv2.COLOR_GRAY2RGB) for i in escalate_indices]
        trocr_raw = trocr_engine.recognize_batch(rgb_crops)
    except Exception:
        trocr_raw = []
    trocr_by_index = dict(zip(escalate_indices, trocr_raw))

    results = {}
    for i, (field_name, big, (tess_value, tess_confidence)) in enumerate(zip(field_names, crops, tess_results)):
        ocr_mode = TEXT_FIELDS[field_name]["ocr_mode"]
        best_value, best_confidence = tess_value, tess_confidence

        if i in trocr_by_index:
            trocr_value, trocr_confidence = trocr_by_index[i]
            mode_filter = _MODE_FILTERS.get(ocr_mode)
            if mode_filter:
                trocr_value = mode_filter(trocr_value)
            if trocr_confidence > best_confidence or (
                trocr_confidence == best_confidence and len(trocr_value) > len(best_value)
            ):
                best_value, best_confidence = trocr_value, trocr_confidence

        vocabulary = FIELD_VOCABULARY.get(field_name)
        if vocabulary and best_value:
            match, similarity = _snap_to_vocabulary(best_value, vocabulary)
            if similarity >= 0.55:
                best_value = match
                best_confidence = max(best_confidence, min(95.0, best_confidence + 15))

        results[field_name] = {"value": best_value, "confidence": best_confidence}

    for field_name, spec in CHAR_BOX_FIELDS.items():
        value, confidence = _ocr_char_boxes(gray, spec)
        vocabulary = FIELD_VOCABULARY.get(field_name)
        if vocabulary and value:
            match, similarity = _snap_to_vocabulary(value, vocabulary)
            if similarity >= 0.55:
                value = match
                confidence = max(confidence, min(95.0, confidence + 15))
        results[field_name] = {"value": value, "confidence": confidence}

    for group in CHECKBOX_GROUPS.values():
        value, confidence = _detect_checkbox_group(gray, group)
        results[group["field_name"]] = {
            "value": value.lower() if value else "",
            "confidence": confidence,
        }

    signature_crop = _crop_signature(color)
    return results, signature_crop
