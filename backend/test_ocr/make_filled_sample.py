import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fitz
from PIL import Image, ImageDraw, ImageFont
import io

from app.ocr.template import TEXT_FIELDS, CHAR_BOX_FIELDS, CHECKBOX_GROUPS, SIGNATURE_BOX, PT_TO_PX

doc = fitz.open(r"K:\InkToWeb\bank_account_opening_form.pdf")
page = doc[0]
zoom = 200 / 72.0
pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("arial.ttf", 20)
except Exception:
    font = ImageFont.load_default()

sample_values = {
    "branch": "Delhi Main",
    "form_date": "10/08/2026",
    "father_spouse_name": "Suresh Sharma",
    "nationality": "Indian",
    "marital_status": "Married",
    "occupation": "Engineer",
    "annual_income": "850000",
    "address_line1": "42 MG Road",
    "address_line2": "Near City Mall",
    "city": "Delhi",
    "state": "Delhi",
    "email": "rohan.sharma@example.com",
    "id_proof_type": "Passport",
    "nominee_name": "Priya Sharma",
    "nominee_relationship": "Spouse",
    "place": "Delhi",
}

for field_name, value in sample_values.items():
    if field_name == "form_date":
        continue
    box = TEXT_FIELDS[field_name]["box"]
    x0, y0, x1, y1 = [c * PT_TO_PX for c in box]
    draw.text((x0 + 3, y0 + 1), value, fill=(10, 10, 120), font=font)

# Character-grid fields — write one glyph per box, like an employee filling
# in boxed cells by hand. A shorter value than the box count is normal
# (leaves trailing boxes blank).
char_box_values = {
    "full_name": "ROHAN SHARMA",
    "date_of_birth": "15061990",
    "mobile_number": "9876543210",
    "pin_code": "110001",
    "aadhaar_id_number": "123456789012",
    "pan_number": "ABCDE1234F",
    "initial_deposit": "50000",
}
try:
    char_font = ImageFont.truetype("arial.ttf", 14)
except Exception:
    char_font = ImageFont.load_default()
for field_name, value in char_box_values.items():
    boxes = CHAR_BOX_FIELDS[field_name]["boxes"]
    for ch, box in zip(value, boxes):
        if ch == " ":
            continue
        x0, y0, x1, y1 = [c * PT_TO_PX for c in box]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        draw.text((cx, cy), ch, fill=(10, 10, 120), font=char_font, anchor="mm")

# Top Date field is 8 individual boxes (DD boxes, MM boxes, YYYY boxes) -
# write one digit per box like a real employee filling the paper form.
date_digit_boxes = [
    [207.5, 76.0, 224.5, 93.0], [228.75, 76.0, 245.76, 93.0],
    [254.0, 76.0, 271.0, 93.0], [275.25, 76.0, 292.26, 93.0],
    [300.55, 76.0, 317.56, 93.0], [321.8, 76.0, 338.81, 93.0],
    [343.05, 76.0, 360.06, 93.0], [364.3, 76.0, 381.31, 93.0],
]
for digit, box in zip("10082026", date_digit_boxes):
    x0, y0, x1, y1 = [c * PT_TO_PX for c in box]
    draw.text((x0 + 12, y0 + 2), digit, fill=(10, 10, 120), font=font)

# Tick Gender=Female, Account Type=Current
for group_name, chosen in [("gender", "Female"), ("account_type", "Current")]:
    box = CHECKBOX_GROUPS[group_name]["options"][chosen]
    x0, y0, x1, y1 = [c * PT_TO_PX for c in box]
    draw.line([(x0 + 2, y0 + 2), (x1 - 2, y1 - 2)], fill=(0, 0, 0), width=3)
    draw.line([(x0 + 2, y1 - 2), (x1 - 2, y0 + 2)], fill=(0, 0, 0), width=3)

# Signature — a quick squiggle rather than real text, like a handwritten sign-off.
sx0, sy0, sx1, sy1 = [c * PT_TO_PX for c in SIGNATURE_BOX]
mid = sy0 + (sy1 - sy0) * 0.6
squiggle = [
    (sx0 + 5, mid), (sx0 + 20, sy0 + 3), (sx0 + 35, mid + 5),
    (sx0 + 50, sy0 + 5), (sx0 + 65, mid), (sx0 + 85, sy0 + 8),
]
draw.line(squiggle, fill=(10, 10, 120), width=2, joint="curve")

out_path = Path(__file__).resolve().parent / "filled_sample.png"
img.save(out_path)
print("Saved:", out_path)
