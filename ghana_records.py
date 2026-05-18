import requests
from bs4 import BeautifulSoup
from datetime import datetime
from colorama import Fore, init

init(autoreset=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

# ─── Ghana Police Alerts ──────────────────────────────────

def get_police_alerts():
    print(Fore.CYAN + "\n[*] Checking Ghana Police Service alerts...")
    alerts = []

    sources = [
        {
            "name": "Ghana Police Service Website",
            "url": "https://police.gov.gh/en/press-releases/",
            "item_tag": "article",
            "title_tag": "h2",
            "link_tag": "a"
        },
        {
            "name": "Ghana Police Cyber Crime Unit",
            "url": "https://police.gov.gh/en/category/cybercrime/",
            "item_tag": "article",
            "title_tag": "h2",
            "link_tag": "a"
        }
    ]

    for source in sources:
        try:
            response = requests.get(
                source["url"],
                headers=HEADERS,
                timeout=10
            )
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                items = soup.find_all(source["item_tag"])[:5]
                for item in items:
                    title_tag = item.find(source["title_tag"])
                    link_tag = item.find(source["link_tag"], href=True)
                    if title_tag:
                        alerts.append({
                            "source": source["name"],
                            "title": title_tag.get_text().strip(),
                            "url": link_tag["href"] if link_tag else source["url"],
                            "type": "Police Alert"
                        })
                print(Fore.GREEN + "[+] " + source["name"] +
                      ": " + str(len(items)) + " alerts found")
            else:
                print(Fore.YELLOW + "[!] Could not reach: " +
                      source["name"])
        except Exception as e:
            print(Fore.YELLOW + "[!] Error: " + str(e))

    return alerts

# ─── Business Registry Check ──────────────────────────────

def check_business_registry(query):
    print(Fore.CYAN + "\n[*] Checking Ghana business registry...")
    results = []

    try:
        url = "https://www.rgd.gov.gh/search?q=" + query.replace(" ", "+")
        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            search_results = soup.find_all("div", class_="search-result")

            if not search_results:
                search_results = soup.find_all(
                    ["tr", "li", "div"],
                    string=lambda t: t and query.lower() in t.lower()
                )[:5]

            for result in search_results[:5]:
                text = result.get_text().strip()
                if text and query.lower() in text.lower():
                    results.append({
                        "source": "Ghana Registrar General",
                        "name": text[:100],
                        "url": url,
                        "type": "Business Registration"
                    })

            if results:
                print(Fore.GREEN + "[+] Found " +
                      str(len(results)) + " business records.")
            else:
                print(Fore.YELLOW + "[!] No business records found.")
                results.append({
                    "source": "Ghana Registrar General",
                    "name": "Search manually at rgd.gov.gh",
                    "url": "https://www.rgd.gov.gh/search?q=" +
                           query.replace(" ", "+"),
                    "type": "Manual Search Link"
                })
        else:
            print(Fore.YELLOW + "[!] Registry portal not accessible.")
            results.append({
                "source": "Ghana Registrar General",
                "name": "Search manually",
                "url": "https://www.rgd.gov.gh",
                "type": "Manual Search Link"
            })

    except Exception as e:
        print(Fore.YELLOW + "[!] Registry check failed: " + str(e))
        results.append({
            "source": "Ghana Registrar General",
            "name": "Visit rgd.gov.gh to search manually",
            "url": "https://www.rgd.gov.gh",
            "type": "Manual Search Link"
        })

    return results

# ─── Fraud News Search ────────────────────────────────────

def search_fraud_news(query):
    print(Fore.CYAN + "\n[*] Searching Ghana fraud news...")
    results = []

    news_sources = [
        {
            "name": "Ghana Web",
            "url": "https://www.ghanaweb.com/GhanaHomePage/NewsArchive/search.php?query=" +
                   query.replace(" ", "+") + "+fraud+scam"
        },
        {
            "name": "MyJoyOnline",
            "url": "https://www.myjoyonline.com/?s=" +
                   query.replace(" ", "+") + "+fraud"
        },
        {
            "name": "Graphic Online",
            "url": "https://www.graphic.com.gh/?s=" +
                   query.replace(" ", "+") + "+fraud"
        },
        {
            "name": "CitiNewsRoom",
            "url": "https://citinewsroom.com/?s=" +
                   query.replace(" ", "+") + "+fraud+scam"
        },
        {
            "name": "3News Ghana",
            "url": "https://3news.com/?s=" +
                   query.replace(" ", "+") + "+fraud"
        }
    ]

    for source in news_sources:
        try:
            response = requests.get(
                source["url"],
                headers=HEADERS,
                timeout=8
            )
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                articles = soup.find_all(
                    ["article", "h2", "h3"],
                    limit=3
                )
                found = 0
                for article in articles:
                    title = article.get_text().strip()
                    if (len(title) > 10 and
                            query.lower() in title.lower()):
                        link = article.find("a", href=True)
                        results.append({
                            "source": source["name"],
                            "title": title[:150],
                            "url": link["href"] if link else source["url"],
                            "type": "News Article"
                        })
                        found += 1

                if found:
                    print(Fore.GREEN + "[+] " + source["name"] +
                          ": " + str(found) + " articles found")
                else:
                    results.append({
                        "source": source["name"],
                        "title": "Search for '" + query +
                                 "' on " + source["name"],
                        "url": source["url"],
                        "type": "Search Link"
                    })
        except Exception as e:
            pass

    print(Fore.GREEN + "[+] News search complete. " +
          str(len(results)) + " results.")
    return results

# ─── Court Records ────────────────────────────────────────

def search_court_records(query):
    print(Fore.CYAN + "\n[*] Searching public court records...")
    results = []

    court_links = [
        {
            "source": "Ghana Judiciary",
            "url": "https://www.judicial.gov.gh/index.php/judgments?search=" +
                   query.replace(" ", "+"),
            "type": "Court Records"
        },
        {
            "source": "Ghana Law Hub",
            "url": "https://ghanalaw.com/?s=" +
                   query.replace(" ", "+"),
            "type": "Legal Records"
        }
    ]

    for court in court_links:
        try:
            response = requests.get(
                court["url"],
                headers=HEADERS,
                timeout=10
            )
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                items = soup.find_all(
                    ["tr", "li", "article", "h2", "h3"],
                    limit=5
                )
                found = 0
                for item in items:
                    text = item.get_text().strip()
                    if (query.lower() in text.lower() and
                            len(text) > 10):
                        link = item.find("a", href=True)
                        results.append({
                            "source": court["source"],
                            "title": text[:150],
                            "url": link["href"] if link else court["url"],
                            "type": court["type"]
                        })
                        found += 1

                if found:
                    print(Fore.GREEN + "[+] " + court["source"] +
                          ": " + str(found) + " records found")
                else:
                    results.append({
                        "source": court["source"],
                        "title": "Search manually for: " + query,
                        "url": court["url"],
                        "type": "Manual Search Link"
                    })
        except Exception as e:
            results.append({
                "source": court["source"],
                "title": "Visit manually to search",
                "url": court["url"],
                "type": "Manual Search Link"
            })

    return results

# ─── Full Ghana Records Search ────────────────────────────

def search_ghana_records(query):
    print(Fore.CYAN + "\n" + "="*50)
    print(Fore.CYAN + "GHANA PUBLIC RECORDS SEARCH")
    print(Fore.CYAN + "="*50)
    print(Fore.WHITE + "Query: " + query)

    all_results = {
        "police_alerts": get_police_alerts(),
        "business_registry": check_business_registry(query),
        "fraud_news": search_fraud_news(query),
        "court_records": search_court_records(query)
    }

    total = sum(len(v) for v in all_results.values())
    print(Fore.GREEN + "\n[+] Total records found: " + str(total))

    return all_results