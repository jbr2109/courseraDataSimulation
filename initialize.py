#! python
# Global State Initializer Function

# initialize() #global state

		#Fill user hashmap:
				# ['userid'] -> ['nickname': '',  'twitter': '',  'dob': '',  'country': '',  'timeStamp': '', 'tags'=[gameaccuracy, purchbeh, adbeh, chatbeh] ]
				# globalUsers = createUserDatabase(minAge, maxAge, meanAge) //returns a hash map
		#Fill team hashmap: ['teamid'] -> ['name': '',  'teamCreationTime': '',  'teamEndTime': '', 'strength': '0-1']
		#Fill user-team assignment current-state hashmap ['assignmentid']->['userid': '', teamid': '',  'sessionid': '',]
		#Create sessions for each user who is playing: ['sessionid']->[ 'assignmentid': '', 'start_timeStamp': '', 'end_timeStamp': '', 'team_level': '', 'platformType': '' ]
		#Fill team current-state hashmap: ['teamid']->[user1, user2,...]

from datasets import *
import copy
import random
import datetime
import math


def getAllMembers(assignmentsList):
	members = {}
	for a in assignmentsList:
		teamid = a['teamid']
		userid = a['userid']
		if teamid in members:
			members[teamid].append(userid)
		else:
			members[teamid]=[userid]

	for k,v in members.items():
		print k,v
	return members


def getPlayingMembers(userSessionsList, assignmentsList):
	members = {}
	for s in userSessionsList:
		teamid = assignmentsList[s['assignmentid']]['teamid']
		userid = assignmentsList[s['assignmentid']]['userid']
		if teamid in members:
			members[teamid].append(userid)
		else:
			members[teamid]=[userid]
	#for k,v in members.items():
	#	print k,v
	return members

def initializeUserSessions(assignmentsList, teamDatabaseList):
	howManySessions = 0.5
	# 50% of assigned users play (have a session) at the start of the game
	pickedAssignments = np.random.choice(assignmentsList, howManySessions * len(assignmentsList), replace=False)
	sessions = []
	platforms	= ['iphone', 'android', 'mac', 'windows', 'linux']
	freq 		= [0.4, 0.35, 0.05, 0.15, 0.05]
	print "Generating sessions ..." 
	for assignment in pickedAssignments:
		newSession = {}
		newSession['assignmentid']	=assignmentsList.index(assignment)
		newSession['startTimeStamp']=assignment["startTimeStamp"] + datetime.timedelta(days=random.uniform(0, 2))
		newSession['endTimeStamp']	=float("inf")
		newSession['team_level']	= teamDatabaseList[assignment['teamid']]['currentLevel'] #get team's current level
		newSession['platformType']	= np.random.choice(platforms, 1, replace=False, p=freq)[0]
		sessions.append(newSession)
	print "  ",len(sessions), "sessions generated from ", len(assignmentsList), " available assignments"
	return sessions

def asssignUsersTOteams(userDatabaseList, teamDatabaseList):
	# team has strength
	# user strength is measured by gameaccuracy
	print 'Generating user-team assignments ...'
	assignments = [] #list
	freeUsers = range(0,len(userDatabaseList))
	#pick a set of indices of teams (60%) that get >1 users assigned
	pickedTeams = np.random.choice(range(0,len(teamDatabaseList)), math.floor(0.6*len(teamDatabaseList)))
	# team length min = 1, max = 30
	teamSizes   = np.random.choice(range(1,30), len(pickedTeams))

	strongTeamThreshhold = 0.6
	for team, n in zip(pickedTeams, teamSizes):
		#print team
		strongPlayers = []
    	#every strong team (strength>0.6) should have 60% strong players (gameaccuracy>0.6)
		if(teamDatabaseList[team]['strength'] > strongTeamThreshhold):
			#print 'getStrongPlayers: before len of freeUsers', len(freeUsers)
			strongPlayers = getStrongPlayers(math.floor(0.6*n), freeUsers, userDatabaseList) #list
			#reduce size of available users
			freeUsers = [x for x in freeUsers if x not in strongPlayers]
			#print 'after len :', len(freeUsers)
			n = n - len(strongPlayers)
			
		morePlayers = getRandomPlayers(n, freeUsers) # list
		#reduce size of available users
		freeUsers = [x for x in freeUsers if x not in morePlayers]
		iter = strongPlayers 
		iter.extend(morePlayers) # merge two lists

		for u in iter:
			newAssignment={}
			newAssignment['userid']	=u
			newAssignment['teamid']	=team
			newAssignment['startTimeStamp']=datetime.datetime.now() - datetime.timedelta(days=random.uniform(0, 3))
			assignments.append(newAssignment)
	#for a in assignments:
	#	print a['userid'],'::',a['teamid'], '::', a['startTimeStamp']
	print '  ',sum(teamSizes) ,' users assigned to ', len(pickedTeams),' teams'
	return assignments

def getStrongPlayers(n, freeusersindex, globalUsersDataset):
	random.shuffle(freeusersindex)
	pick = []
	pickinitial = np.random.choice(freeusersindex, n, replace=False)
	for p in pickinitial:
		if(globalUsersDataset[p]['tags']['gameaccuracy'] > 0.6):
			pick.append(p)
		else:
			while (p in pickinitial) or (globalUsersDataset[p]['tags']['gameaccuracy'] <= 0.6):
				p = np.random.choice(freeusersindex, 1)
			pick.extend(p.tolist())
	#for t in pick:
	#	print globalUsersDataset[t]['tags']['gameaccuracy']
	return pick

def getRandomPlayers(n, freeusersindex):
	random.shuffle(freeusersindex)
	pick = np.random.choice(freeusersindex, n, replace=False) #just return n random
	return pick.tolist()




def createTeamDatabase(noOfTeams=100):
	teams=[]

	#~~~~~~~~~~~~~~~~~~1. generate teams ~~~~~~~~~~~~~~~~~~
	teamNames		= getUserNames(noOfTeams)
	strengthFactor 	= getProbabilities(.5, 0.5, noOfTeams) #mu 0.5, sigma 0.5 (high number means strong) 
	#date when user accounts started
	startdate= datetime.datetime.now() - datetime.timedelta(7300) #days=20yrs*365
	teamAges = getages(0, 4, 1, noOfTeams, 1) #min (0days), max (4days), mean (1day), sigma 1

	print('Generating teams ...')
	for i in range(0, noOfTeams):
		newTeam={}

		newTeam['name']	=teamNames[i]
		newTeam['teamCreationTime']	=datetime.datetime.now() - datetime.timedelta(days=teamAges[i]+random.uniform(0, 2))
		newTeam['teamEndTime']		=float("inf")
		newTeam['strength']	=strengthFactor[i]
		newTeam['currentLevel']=1 #every team starts at level 1
		teams.append(newTeam)
	print '  ', noOfTeams, '  teams generated'
	return teams # list of users, where teamID = index on the list


def createUserDatabase(noOfUsers=2000):
	users=[] # list of users, where userID = index on the list

	#~~~~~~~~~~~~~~~~~~1. generate users ~~~~~~~~~~~~~~~~~~
	countries = getCountries(noOfUsers) #list
	random.shuffle(countries)
	ages = getages(18, 70, 25, noOfUsers, 30) #min (18), max (70), mean 25, sigma 30
	accuracyFactor 	= getProbabilities(.5, .4, noOfUsers) #mu 0.5, sigma 0.4
	purchaseFactor 	= getProbabilities(.5, .2, noOfUsers)
	adFactor 		= getProbabilities(.5, .5, noOfUsers)
	chatFactor 		= getProbabilities(.5, .4, noOfUsers) # = accuracyFactor
	twitterHandles	= getTwitterIDs(noOfUsers)
	nicknames		= getUserNames(noOfUsers)

	#date when user accounts started
	startdate=datetime.datetime.now() - datetime.timedelta(7300) #days=20yrs*365
	
	print('Generating users ...')
	for i in range(0, noOfUsers):
		newUser={}

		newUser['nickname']	=nicknames[i]
		newUser['twitter']	=twitterHandles[i]
		newUser['dob']		=datetime.date.today() - datetime.timedelta(days=365*ages[i])
		newUser['country']	=countries[i]
		newUser['timeStamp']=startdate+datetime.timedelta(random.uniform(1,7300)) #days=20yrs*365
		#'tags is a list'=[gameaccuracy, purchbeh, adbeh, chatbeh]
		newUser['tags']={'gameaccuracy':round(accuracyFactor[i], 3), 
						 'purchbeh':round(purchaseFactor[i],3), 
						 'adbeh':round(adFactor[i],3), 'chatbeh':round(chatFactor[i],3) }
		users.append(newUser)

	print '  ', noOfUsers, ' users generated'
	return users

	# ['userid'] -> ['nickname': '',  'twitter': '',  'dob': '',  'country': '',  'timeStamp': '', 'tags'=[gameaccuracy, purchbeh, adbeh, chatbeh] ]


