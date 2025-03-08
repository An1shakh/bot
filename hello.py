import time
import random
from collections import defaultdict
from playwright.sync_api import sync_playwright
import requests
from fake_useragent import UserAgent

# Telegram bot sozlamalari
TOKEN = "7999971239:AAFzmdISsmE79sWpQcHxxNWK9arxecKMmjU"
CHAT_ID = "7532592047"

# Proxy sozlamalari
USE_PROXY = True  # VPN ishlatayotgan bo‘lsangiz, False qiling

PROXIES = [
    "http://185.107.56.149:80",
    "http://135.125.234.187:3128",
    "http://51.83.135.206:8080",
    "http://51.15.87.152:7890",
]

ua = UserAgent()
visited_pages = defaultdict(int)  # Har bir sahifaga nechta bot kirganini saqlaydi
successful_visits = 0
active_bots = 0  # Hozirgi ishlayotgan botlar soni

def send_telegram_message(text):
    """Telegram bot orqali xabar yuboradi"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, json=payload)

def check_proxy(proxy):
    """Proxy ishlayotganini tekshiradi"""
    try:
        response = requests.get("https://www.google.com", proxies={"http": proxy, "https": proxy}, timeout=5)
        return response.status_code == 200
    except:
        return False

def get_working_proxy():
    """Ishlaydigan proxyni tanlaydi"""
    random.shuffle(PROXIES)
    for proxy in PROXIES:
        if check_proxy(proxy):
            return proxy
    return None

def visit_site():
    """Saytga tashrif buyurib, harakatlanadi"""
    global successful_visits, active_bots
    proxy = get_working_proxy() if USE_PROXY else None
    proxy_config = {"server": proxy} if proxy else None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, proxy=proxy_config)
        context = browser.new_context(user_agent=ua.random)
        page = context.new_page()

        try:
            page.goto("https://sangzor.uz", timeout=60000)
            time.sleep(random.uniform(5, 10))

            for _ in range(random.randint(3, 10)):
                page.mouse.wheel(0, random.randint(300, 800))
                time.sleep(random.uniform(2, 5))

            links = page.query_selector_all("a")
            if links:
                chosen_link = random.choice(links).get_attribute("href")
                if chosen_link:
                    page.goto(chosen_link, timeout=60000)
                    time.sleep(random.uniform(5, 15))
                    
                    visited_pages[chosen_link] += 1  # Ushbu sahifaga nechta bot kirganini hisoblash
                    successful_visits += 1
                    active_bots += 1

                    # Telegram xabar yuborish
                    send_telegram_message(
                        f"✅ {successful_visits}-bot tashrif buyurdi! \n"
                        f"🔹 Yangilik: {chosen_link}\n"
                        f"🔹 Shu sahifaga jami: {visited_pages[chosen_link]} bot tashrif buyurdi\n"
                        f"🔹 Hozirda ishlayotgan botlar soni: {active_bots}\n"
                        f"🔹 Jami tashriflar: {sum(visited_pages.values())}"
                    )
        except Exception as e:
            send_telegram_message(f"⚠️ Xatolik yuz berdi ({proxy}): {e}")
        finally:
            active_bots -= 1
            browser.close()

# Bitta botni ishga tushirish
visit_site()
