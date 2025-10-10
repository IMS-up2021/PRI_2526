import urllib.parse
from decimal import Decimal, InvalidOperation
from urllib.parse import urljoin
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_price_by_isbn_from_directtextbook(isbn: str, timeout: int = 15):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0 Safari/537.36"
    ]

    opts = Options()
    opts.add_argument(f"user-agent={random.choice(user_agents)}")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1366,768")

    drv = webdriver.Chrome(options=opts)
    drv.set_page_load_timeout(timeout)

    try:
        url = f"https://www.directtextbook.com/isbn/{isbn}"
        drv.get(url)
        time.sleep(random.uniform(2, 5))

        # Find the first pricing-total-holder and get the h5 inside it
        holder = WebDriverWait(drv, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pricing-total-holder"))
        )
        h5_elem = holder.find_element(By.TAG_NAME, "h5")
        price_text = h5_elem.text.strip()
        return price_text
    except Exception:
        return None
    finally:
        try:
            drv.quit()
        except Exception:
            pass


def _fix_scientific_str(s: str) -> str:
    try:
        s = s.replace(',', '.') 
        d = Decimal(s)
        return str(int(d))
    except (InvalidOperation, ValueError, OverflowError):
        return s
    
