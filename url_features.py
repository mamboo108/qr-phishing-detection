import re
import math
from urllib.parse import urlparse

SUSPICIOUS_WORDS = [
    "login","verify","secure","account",
    "update","bank","paypal","password",
    "confirm","free","bonus","crypto"
]

def shannon_entropy(url):
    prob = [float(url.count(c)) / len(url) for c in dict.fromkeys(list(url))]
    entropy = - sum([p * math.log2(p) for p in prob])
    return entropy

def extract_features(url):

    parsed = urlparse(url)
    domain = parsed.netloc

    url_length = len(url)
    domain_length = len(domain)
    subdomains = domain.count('.') - 1

    letters = sum(c.isalpha() for c in url)
    digits = sum(c.isdigit() for c in url)
    hyphens = url.count('-')
    dots = url.count('.')
    at_symbol = 1 if '@' in url else 0
    double_slash = 1 if url.count('//') > 1 else 0

    letter_ratio = letters/url_length if url_length else 0
    digit_ratio = digits/url_length if url_length else 0

    suspicious_score = sum(word in url.lower() for word in SUSPICIOUS_WORDS)

    https = 1 if url.startswith("https") else 0

    entropy = shannon_entropy(url)

    long_subdomain = 1 if domain_length > 25 else 0

    return [
        url_length,
        domain_length,
        subdomains,
        letters,
        digits,
        hyphens,
        dots,
        at_symbol,
        double_slash,
        letter_ratio,
        digit_ratio,
        suspicious_score,
        https,
        entropy,
        long_subdomain
    ]