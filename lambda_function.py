import yfinance as yf
import datetime
import boto3

faang_stocks = ['FB', 'AAPL', 'AMZN', 'MSFT', 'GOOGL']
max_percent_dip = 10.0
today_date = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5))).strftime('%Y-%m-%d')
five_days_ago_date = (datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5))) - datetime.timedelta(days=5)).strftime('%Y-%m-%d')
tomorrow_date = (datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5))) + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
email_sender = 'danny.balezy@gmail.com'
email_receivers = ['danny.balezy@gmail.com','danny.balezy@outlook.com']

ses = boto3.client('ses', region_name='us-east-1')

def lambda_handler(event, context):
    stock_dip_list = retrieve_stock_dip_list()
    if stock_dip_list:
        send_email(stock_dip_list)

def retrieve_stock_dip_list():
    stock_info_list = []
    for stock in faang_stocks:
        price_history = yf.download(stock, start=five_days_ago_date, end=tomorrow_date)
        stock_summary = yf.Ticker(stock).info['fiftyTwoWeekHigh']
        current_price = price_history['Adj Close'].iloc[-1]
        percent_dip = abs(current_price - stock_summary) / stock_summary * 100
        if percent_dip > max_percent_dip:
            stock_info_list.append({
                'ticker': stock,
                'currentPrice': current_price,
                'allTimeHigh': stock_summary,
                'percentDip': percent_dip
            })
    return stock_info_list

def send_email(stock_dip_list):
    subject = f"FAANG Stocks Dip More than {max_percent_dip} detected {today_date}"
    body = f"Below are the FAANG stocks that dip more than {max_percent_dip} from their 52-week high:\n\n{stock_dip_list}\n\n-from my lambda"

    params = {
        'Source': email_sender,
        'Destination': {
            'ToAddresses': email_receivers
        },
        'Message': {
            'Subject': {
                'Charset': 'UTF-8',
                'Data': subject
            },
            'Body': {
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': body
                }
            }
        }
    }

    try:
        response = ses.send_email(**params)
        print(f"Successfully sent email: {response}")
    except Exception as e:
        print(f"There is an error while sending emails: {e}")

if __name__ == "__main__":
    lambda_handler(None, None)
