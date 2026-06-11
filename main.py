import os
import re
import requests
import smtplib
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Live Amazon Site
url = "https://www.amazon.com/dp/B075CYMYK6?psc=1&ref_=cm_sw_r_cp_ud_ct_FM9M699VKHTT47YD50Q6"

header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.5",
    "Dnt": "1",
    "Priority": "u=1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Sec-Gpc": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
}

response = requests.get(url, headers=header)
soup = BeautifulSoup(response.content, "html.parser")

title_element = soup.find(id="productTitle")

if title_element:
    title = " ".join(title_element.get_text().split())
    print(f"Product: {title}")

    # --- Robust Price Extraction Strategy ---
    price_as_float = None
    price_text = ""

    # Strategy 1: Try your original class
    price_element = soup.find(class_="a-offscreen")
    if price_element:
        price_text = price_element.get_text().strip()

    # Strategy 2: Fallback to whole + fraction classes
    if not price_text:
        whole_element = soup.find(class_="a-price-whole")
        fraction_element = soup.find(class_="a-price-fraction")
        if whole_element and fraction_element:
            price_text = f"{whole_element.get_text().strip()}{fraction_element.get_text().strip()}"

    # Strategy 3: Global Page Search Fallback (Finds any pattern like $79.99 or $79)
    if not price_text:
        # Search the entire raw text of the page for a standard dollar pattern
        page_text = soup.get_text()
        price_matches = re.findall(r"\$[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?", page_text)
        if price_matches:
            # Grab the first valid price pattern found on the page
            price_text = price_matches[0]

    print(f"Raw Price Found: '{price_text}'")

    # Parse out numbers using Regex
    if price_text:
        # Strip commas and find the raw float number
        price_match = re.search(r"([0-9]+(?:\.[0-9]+)?)", price_text.replace(",", ""))
        if price_match:
            price_as_float = float(price_match.group(1))
            print(f"Parsed Price: ${price_as_float}")

    # --- Process the Price Trigger ---
    if price_as_float is not None:
        BUY_PRICE = 80.00

        if price_as_float < BUY_PRICE:
            message = f"{title} is on sale for ${price_as_float}!"
            print("Target price hit! Attempting to send email...")

            try:
                with smtplib.SMTP(os.environ["SMTP_ADDRESS"], port=587) as connection:
                    connection.starttls()
                    connection.login(os.environ["EMAIL_ADDRESS"], os.environ["EMAIL_PASSWORD"])
                    
                    email_body = f"Subject:Amazon Price Alert!\n\n{message}\n\nBuy it here:\n{url}"
                    
                    connection.sendmail(
                        from_addr=os.environ["EMAIL_ADDRESS"],
                        to_addrs=os.environ["EMAIL_ADDRESS"],
                        msg=email_body.encode("utf-8")
                    )
                print("Email alert sent successfully!")
            except Exception as e:
                print(f"Failed to send email: {e}")
        else:
            print(f"Price (${price_as_float}) is still above your budget (${BUY_PRICE}). No email sent.")
    else:
        print("Error: Could not extract a valid price using any method.")
else:
    print("Error: Amazon blocked the request entirely (Captcha) or changed their HTML layout.")
    if soup.title:
        print(f"Page Title returned: {soup.title.text}")