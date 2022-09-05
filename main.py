from tda import auth,client
import json
import pandas as pd
from datetime import datetime
import TDAsecrets
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns



try:
    c = auth.client_from_token_file(TDAsecrets.token_path, TDAsecrets.api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome() as driver:
        c = auth.client_from_login_flow(
            driver, TDAsecrets.api_key, TDAsecrets.redirect_uri, TDAsecrets.token_path)

r = c.get_option_chain(symbol="SPY", contract_type=c.Options.ContractType.ALL,
                       exp_month=c.Options.ExpirationMonth.SEPTEMBER, strike_count=10)
assert r.status_code == 200, r.raise_for_status()

#How to get Raw JSON Dump data (tricky to view)
#print(json.dumps(r.json()['putExpDateMap'], indent=4))

#How to get option data in the JSON format
#r.json()['putExpDateMap']['2022-08-24:5']['422.0'][0]['openInterest'])

septExpiry = list(r.json()['callExpDateMap'].keys())

contractTypeList = ['callExpDateMap','putExpDateMap']
nearest5expiryList = septExpiry[:5]
strikeList = list(r.json()['callExpDateMap']['2022-09-06:1'])
volumeOI = ['totalVolume','openInterest']

index_1 = pd.MultiIndex.from_product([contractTypeList, nearest5expiryList,strikeList], names = ['call/put','date','strike'])
optionsDf = pd.DataFrame(index=index_1, columns=['openInterest','totalVolume'])

for a in contractTypeList:
    for b in nearest5expiryList:
        for c in list(r.json()[a][b]):
            for d in volumeOI:
                optionsDf.loc[(a,b,c),d] = r.json()[a][b][c][0][d]



f,a = plt.subplots(2,5,figsize=(20, 20))


for i,expiry in zip(range(0,5),nearest5expiryList):
    optionsDf.xs(('callExpDateMap',expiry)).plot(kind='bar',ax=a[0][i], color= ['blue','green'])
    a[0][i].get_legend().remove()
    a[0][i].set_title(expiry[0:10])
    optionsDf.xs(('putExpDateMap',expiry)).plot(kind='bar',ax=a[1][i], color= ['red','orange'])
    a[1][i].get_legend().remove()
    a[1][i].set_title(expiry[0:10])


f.legend(optionsDf.columns, loc='upper right',fontsize=15)
plt.legend(bbox_to_anchor=(1, 1), loc="upper left",fontsize=15)
plt.figure(figsize=(20, 20))
plt.subplots_adjust(left=0.2, bottom=0.4, right=0.7, top=0.8, wspace=1, hspace=0.5)
f.savefig('optionsDataSeptember.pdf',bbox_inches='tight')
plt.show()

if __name__ =="__main__":
    writer = pd.ExcelWriter('optionsDataSeptember.xlsx')
    optionsDf.to_excel(writer,'septemberOptions')
    writer.save()











