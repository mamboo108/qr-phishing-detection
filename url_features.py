import math
from urllib.parse import urlparse

SUSPICIOUS_WORDS = ["login","verify","secure","account","update","bank","paypal","password","confirm"]

def shannon_entropy(url):
    if not url: return 0
    prob = [float(url.count(c)) / len(url) for c in dict.fromkeys(list(url))]
    return - sum([p * math.log2(p) for p in prob])

def extract_url_features(url):
    parsed = urlparse(str(url))
    domain = parsed.netloc.lower()
    url_str = str(url)
    url_len = len(url_str)
    
    letters = sum(c.isalpha() for c in url_str)
    digits = sum(c.isdigit() for c in url_str)
    entropy = shannon_entropy(url_str)

    return [
        url_len, len(domain), domain.count('.'), letters, digits, 
        url_str.count('-'), url_str.count('.'), sum(c.isdigit() for c in domain),
        1 if '@' in url_str else 0, 1 if url_str.count('//') > 1 else 0,
        letters/url_len if url_len > 0 else 0, digits/url_len if url_len > 0 else 0,
        sum(word in url_str.lower() for word in SUSPICIOUS_WORDS),
        1 if url_str.startswith("https") else 0, entropy, 
        1 if len(domain) > 25 else 0, 0
    ]