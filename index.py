#Flask imports
from flask import Flask, render_template, url_for

#Project imports
from processing.computation import *

#python imports
import threading
import atexit
import os
import sys
import signal
import datetime 

POOL_TIME = 3600 #Seconds

tdEARD = None
lastUpdated = None

class LockdownInfo:
	def __init__(self, lockdownName, lockdownDateInfo, plotInfo, ratesInfoList, stateInfoList):
		self.lockdownName = lockdownName
		self.lockdownDateInfo = lockdownDateInfo
		self.plotInfo = plotInfo
		self.ratesInfoList = ratesInfoList 
		self.stateInfoList = stateInfoList

lockdownInfoObjList = []

updateEARDThread = threading.Thread()
updateLockdownInfoListThread = threading.Thread()

def updateEARDEveryHour():

	global tdEARD, lastUpdated
	global updateEARDThread
	print(f"Updating EARD Info list {datetime.datetime.now()}")
	tdEARD, lastUpdated = getEARD()
	
	updateEARDThread = threading.Timer(POOL_TIME, updateEARDEveryHour, ())
	updateEARDThread.start()

def updateLockdownInfoListEveryMidnight():

	global updateLockdownInfoListThread
	global lockdownInfoObjList
	print(f"Updating lockdown Info list {datetime.datetime.now()}")
	for lockdownInfoObj in lockdownInfoObjList:
		if (lockdownInfoObj.lockdownName == "l4"):
			lockdownDateInfo, plotInfo, ratesInfoList, stateInfoList = getDatePlotRateInfo(lockdownInfoObj.lockdownName)
			lockdownInfoObj.lockdownDateInfo = lockdownDateInfo
			lockdownInfoObj.plotInfo = plotInfo
			lockdownInfoObj.ratesInfoList = ratesInfoList
			lockdownInfoObj.stateInfoList = stateInfoList
		else:
			print(f"No need to update {lockdownInfoObj.lockdownName}")

	nextUpdateTime = datetime.datetime.combine((datetime.datetime.now() + datetime.timedelta(days=1)), datetime.datetime.min.time()) - datetime.datetime.now()
	#nextUpdateTime = (datetime.datetime.now() + datetime.timedelta(minutes=1)) - datetime.datetime.now()
	updateLockdownInfoListThread = threading.Timer(nextUpdateTime.total_seconds(), updateLockdownInfoListEveryMidnight, ())
	updateLockdownInfoListThread.start()

def sigHandler(signo, frame):
    sys.exit(0)

def interrupt():
	global updateEARDThread
	global updateLockdownInfoListThread

	updateEARDThread.cancel()
	updateLockdownInfoListThread.cancel()

def createApp():
	app = Flask(__name__)

	global tdEARD, lastUpdated
	tdEARD, lastUpdated = getEARD()		

	global updateEARDThread
	updateEARDThread = threading.Timer(POOL_TIME, updateEARDEveryHour, ())
	updateEARDThread.start()

	global lockdownInfoObjList
	lockdownNameList = ['all','l1','l2','l3','l4']
	for lockdownName in lockdownNameList:
		lockdownDateInfo, plotInfo, ratesInfoList, stateInfoList = getDatePlotRateInfo(lockdownName)
		lockdownInfoObjList.append(LockdownInfo(lockdownName, lockdownDateInfo, plotInfo, ratesInfoList, stateInfoList))
	
	global updateLockdownInfoListThread
	nextUpdateTime = (datetime.datetime.now() + datetime.timedelta(seconds=30)) - datetime.datetime.now()
	updateLockdownInfoListThread = threading.Timer(nextUpdateTime.total_seconds(), updateLockdownInfoListEveryMidnight, ())
	updateLockdownInfoListThread.start()	

	# When you kill Flask (SIGTERM), clear the trigger for the next thread
	atexit.register(interrupt)
	return app	

app = createApp()

@app.route("/info")
def info():
	return render_template('info.html')

@app.route("/<string:lockdownName>")
def home(lockdownName='all'):
	
	global tdEARD
	global lockdownInfoObjList

	for lockdownInfoObj in lockdownInfoObjList:
		if lockdownInfoObj.lockdownName == lockdownName:
			return render_template('index.html',tdEARD=tdEARD,TodayDateTime=lastUpdated,lockdownDateInfo=lockdownInfoObj.lockdownDateInfo,plotInfo=lockdownInfoObj.plotInfo,ratesInfoList=lockdownInfoObj.ratesInfoList,stateInfoList=lockdownInfoObj.stateInfoList)
