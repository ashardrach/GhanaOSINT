import requests
import threading
import time
from colorama import Fore, init

init(autoreset=True)

PLATFORMS = {
    # ── Reliably detectable ──
    "GitHub": {
        "url": "https://github.com/{username}",
        "not_found": ["not found", "this is not the web page"]
    },
    "Twitter/X": {
        "url": "https://twitter.com/{username}",
        "not_found": ["this account doesn't exist",
                      "page doesn't exist",
                      "this account has been suspended"]
    },
    "Telegram": {
        "url": "https://t.me/{username}",
        "not_found": ["if you have telegram", "a telegram",
                      "telegram web"]
    },
    "Snapchat": {
        "url": "https://www.snapchat.com/add/{username}",
        "not_found": ["page not found", "this page is unavailable",
                      "sorry, we couldn't find"]
    },
    "Pinterest": {
        "url": "https://www.pinterest.com/{username}/",
        "not_found": ["sorry, we couldn't find that page",
                      "user not found"]
    },
    "Reddit": {
        "url": "https://www.reddit.com/user/{username}/about.json",
        "not_found": ["\"error\": 404", "not found"]
    },
    "SoundCloud": {
        "url": "https://soundcloud.com/{username}",
        "not_found": ["we can't find that user", "404",
                      "page not found"]
    },
    "Last.fm": {
        "url": "https://www.last.fm/user/{username}",
        "not_found": ["page not found", "user not found"]
    },
    "Steam": {
        "url": "https://steamcommunity.com/id/{username}",
        "not_found": ["the specified profile could not be found",
                      "error", "no user"]
    },
    "Keybase": {
        "url": "https://keybase.io/{username}",
        "not_found": ["not found", "404"]
    },
    "Indie Hackers": {
        "url": "https://www.indiehackers.com/{username}",
        "not_found": ["page not found", "404",
                      "this user doesn't exist"]
    },
    "Ko-fi": {
        "url": "https://ko-fi.com/{username}",
        "not_found": ["page not found", "404",
                      "oops! we can't find",
                      "we can't find this profile",
                      "profile hasn't been turned off"]
    },
    "Anchor": {
        "url": "https://anchor.fm/{username}",
        "not_found": ["not found", "404"]
    },
    "Dev.to": {
        "url": "https://dev.to/{username}",
        "not_found": ["page not found", "404"]
    },
    "Medium": {
        "url": "https://medium.com/@{username}",
        "not_found": ["page not found", "404"]
    },
    "Hashnode": {
        "url": "https://hashnode.com/@{username}",
        "not_found": ["page not found", "404"]
    },
    "HackerNews": {
        "url": "https://news.ycombinator.com/user?id={username}",
        "not_found": ["no such user", "unknown"]
    },
    "CodePen": {
        "url": "https://codepen.io/{username}",
        "not_found": ["not found", "404"]
    },
    "Replit": {
        "url": "https://replit.com/@{username}",
        "not_found": ["not found", "404"]
    },
    "GitLab": {
        "url": "https://gitlab.com/{username}",
        "not_found": ["not found", "404"]
    },
    "Twitch": {
        "url": "https://www.twitch.tv/{username}",
        "not_found": ["sorry. unless you", "404"]
    },
    "Tumblr": {
        "url": "https://{username}.tumblr.com",
        "not_found": ["there's nothing here",
                      "whatever you were looking for"]
    },
    "WordPress": {
        "url": "https://{username}.wordpress.com",
        "not_found": ["doesn't exist", "no longer exists",
                      "coming soon", "cannot be registered",
                      "that site is reserved"]
    },
    "Substack": {
        "url": "https://{username}.substack.com",
        "not_found": ["this publication does not exist",
                      "not found"]
    },
    "Blogger": {
        "url": "https://{username}.blogspot.com",
        "not_found": ["blog not found", "sorry, the blog",
                      "doesn't exist"]
    },
    "Linktree": {
        "url": "https://linktr.ee/{username}",
        "not_found": ["page not found", "404", "doesn't exist"]
    },
    "Patreon": {
        "url": "https://www.patreon.com/{username}",
        "not_found": ["page not found", "404"]
    },
    "Product Hunt": {
        "url": "https://www.producthunt.com/@{username}",
        "not_found": ["page not found", "404"]
    },
    "Mastodon": {
        "url": "https://mastodon.social/@{username}",
        "not_found": ["not found", "404"]
    },
    "Letterboxd": {
        "url": "https://letterboxd.com/{username}/",
        "not_found": ["page not found", "404",
                      "there is no letterboxd member"]
    },
    "Wikipedia User": {
        "url": "https://en.wikipedia.org/wiki/User:{username}",
        "not_found": ["there is currently no text",
                      "this page does not exist"]
    },
    "Chess.com": {
        "url": "https://www.chess.com/member/{username}",
        "not_found": ["page not found", "404"]
    },
    "Lichess": {
        "url": "https://lichess.org/@/{username}",
        "not_found": ["page not found", "404"]
    },
    "Goodreads": {
        "url": "https://www.goodreads.com/{username}",
        "not_found": ["page not found", "404"]
    },
    "Quora": {
        "url": "https://www.quora.com/profile/{username}",
        "not_found": ["page not found", "404"]
    },
    "Fiverr": {
        "url": "https://www.fiverr.com/{username}",
        "not_found": ["this page is no longer available",
                      "404", "not found"]
    },
    "Kickstarter": {
        "url": "https://www.kickstarter.com/profile/{username}",
        "not_found": ["page not found", "404"]
    },
    "Etsy": {
        "url": "https://www.etsy.com/shop/{username}",
        "not_found": ["page not found", "404",
                      "sorry, this shop is no longer available"]
    },
    "AudioMack": {
        "url": "https://audiomack.com/{username}",
        "not_found": ["page not found", "404",
                      "this page doesn't exist"]
    },
    "Nairaland": {
        "url": "https://www.nairaland.com/{username}",
        "not_found": ["page not found", "404",
                      "invalid username"]
    },
    "Tonaton Ghana": {
        "url": "https://tonaton.com/en/user/{username}",
        "not_found": ["page not found", "404", "not found"]
    },
    "Jiji Ghana": {
        "url": "https://jiji.com.gh/users/{username}",
        "not_found": ["page not found", "404", "not found"]
    },
    "Behance": {
        "url": "https://www.behance.net/{username}",
        "not_found": ["page not found", "404"]
    },
    "Dribbble": {
        "url": "https://dribbble.com/{username}",
        "not_found": ["page not found", "404"]
    },
    "ArtStation": {
        "url": "https://www.artstation.com/{username}",
        "not_found": ["page not found", "404"]
    },
    "DeviantArt": {
        "url": "https://www.deviantart.com/{username}",
        "not_found": ["page not found", "404",
                      "this user does not exist"]
    },
    "Stack Overflow": {
        "url": "https://stackoverflow.com/users/{username}",
        "not_found": ["page not found", "does not exist"]
    },
    "Academia": {
        "url": "https://independent.academia.edu/{username}",
        "not_found": ["page not found", "404"]
    },
    "ResearchGate": {
        "url": "https://www.researchgate.net/profile/{username}",
        "not_found": ["page not found", "404"]
    },
    "Crunchbase": {
        "url": "https://www.crunchbase.com/person/{username}",
        "not_found": ["page not found", "404"]
    },
    "AngelList": {
        "url": "https://angel.co/u/{username}",
        "not_found": ["page not found", "404"]
    },
    "Clubhouse": {
        "url": "https://www.clubhouse.com/@{username}",
        "not_found": ["not found", "404", "user not found"]
    },
    "Flickr": {
        "url": "https://www.flickr.com/people/{username}",
        "not_found": ["page not found", "404", "uh oh!"]
    },
}

# ── Phone number specific platforms ──
PHONE_PLATFORMS = {
    "WhatsApp": {
        "url": "https://wa.me/{username}",
        "not_found": ["page not found", "invalid",
                      "phone number is not registered"]
    },
    "Telegram": {
        "url": "https://t.me/{username}",
        "not_found": ["if you have telegram",
                      "a telegram", "telegram web",
                      "open this link"]
    },
    "Snapchat": {
        "url": "https://www.snapchat.com/add/{username}",
        "not_found": ["page not found",
                      "this page is unavailable",
                      "sorry, we couldn't find"]
    },
    "Tonaton Ghana": {
        "url": "https://tonaton.com/en/user/{username}",
        "not_found": ["page not found", "404", "not found"]
    },
    "Jiji Ghana": {
        "url": "https://jiji.com.gh/users/{username}",
        "not_found": ["page not found", "404", "not found"]
    },
}

search_lock = threading.Lock()

def check_platform(platform_name, platform_data,
                   username, results):
    username = username.strip().replace(" ", "")
    url = platform_data["url"].replace("{username}", username)
    not_found_phrases = platform_data.get("not_found", [])

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,*/*"
        }
        response = requests.get(
            url, headers=headers,
            timeout=8, allow_redirects=True
        )

        if response.status_code == 404:
            return

        if response.status_code == 200:
            body = response.text.lower()
            for phrase in not_found_phrases:
                if phrase.lower() in body:
                    return

            with search_lock:
                results.append({
                    "platform": platform_name,
                    "url": url,
                    "status": response.status_code
                })
            print(Fore.GREEN + "[+] FOUND: " +
                  platform_name + " → " + url)

    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.ConnectionError:
        pass
    except Exception:
        pass

def search_username(username, platforms=None):
    if platforms is None:
        platforms = PLATFORMS

    print(Fore.CYAN + "\n[*] Searching " +
          str(len(platforms)) +
          " platforms for: " + username)
    print(Fore.YELLOW + "[*] Using smart verification " +
          "to reduce false positives...")
    print(Fore.YELLOW + "[*] This may take 2-4 minutes...\n")

    results = []
    threads = []

    for platform_name, platform_data in platforms.items():
        t = threading.Thread(
            target=check_platform,
            args=(platform_name, platform_data,
                  username, results)
        )
        threads.append(t)
        t.start()
        if len(threads) % 10 == 0:
            time.sleep(0.3)

    for t in threads:
        t.join()

    print(Fore.CYAN + "\n[*] Search complete.")
    print(Fore.GREEN + "[+] Found " + str(len(results)) +
          " verified profiles for: " + username)
    return results