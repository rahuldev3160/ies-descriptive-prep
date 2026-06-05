import re
import unicodedata

ABBREVIATION_MAP = {
    r"\bgdp\b": "gross domestic product",
    r"\bgnp\b": "gross national product",
    r"\bgva\b": "gross value added",
    r"\bgfcf\b": "gross fixed capital formation",
    r"\bcad\b": "current account deficit",
    r"\bfad\b": "food availability decline",
    r"\bwpi\b": "wholesale price index",
    r"\bcpi\b": "consumer price index",
    r"\breer\b": "real effective exchange rate",
    r"\bneer\b": "nominal effective exchange rate",
    r"\bfrbm\b": "fiscal responsibility and budget management",
    r"\bfci\b": "food corporation of india",
    r"\bnsdp\b": "net state domestic product",
    r"\bmrs\b": "marginal rate of substitution",
    r"\bmrt\b": "marginal rate of transformation",
    r"\bfit\b": "flexible inflation targeting",
    r"\bmpc\b": "monetary policy committee",
    r"\bcrr\b": "cash reserve ratio",
    r"\bslr\b": "statutory liquidity ratio",
    r"\bmsf\b": "marginal standing facility",
    r"\bnpa\b": "non performing asset",
    r"\bnpas\b": "non performing assets",
    r"\bfdi\b": "foreign direct investment",
    r"\bfii\b": "foreign institutional investor",
    r"\bfpi\b": "foreign portfolio investment",
    r"\bsei\b": "special economic zone",
    r"\bsez\b": "special economic zone",
    r"\bpsu\b": "public sector undertaking",
    r"\bibc\b": "insolvency and bankruptcy code",
    r"\bgstn\b": "goods and services tax network",
    r"\bgst\b": "goods and services tax",
    r"\bneft\b": "national electronic funds transfer",
    r"\brtgs\b": "real time gross settlement",
    r"\bupi\b": "unified payments interface",
    r"\bimf\b": "international monetary fund",
    r"\bwto\b": "world trade organisation",
    r"\bwb\b": "world bank",
    r"\badb\b": "asian development bank",
    r"\bsdg\b": "sustainable development goals",
    r"\bndc\b": "nationally determined contribution",
    r"\bniti\b": "national institution for transforming india",
}


def normalize(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    for pattern, expansion in ABBREVIATION_MAP.items():
        text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
    text = re.sub(r"[^\w\s\-']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
