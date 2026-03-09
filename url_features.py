import math
from urllib.parse import urlparse

SUSPICIOUS_WORDS = [
    "login","verify","secure","account",
    "update","bank","paypal","password",
    "confirm","free","bonus","crypto"
]

POPULAR_BRANDS = [
    "google","paypal","facebook","amazon",
    "microsoft","apple","github"
]

SUSPICIOUS_TLDS = [
    "xyz","top","ru","tk","ml","ga"
]


def shannon_entropy(url):
    prob = [float(url.count(c)) / len(url) for c in dict.fromkeys(list(url))]
    entropy = - sum([p * math.log2(p) for p in prob])
    return entropy


def extract_features(url):

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    url_length = len(url)
    domain_length = len(domain)
    subdomains = domain.count('.') - 1

    letters = sum(c.isalpha() for c in url)
    digits = sum(c.isdigit() for c in url)
    hyphens = url.count('-')
    dots = url.count('.')

    # digits inside domain (important for typosquatting)
    domain_digits = sum(c.isdigit() for c in domain)

    at_symbol = 1 if '@' in url else 0
    double_slash = 1 if url.count('//') > 1 else 0

    letter_ratio = letters/url_length if url_length else 0
    digit_ratio = digits/url_length if url_length else 0

    suspicious_score = sum(word in url.lower() for word in SUSPICIOUS_WORDS)

    https = 1 if url.startswith("https") else 0

    entropy = shannon_entropy(url)

    long_subdomain = 1 if domain_length > 25 else 0

    # brand impersonation feature
    brand_flag = 0
    for brand in POPULAR_BRANDS:
        if brand in domain:
            brand_flag = 1

    # suspicious TLD feature
    tld = domain.split('.')[-1]
    suspicious_tld = 1 if tld in SUSPICIOUS_TLDS else 0

    return [
        url_length,
        domain_length,
        subdomains,
        letters,
        digits,
        hyphens,
        dots,
        domain_digits,
        at_symbol,
        double_slash,
        letter_ratio,
        digit_ratio,
        suspicious_score,
        https,
        entropy,
        long_subdomain,
        brand_flag,
        suspicious_tld
    ]