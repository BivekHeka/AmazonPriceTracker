from bs4 import BeautifulSoup
import requests
import smtplib

MY_EMAIL = "bevillheka@gmail.com"
MY_PASSWORD = "oksfcveiwlghuikt"

practice_url = "https://appbrewery.github.io/instant_pot/"

# live_url = "https://www.amazon.com/dp/B075CYMYK6?psc=18ref_=cm_sw_r_cp_ud_ct_FM9M699VKHTT47YD50Q6"


response = requests.get(practice_url)

soup = BeautifulSoup(response.content, "html.parser")
# print(soup.prettify())


price = soup.find(class_ = "a-offscreen").get_text()


price_without_currency = price.split("$")[1]

price_as_float = float(price_without_currency)
print(price_as_float)



# SEND EMAIL 

# Get the product title
title = soup.find(id="productTitle").get_text().strip()
print(title) 

#Set the price below which you would like to get a notification
BUY_PRICE = 100

if price_as_float < BUY_PRICE:
    message = f"{title} is on sale for {price}"

    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        result = connection.login(MY_EMAIL,MY_PASSWORD)
        connection.sendmail(
            from_addr = MY_EMAIL,
            to_addrs = MY_EMAIL,
            msg= f"Subject: Amazon Price Alert! \n \n {message}\n{practice_url}".encode("utf-8")

        )