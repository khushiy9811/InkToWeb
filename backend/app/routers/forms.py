import uuid
from pathlib import Path

import cv2
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.concurrency import run_in_threadpool

from .. import models, schemas, auth
from ..config import UPLOAD_DIR
from ..ocr.pipeline import load_as_image, extract_form_fields

router = APIRouter(prefix="/api/forms", tags=["forms"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}


@router.post("/extract", response_model=schemas.ExtractionResponse)
async def extract(
    file: UploadFile = File(...),
    current_employee: models.Employee = Depends(auth.get_current_employee),
):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Upload a JPG, PNG, or PDF.",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file upload.")

    try:
        # extract_form_fields is CPU-bound and takes tens of seconds (~230
        # Tesseract calls plus a TrOCR pass) — run it off the event loop so
        # a single in-flight extraction can't block every other request
        # (including login/health checks) on this single-worker server.
        img = load_as_image(file_bytes, file.filename or "upload" + suffix)
        fields, signature_crop = await run_in_threadpool(extract_form_fields, img)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"OCR extraction failed: {exc}")

    # Browsers can't render PDFs via <img>, and the review/detail screens
    # need to display the hard copy inline. Store the rasterized page as
    # the attachment for PDFs; keep the original bytes for JPG/PNG.
    if suffix == ".pdf":
        stored_name = f"{uuid.uuid4().hex}.png"
        stored_path = UPLOAD_DIR / stored_name
        cv2.imwrite(str(stored_path), img)
    else:
        stored_name = f"{uuid.uuid4().hex}{suffix}"
        stored_path = UPLOAD_DIR / stored_name
        stored_path.write_bytes(file_bytes)

    signature_name = f"{uuid.uuid4().hex}_signature.png"
    signature_path = UPLOAD_DIR / signature_name
    if signature_crop.size > 0:
        cv2.imwrite(str(signature_path), signature_crop)
        signature_url = f"/uploads/{signature_name}"
    else:
        signature_url = None

    return schemas.ExtractionResponse(
        fields=fields,
        image_path=f"/uploads/{stored_name}",
        signature_image_path=signature_url,
    )
