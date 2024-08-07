import os
import pickle
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def check_and_navigate(driver, target_url):
    # Get the current URL
    current_url = driver.current_url
    
    # Compare the current URL with the target URL
    if current_url != target_url:
        # If they are different, navigate to the target URL
        driver.get(target_url)

def login(driver, email, password, timeout=10):
    check_and_navigate(driver, "https://www.linkedin.com/login")
    WebDriverWait(driver, 150).until(EC.presence_of_element_located((By.ID, "username")))

    email_elem = driver.find_element(By.ID, "username")
    email_elem.send_keys(email)

    password_elem = driver.find_element(By.ID, "password")
    password_elem.send_keys(password)
    password_elem.submit()

    # Check for the remember me prompt
    if driver.current_url == 'https://www.linkedin.com/checkpoint/lg/login-submit':
        try:
            remember = driver.find_element(By.ID, "remember-me-prompt__form-primary")
            if remember:
                remember.submit()
        except:
            pass

    # Wait for the main page to load
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, "global-nav__primary-link")))

def load_cookies(driver, cookies_file):
    try:
        if os.path.exists(cookies_file):
            # Check if the cookies file is older than one week
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cookies_file))
            if file_age > timedelta(weeks=1):
                os.remove(cookies_file)
                return False

        cookies = pickle.load(open(cookies_file, "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        return True
    except FileNotFoundError:
        return False

def save_cookies(driver, cookies_file):
    cookies = driver.get_cookies()
    with open(cookies_file, 'wb') as f:
        pickle.dump(cookies, f)

def linkedin_login(email, password, sandbox=False, cookies_file="cookies.pkl"):
    # Set driver path
    driver_path = "./chromedriver"

    # Make driver headless
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

    if(sandbox):
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    # Set driver path environment variable
    os.environ["webdriver.chrome.driver"] = driver_path

    # Create driver
    driver = webdriver.Chrome(options=options)

    # Navigate to LinkedIn before loading cookies
    check_and_navigate(driver, "https://www.linkedin.com")

    # Load cookies if they exist
    if load_cookies(driver, cookies_file):
        check_and_navigate(driver, "https://www.linkedin.com")
        # Wait to see if login was successful
        try:
            WebDriverWait(driver, 150).until(EC.presence_of_element_located((By.CLASS_NAME, "global-nav__primary-link")))
        except:
            # If not successful, login with credentials
            login(driver, email, password)
            save_cookies(driver, cookies_file)
    else:
        # Login with credentials and save cookies
        login(driver, email, password)
        save_cookies(driver, cookies_file)

    return driver

def fetch_user_location(driver, profile_url, timeout=10):
    check_and_navigate(driver, profile_url)
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ph5.pb5")))

    try:
        location_elem = driver.find_element(By.CSS_SELECTOR, "span.text-body-small.inline.t-black--light.break-words")
        location = location_elem.text
        return location
    except: 
        return None
    

def fetch_user_profile_image(driver, profile_url, timeout=10):
    check_and_navigate(driver, profile_url)
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ph5.pb5")))

    try:
        # Locate the profile image element
        profile_image_elem = driver.find_element(By.CSS_SELECTOR, "img.pv-top-card-profile-picture__image--show.ember-view")
        profile_image_url = profile_image_elem.get_attribute("src")
        return profile_image_url
    except:
        return None