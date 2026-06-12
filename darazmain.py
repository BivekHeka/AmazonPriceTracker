import os
import re
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Import Selenium components to manage the browser session
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import smtplib

# Load environmental configs
current_directory = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_directory, '.env')
load_dotenv(dotenv_path=dotenv_path)

# Your target live product URL
url = "https://www.daraz.com.np/products/chrome-hearts-glasses-for-men-and-women-square-frame-transparent-sunglasses-stylish-daily-wear-eyewear-with-case-i512047018-s12336033366.html"

print("Launching background browser environment to bypass JavaScript blocking...")

# Setup hidden browser configurations
chrome_options = Options()
chrome_options.add_argument("--headless")  # Runs quietly in the background without opening a physical app window
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Initialize the automated web browser driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    driver.get(url)
    print("Page requested. Waiting 5 seconds for Daraz's interactive elements to load...")
    time.sleep(5)  # Crucial pause to allow dynamic prices to populate completely

    # Capture the completely rendered HTML source text from the active browser session
    rendered_html = driver.page_source
finally:
    driver.quit()  # Safely turn off the background browser engine

# Pass the fully loaded page content over to BeautifulSoup for pattern matching
soup = BeautifulSoup(rendered_html, "html.parser")

# Extract page title
title_element = soup.find("title")
if title_element:
    title = title_element.get_text().split("|")[0].strip()
else:
    title = "Chrome Hearts Glasses"

# Parse the text contents for price currency patterns
page_text = soup.get_text()
daraz_price_match = re.search(r"Rs\.\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?)", page_text)

if daraz_price_match:
    price_as_float = float(daraz_price_match.group(1).replace(",", ""))
    
    print("\n--- Live Data Extracted Successfully! ---")
    print(f"Product Title: {title}")
    print(f"Current Live Price: Rs. {price_as_float}")
    print("-------------------------------------------\n")
    
    BUY_PRICE = 1000.00  # Set your target baseline budget
    
    if price_as_float < BUY_PRICE:
        message = f"{title} is on sale for Rs. {price_as_float}!"
        print("Target budget matches. Activating mail server delivery sequence...")
        try:
            with smtplib.SMTP(os.environ["SMTP_ADDRESS"], port=587) as connection:
                connection.starttls()
                connection.login(os.environ["EMAIL_ADDRESS"], os.environ["EMAIL_PASSWORD"])
                
                email_body = f"Subject:Daraz Price Alert!\n\n{message}\n\nLink:\n{url}"
                connection.sendmail(
                    from_addr=os.environ["EMAIL_ADDRESS"],
                    to_addrs=os.environ["EMAIL_ADDRESS"],
                    msg=email_body.encode("utf-8")
                )
            print("Alert notice processed and sent!")
        except Exception as mail_err:
            print(f"Mail delivery issue: {mail_err}")
    else:
        print(f"Status: Price (Rs. {price_as_float}) remains above target threshold (Rs. {BUY_PRICE}).")

else:
    print("\nExtraction Failed.")
    print("The system dropped connection before values rendered, or the URL parameters expired.")