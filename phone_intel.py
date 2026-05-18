import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import requests
import re
from datetime import datetime
from colorama import Fore, init

init(autoreset=True)

# ─── Ghana Network Prefixes ───────────────────────────────

GHANA_NETWORKS = {
    # MTN Ghana
    "020": "MTN Ghana",
    "024": "MTN Ghana",
    "054": "MTN Ghana",
    "055": "MTN Ghana",
    "059": "MTN Ghana",
    # Vodafone Ghana
    "020": "Vodafone Ghana",
    "050": "Vodafone Ghana",
    # AirtelTigo
    "026": "AirtelTigo",
    "027": "AirtelTigo",
    "056": "AirtelTigo",
    "057": "AirtelTigo",
    # Telecel
    "020": "Telecel Ghana",
    "030": "Telecel Ghana",
}

GHANA_NETWORK_PREFIXES = {
    "MTN Ghana":      ["020", "024", "054", "055", "059"],
    "Vodafone Ghana": ["050", "020"],
    "AirtelTigo":     ["026", "027", "056", "057"],
    "Telecel Ghana":  ["030", "031"],
    "Glo Ghana":      ["023", "028"],
}

# ─── Known Fraud Numbers Database ─────────────────────────

KNOWN_FRAUD_PATTERNS = [
    "prize", "won", "winning", "promo",
    "reverse", "refund", "mistake",
    "agent", "customer care", "block"
]

# ─── Phone Analysis ───────────────────────────────────────

def clean_phone(phone):
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    if cleaned.startswith("233"):
        cleaned = "0" + cleaned[3:]
    if cleaned.startswith("+233"):
        cleaned = "0" + cleaned[4:]
    return cleaned

def get_network(phone):
    cleaned = clean_phone(phone)
    prefix = cleaned[:3]
    for network, prefixes in GHANA_NETWORK_PREFIXES.items():
        if prefix in prefixes:
            return network
    return "Unknown Network"

def validate_ghana_number(phone):
    cleaned = clean_phone(phone)
    if len(cleaned) != 10:
        return False, "Invalid length (must be 10 digits)"
    if not cleaned.startswith("0"):
        return False, "Must start with 0"
    valid_prefixes = []
    for prefixes in GHANA_NETWORK_PREFIXES.values():
        valid_prefixes.extend(prefixes)
    if cleaned[:3] not in valid_prefixes:
        return False, "Unknown prefix: " + cleaned[:3]
    return True, "Valid Ghana number"

def format_international(phone):
    cleaned = clean_phone(phone)
    return "+233" + cleaned[1:]

def analyze_phone(phone):
    print(Fore.CYAN + "\n[*] Analyzing phone number: " + phone)
    results = {}

    cleaned = clean_phone(phone)
    results["original"] = phone
    results["cleaned"] = cleaned
    results["international"] = format_international(cleaned)

    valid, message = validate_ghana_number(cleaned)
    results["valid"] = valid
    results["validation_message"] = message

    if valid:
        network = get_network(cleaned)
        results["network"] = network
        results["momo_capable"] = True
        print(Fore.GREEN + "[+] Network: " + network)
        print(Fore.GREEN + "[+] MoMo capable: Yes")
        print(Fore.GREEN + "[+] International: " +
              results["international"])
    else:
        results["network"] = "Invalid"
        results["momo_capable"] = False
        print(Fore.RED + "[-] " + message)

    return results