#Pandas import
import pandas as pd
from pandas.io.json import json_normalize 
import urllib.request, json

#Python imports
import array
import re
import datetime
import locale
import random

#Other project file imports
from processing.plot import *

colors = ['#78B9FC','#FB8989','#6E6C6C','#90BE6D']

data_link = "https://api.covid19india.org/data.json"

lockdownDatetimeList = [datetime.datetime(2020, 3, 25), datetime.datetime(2020, 4, 15), datetime.datetime(2020, 5, 4), datetime.datetime(2020, 5, 18)]

locale.setlocale(locale.LC_NUMERIC, 'hi_IN')

class LockdownDateInfo:
	def __init__(self,lockdownStartDate,lockdownEndDate):
		self.lockdownStartDate = lockdownStartDate
		self.lockdownEndDate = lockdownEndDate

class RateInfo:
	def __init__(self,rateType,rateValue):
		self.rateType = rateType
		self.rateValue = rateValue

class PlotInfo:
	def __init__(self, script, div):
		self.script = script
		self.div = div

def cleanDates(date): 
    z = re.match('(.*) (.*) ', date)
    d=None
    if z:
        if z.groups()[1] == 'January':
            d = f'2020-01-{z.groups()[0]}'            
        elif z.groups()[1] == 'February':
            d=f'2020-02-{z.groups()[0]}'
        elif z.groups()[1] == 'March':
            d=f'2020-03-{z.groups()[0]}'
        elif z.groups()[1] == 'April':
            d=f'2020-04-{z.groups()[0]}'
        elif z.groups()[1] == 'May':
            d=f'2020-05-{z.groups()[0]}'         
        return datetime.datetime.strptime(d, '%Y-%m-%d')

def getData(info):
	with urllib.request.urlopen(data_link) as url:
		raw_data = json.loads(url.read().decode())
	df = json_normalize(raw_data[info])	
	return df

def getDoublingRate(noOfTotalConfirmedCasesList):
	days = 0 
	totalDays=0
	noOfTimeDoubles = 0 
	firstElement = noOfTotalConfirmedCasesList[0] 
	rate = 2
	for totalcases in noOfTotalConfirmedCasesList:
		if totalcases / firstElement >= rate:
		    totalDays +=days
		    days=0
		    rate=2*rate
		    noOfTimeDoubles+=1
		days +=1
	if (noOfTimeDoubles == 0):
		return None
	return int(totalDays/noOfTimeDoubles)

class StateInfo:
	def __init__(self, stateName, confirmedcasesNumber):
		self.stateName = stateName
		if confirmedcasesNumber:
			self.confirmedcasesNumber = locale.format("%d", int(confirmedcasesNumber), grouping=True)
		else:
			self.confirmedcasesNumber = confirmedcasesNumber

def getWorstHitState(lockdownStartDate,lockdownEndDate):
	#Get the data
	with urllib.request.urlopen("https://api.covid19india.org/states_daily.json") as url:
		raw_data = json.loads(url.read().decode())
	df_states = json_normalize(raw_data['states_daily']) 
	df_states['date'] = pd.to_datetime(df_states['date'],format='%d-%b-%y')
	df_states_confirmed = df_states[(df_states['status'] == 'Confirmed') & (df_states['date'] >= lockdownStartDate) & (df_states['date'] <= lockdownEndDate)].drop(['date','status','tt'],axis=1)
	df_state_statecode = getData('statewise')
	df_state_statecode['statecode'] = df_state_statecode['statecode'].str.lower()
	stateInfoList = []
	for stateInfo in df_states_confirmed.astype(int).sum().nlargest(10).iteritems():
		stateInfoList.append(StateInfo(df_state_statecode[df_state_statecode['statecode'] == stateInfo[0]]['state'].iloc[0],stateInfo[1]))
	return stateInfoList

def getDatePlotRateInfo(lockdown):
	df = getData('cases_time_series')

	#Getting lockdown date info
	lockdownStartDate=None
	lockdownEndDate=None
	
	df['date'] = df['date'].apply(cleanDates)

	if lockdown == "all":
		lockdownStartDate = lockdownDatetimeList[0]
		lockdownEndDate = datetime.datetime.today() - datetime.timedelta(days=1)
	elif lockdown == "l1":
		lockdownStartDate = lockdownDatetimeList[0]
		lockdownEndDate = lockdownDatetimeList[1] - datetime.timedelta(days=1)
	elif lockdown == "l2":
		lockdownStartDate = lockdownDatetimeList[1]
		lockdownEndDate = lockdownDatetimeList[2] - datetime.timedelta(days=1)
	elif lockdown == "l3":
		lockdownStartDate = lockdownDatetimeList[2]
		lockdownEndDate = lockdownDatetimeList[3] - datetime.timedelta(days=1)
	elif lockdown == "l4":
		lockdownStartDate = lockdownDatetimeList[3]
		lockdownEndDate = datetime.datetime.today() - datetime.timedelta(days=1)
	lockdownDateInfo = LockdownDateInfo(lockdownStartDate.strftime("%d-%b-%Y"), lockdownEndDate.strftime("%d-%b-%Y"))
	df_lockdownPhase = df[(df['date'] >= lockdownStartDate) & (df['date'] <= lockdownEndDate)]
	
	#Getting the plot 

	plotScript, plotDiv = plotGraph(df_lockdownPhase,colors[random.randrange(len(colors))])
	plotInfo = PlotInfo(plotScript,plotDiv)

	#Getting the rates

	doublingRate = getDoublingRate(list(df_lockdownPhase['totalconfirmed'].astype(int)))
	recoveryRate = (int(df_lockdownPhase.iloc[-1]['totalrecovered'])/int(df_lockdownPhase.iloc[-1]['totalconfirmed'])) * 100
	mortalityRate = (int(df_lockdownPhase.iloc[-1]['totaldeceased'])/int(df_lockdownPhase.iloc[-1]['totalconfirmed'])) * 100
	ratesInfoList = [RateInfo("Doubling",doublingRate), RateInfo("Recovery",recoveryRate), RateInfo("Mortality",mortalityRate)]
	
	#Getting the worst hit states

	stateInfoList = getWorstHitState(lockdownStartDate,lockdownEndDate)
	return lockdownDateInfo, plotInfo, ratesInfoList, stateInfoList

class TDEARD:
	def __init__(self, state, total, delta):
		self.state=state
		if total:
			self.total=locale.format("%d", int(total), grouping=True)
		else:
			self.total=total
		if delta:
			self.delta=locale.format("%d",int(delta), grouping=True)
		else:
			self.delta=delta

def getEARD():
	df = getData('statewise')
	df_state = df.set_index('state')
	tdEARD = [ TDEARD("Effected",df_state.loc['Total']['confirmed'],df_state.loc['Total']['deltaconfirmed']),TDEARD("Active",df_state.loc['Total']['active'],None),TDEARD("Recovered",df_state.loc['Total']['recovered'],df_state.loc['Total']['deltarecovered']),TDEARD("Decreased",df_state.loc['Total']['deaths'],df_state.loc['Total']['deltadeaths']) ]
	lastUpdated=df_state.loc['Total']['lastupdatedtime']
	return tdEARD, lastUpdated
