import re
import unicodedata

# ---------------- Yardımcılar ----------------
def _fold(text: str) -> str:
    """Büyük/küçük harf, aksan ve gizli karakter farklarını yok ederek karşılaştırmaya hazırlar."""
    text = re.sub(r"[\u200b-\u200f\u2060\ufeff]", "", text)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower().replace("ı", "i")
    return re.sub(r"\s+", " ", text)


# ---------------- Prompt Injection ----------------
# Not: Bu liste temel bir sezgisel (heuristic) filtredir; tek başına yeterli değildir.
INJECTION_PATTERNS = [
    (r"ignore (all |any |the |your )?(previous|prior|above|earlier|preceding) (instructions?|prompts?|rules?|directions?)",
     "Önceki talimatları yok sayma girişimi"),
    (r"disregard (all |any |the |your )?(previous |prior |above |earlier )?(instructions?|rules?|guidelines?)",
     "Talimatları göz ardı etme girişimi"),
    (r"(forget|override|bypass) (all |any |the |your )?(previous |prior |safety |security )?(instructions?|rules?|guidelines?|filters?|restrictions?)",
     "Kuralları atlatma girişimi"),
    (r"you are now (dan|an? (unrestricted|unfiltered|jailbroken)|in (developer|debug|god) mode)",
     "Rol değiştirme girişimi"),
    (r"\b(jailbreak|dan mode|developer mode|god mode)\b",
     "Jailbreak girişimi"),
    (r"(reveal|show|print|repeat|leak) (me )?(your |the )?(system|hidden|initial) (prompt|instructions?|message)",
     "Sistem istemini sızdırma girişimi"),
    # Türkçe (aksansız hale getirilmiş metne göre)
    (r"(onceki|yukaridaki|tum|butun) (talimat|komut|kural|yonerge)\w* (yok ?say|unut|gormezden gel|iptal et|gecersiz)\w*",
     "Önceki talimatları yok sayma girişimi (TR)"),
    (r"(talimat|komut|kural|yonerge)\w* (yok ?say|unut|gormezden gel|iptal et)\w*",
     "Kuralları yok sayma girişimi (TR)"),
    (r"(sistem|gizli|ilk) (istem|prompt|talimat|mesaj)\w* (goster|acikla|yaz|paylas|soyle)\w*",
     "Sistem istemini sızdırma girişimi (TR)"),
    (r"(guvenlik|kisitlama|filtre)\w* (kaldir|devre disi|kapat|atla)\w*",
     "Güvenlik filtresini devre dışı bırakma girişimi (TR)"),
    (r"artik (sen|bir) \w+ (gibi|olarak) (davran|cevap)\w*",
     "Rol değiştirme girişimi (TR)"),
    # Prompt ayraçlarını taklit etme
    (r"</?(kaynak|talimat)>", "Prompt ayraç etiketi enjeksiyonu"),
]
_COMPILED_INJECTION = [(re.compile(p), msg) for p, msg in INJECTION_PATTERNS]


def check_prompt_injection(text: str):
    """(tespit_edildi_mi, mesaj) döndürür."""
    folded = _fold(text or "")
    for pattern, msg in _COMPILED_INJECTION:
        if pattern.search(folded):
            return True, f"Güvenlik filtresi: {msg}"
    return False, ""


# ---------------- PII Maskeleme ----------------
def _luhn_valid(digits: str) -> bool:
    if not 13 <= len(digits) <= 19:
        return False
    total, alt = 0, False
    for ch in reversed(digits):
        d = int(ch)
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        alt = not alt
    return total % 10 == 0


def _tc_valid(digits: str) -> bool:
    if len(digits) != 11 or digits[0] == "0":
        return False
    d = [int(c) for c in digits]
    if ((sum(d[0:9:2]) * 7) - sum(d[1:8:2])) % 10 != d[9]:
        return False
    return sum(d[:10]) % 10 == d[10]


def mask_pii_data(text: str):
    """(maskelenmiş_metin, bulunan_tür_listesi) döndürür."""
    found = []

    def apply(pattern, label, validator=None, flags=0):
        nonlocal text

        def repl(m):
            raw = m.group(0)
            if validator and not validator(re.sub(r"\D", "", raw)):
                return raw
            if label not in found:
                found.append(label)
            return f"[{label}]"

        text = re.sub(pattern, repl, text, flags=flags)

    apply(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", "EMAIL")
    apply(r"\bTR\d{2}(?:\s?\d{4}){5}\s?\d{2}\b", "IBAN", flags=re.I)
    apply(r"(?<!\d)\d(?:[ -]?\d){12,18}(?!\d)", "KREDI_KARTI", validator=_luhn_valid)
    apply(r"(?<!\d)\d{11}(?!\d)", "TC_KIMLIK", validator=_tc_valid)
    apply(r"(?<!\d)(?:\+?90[\s-]?)?0?5\d{2}[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}(?!\d)", "TELEFON")
    return text, found