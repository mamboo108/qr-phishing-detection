import re
from urllib.parse import urlparse, parse_qs, unquote

HANDLES = {
    'okaxis': 'GPay (Axis Bank)',
    'okhdfcbank': 'GPay (HDFC Bank)',
    'okicici': 'GPay (ICICI Bank)',
    'oksbi': 'GPay (SBI)',
    'ybl': 'PhonePe (Yes Bank)',
    'ibl': 'PhonePe (IndusInd Bank)',
    'axl': 'PhonePe (Axis Bank)',
    'paytm': 'Paytm',
    'ptaxis': 'Paytm (Axis Bank)',
    'pthdfc': 'Paytm (HDFC Bank)',
    'upi': 'BHIM UPI',
    'bhim': 'BHIM',
    'apl': 'Amazon Pay',
    'abfspay': 'Aditya Birla Finance',
    'jupiteraxis': 'Jupiter',
    'icici': 'ICICI Bank',
    'hdfcbank': 'HDFC Bank',
    'sbi': 'State Bank of India',
    'allbank': 'Allahabad Bank',
    'aubank': 'AU Small Finance Bank',
    'idbi': 'IDBI Bank',
    'kotak': 'Kotak Mahindra Bank',
    'freecharge': 'Freecharge',
    'mobikwik': 'MobiKwik',
    'timecosmos': 'Timecosmos',
}

def analyze_upi(url):
    url = url.strip()
    upi_id = None
    name = None
    amount = None
    currency = "INR"
    note = None

    # Parse components
    if url.lower().startswith("upi://pay"):
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if 'pa' in params:
            upi_id = params['pa'][0]
        if 'pn' in params:
            name = params['pn'][0]
        if 'am' in params:
            amount = params['am'][0]
        if 'cu' in params:
            currency = params['cu'][0]
        if 'tn' in params:
            note = params['tn'][0]
    else:
        # Fallback to regex if standard URI scheme is missing
        match = re.search(r'[?&]pa=([^&]+)', url, re.IGNORECASE)
        if match:
            upi_id = unquote(match.group(1))

    # If we couldn't even extract a UPI ID
    if not upi_id:
        return {
            "status": "Safe Structure",
            "reason": "QR is a generic payment format but standard UPI ID could not be extracted.",
        }

    upi_details = {
        "id": upi_id,
        "name": name,
        "amount": amount,
        "currency": currency,
        "note": note,
        "provider": None
    }

    # Extract Handle Provider
    handle = upi_id.split('@')[-1].lower() if '@' in upi_id else None
    if handle:
        upi_details["provider"] = HANDLES.get(handle, None)

    # Discrepancy Checks
    if not name:
        return {
            "status": "Fake",
            "reason": f"Payment QR detected but Payee Name is MISSING. High risk of fraud.",
            "upi_details": upi_details
        }
        
    if not handle or '@' not in upi_id:
        return {
            "status": "Fake",
            "reason": f"Payment QR detected but Payee ID ({upi_id}) is malformed. Proceed with extreme caution.",
            "upi_details": upi_details
        }

    # Check for suspicious words in the note or name pretending to be a bank
    suspicious_keywords = ['cashback', 'refund', 'lucky', 'winner', 'support', 'helpdesk']
    note_lower = (note or "").lower()
    name_lower = (name or "").lower()
    
    for kw in suspicious_keywords:
        if kw in note_lower or kw in name_lower:
            return {
                "status": "Fake",
                "reason": f"Payment QR detected suspicious keyword '{kw}'. This may be a social engineering scam.",
                "upi_details": upi_details
            }
            
    # Optional WARNING for unknown handles
    if not upi_details["provider"]:
        return {
            "status": "Safe Structure",
            "reason": f"Valid UPI QR for {name}, but the handle '@{handle}' is not recognized. Verify before paying.",
            "upi_details": upi_details
        }
        
    return {
        "status": "Safe",
        "reason": f"Verified Payment QR for {name} ({upi_details['provider']}).",
        "upi_details": upi_details
    }
