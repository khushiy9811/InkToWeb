"""
Third pass: makes every character-box field use ONE consistent box size
across the whole form (previously Aadhaar/mobile used much smaller boxes
than full_name/PAN/deposit — inconsistent). Also adds boxes to the address
lines, city, state, PIN code stays boxed, annual income, and email's
sibling (mobile) gets more room.

Rows that pair two fields side by side (Branch+Date, Nationality+Marital
Status, Occupation+Annual Income, City+State+PIN, Aadhaar+PAN,
Mobile+Email, Nominee Name+Relationship) are REBALANCED in place — the
shorter-value field's label shifts right to give the longer-value field
enough boxes — rather than adding new rows, so the form still fits one
page. Text widths are measured with PyMuPDF so nothing collides.

Email is deliberately left freeform (variable length + needs lowercase/
symbols, doesn't fit the uppercase-block-letter convention used
elsewhere) — its label just moves to make room for Mobile's boxes.

Run from backend/: python test_ocr/add_char_boxes_3.py
Writes a PREVIEW first; the source PDF is only overwritten after review.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fitz

SRC_PDF = Path(r"K:\InkToWeb\bank_account_opening_form.pdf")

BOX_STROKE = (0, 0, 0)
BOX_WIDTH = 0.6
FONT = "helv"
FONT_SIZE = 8.52
LABEL_COLOR = (0, 0, 0)

# One size for every character box on the whole form.
BOX_W = 13.0
BOX_H = 14.0
GAP = 2.5
PITCH = BOX_W + GAP


def char_boxes(x0, y0, y1, count):
    boxes = []
    x = x0
    for _ in range(count):
        boxes.append([round(x, 2), y0, round(x + BOX_W, 2), y1])
        x += PITCH
    return boxes


def label_width(page, text):
    return fitz.get_text_length(text, fontname=FONT, fontsize=FONT_SIZE)


def build(out_path: Path):
    doc = fitz.open(SRC_PDF)
    page = doc[0]

    def wipe(x0, y0, x1, y1, pad=0.5):
        page.draw_rect(fitz.Rect(x0 - pad, y0 - pad, x1 + pad, y1 + pad), color=None, fill=(1, 1, 1))

    def draw_label(text, x, y_baseline):
        page.insert_text((x, y_baseline), text, fontname=FONT, fontsize=FONT_SIZE, color=LABEL_COLOR)

    def draw_boxes(boxes):
        for b in boxes:
            page.draw_rect(fitz.Rect(*b), color=BOX_STROKE, width=BOX_WIDTH, fill=None)

    # ---- Full Name (own row, full width — re-box at the uniform size) ---
    wipe(126.1, 126.0, 554.9, 145.0)
    y0, y1 = 128.5, 142.5
    full_name_boxes = char_boxes(131.0, y0, y1, 26)
    draw_boxes(full_name_boxes)

    # ---- Date of Birth + Gender ------------------------------------------
    # DOB's 8 uniform boxes need more width than before, so Gender's label
    # and its 3 checkboxes (baked into the original page content) all shift
    # right to make room, rather than adding a new row.
    wipe(91.9, 169.0, 554.9, 195.0)
    y0, y1, baseline = 172.0, 186.0, 185.8
    dob_boxes = char_boxes(93.0, y0, y1, 8)
    draw_boxes(dob_boxes)

    GENDER_SHIFT = 31.0
    x = dob_boxes[-1][2] + 10
    draw_label("Gender:", x, baseline)
    checkbox_specs = [
        ("Male", 239.0, 178.8, 255.0, 193.8, 255.5, 273.3, 183.0, 192.5),
        ("Female", 278.5, 178.6, 294.6, 193.6, 293.6, 321.5, 182.1, 191.7),
        ("Other", 328.2, 177.7, 344.8, 193.3, 343.4, 364.7, 182.1, 191.7),
    ]
    for name, bx0, by0, bx1, by1, tx0, tx1, ty0, ty1 in checkbox_specs:
        nx0, nx1 = bx0 + GENDER_SHIFT, bx1 + GENDER_SHIFT
        page.draw_rect(fitz.Rect(nx0, by0, nx1, by1), color=BOX_STROKE, width=BOX_WIDTH, fill=None)
        draw_label(name, tx0 + GENDER_SHIFT + 3.0, ty1 - 0.9)

    # ---- Father's / Spouse's Name (own row, full width) ------------------
    wipe(142.0, 148.5, 554.9, 167.0)
    y0, y1 = 151.0, 165.0
    father_boxes = char_boxes(147.0, y0, y1, 24)
    draw_boxes(father_boxes)

    # ---- Row: Branch + Date -------------------------------------------
    # Original: "Branch:" 42.5-71.2 y[77.4,86.9]; "Date:" label 181.0-201.4,
    # existing 8 digit-boxes 207.5-381.3 y[76.0,93.0].
    wipe(71.2, 74.0, 554.9, 93.0)
    y0, y1, baseline = 76.0, 90.0, 86.9
    x = 76.0
    branch_boxes = char_boxes(x, y0, y1, 14)
    draw_boxes(branch_boxes)
    x = branch_boxes[-1][2] + 10
    draw_label("Date:", x, baseline)
    x += label_width(page, "Date:") + 6
    date_boxes = char_boxes(x, y0, y1, 8)
    draw_boxes(date_boxes)

    # ---- Row: Nationality + Marital Status ------------------------------
    # Original: "Nationality:" 42.5-84.5; "Marital Status:" 170.9-225.3;
    # row y[199.3,214.6].
    wipe(84.5, 197.0, 554.9, 216.0)
    y0, y1, baseline = 200.0, 214.0, 211.8
    x = 89.0
    nat_boxes = char_boxes(x, y0, y1, 11)
    draw_boxes(nat_boxes)
    x = nat_boxes[-1][2] + 14
    draw_label("Marital Status:", x, baseline)
    x += label_width(page, "Marital Status:") + 6
    marital_boxes = char_boxes(x, y0, y1, 11)
    draw_boxes(marital_boxes)

    # ---- Row: Occupation + Annual Income --------------------------------
    # Original: "Occupation:" 42.5-87.9; "Annual Income (Rs.):" 200.9-280.7;
    # row y[222.0,237.3].
    wipe(87.9, 219.5, 554.9, 239.0)
    y0, y1, baseline = 223.0, 237.0, 234.5
    x = 93.0
    occ_boxes = char_boxes(x, y0, y1, 13)
    draw_boxes(occ_boxes)
    x = occ_boxes[-1][2] + 14
    draw_label("Annual Income (Rs.):", x, baseline)
    x += label_width(page, "Annual Income (Rs.):") + 6
    income_boxes = char_boxes(x, y0, y1, 9)
    draw_boxes(income_boxes)

    # ---- Address Line 1 (own row, full width) ---------------------------
    wipe(146.0, 273.0, 554.9, 292.0)
    y0, y1 = 276.0, 290.0
    addr1_boxes = char_boxes(149.8, y0, y1, 26)
    draw_boxes(addr1_boxes)

    # ---- Address Line 2 (own row, full width) ---------------------------
    wipe(146.0, 295.7, 554.9, 315.0)
    y0, y1 = 299.0, 313.0
    addr2_boxes = char_boxes(149.8, y0, y1, 26)
    draw_boxes(addr2_boxes)

    # ---- Row: City + State + PIN Code -----------------------------------
    # Original: "City:" 42.5-59.6; "State:" 151.0-173.2; "PIN Code:" 260.9-300.2;
    # row y[320.9,336.2].
    wipe(59.6, 318.5, 554.9, 338.0)
    y0, y1, baseline = 321.0, 335.0, 333.4
    x = 63.8
    city_boxes = char_boxes(x, y0, y1, 11)
    draw_boxes(city_boxes)
    x = city_boxes[-1][2] + 14
    draw_label("State:", x, baseline)
    x += label_width(page, "State:") + 6
    state_boxes = char_boxes(x, y0, y1, 11)
    draw_boxes(state_boxes)
    x = state_boxes[-1][2] + 14
    draw_label("PIN Code:", x, baseline)
    x += label_width(page, "PIN Code:") + 6
    pin_boxes = char_boxes(x, y0, y1, 6)
    draw_boxes(pin_boxes)

    # ---- Row: Mobile Number + Email Address ------------------------------
    # Original: "Mobile Number:" 42.5-102.5; "Email Address:" 200.9-258.1;
    # row y[343.6,358.9]. Email stays freeform, just moves right.
    wipe(102.5, 341.0, 554.9, 361.0)
    y0, y1, baseline = 344.0, 358.0, 356.1
    x = 107.0
    mobile_boxes = char_boxes(x, y0, y1, 11)
    draw_boxes(mobile_boxes)
    x = mobile_boxes[-1][2] + 14
    draw_label("Email Address:", x, baseline)
    email_line_x0 = x + label_width(page, "Email Address:") + 6
    page.draw_line((email_line_x0, y1 - 1), (554.9, y1 - 1), color=(0, 0, 0), width=0.75)

    # ---- Row: Aadhaar + PAN No. ------------------------------------------
    # Original: "Aadhaar / National ID Number:" 42.5-163.0; "PAN No.:" 251.0-286.4;
    # row y[397.1,412.4]. Tightest row on the form.
    wipe(163.0, 394.5, 554.9, 414.0)
    y0, y1, baseline = 397.0, 411.0, 409.6
    x = 168.0
    aadhaar_boxes = char_boxes(x, y0, y1, 12)
    draw_boxes(aadhaar_boxes)
    x = aadhaar_boxes[-1][2] + 12
    draw_label("PAN No.:", x, baseline)
    x += label_width(page, "PAN No.:") + 6
    pan_boxes = char_boxes(x, y0, y1, 10)
    draw_boxes(pan_boxes)

    # ---- ID Proof Type (own row, full width) -----------------------------
    wipe(195.0, 417.5, 554.9, 437.0)
    y0, y1 = 420.0, 434.0
    idproof_boxes = char_boxes(200.0, y0, y1, 22)
    draw_boxes(idproof_boxes)

    # ---- Initial Deposit (shares row with Account Type checkboxes;
    # checkboxes untouched, deposit already has generous room) ------------
    # Original: "Initial Deposit (Rs.):" label ends 276.7, boxes to margin.
    wipe(278.0, 470.5, 554.9, 490.0)
    y0, y1 = 473.0, 487.0
    deposit_boxes = char_boxes(281.2, y0, y1, 18)
    draw_boxes(deposit_boxes)

    # ---- Nominee Name (own row, spread to the full row width — nominee
    # names can be long) ----------------------------------------------------
    wipe(104.0, 524.0, 554.9, 544.0)
    y0, y1 = 527.0, 541.0
    nominee_boxes = char_boxes(108.2, y0, y1, 28)
    draw_boxes(nominee_boxes)

    # ---- Shift DECLARATION heading + divider + paragraph down by 15pt to
    # make room for a Relationship row above (drawn after this, so its own
    # wipe/redraw isn't clobbered by this one). Runs before Relationship so
    # the two wipe regions don't touch each other's freshly-drawn ink.
    DECL_SHIFT = 15.0
    wipe(0, 561.0, 554.9, 592.0)
    page.insert_text(
        (42.48, 567.63 + DECL_SHIFT), "DECLARATION",
        fontname="hebo", fontsize=10.56, color=(0, 0, 0),
    )
    page.draw_line((42.5, 571.0 + DECL_SHIFT), (552.74, 571.0 + DECL_SHIFT), color=(0, 0, 0), width=1.0)
    page.insert_text(
        (42.5, 589.5 + DECL_SHIFT),
        "I hereby declare that the information provided above is true and correct to the best of my knowledge.",
        fontname=FONT, fontsize=FONT_SIZE, color=(0, 0, 0),
    )

    # ---- Relationship (own row below Nominee Name, above the now-shifted
    # DECLARATION heading) ---------------------------------------------------
    wipe(0, 543.0, 554.9, 561.0)
    y0, y1, baseline = 546.0, 560.0, 557.8
    draw_label("Relationship:", 42.5, baseline)
    x = 42.5 + label_width(page, "Relationship:") + 6
    relationship_boxes = char_boxes(x, y0, y1, 24)
    draw_boxes(relationship_boxes)

    # ---- Place (declaration row, already had ample room) -----------------
    wipe(256.3, 608.5, 554.9, 628.0)
    y0, y1 = 611.0, 625.0
    place_boxes = char_boxes(260.5, y0, y1, 19)
    draw_boxes(place_boxes)

    # ---- Signature Date (bottom "Date:" row — previously freeform and not
    # even captured by the OCR pipeline; DDMMYYYY, same style as the header
    # date field) -------------------------------------------------------------
    wipe(62.8, 634.5, 554.9, 654.0)
    y0, y1 = 637.0, 651.0
    sig_date_boxes = char_boxes(68.0, y0, y1, 8)
    draw_boxes(sig_date_boxes)

    doc.save(out_path)
    print("Saved:", out_path)

    doc2 = fitz.open(out_path)
    pix = doc2[0].get_pixmap(matrix=fitz.Matrix(200 / 72.0, 200 / 72.0))
    preview_path = out_path.with_suffix(".png")
    pix.save(preview_path)
    print("Preview:", preview_path)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "boxed_form_preview3.pdf"
    build(out)
