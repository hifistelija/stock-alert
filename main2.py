import requests
from twilio.rest import Client
import os
from twilio.http.http_client import TwilioHttpClient

proxy_client = TwilioHttpClient(proxy={'http': os.environ['http_proxy'],
                                       'https': os.environ['https_proxy']})

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
apikey = os.environ.get("apikey")
apikey_news = os.environ.get("apikey_news")

# Twilio API credentials
account_sid = os.environ.get("account_sid")
auth_token = os.environ.get("auth_token")
twilio_phone_number = os.environ.get("twilio_phone_number")
my_phone_number = os.environ.get("my_phone_number")

alphavantage_params = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK_NAME,
    "outputsize": "compact",
    "apikey": apikey
}

response = requests.get(STOCK_ENDPOINT, params=alphavantage_params)
data = response.json()["Time Series (Daily)"]

daily_data_list = [value for (key, value) in data.items()]
latest_data = daily_data_list[0]
latest_closing_price = float(latest_data["4. close"])
previous_data = daily_data_list[1]
previous_closing_price = float(previous_data["4. close"])

percentage_difference = ((latest_closing_price - previous_closing_price) / previous_closing_price) * 100

if percentage_difference > 5:
    newsapi_params = {
        "apikey": apikey_news,
        "qInTitle": COMPANY_NAME,
        "language": "en",
    }

    news_response = requests.get(NEWS_ENDPOINT, params=newsapi_params)
    news_response.raise_for_status()
    article = news_response.json()["articles"][0]["title"]

    # Send SMS using Twilio API
    client = Client(account_sid, auth_token, http_client=proxy_client)
    message = client.messages.create(
        body=
        f"{COMPANY_NAME}: {round(percentage_difference, 2)}%\n"
        f"Brief: {article}",
        from_=twilio_phone_number,
        to=my_phone_number
    )

    print(message.status)
