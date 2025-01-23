import cloudscraper
import requests
import json
from io import StringIO as sio
import pandas as pd
from bs4 import BeautifulSoup as bs
headers={
    "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4437.0 Safari/537.36 Edg/91.0.831.1",
    "Accept": "application/json, text/plain, */*",}
scraper = cloudscraper.create_scraper()

# %%
report_url="https://nepsealpha.com/financials-reports?fiscal_year=078-079&quater=1&symbol="
financial_url="https://nepsealpha.com/ajax/financials-menu/{}"
w_season_url="https://nepsealpha.com/seasonality/weekly/{}"
m_season_url="https://nepsealpha.com/seasonality/monthly/{}"
compare_url="https://nepsealpha.com/financials-screener/ajax?symbol_a=NICA&fiscal_year_a=77078&quater_a=3&symbol_b=NABIL&fiscal_year_b=77078&quater_b=3"
mf_list_url="https://nepsealpha.com/mutual-fund-navs"
mf_holding_url="https://nepsealpha.com/mutual-fund-navs/{}"
# %%
resp=scraper.get(mf_list_url,headers=headers).text

# %%
soup=bs(resp,"html.parser")
preloader = soup.find("div", id="preloader")
if preloader:
    preloader.decompose()
finder=soup.div
data=finder.get('data-page')
# %%
props=json.loads(data)["props"]
mflist=pd.DataFrame(props["navs_trends"])
mflist["created_at"]=mflist["created_at"].str[:10]
mflist["updated_at"]=mflist["updated_at"].str[:10]
mflist.set_index("symbol",inplace=True)
# %%
mflist1=pd.concat([mflist,pd.DataFrame.from_dict(props["pe_ratios"],orient="index")],axis=1)
mflist.rename(columns={mflist.columns[-1]: "pe_ratio"}, inplace=True)
# %%
##Mutual Fund Holding
def get_holding(symbol):
  holding_raw=scraper.get(mf_holding_url.format(symbol),headers=headers)
  df=pd.read_html(sio(holding_raw.text))[0]
  df["mf"]=symbol
  return df
df1=pd.DataFrame()
for ind in mflist.index:
  df1=pd.concat([df1,get_holding(ind)])
df1.to_csv("Mutual fund holding/"+df1.iloc[0,2],index=False)