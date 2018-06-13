import csv
#from dotenv import load_dotenv
import json
import os
import pdb
import requests
import datetime
import sys
from operator import itemgetter


def parse_response(response_text):
    # response_text can be either a raw JSON string or an already-converted dictionary
    if isinstance(response_text, str): # if not yet converted, then:
        response_text = json.loads(response_text) # convert string to dictionary

    results = []
    time_series_daily = response_text["Time Series (Daily)"] #> a nested dictionary
    for trading_date in time_series_daily: # FYI: can loop through a dictionary's top-level keys/attributes
        #print(trading_date)
        prices = time_series_daily[trading_date] #> {'1. open': '101.0924', '2. high': '101.9500', '3. low': '100.5400', '4. close': '101.6300', '5. volume': '22165128'}
        result = {
            "date": trading_date,
            "open": prices["1. open"],
            "high": prices["2. high"],
            "low": prices["3. low"],
            "close": prices["4. close"],
            "volume": prices["5. volume"]
        }
        results.append(result)
    return results

def write_prices_to_file(prices,stock_name):
    filename="db/" + stock_name + ".csv"
    csv_filepath = os.path.join(os.path.dirname(__file__), "..", filename)
    with open(csv_filepath, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        for d in prices:
            row = {
                "timestamp": d["date"], # change attribute name to match project requirements 
                "open": d["open"],
                "high": d["high"],
                "low": d["low"],
                "close": d["close"],
                "volume": d["volume"]
            }
            writer.writerow(row)



if __name__ == '__main__': # only execute if file invoked from the command-line, not when imported into other files, like tests

    # load_dotenv() # loads environment variables set in a ".env" file, including the value of the ALPHAVANTAGE_API_KEY variable
    api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "OOPS. Please set an environment variable named 'ALPHAVANTAGE_API_KEY'."

    symbol = input("Please input the stock symbol, if you have more than one, please separate by space ")
    symbol_split = symbol.split()
    for stock_name in symbol_split:
        print("---------------------")
        print("processing " + stock_name)
        print("---------------------")
        if len(stock_name) <6 and len(stock_name)>0 and stock_name.isalpha():
            print("this is a valid input")
        else: 
            print("invalid input, please enter letters only")
            sys.exit()
        

        request_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + stock_name + "&apikey=" + api_key
        response = requests.get(request_url)
        # print(response.status_code)
        # print(response.text)
        # see: https://www.alphavantage.co/documentation/#daily

        # VALIDATE RESPONSE AND HANDLE ERRORS
        if "Error Message" in response.text:
            print("REQUEST ERROR, PLEASE TRY AGAIN. CHECK YOUR STOCK SYMBOL.")
            quit("Stopping the program")

        # PARSE RESPONSE (AS LONG AS THERE ARE NO ERRORS)
        daily_prices = parse_response(response.text)
        # print(daily_prices)

        # WRITE TO CSV
        write_prices_to_file(daily_prices, stock_name)

        # PERFORM CALCULATIONS
        # ... todo (HINT: use the daily_prices variable, and don't worry about the CSV file anymore :-)
        latest_closing_price = daily_prices[0]["close"] #> '361.4500'
        latest_closing_price = float(latest_closing_price)
        latest_closing_price_usd = "${0:,.2f}".format(latest_closing_price)

        print("stock: " + stock_name)
        now = datetime.datetime.now()
        print("Run on " + now.strftime("%B-%d-%Y %-I:%M %p")) 
        response_text = json.loads(response.text) 
        print("Latest Data from ", daily_prices[0]["date"])  
        print("Latest closing price is ", latest_closing_price_usd) 

        high = []
        low = []

        for day in daily_prices:
            high.append(day["high"])
            low.append(day["low"])
            
        average_high = max(high)
        average_low = min(low)

        average_high = float(average_high)
        average_high_string = "${0:,.2f}".format(average_high)
        average_low = float(average_low)
        average_low_string = "${0:,.2f}".format(average_low)
        threshold = average_low * 1.2
        threshold_string = "${0:,.2f}".format(threshold)
        
        print("Recent average high price is " +  average_high_string)
        print("Recent average low price is " + average_low_string)

        if threshold > latest_closing_price:
            print("We recommend you to buy because this stock's latest closing price is under the threshold " + threshold_string)
        else:
            print("We don't recommend you to buy because this stock's latest closing price exceeds the threshold " + threshold_string)
#     # PRODUCE FINAL RECOMMENDATION
#     # ... todo
	
#     # TODO: assemble the request url to get daily data for the given stock symbol

# # TODO: issue a "GET" request to the specified url, and store the response in a variable

# # TODO: parse the JSON response

# print(f"LATEST DAILY CLOSING PRICE FOR {symbol} IS: {latest_price_usd}")

