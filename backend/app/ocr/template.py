"""
Field bounding-box template for bank_account_opening_form.pdf.

Coordinates are in PDF points, taken from the source-of-truth PDF at its
native page size. All boxes are [x0, y0, x1, y1] with y increasing
downward, matching PDF/image convention after rendering the page
top-left-origin.

Any uploaded image is normalized (deskewed + resized) to PAGE_SIZE_PT
scaled by RENDER_DPI before these boxes are applied.

The form template prints a per-character grid box for every field except
email (needs lowercase/symbols) and the signature (an inherently
free-form mark) — see CHAR_BOX_FIELDS. This is far more reliable to OCR
than a freeform line: a boxed character removes both segmentation
ambiguity and cursive joins, the two hardest parts of handwriting OCR.
Every box on the form is the same size for visual consistency; rows that
originally paired two fields side by side (e.g. Branch+Date) were
rebalanced in place — see backend/test_ocr/add_char_boxes_3.py, which
generated this layout — rather than adding new rows, so the form still
fits one page.
"""

PAGE_WIDTH_PT = 595.56
PAGE_HEIGHT_PT = 842.04

# DPI used to rasterize the normalized/template page. Field boxes below are
# defined in PDF points and converted to pixels using this DPI at OCR time.
RENDER_DPI = 200
PT_TO_PX = RENDER_DPI / 72.0

TEMPLATE_WIDTH_PX = round(PAGE_WIDTH_PT * PT_TO_PX)
TEMPLATE_HEIGHT_PX = round(PAGE_HEIGHT_PT * PT_TO_PX)

# Only email remains a freeform, whole-field OCR crop. Its label shifted
# right (to 289.0) to make room for Mobile Number's boxes on the same row,
# so the value line now starts further right too (was 262.4).
TEXT_FIELDS = {
    "email": {"box": [354.0, 344.0, 554.9, 358.0], "ocr_mode": "email"},
}


def _char_grid(x0, y0, y1, box_w, gap, count):
    """Generate `count` evenly-pitched [x0, y0, x1, y1] character boxes
    starting at x0, matching the grid drawn on the form template."""
    boxes = []
    x = x0
    for _ in range(count):
        boxes.append([round(x, 2), y0, round(x + box_w, 2), y1])
        x += box_w + gap
    return boxes


# One consistent box size for every character-grid field on the form.
_BOX_W = 13.0
_GAP = 2.5

# Per-character grid fields. ocr_mode here selects a single-character
# Tesseract whitelist (see pipeline._CHAR_WHITELIST) rather than a
# line-reading config — each box is OCR'd independently and concatenated.
# "text_char" fields treat a run of blank boxes as a single space; digit/
# alnum fields simply skip blanks (shorter values than the max box count
# are normal, e.g. a 5-digit deposit in an 18-box field).
CHAR_BOX_FIELDS = {
    "branch": {"boxes": _char_grid(76.0, 76.0, 90.0, _BOX_W, _GAP, 14), "ocr_mode": "text_char"},
    "form_date": {"boxes": _char_grid(326.86, 76.0, 90.0, _BOX_W, _GAP, 8), "ocr_mode": "digit_char"},
    "full_name": {"boxes": _char_grid(131.0, 128.5, 142.5, _BOX_W, _GAP, 26), "ocr_mode": "text_char"},
    "father_spouse_name": {"boxes": _char_grid(147.0, 151.0, 165.0, _BOX_W, _GAP, 24), "ocr_mode": "text_char"},
    "date_of_birth": {"boxes": _char_grid(93.0, 172.0, 186.0, _BOX_W, _GAP, 8), "ocr_mode": "digit_char"},
    "nationality": {"boxes": _char_grid(89.0, 200.0, 214.0, _BOX_W, _GAP, 11), "ocr_mode": "text_char"},
    "marital_status": {"boxes": _char_grid(331.45, 200.0, 214.0, _BOX_W, _GAP, 11), "ocr_mode": "text_char"},
    "occupation": {"boxes": _char_grid(93.0, 223.0, 237.0, _BOX_W, _GAP, 13), "ocr_mode": "text_char"},
    "annual_income": {"boxes": _char_grid(392.02, 223.0, 237.0, _BOX_W, _GAP, 9), "ocr_mode": "digit_char"},
    "address_line1": {"boxes": _char_grid(149.8, 276.0, 290.0, _BOX_W, _GAP, 26), "ocr_mode": "text_char"},
    "address_line2": {"boxes": _char_grid(149.8, 299.0, 313.0, _BOX_W, _GAP, 26), "ocr_mode": "text_char"},
    "city": {"boxes": _char_grid(63.8, 321.0, 335.0, _BOX_W, _GAP, 11), "ocr_mode": "text_char"},
    "state": {"boxes": _char_grid(274.06, 321.0, 335.0, _BOX_W, _GAP, 11), "ocr_mode": "text_char"},
    "pin_code": {"boxes": _char_grid(501.36, 321.0, 335.0, _BOX_W, _GAP, 6), "ocr_mode": "digit_char"},
    "mobile_number": {"boxes": _char_grid(107.0, 344.0, 358.0, _BOX_W, _GAP, 11), "ocr_mode": "digit_char"},
    "aadhaar_id_number": {"boxes": _char_grid(168.0, 397.0, 411.0, _BOX_W, _GAP, 12), "ocr_mode": "digit_char"},
    "pan_number": {"boxes": _char_grid(405.01, 397.0, 411.0, _BOX_W, _GAP, 10), "ocr_mode": "alnum_char"},
    "id_proof_type": {"boxes": _char_grid(200.0, 420.0, 434.0, _BOX_W, _GAP, 22), "ocr_mode": "text_char"},
    "initial_deposit": {"boxes": _char_grid(281.2, 473.0, 487.0, _BOX_W, _GAP, 18), "ocr_mode": "digit_char"},
    "nominee_name": {"boxes": _char_grid(108.2, 527.0, 541.0, _BOX_W, _GAP, 28), "ocr_mode": "text_char"},
    "nominee_relationship": {"boxes": _char_grid(97.75, 546.0, 560.0, _BOX_W, _GAP, 24), "ocr_mode": "text_char"},
    "place": {"boxes": _char_grid(260.5, 611.0, 625.0, _BOX_W, _GAP, 19), "ocr_mode": "text_char"},
    "signature_date": {"boxes": _char_grid(68.0, 637.0, 651.0, _BOX_W, _GAP, 8), "ocr_mode": "digit_char"},
}

# Signature capture region: the blank strip below "Applicant Signature:".
# Never OCR'd as text — cropped from the normalized *color* image and
# stored as a standalone snapshot so the employee can see the actual
# signature. Starts just after the (now shifted-down) declaration
# paragraph rather than the label row itself, so there's some headroom
# above the line for tall strokes/loops without capturing paragraph text.
SIGNATURE_BOX = [119.0, 606.0, 230.0, 636.0]

# Checkbox groups: crop box for each option, padded a couple points beyond
# the drawn/rendered square so ink extending past the border is still caught.
# Gender shifted +31pt right of its original position to make room for
# Date of Birth's wider uniform-size box grid on the same row.
CHECKBOX_GROUPS = {
    "gender": {
        "options": {
            "Male": [270.0, 178.8, 286.0, 193.8],
            "Female": [309.5, 178.6, 325.6, 193.6],
            "Other": [359.2, 177.7, 375.8, 193.3],
        },
        "field_name": "gender",
    },
    "account_type": {
        "options": {
            "Savings": [98.0, 477.2, 115.0, 493.0],
            "Current": [147.3, 477.2, 164.2, 493.0],
        },
        "field_name": "account_type",
    },
}

ALL_TEXT_FIELD_NAMES = list(TEXT_FIELDS.keys()) + list(CHAR_BOX_FIELDS.keys())
