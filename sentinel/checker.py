from typing import Tuple

import requests
from requests import Response
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from sentinel.config import USER_AGENT


def check_link_with_requests(url: str, timeout: int, max_retries: int) -> Tuple[bool, str]:
    headers = {"User-Agent": USER_AGENT}
    attempts = max(1, max_retries + 1)
    last_error = ""

    for _ in range(attempts):
        try:
            response: Response = requests.head(
                url, allow_redirects=True, timeout=timeout, headers=headers
            )
            if response.status_code == 405:
                response = requests.get(
                    url, allow_redirects=True, timeout=timeout, headers=headers
                )
            if 200 <= response.status_code < 400:
                return True, ""
            last_error = f"status {response.status_code}"
        except requests.RequestException as exc:
            last_error = str(exc)
    return False, last_error


def init_selenium_driver(timeout: int) -> webdriver.Chrome | None:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--user-agent={USER_AGENT}")
    binary_location = "/usr/bin/chromium"
    options.binary_location = binary_location

    service = Service()  # System chromedriver in path
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(timeout)
        return driver
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[warn] Failed to start Selenium driver, browser fallback disabled: {exc}")
        return None


def check_link_with_browser(url: str, driver: webdriver.Chrome, timeout: int) -> Tuple[bool, str]:
    try:
        driver.set_page_load_timeout(timeout)
        driver.get(url)
        current_url = driver.current_url or ""
        if current_url.startswith("chrome-error://"):
            return False, "browser error page"
        title = driver.title or ""
        if title or len(driver.page_source) > 0:
            return True, ""
        return False, "empty page"
    except (TimeoutException, WebDriverException) as exc:
        return False, str(exc)
    except Exception as exc:  # pylint: disable=broad-except
        return False, str(exc)


def check_link_hybrid(
    url: str,
    driver: webdriver.Chrome | None,
    timeout: int,
    max_retries: int,
) -> Tuple[bool, str, str]:
    is_alive, error = check_link_with_requests(url, timeout, max_retries)
    if is_alive:
        return True, "requests", ""

    if driver:
        attempts = max(1, max_retries + 1)
        last_error = error
        for _ in range(attempts):
            alive, browser_error = check_link_with_browser(url, driver, timeout)
            if alive:
                return True, "browser", ""
            last_error = browser_error
        return False, "browser", last_error

    return False, "requests", error

