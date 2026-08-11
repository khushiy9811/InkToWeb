import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = f"sqlite:///{BASE_DIR / 'inktoweb.db'}"

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-in-production-3f8a9c2e")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 12

# On Linux (Docker/deployed), `apt install tesseract-ocr` puts the binary on
# PATH as plain "tesseract" — prefer that if present. Falls back to the
# Windows install path for local dev, or TESSERACT_CMD to override either way.
TESSERACT_CMD = os.environ.get(
    "TESSERACT_CMD",
    shutil.which("tesseract") or r"C:\Program Files\Tesseract-OCR\tesseract.exe",
)

LOW_CONFIDENCE_THRESHOLD = 65.0

# TrOCR (torch + transformers) meaningfully improves handwriting accuracy
# but its baseline memory footprint alone exceeds free-tier hosting limits
# (512MB on Render) once loaded — set ENABLE_TROCR=false in a constrained
# deployment to fall back to Tesseract-only and stay within memory limits.
# torch/transformers are only actually imported when trocr_engine.recognize_batch
# is called (see ocr/trocr_engine.py), so leaving this off skips that import
# entirely rather than just skipping inference.
ENABLE_TROCR = os.environ.get("ENABLE_TROCR", "true").lower() == "true"

# Comma-separated list of allowed frontend origins, e.g.
# "https://inktoweb.vercel.app,http://localhost:5173"
CORS_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

# No SMTP/email-API credentials are configured yet, so OTP emails can't
# actually be sent. In dev mode the OTP is logged server-side and also
# returned in the signup/resend API response so the flow is fully testable
# end-to-end without an email account. Set EMAIL_DEV_MODE=false once real
# credentials are wired into app/email_service.py.
EMAIL_DEV_MODE = os.environ.get("EMAIL_DEV_MODE", "true").lower() == "true"
OTP_EXPIRE_MINUTES = 10
