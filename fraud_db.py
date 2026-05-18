import json
import os
from datetime import datetime
from colorama import Fore, init

init(autoreset=True)

FRAUD_DB_FILE = "ghana_fraud_db.json"

# ─── Load/Save Database ───────────────────────────────────

def load_fraud_db():
    if os.path.exists(FRAUD_DB_FILE):
        with open(FRAUD_DB_FILE, "r") as f:
            return json.load(f)
    return {
        "reported_numbers": {},
        "reported_emails": {},
        "reported_names": {},
        "total_reports": 0,
        "last_updated": str(datetime.now())
    }

def save_fraud_db(db):
    db["last_updated"] = str(datetime.now())
    with open(FRAUD_DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

# ─── Report Fraud ─────────────────────────────────────────

def report_fraud(identifier, id_type, scam_type,
                 description, reporter="anonymous"):
    db = load_fraud_db()
    timestamp = str(datetime.now())

    report = {
        "scam_type": scam_type,
        "description": description,
        "reporter": reporter,
        "timestamp": timestamp,
        "verified": False
    }

    key = id_type + "s"
    if identifier not in db[key]:
        db[key][identifier] = {
            "reports": [],
            "risk_score": 0,
            "first_reported": timestamp,
            "report_count": 0
        }

    db[key][identifier]["reports"].append(report)
    db[key][identifier]["report_count"] += 1
    db[key][identifier]["risk_score"] = min(
        100,
        db[key][identifier]["report_count"] * 20
    )
    db["total_reports"] += 1

    save_fraud_db(db)
    print(Fore.GREEN + "[+] Fraud report submitted.")
    print(Fore.GREEN + "[+] Risk score: " +
          str(db[key][identifier]["risk_score"]) + "/100")
    return db[key][identifier]

# ─── Check Fraud Database ─────────────────────────────────

def check_fraud_db(identifier, id_type):
    db = load_fraud_db()
    key = id_type + "s"

    if identifier in db.get(key, {}):
        entry = db[key][identifier]
        risk = entry["risk_score"]

        if risk >= 60:
            color = Fore.RED
            verdict = "HIGH RISK — Multiple fraud reports"
        elif risk >= 40:
            color = Fore.YELLOW
            verdict = "MEDIUM RISK — Fraud reports exist"
        else:
            color = Fore.YELLOW
            verdict = "LOW RISK — Few reports"

        print(color + "\n[!] FRAUD DATABASE HIT!")
        print(color + "    Reports: " +
              str(entry["report_count"]))
        print(color + "    Risk Score: " +
              str(risk) + "/100")
        print(color + "    Verdict: " + verdict)
        print(color + "    First reported: " +
              entry["first_reported"][:10])

        return {
            "found": True,
            "risk_score": risk,
            "report_count": entry["report_count"],
            "verdict": verdict,
            "reports": entry["reports"]
        }
    else:
        print(Fore.GREEN + "[+] Not in fraud database.")
        return {"found": False, "risk_score": 0}

# ─── Get Statistics ───────────────────────────────────────

def get_fraud_stats():
    db = load_fraud_db()
    return {
        "total_reports": db["total_reports"],
        "reported_numbers": len(db["reported_numbers"]),
        "reported_emails": len(db["reported_emails"]),
        "reported_names": len(db["reported_names"]),
        "last_updated": db["last_updated"]
    }