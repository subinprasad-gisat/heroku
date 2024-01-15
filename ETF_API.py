from flask import Flask, jsonify, request
import requests
import openai
import re
app = Flask(__name__)


open_apikey='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'
ytd_api_key = "7fd525b1eb69a710a24dd46dc1080e99"

def ytdName(name):
    api_key = open_apikey
    openai.api_key = api_key
    prompt_text = f"give TOP 3 alternatives of {name} ETF, strictly within the same sector as {name}, return the results as a list only and i need only ticker names"
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": "give ticker name only and consider the alternatives within the same sector"},
            {"role": "user", "content": prompt_text}
        ],
        temperature=0.1
    )
    generated_text = response['choices'][0]['message']['content']
    print(generated_text)
    matches = re.sub(r'\d+\.?', '', generated_text).split('\n')
    print(type(matches))
    return matches
 
 
 
def Sector(sector):
    api_key = open_apikey
    openai.api_key = api_key
    prompt_text = f"return only the sector name for {sector} ETF?"
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": "give the answer in the following format 'the name etf focuses on sector name'"},
            {"role": "user", "content": prompt_text}
        ],
        temperature=0.5
    )
    generated_text = response['choices'][0]['message']['content']
    pattern = r'(?<=focuses on the\s)(.*)'
    match = re.search(pattern, generated_text)

    return  match.group(1).capitalize()
 
def ytdValue(ytdName):
 
    url = f"https://financialmodelingprep.com/api/v3/stock-price-change/{ytdName}?apikey={ytd_api_key}"
    response = requests.get(url)
    return response.json()
 
def ytdDescription(ytdValue):
    api_key = "7fd525b1eb69a710a24dd46dc1080e99"
    url = f"https://financialmodelingprep.com/api/v3/profile/{ytdValue}?apikey={ytd_api_key}"
    response = requests.get(url)
    return response.json()
 
def etfname(userinput):
    api_key = "7fd525b1eb69a710a24dd46dc1080e99"
    url = f"https://financialmodelingprep.com/api/v3/search-name?query={userinput}&apikey={ytd_api_key}"
    response = requests.get(url)
    return response.json()



@app.route('/api/Etf', methods=['GET'])
def etf():
    data = []
    best_dict={}
    in_TickerName = request.args.get('TickerName')
    ytd_value =ytdValue(in_TickerName)[0]['1Y']
    YTD_percentage=str(ytd_value)+"%"
    ytd_ISIN = ytdDescription(in_TickerName.strip(" "))[0]['isin']
    ytd_Sector = Sector(in_TickerName)
    best_dict.update({in_TickerName:ytd_value})

    ticker_dict = {
                        "TickerName": in_TickerName,
                        "ISIN": ytd_ISIN,
                        "1YearPerformance": YTD_percentage,
                        "Sector": ytd_Sector,
                    }
    data.append(ticker_dict)

    ytdNames =  ytdName(in_TickerName)
    for name in ytdNames:
        ytd_value =ytdValue(name.strip(" "))[0]['1Y']
        YTD_percentage=str(ytd_value)+"%"
        ytd_Sector = Sector(name)
        ytd_description = ytdDescription(name.strip(" "))[0]['description']
        ytd_CompanyName = ytdDescription(name.strip(" "))[0]['companyName']   
        ytd_ISIN = ytdDescription(name.strip(" "))[0]['isin']
        ticker_dict = {
                        "TickerName": name.strip(" "),
                        "ISIN": ytd_ISIN,
                        "CompanyName": ytd_CompanyName,
                        "1YearPerformance": YTD_percentage,
                        "Sector": ytd_Sector,
                        "Description": ytd_description
                    }
        best_dict.update({name:ytd_value})
        data.append(ticker_dict)
    max_best= max(best_dict, key=lambda k: best_dict[k])
    data.append({
          "BestTickerName": max_best.strip(" "),
          "BestYTD":best_dict[max_best]
        })

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
