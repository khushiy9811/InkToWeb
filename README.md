# InkToWeb — Bank Form Digitization System

A full-stack internal tool that digitizes handwritten (pen-filled) bank account
opening forms. A bank employee logs in, uploads a photo/scan of a filled paper
form, the system runs OCR against a known field template (including
checkbox/tick detection for Gender and Account Type), and shows the extracted
data on a review screen for the employee to verify and correct. Nothing is
written to the database until the employee explicitly confirms.

## Human-in-the-Loop, by design

OCR on handwriting is never 100% reliable — this system does not pretend
otherwise. Every extraction is treated as a **draft**, not a fact:

- Extracted values are shown next to the original scanned image so the
  employee can visually compare, not just trust.
- Each field carries a per-field confidence score. Fields below the
  confidence threshold (65%) are visually flagged (amber border + "⚠ Check"
  badge) so the employee's eye goes straight to what needs verifying.
- **The system never auto-saves OCR output.** A customer record is only
  created after the employee clicks "Confirm & Save" on the review screen.
  There is no code path that writes OCR output directly to the database.
- Editing a flagged field immediately marks it as reviewed (confidence →
  100%), so the UI reflects what a human has actually checked.

This is a deliberate reliability boundary, not a missing feature: OCR
proposes, a human disposes.

## Employee accounts & email verification

New employees can self-register from the landing page ("Create Account")
instead of only using the seeded admin login. Signup requires email
verification via a 6-digit OTP before the account can log in.

**No SMTP/email-API credentials are configured for this project**, so OTP
delivery currently runs in **dev mode**: the code is logged to the backend
console and also returned directly in the signup/resend API response, so the
verification screen can show it inline with a clearly labeled "Dev mode" banner.
This keeps the full signup → verify → login flow testable end-to-end without
needing a real mailbox. To wire up real email later, implement the body of
`send_otp_email()` in `backend/app/email_service.py` (SMTP via `smtplib`, or
an API like Resend/SendGrid) and set `EMAIL_DEV_MODE=false` — nothing else in
the flow needs to change.

## Tech Stack

- **Frontend:** React 19 (Vite), Tailwind CSS, React Router, Axios.
- **Backend:** FastAPI (Python), SQLAlchemy, Pydantic v2.
- **Database:** SQLite (file-based, zero setup for local/demo use — the
  SQLAlchemy models map cleanly onto Postgres if this needs to move to a
  shared environment later).
- **OCR:** Tesseract 5 via `pytesseract`, driven by a hand-built field
  template (`backend/app/ocr/template.py`) whose bounding boxes were
  extracted directly from `bank_account_opening_form.pdf`'s text/vector
  layout — not eyeballed.
- **Image processing:** OpenCV — deskew, per-field cropping, and ink-density
  based checkbox detection.
- **Auth:** bcrypt password hashing (via passlib) + JWT bearer tokens.
- **File storage:** uploaded form images are stored on local disk
  (`backend/uploads/`) with the path saved in the database — not as DB blobs.

## How the OCR pipeline works

1. **Normalize** — the uploaded photo/scan is deskewed (via `cv2.minAreaRect`
   on ink pixels) and resized to the template's standard page dimensions, so
   every field's known coordinates line up regardless of the source photo's
   resolution.
2. **Per-field cropping** — rather than OCR-ing the whole page, each of the
   ~24 fields is cropped individually using coordinates taken from the form
   PDF itself, then upscaled and binarized before running Tesseract on just
   that crop. This is significantly more accurate than whole-page OCR for a
   fixed-layout form.
3. **Checkbox detection** — Gender (Male/Female/Other) and Account Type
   (Savings/Current) are *not* read as text. Each checkbox's region is
   cropped, ink density inside the box is measured, and the option with the
   highest density above a threshold — with a healthy margin over the
   runner-up — is selected.
4. **Confidence scoring** — Tesseract's per-word confidence is averaged per
   field; checkbox confidence is derived from the ink-density margin between
   the winning option and the runner-up.
5. The result is returned as `{ field_name: { value, confidence } }` for the
   review screen — nothing is persisted at this stage.

## Project Structure

```
backend/
  app/
    main.py          FastAPI app, CORS, static file mount for /uploads
    models.py         SQLAlchemy models (employees, customers)
    schemas/          Pydantic request/response schemas
    auth.py            bcrypt + JWT
    routers/           auth, customers (CRUD), forms (upload/extract)
    ocr/
      template.py       Field bounding boxes (from the PDF template)
      pipeline.py        Preprocessing, OCR, checkbox detection
  seed.py               Seeds a default employee login
  test_ocr/             Synthetic filled-form generator for pipeline testing
frontend/
  src/
    pages/              Login, Dashboard, Upload, Review, CustomerDetail
    components/         Layout, FieldInput, ConfidenceBadge, ProtectedRoute
    context/            AuthContext (JWT session)
    fieldConfig.js       Shared field/section definitions (review + detail)
```

## Running locally

### Backend

```bash
cd backend
python -m venv venv
./venv/Scripts/pip install -r requirements.txt   # Windows
python seed.py                                    # creates admin / admin123
./venv/Scripts/python -m uvicorn app.main:app --reload
```

Requires [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
installed separately (the engine binary, not just the Python wrapper). The
backend looks for it at `C:\Program Files\Tesseract-OCR\tesseract.exe` by
default — override with the `TESSERACT_CMD` environment variable if it's
installed elsewhere.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Copy `.env.example` to `.env` if the backend isn't running on the default
`http://127.0.0.1:8000`.

### Demo login

```
username: admin
password: admin123
```

## Known limitations (v1)

- Field regions assume the uploaded image is a reasonably full, upright
  photo/scan of the form — there's no perspective/corner-detection warp yet,
  only deskew + resize. A form photographed at a sharp angle will misalign.
- Handwriting OCR accuracy on tightly-boxed fields (the DD/MM/YYYY date
  boxes) is the weakest part of the pipeline — this is exactly the kind of
  case the confidence-flagging system exists to catch.
- Single form template only (matches `bank_account_opening_form.pdf`), per
  the v1 scope in the project brief. Multi-template support is a stretch
  goal.
