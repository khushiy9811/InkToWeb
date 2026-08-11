"""
One-off script: redesigns bank_account_opening_form.pdf to add per-character
grid boxes for the highest-stakes fields (full_name, date_of_birth,
mobile_number, pin_code, aadhaar_id_number, pan_number, initial_deposit).

Per-character boxes are a well-established technique for form OCR: they
eliminate segmentation ambiguity (where one letter ends and the next
begins) and cursive joins, which is why real bank/govt forms use them for
exactly these fields. Freeform fields (address, occupation, nominee, etc.)
and the signature are untouched.

Run from backend/: python test_ocr/add_char_boxes.py
Writes a PREVIEW png first; the source PDF is only overwritten after
visual review (see finalize_boxed_form.py).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fitz

SRC_PDF = Path(r"K:\InkToWeb\bank_account_opening_form.pdf")

BOX_STROKE = (0, 0, 0)
BOX_WIDTH = 0.6

# Each spec: field_name -> (x0, y0, x1, y1 of the ORIGINAL field box to wipe,
# then the new box grid: grid_x0, grid_y0, grid_y1, box_w, gap, count)
FIELD_BOX_SPECS = {
    "full_name": {
        "wipe": (130.4, 127.9, 554.9, 143.2),
        "grid_y0": 128.5, "grid_y1": 142.5,
        "grid_x0": 131.0, "box_w": 13.5, "gap": 2.77, "count": 26,
    },
    "date_of_birth": {
        "wipe": (91.9, 165.7, 196.2, 199.3),  # covers old field + printed slashes
        "grid_y0": 172.0, "grid_y1": 187.0,
        "grid_x0": 93.0, "box_w": 10.0, "gap": 2.375, "count": 8,
    },
    "mobile_number": {
        "wipe": (106.9, 343.6, 196.6, 358.9),
        "grid_y0": 344.0, "grid_y1": 358.0,
        "grid_x0": 107.0, "box_w": 7.2, "gap": 1.76, "count": 10,
    },
    "pin_code": {
        "wipe": (304.4, 320.9, 554.9, 336.2),
        "grid_y0": 321.0, "grid_y1": 335.0,
        "grid_x0": 306.0, "box_w": 20.0, "gap": 4.0, "count": 6,
    },
    "aadhaar_id_number": {
        "wipe": (163.0, 397.1, 246.6, 412.4),
        "grid_y0": 397.0, "grid_y1": 411.0,
        "grid_x0": 163.0, "box_w": 5.5, "gap": 1.4, "count": 12,
    },
    "pan_number": {
        "wipe": (290.8, 397.1, 554.9, 412.4),
        "grid_y0": 397.0, "grid_y1": 411.0,
        "grid_x0": 290.8, "box_w": 20.0, "gap": 4.0, "count": 10,
    },
    "initial_deposit": {
        "wipe": (281.2, 473.3, 554.9, 488.6),
        "grid_y0": 473.0, "grid_y1": 487.0,
        "grid_x0": 281.2, "box_w": 22.0, "gap": 5.0, "count": 9,
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

    # Render a preview PNG for visual review.
    doc2 = fitz.open(out_path)
    pix = doc2[0].get_pixmap(matrix=fitz.Matrix(200 / 72.0, 200 / 72.0))
    preview_path = out_path.with_suffix(".png")
    pix.save(preview_path)
    print("Preview:", preview_path)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "boxed_form_preview.pdf"
    build(out)
