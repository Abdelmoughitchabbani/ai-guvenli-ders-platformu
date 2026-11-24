import io
from pypdf import PdfReader
from core.security import mask_pii_data, check_prompt_injection

def extract_and_sanitize_pdf(file_bytes: bytes) -> dict:
    """PDF baytlarini okur, metne donusturur ve guvenlik taramasindan gecirir."""
    pdf_file = io.BytesIO(file_bytes)
    reader = PdfReader(pdf_file)
    
    extracted_text = ""
    for page_idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        extracted_text += f"\n--- Sayfa {page_idx + 1} ---\n" + text

    # 1. Dokuman icinde Prompt Injection var mi?
    is_injection, msg = check_prompt_injection(extracted_text)
    
    # 2. Dokumandaki PII (Kisisel Verileri) maskele
    clean_text, masked_types = mask_pii_data(extracted_text)

    return {
        "raw_text": extracted_text,
        "clean_text": clean_text,
        "has_injection": is_injection,
        "injection_message": msg,
        "masked_pii": masked_types,
        "total_pages": len(reader.pages)
    }