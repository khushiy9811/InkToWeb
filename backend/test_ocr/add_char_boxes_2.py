"""
Second pass: adds per-character grid boxes to the remaining short/fixed
freeform fields (branch, father's/spouse's name, nationality, marital
status, occupation, ID proof type, nominee name, nominee relationship).

city/state are deliberately skipped — they share a cramped row with PIN
Code and Indian state names vary too much in length (5 to 28+ characters)
to box without truncating real values. address_line1/2 and email are also
skipped (long free text / need lowercase+symbols).

Run from backend/: python test_ocr/add_char_boxes_2.py
Writes a PREVIEW first; the source PDF is only overwritten after review.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fitz

SRC_PDF = Path(r"K:\InkToWeb\bank_account_opening_form.pdf")

BOX_STROKE = (0, 0, 0)
BOX_WIDTH = 0.6

FIELD_BOX_SPECS = {
    "branch": {
        "wipe": (82.5, 74.4, 178.0, 89.7),
        "grid_y0": 75.0, "grid_y1": 89.0,
        "grid_x0": 82.5, "box_w": 6.5, "gap": 1.46, "count": 12,
    },
    "father_spouse_name": {
        "wipe": (146.5, 150.5, 554.9, 165.7),
        "grid_y0": 151.0, "grid_y1": 165.0,
        "grid_x0": 147.0, "box_w": 13.5, "gap": 2.77, "count": 24,
    },
    "nationality": {
        "wipe": (88.9, 199.3, 166.5, 214.6),
        "grid_y0": 200.0, "grid_y1": 214.0,
        "grid_x0": 89.0, "box_w": 6.0, "gap": 1.7, "count": 10,
    },
    "marital_status": {
        "wipe": (229.5, 199.3, 554.9, 214.6),
        "grid_y0": 200.0, "grid_y1": 214.0,
        "grid_x0": 230.0, "box_w": 14.0, "gap": 3.0, "count": 10,
    },
    "occupation": {
        "wipe": (92.2, 222.0, 197.0, 237.3),
        "grid_y0": 223.0, "grid_y1": 237.0,
        "grid_x0": 93.0, "box_w": 7.0, "gap": 1.7, "count": 12,
    },
    "id_proof_type": {
        "wipe": (199.4, 419.8, 554.9, 435.1),
        "grid_y0": 420.0, "grid_y1": 434.0,
        "grid_x0": 200.0, "box_w": 14.5, "gap": 2.8, "count": 20,
    },
    "nominee_name": {
        "wipe": (108.2, 526.4, 267.0, 541.6),
        "grid_y0": 527.0, "grid_y1": 541.0,
        "grid_x0": 108.2, "box_w": 9.5, "gap": 1.85, "count": 14,
    },
    "nominee_relationship": {
        "wipe": (324.5, 526.4, 554.9, 541.6),
        "grid_y0": 527.0, "grid_y1": 541.0,
        "grid_x0": 325.0, "box_w": 11.3, "gap": 2.85, "count": 16,
    },
}


def char_boxes_for(spec):
    x = spec["grid_x0"]
    boxes = []
    for _ in range(spec["count"]):
        boxes.append([round(x, 2), spec["grid_y0"], round(x + spec["box_w"], 2), spec["grid_y1"]])
        x += spec["box_w"] + spec["gap"]
    return boxes


def build(out_path: Path):
    doc = fitz.open(SRC_PDF)
    page = doc[0]

    for field_name, spec in FIELD_BOX_SPECS.items():
        wx0, wy0, wx1, wy1 = spec["wipe"]
        page.draw_rect(fitz.Rect(wx0, wy0, wx1, wy1), color=None, fill=(1, 1, 1))

        for box in char_boxes_for(spec):
            page.draw_rect(fitz.Rect(*box), color=BOX_STROKE, width=BOX_WIDTH, fill=None)

    doc.save(out_path)
    print("Saved:", out_path)

    doc2 = fitz.open(out_path)
    pix = doc2[0].get_pixmap(matrix=fitz.Matrix(200 / 72.0, 200 / 72.0))
    preview_path = out_path.with_suffix(".png")
    pix.save(preview_path)
    print("Preview:", preview_path)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "boxed_form_preview2.pdf"
    build(out)
