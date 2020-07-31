import requests
import json
import os
import sys
import argparse
import time
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('wsname')
args = parser.parse_args()
params = vars(args)

def getJenkinsNode(ip, authKey, projectId, wbmap, wsname, bnmap):
    getResourceUrl = 'http://{ip}:8085/api/v2/monitoring/resources'.format(ip=ip)
    getBenchStatus = 'http://{ip}:8085/api/v2/monitoring/testexecution'.format(ip=ip)
    getBenchHeartBeat = 'http://{ip}:8085/api/v2/monitoring/heartbeat'.format(ip=ip)
    params = {'projectId':projectId, 'authKey':authKey}
    benches = requests.get(getResourceUrl, params).json()
    avaBenches = loadJson(wbmap)[0][wsname]
    exeProgressDict = {}
    for bench in avaBenches:
        for b in benches:
            if bench in b.values():
                resourceId = benches[benches.index(b)] # type: Dict
        params.update(resourceId)
        online = requests.get(getBenchHeartBeat, params).json()['online']
        if online:
            exeInfo = requests.get(getBenchStatus, params).json()
            benchStatus = exeInfo['status']
            if benchStatus == 'IDLE':
                nodeLabel = loadJson(bnmap)[0][bench]
                return nodeLabel
            else:
                exeProgress = exeInfo['actual']/exeInfo['total']
                exeProgressDict[bench] = exeProgress
            
    idlestBench = list(exeProgressDict.keys())[list(exeProgressDict.values()).index(min(exeProgressDict.values()))]
    nodeLabel = loadJson(bnmap)[0][idlestBench]
    return nodeLabel

def loadJson(jsonPath):
    with open(jsonPath, 'r') as f:
        jsonContent = f.read()
    text = json.loads(jsonContent)
    return text

ip = '127.0.0.1'
bench_node = 'bench_node_mapping.json'
ws_bench = 'ws_bench_mapping.json'
authKey = 'paxAxunszIK1YjFegnHLIoYmAZGRFmdBZV0NsO-yJTbINMCbvYkPb34RLDAlgSqn4RksSoSYmdu3BXsJimbPR193YsgMzOBDfedQGVByruZhlhaTKP66OVCjeVN0FMCmftQLlSZKiQqzoEFUioSZIvG3ZMcGbChx3tN1yxkGW1Q5uip6EyJfkR53ZZLDXXTZ0VDn8Lvxw5GQJab9SQNsBdIkG-0DWtnhWdxeT7fNlbo9roAo9sZEIz_pmBSwIE_gWihyv1Srycc7ygPaL1FIdweE9XI7PB67kWpUSQfkBsm-LkeeGShm84qYdh9B1ZfDISpoAlIAbxM4B43D7R-PnGlJ7rkYpg5U2eclEFVtSJO-TkQHVVfrH5SQ2tUOzf8yOjaKtPtDw422CnVc1U4mPw=='
projectId = '1'
wsname = params['wsname']


idlestBench = getJenkinsNode(ip, authKey, projectId, ws_bench, wsname, bench_node)
with open(r'jenkinsNode.properties', 'w') as f:
    f.write('env.jenkinsNode="{}"'.format(idlestBench))
# print(idlestBench)