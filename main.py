import os
import sys
from datetime import datetime
from colorama import Fore, Style, init
from phone_intel import analyze_phone
from username_search import search_username, PLATFORMS, PHONE_PLATFORMS
from email_intel import analyze_email, extract_username_from_email
from fraud_db import check_fraud_db, report_fraud, get_fraud_stats
from reporter import generate_html_report
from ghana_records import search_ghana_records

init(autoreset=True)

def print_banner():
    print(Fore.CYAN + """
╔══════════════════════════════════════════════════════╗
║          GhanaOSINT — Intelligence Tool              ║
║          MoMo Fraud Investigation & OSINT            ║
║          For authorized and ethical use only         ║
╚══════════════════════════════════════════════════════╝
""")

def calculate_risk_score(results):
    score = 0
    if results.get("fraud_check", {}).get("found"):
        score += results["fraud_check"]["risk_score"]
    if results.get("email_info", {}).get(
            "domain_info", {}).get("disposable"):
        score += 40
    if results.get("email_info", {}).get(
            "breach_info", {}).get("breached"):
        score += 20
    return min(100, score)

def generate_google_dorks(name):
    import urllib.parse
    encoded = urllib.parse.quote('"' + name + '"')
    dorks = [
        {
            "description": "Facebook profile",
            "url": "https://www.google.com/search?q=site:facebook.com+" + encoded
        },
        {
            "description": "Instagram profile",
            "url": "https://www.google.com/search?q=site:instagram.com+" + encoded
        },
        {
            "description": "Twitter/X profile",
            "url": "https://www.google.com/search?q=site:twitter.com+" + encoded
        },
        {
            "description": "TikTok profile",
            "url": "https://www.google.com/search?q=site:tiktok.com+" + encoded
        },
        {
            "description": "LinkedIn profile",
            "url": "https://www.google.com/search?q=site:linkedin.com+" + encoded
        },
        {
            "description": "YouTube channel",
            "url": "https://www.google.com/search?q=site:youtube.com+" + encoded
        },
        {
            "description": "Any social media",
            "url": "https://www.google.com/search?q=" + encoded + "+ghana+social+media"
        },
        {
            "description": "News articles",
            "url": "https://www.google.com/search?q=" + encoded + "+ghana"
        },
        {
            "description": "Phone number linked",
            "url": "https://www.google.com/search?q=" + encoded + "+0244+OR+0554+OR+0200+ghana"
        },
        {
            "description": "Business listing",
            "url": "https://www.google.com/search?q=" + encoded + "+ghana+business"
        },
    ]
    print(Fore.YELLOW + "\n[*] Open these links to search manually:")
    print(Fore.WHITE + "-" * 50)
    for d in dorks:
        print(Fore.GREEN + "[→] " + d["description"])
        print(Fore.WHITE + "    " + d["url"])
    print(Fore.WHITE + "-" * 50)
    return dorks

def investigate_phone(phone):
    print(Fore.CYAN + "\n" + "="*50)
    print(Fore.CYAN + "PHONE NUMBER INVESTIGATION")
    print(Fore.CYAN + "="*50)

    results = {}
    phone_info = analyze_phone(phone)
    results["phone_info"] = phone_info

    fraud_check = check_fraud_db(phone, "reported_number")
    results["fraud_check"] = fraud_check

    search_profiles = input(
        "\nSearch social media for this number? (y/n): "
    ).strip().lower()

    if search_profiles == "y":
        profiles = search_username(phone, PHONE_PLATFORMS)
        results["social_profiles"] = profiles
    else:
        results["social_profiles"] = []

    print(Fore.CYAN + "\n[*] Generating Google search links...")
    google_links = generate_google_dorks(phone)
    results["google_dorks"] = google_links

    results["overall_risk_score"] = calculate_risk_score(results)
    return results, phone, "Phone Number"

def investigate_email(email):
    print(Fore.CYAN + "\n" + "="*50)
    print(Fore.CYAN + "EMAIL INVESTIGATION")
    print(Fore.CYAN + "="*50)

    results = {}
    email_info = analyze_email(email)
    results["email_info"] = email_info

    fraud_check = check_fraud_db(email, "reported_email")
    results["fraud_check"] = fraud_check

    username = extract_username_from_email(email)
    search_term = username

    print(Fore.CYAN + "\n[*] Searching social media for username: " +
          search_term)
    profiles = search_username(search_term)
    results["social_profiles"] = profiles

    print(Fore.CYAN + "\n[*] Generating Google search links...")
    google_links = generate_google_dorks(email)
    results["google_dorks"] = google_links

    results["overall_risk_score"] = calculate_risk_score(results)

    if profiles:
        print(Fore.YELLOW + "\n" + "="*50)
        print(Fore.YELLOW + "⚠️  REMINDER")
        print(Fore.YELLOW + "="*50)
        print(Fore.WHITE + "Found " + str(len(profiles)) +
              " profiles for: " + email)
        print(Fore.WHITE + "If this person is a scammer,")
        print(Fore.WHITE + "please report using option 4.")
        print(Fore.YELLOW + "="*50)

    return results, email, "Email Address"

def investigate_username(username):
    print(Fore.CYAN + "\n" + "="*50)
    print(Fore.CYAN + "USERNAME INVESTIGATION")
    print(Fore.CYAN + "="*50)

    results = {}
    fraud_check = check_fraud_db(username, "reported_name")
    results["fraud_check"] = fraud_check

    if " " in username.strip():
        print(Fore.YELLOW + "\n[*] Name contains spaces.")
        print(Fore.YELLOW + "[*] Social media usernames don't use spaces.")
        print(Fore.WHITE + "\nHow should we search this name?")
        print("1. Remove spaces  → " + username.replace(" ", ""))
        print("2. Use underscores → " + username.replace(" ", "_"))
        print("3. Search as-is   → " + username)

        fmt = input("\nChoice (1/2/3): ").strip()
        if fmt == "1":
            search_term = username.replace(" ", "")
        elif fmt == "2":
            search_term = username.replace(" ", "_")
        else:
            search_term = username
    else:
        search_term = username

    print(Fore.CYAN + "\n[*] Searching for: " + search_term)
    profiles = search_username(search_term)
    results["social_profiles"] = profiles

    print(Fore.CYAN + "\n[*] Generating Google search links...")
    google_links = generate_google_dorks(username)
    results["google_dorks"] = google_links

    results["overall_risk_score"] = calculate_risk_score(results)

    if profiles:
        print(Fore.YELLOW + "\n" + "="*50)
        print(Fore.YELLOW + "⚠️  REMINDER")
        print(Fore.YELLOW + "="*50)
        print(Fore.WHITE + "Found " + str(len(profiles)) +
              " profiles for: " + username)
        print(Fore.WHITE + "If this person is a scammer or fraudster,")
        print(Fore.WHITE + "please report them using option 4.")
        print(Fore.YELLOW + "="*50)

    return results, username, "Username/Name"

def investigate_ghana_records(query):
    print(Fore.CYAN + "\n" + "="*50)
    print(Fore.CYAN + "GHANA PUBLIC RECORDS SEARCH")
    print(Fore.CYAN + "="*50)

    ghana_results = search_ghana_records(query)

    results = {
        "overall_risk_score": 0,
        "fraud_check": {
            "found": False,
            "risk_score": 0,
            "report_count": 0,
            "verdict": "Clean"
        },
        "ghana_records": ghana_results,
        "google_dorks": generate_google_dorks(query)
    }

    return results, query, "Ghana Public Records"

def report_fraud_menu():
    print(Fore.CYAN + "\n" + "="*50)
    print(Fore.CYAN + "REPORT FRAUD")
    print(Fore.CYAN + "="*50)

    print("\nWhat are you reporting?")
    print("1. Phone number")
    print("2. Email address")
    print("3. Name")

    choice = input("Choice (1-3): ").strip()
    types = {
        "1": "reported_number",
        "2": "reported_email",
        "3": "reported_name"
    }
    id_type = types.get(choice, "reported_number")
    labels = ["phone", "email", "name"]
    label = labels[int(choice)-1] if choice in ["1","2","3"] else "identifier"

    identifier = input("Enter the " + label + ": ").strip()

    print("\nScam type:")
    print("1. MoMo reversal scam")
    print("2. Fake prize/winning")
    print("3. Fake agent/official")
    print("4. Job scam")
    print("5. Other")

    scam_choice = input("Choice (1-5): ").strip()
    scam_types = {
        "1": "MoMo Reversal",
        "2": "Fake Prize",
        "3": "Impersonation",
        "4": "Job Scam",
        "5": "Other"
    }
    scam_type = scam_types.get(scam_choice, "Other")
    description = input("Brief description: ").strip()
    report_fraud(identifier, id_type, scam_type, description)

def main_menu():
    while True:
        print_banner()

        stats = get_fraud_stats()
        print(Fore.YELLOW + "Fraud Database: " +
              str(stats["total_reports"]) + " reports | " +
              str(stats["reported_numbers"]) + " numbers | " +
              str(stats["reported_emails"]) + " emails\n")

        print("What do you want to investigate?")
        print("1. Phone number (MoMo fraud check)")
        print("2. Email address")
        print("3. Username / Name")
        print("4. Report a fraud")
        print("5. Ghana Public Records (Police, Business, Court, News)")
        print("6. Exit")

        choice = input("\nEnter choice (1-6): ").strip()

        results = None
        query = ""
        query_type = ""

        if choice == "1":
            phone = input("\nEnter phone number: ").strip()
            results, query, query_type = investigate_phone(phone)

        elif choice == "2":
            email = input("\nEnter email address: ").strip()
            results, query, query_type = investigate_email(email)

        elif choice == "3":
            username = input("\nEnter username or name: ").strip()
            results, query, query_type = investigate_username(username)

        elif choice == "4":
            report_fraud_menu()
            input("\nPress Enter to continue...")
            continue

        elif choice == "5":
            query = input("\nEnter name, number or business to search: ").strip()
            results, query, query_type = investigate_ghana_records(query)

        elif choice == "6":
            print("Goodbye.")
            sys.exit(0)

        if results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_query = query.replace(
                "@", "_").replace(".", "_").replace("+", "")
            filename = "osint_" + clean_query + "_" + timestamp + ".html"

            generate_html_report(query, query_type, results, filename)

            print(Fore.CYAN + "\n" + "="*50)
            print(Fore.CYAN + "INVESTIGATION COMPLETE")
            print(Fore.CYAN + "="*50)
            print(Fore.WHITE + "Overall Risk Score: " +
                  str(results["overall_risk_score"]) + "/100")
            profiles = results.get("social_profiles", [])
            if profiles:
                print(Fore.GREEN + "Profiles found: " +
                      str(len(profiles)))
            print(Fore.GREEN + "Report: " + filename)

            input("\nPress Enter for main menu...")
            os.system("cls" if os.name == "nt" else "clear")

if __name__ == "__main__":
    main_menu()