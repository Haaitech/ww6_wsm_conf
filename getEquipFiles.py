import os
import json
from bs4 import BeautifulSoup

rawReceiver_list = []
receiver_list = []

baseDir = "/Users/tomhaaima/Desktop/senn_eqp_files/"

files = os.listdir(baseDir)

for file in files:
    with open(baseDir+file, "r") as eqpFile:
        eqpData = eqpFile.read()

    Bs_eqp_data = BeautifulSoup(eqpData, 'xml')

    model = Bs_eqp_data.find('model').contents[0].replace(' copy','').replace(' ','')
    band = Bs_eqp_data.find('band').contents[0].replace(' ','')
    start = Bs_eqp_data.find('start').contents[0]
    end = Bs_eqp_data.find('end').contents[0]


    receiver = {"model":model, "band":band, "start":start, "end":end}

    rawReceiver_list.append(receiver)


for item in rawReceiver_list:
    if not any(x['model'] == item['model'] for x in receiver_list):
        receiver = {'model':item['model'], "bands":{item['band']:{"start":item['start'], "end":item['end']}}}
        receiver_list.append(receiver)

    elif any(y['model'] == item['model'] for y in receiver_list):
        for receiver in receiver_list:
            if item['model'] == receiver['model']:
                band = {str(item['band']):{"start":item['start'], "end":item['end']}}
                receiver['bands'].update(band)
    else:
        print('something went wrong')



with open('receiver_list.json', 'w') as f:
    json.dump(receiver_list, f)
    

