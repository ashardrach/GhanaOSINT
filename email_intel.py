import re
import requests
import json
from colorama import Fore, init

init(autoreset=True)

# ─── Email Validation ─────────────────────────────────────

def validate_email(email):
    pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    return bool(pattern.match(email))

def extract_username_from_email(email):
    return email.split("@")[0]

def extract_domain_from_email(email):
    return email.split("@")[1]

# ─── Domain Intelligence ──────────────────────────────────

KNOWN_PROVIDERS = {
    "gmail.com":     "Google Gmail",
    "yahoo.com":     "Yahoo Mail",
    "outlook.com":   "Microsoft Outlook",
    "hotmail.com":   "Microsoft Hotmail",
    "live.com":      "Microsoft Live",
    "icloud.com":    "Apple iCloud",
    "protonmail.com":"ProtonMail (Privacy focused)",
    "tutanota.com":  "Tutanota (Privacy focused)",
    "yandex.com":    "Yandex Mail",
    "mail.com":      "Mail.com",
    "gmx.com":       "GMX Mail",
}

DISPOSABLE_DOMAINS = [
    "tempmail.com", "throwaway.email",
    "guerrillamail.com", "mailinator.com",
    "10minutemail.com", "sharklasers.com",
    "guerrillamailblock.com", "grr.la",
    "yopmail.com", "trashmail.com",
    "fakeinbox.com", "dispostable.com",
]

def analyze_email_domain(email):
    domain = extract_domain_from_email(email)
    results = {
        "domain": domain,
        "provider": "Unknown",
        "disposable": False,
        "suspicious": False
    }

    if domain in KNOWN_PROVIDERS:
        results["provider"] = KNOWN_PROVIDERS[domain]
    if domain in DISPOSABLE_DOMAINS:
        results["disposable"] = True
        results["suspicious"] = True
        print(Fore.RED + "[!] DISPOSABLE EMAIL DETECTED: " + domain)

    return results

# ─── Breach Check ─────────────────────────────────────────

def check_breach(email):
    print(Fore.CYAN + "\n[*] Checking breach databases...")
    results = {
        "breached": False,
        "breach_count": 0,
        "breaches": [],
        "note": ""
    }

    try:
        headers = {
            "User-Agent": "GhanaOSINT-Educational-Tool",
            "hibp-api-key": ""
        }
        url = "https://haveibeenpwned.com/api/v3/breachedaccount/" + email
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            breaches = response.json()
            results["breached"] = True
            results["breach_count"] = len(breaches)
            results["breaches"] = [b["Name"] for b in breaches]
            print(Fore.RED + "[!] Found in " +
                  str(len(breaches)) + " data breaches!")
            for breach in breaches[:5]:
                print(Fore.RED + "    - " + breach["Name"])
        elif response.status_code == 404:
            print(Fore.GREEN + "[+] Not found in known breaches.")
        elif response.status_code == 401:
            results["note"] = "HIBP API key required for full check."
            print(Fore.YELLOW + "[!] Breach check requires API key.")
            print(Fore.YELLOW + "    Visit: haveibeenpwned.com/API/Key")
        else:
            results["note"] = "Could not check breaches."

    except Exception as e:
        results["note"] = "Breach check failed: " + str(e)
        print(Fore.YELLOW + "[!] Could not check breaches: " + str(e))

    return results

# ─── Social Search by Email ───────────────────────────────

def search_email_social(email):
    username = extract_username_from_email(email)
    print(Fore.CYAN + "\n[*] Extracting username from email: " + username)
    return username

# ─── Full Email Analysis ──────────────────────────────────

def analyze_email(email):
    print(Fore.CYAN + "\n[*] Analyzing email: " + email)
    results = {}

    if not validate_email(email):
        print(Fore.RED + "[-] Invalid email format.")
        return {"error": "Invalid email format"}

    results["email"] = email
    results["username"] = extract_username_from_email(email)
    results["domain_info"] = analyze_email_domain(email)
    results["breach_info"] = check_breach(email)

    domain = results["domain_info"]["domain"]
    provider = results["domain_info"]["provider"]

    print(Fore.GREEN + "[+] Email valid: " + email)
    print(Fore.GREEN + "[+] Provider: " + provider)
    print(Fore.GREEN + "[+] Username to search: " + results["username"])

    if results["domain_info"]["disposable"]:
        print(Fore.RED + "[!] WARNING: Disposable email address detected!")
        print(Fore.RED + "[!] HIGH RISK — commonly used by scammers")

    return results