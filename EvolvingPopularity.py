def getHoursAccordingToFollowerOrder(db_name, outputDirFollower, portInput=None):
    global port
    if portInput != None:
        port = portInput
        
    from MongoDBInterface import getMongoClient
    client = getMongoClient(port)
    db = client[db_name]
    collectionToRead = db["followerInfo"]
    
    import os
    hoursInOrder = []
    from MongoDBInterface import getMongoClient
    client = getMongoClient(port)
    dbnames = client.list_database_names()
    if db_name in dbnames:
        db = client[db_name]
        if "influencerOverWhichFollowerInfoCollected" in db.list_collection_names():
            userInfoPath = outputDirFollower+str(db_name.lower())+".pickle"
            import pickle
            with open(userInfoPath, "rb") as fp:
                followers = pickle.load(fp)

            idToDate = {}
            query = {}
            tweetCursor = collectionToRead.find(query, no_cursor_timeout=True)
            for userInfo in tweetCursor:
                idToDate[str(userInfo["id_str"])] = userInfo["created_at"]
        
            hoursInOrder = []
            datesInOrder = []
            for follower in followers:
                if follower in idToDate:
                    hoursInOrder.append(idToDate[follower].hour)
                    datesInOrder.append(idToDate[follower])
            
            print(str(len(hoursInOrder)) + " account creation times in order")
            
    if len(hoursInOrder) == 0:
        print("Error could not load any hours")
        import sys
        sys.exit()
    return hoursInOrder, datesInOrder

#attempts to match based on slope that is closest to -1
def dailyTurnBasedOnSlope(L1, n=24):
    import numpy as np
    slopes = []
    sizes = []
    resultsToHour = {}
    for s in range(5, int(len(L1)/n), 5):
        peaks = []
        for i in range(0,n,1):
            hoursV = L1[i*s:i*s+s]

            hoursH = [0]*24
            for h in hoursV: hoursH[h] += 1
            
            normH = [float(i)/np.sum(hoursH) for i in hoursH]
            peaks.append(normH.index(np.max(normH)))
        
        startHour = peaks[0]
        transform = []
        toAdd = 24
        for peakHour in peaks:
            if not peakHour <= startHour: 
                toAdd = 0
            transform.append(peakHour+toAdd)
            
        uniqueHours = len(set(peaks))
        y = transform
        x = range(0,24,1)
        slope, intercept = np.polyfit(range(0,24,1), transform, 1)
        p = np.poly1d([slope, intercept])
        ybar = np.sum(y) / len(y)
        ssreg = np.sum((p(x) - ybar) ** 2)
        sstot = np.sum((y - ybar) ** 2)
        Rsqr = ssreg / sstot
        
        result = {}
        result["slope"] = slope
        result["uniqueHours"] = uniqueHours
        result["Rsqr"] = Rsqr
        resultsToHour[s] = result
        if Rsqr > 0.8:
            slopes.append(abs(1+slope))
            sizes.append(s)
            
    if len(slopes) > 0:
        turnRate1H = sizes[slopes.index(np.min(slopes))]
        result = resultsToHour[turnRate1H]
        maxR2 = result["Rsqr"]
        uniqueHoursB = result["uniqueHours"]
    else:
        turnRate1HTouniqueHoursB = {}
        for turnRate1H in resultsToHour:
            turnRate1HTouniqueHoursB[turnRate1H] = resultsToHour[turnRate1H]["uniqueHours"]
        topN, influencerToChangeInFollower = getTopNFromDict(turnRate1HTouniqueHoursB, 1)
        if len(topN) > 0:
            turnRate1H = topN[0]
            result = resultsToHour[turnRate1H]
            maxR2 = result["Rsqr"]
            uniqueHoursB = result["uniqueHours"]
        else:
            turnRate1H = None
            result = None
            maxR2 = None
            uniqueHoursB = None
            return None, None, None
        
    return turnRate1H*24, maxR2, uniqueHoursB

#turn rate based on cosine similarity
def dailyTurnBasedOnCosineSimilarity(L1, n=24):
    import numpy as np
    from EvolvingPopularity import cos_sim
    cosineSimOptimal = [cos_sim(0, hour) for hour in range(0,n,1)]

    maxR2 = 0
    turnRate1H = 0
    uniqueHoursB = 0
    for s in range(5, int(len(L1)/n), 5):
        peaks = []
        for i in range(0,n,1):
            hoursV = L1[i*s:i*s+s]

            hoursH = [0]*24
            for h in hoursV: hoursH[h] += 1
            
            normH = [float(i)/np.sum(hoursH) for i in hoursH]
            peaks.append(normH.index(np.max(normH)))
        cosineSim = [cos_sim(peaks[0], h) for h in peaks]
        #if np.min(cosineSim) < -0.5 and np.max(cosineSim) > 0.5:
        #    if twoPointTest(cosineSim, n):
        uniqueHours = len(set(peaks))

        from scipy.stats.stats import pearsonr
        rsqr = pearsonr(cosineSim, cosineSimOptimal)[0]**2
        if rsqr > maxR2: 
            maxR2 = rsqr
            turnRate1H = s
            uniqueHoursB = uniqueHours
    
    return turnRate1H*24, maxR2, uniqueHoursB

#approach a modification of method proposed by Meeder et al.
def dailyTurnBasedOnFollowerOrder(followerCollectionTime, datesInOrder):
    differences = []
    secPerFollower = []
    i = 0
    secondsCutoff = 3600*24
    for date in datesInOrder:
        difference = followerCollectionTime-date
        diffDay = abs(difference.total_seconds())
        differences.append(diffDay)
        if diffDay >= secondsCutoff:
            secPerFollower.append(float(diffDay)/float(i+1))
        i += 1
        
    cutOff = len(differences)-1
    i = len(differences)-1
    for difference in reversed(differences):
        if difference <= secondsCutoff:
            cutOff = i
            break
        i -= 1
    
    import numpy as np
    baseline1 = int(float(86400)/float(np.min(secPerFollower)))
    baseline2 = cutOff
    
    return baseline1, baseline2

def calculateDailyFollowerGain(step, db_name, followerFolder, port, followerCollectionTime, outputDir):
    hoursInOrder, datesInOrder = getHoursAccordingToFollowerOrder(db_name, followerFolder, port)
    
    turnRateCos, maxR2, uniqueHoursB = dailyTurnBasedOnCosineSimilarity(hoursInOrder[:step])
    turnRateUsingSlope, maxR2, uniqueHoursB = dailyTurnBasedOnSlope(hoursInOrder[:step])
    baseline1, baseline2 = dailyTurnBasedOnFollowerOrder(followerCollectionTime, datesInOrder[:step])
    
    rows = [["day", "CosineSim", "UsingSlope", "Baseline1", "Baseline2"]]
    row = [1, turnRateCos, turnRateUsingSlope, baseline1, baseline2]
    rows.append(row)
    
    followersProcessed = [turnRateCos, turnRateUsingSlope, baseline1, baseline2]
    col0 = []
    col1 = []
    col2 = []
    col3 = []
    print("calculating 24 hour turn rate using cosine similarity")
    count = 0
    while (len(hoursInOrder)>(step+followersProcessed[0])):
        turnRateCos, maxR2, uniqueHoursB = dailyTurnBasedOnCosineSimilarity(hoursInOrder[followersProcessed[0]:step+followersProcessed[0]])
        followersProcessed[0] += turnRateCos
        col0 += [turnRateCos]
        print("day " + str(count) + ', ' + str(followersProcessed[0]))
        count += 1
    print("calculating 24 hour turn rate using slope of best fit line")
    count = 0
    while (len(hoursInOrder)>(step+followersProcessed[1])):
        turnRateUsingSlope, maxR2, uniqueHoursB = dailyTurnBasedOnSlope(hoursInOrder[followersProcessed[1]:step+followersProcessed[1]])
        followersProcessed[1] += turnRateUsingSlope
        col1 += [turnRateUsingSlope]
        print("day " + str(count) + ', ' + str(followersProcessed[1]))
        count += 1
    from datetime import timedelta
    print("calculating 24 hour turn rate using baseline 1 based on modified Meeder")
    count = 0
    while (len(hoursInOrder)>(step+followersProcessed[2])):
        baseline1, baseline2 = dailyTurnBasedOnFollowerOrder(followerCollectionTime-timedelta(days=count+1), datesInOrder[followersProcessed[2]:step+followersProcessed[2]])
        followersProcessed[2] += baseline1
        col2 += [baseline1]
        print("day " + str(count) + ', ' + str(followersProcessed[2]))
        count += 1
    print("calculating 24 hour turn rate using baseline 2 based on modified Meeder")
    count = 0
    while (len(hoursInOrder)>(step+followersProcessed[3])):    
        baseline1, baseline2 = dailyTurnBasedOnFollowerOrder(followerCollectionTime-timedelta(days=count+1), datesInOrder[followersProcessed[3]:step+followersProcessed[3]])
        followersProcessed[3] += baseline2
        col3 += [baseline2]
        print("day " + str(count) + ', ' + str(followersProcessed[3]))
        count += 1
    
    import numpy as np
    numRows = np.max([len(col0),len(col1),len(col2),len(col3)])
    day = 2
    for i in range(0, numRows, 1):
        turnRateCos = 0
        turnRateUsingSlope = 0
        baseline1 = 0
        baseline2 = 0
        if len(col0) > i:
            turnRateCos = col0[i]
        if len(col1) > i:
            turnRateUsingSlope = col1[i]
        if len(col2) > i:
            baseline1 = col2[i]
        if len(col3) > i:
            baseline2 = col3[i]
            
        row = [day, turnRateCos, turnRateUsingSlope, baseline1, baseline2]
        rows.append(row)
        day += 1
        
    writeRowsToCSV(rows, outputDir + str(db_name) + "_InferredDailyFollowerGain.csv")

def writeRowsToCSV(rows, fileToWriteToCSV):
    import csv
    if len(rows) > 0:
        with open(fileToWriteToCSV, "w") as fp:
            a = csv.writer(fp, delimiter=',')
            a.writerows(rows)
            fp.close()
            print("Written " + str(len(rows)) + " rows to: " + fileToWriteToCSV)

def getTopNFromDict(dictToSort, N, reverseIn=True):
    import operator
    sortedDict = sorted(dictToSort.items(), key = operator.itemgetter(1), reverse=reverseIn)
    count = 0
    topN = []
    topNToCount = {}
    for result in sortedDict:
        topN.append(result[0])
        topNToCount[result[0]] = float(result[1])
        count += 1
        if count >= N:
            break
    
    return topN, topNToCount

def cos_sim(hour1, hour2):
    import numpy as np
    A = np.array(getCosineAndSineComponent(60*60*hour1))
    B = np.array(getCosineAndSineComponent(60*60*hour2))

    cos_sim=np.dot(A,B)/(np.linalg.norm(A)*np.linalg.norm(B))
    return cos_sim

def getCosineAndSineComponent(seconds):
    seconds_in_day = 24*60*60

    import numpy as np
    sineComponent = float(np.sin(2*np.pi*float(seconds)/seconds_in_day))
    cosineComponent = float(np.cos(2*np.pi*float(seconds)/seconds_in_day))

    return sineComponent, cosineComponent
