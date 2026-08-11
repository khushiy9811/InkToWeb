"""
Lazy-loaded TrOCR (handwriting-trained transformer OCR) engine.

Tesseract is fundamentally a printed-text engine and has a hard accuracy
ceiling on real cursive handwriting. TrOCR (microsoft/trocr-small-handwritten,
fine-tuned on the IAM handwriting dataset) reads a full text-line crop
directly and is used as an additional per-field candidate alongside
Tesseract in pipeline.py — whichever scores higher confidence wins.

Using the *small* checkpoint deliberately, not base/large: on CPU (no GPU
in this deployment) the base model's per-request latency was in the
multi-minute range, which made the review screen practically unusable.
Small trades some accuracy for roughly an order of magnitude faster
inference — combined with pipeline.py only invoking TrOCR for fields
Tesseract was already unsure about (see extract_form_fields), this keeps
extraction fast without giving up the accuracy win on messy handwriting.

The model (~130MB) downloads from Hugging Face on first use and is cached
under the local HF cache afterward (~/.cache/huggingface on this machine);
needs internet access once.
"""
import numpy as np

_processor = None
_model = None


def _load():
    global _processor, _model
    if _model is not None:
        return
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel

    _processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-handwritten")
    _model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-handwritten")
    _model.eval()


def recognize_batch(images_rgb: list) -> list:
    """Run TrOCR on a batch of single-text-line crops (RGB uint8 arrays) in
    one forward pass — much faster on CPU than one call per field. Returns
    a list of (text, confidence 0-100) aligned to the input order.
    Confidence is derived from the average per-token generation probability."""
    if not images_rgb:
        return []

    _load()
    import torch
    from PIL import Image

    pil_imgs = [Image.fromarray(img) for img in images_rgb]
    pixel_values = _processor(images=pil_imgs, return_tensors="pt").pixel_values

    with torch.no_grad():
        outputs = _model.generate(
            pixel_values,
            max_new_tokens=20,
            output_scores=True,
            return_dict_in_generate=True,
        )

    texts = _processor.batch_decode(outputs.sequences, skip_special_tokens=True)
    transition_scores = _model.compute_transition_scores(
        outputs.sequences, outputs.scores, normalize_logits=True
    )

    results = []
    for i, text in enumerate(texts):
        text = text.strip()
        scores = transition_scores[i]
        valid = scores[scores > -1e8]
        if len(valid) == 0 or not text:
            results.append((text, 0.0))
            continue
        avg_log_prob = valid.mean().item()
        confidence = round(min(99.0, max(0.0, float(np.exp(avg_log_prob)) * 100)), 1)
        results.append((text, confidence))
    return results
