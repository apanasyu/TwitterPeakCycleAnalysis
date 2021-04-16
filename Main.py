if __name__ == '__main__':
    pass

    outputDir = "programOutput/"
    import os
    if not os.path.isdir(outputDir):
        os.mkdir(outputDir)
    outputDir2 = "peakAnalysis/"
    import os
    if not os.path.isdir(outputDir2):
        os.mkdir(outputDir2)
    followersDir = "collectFollowers/"
    import os
    if not os.path.isdir(followersDir):
        os.mkdir(followersDir)

    port = 27021
    userNames = ['npr', 'bbcworld']
    for influencerScreenName in userNames:
        step1 = False
        if step1:
            '''collect influencer's followers and profile information of each follower'''
            from MainDBSetup import setupDBUsingSingleUser
            from TwitterAPI import getAPI
            twitterAPI1 = getAPI()
            maxFollowerToCollect = 100000
            setupDBUsingSingleUser(twitterAPI1, influencerScreenName, maxFollowerToCollect, followersDir, port)
    
        step2 = False
        if step2:
            print("Step 2")
            filePath = followersDir+influencerScreenName+'.pickle'
            import os.path, time
            ctimeCreatedAt = time.ctime(os.path.getctime(filePath))
            print("created: %s" % ctimeCreatedAt)
            import datetime
            datetimeCreatedAt = datetime.datetime.strptime(ctimeCreatedAt, "%a %b %d %H:%M:%S %Y")
            print("created: %s" % datetimeCreatedAt)
            followerCollectionTime = datetimeCreatedAt
            
            db_name = influencerScreenName
            step = 20000 #number of followers to consider
            from EvolvingPopularity import calculateDailyFollowerGain
            calculateDailyFollowerGain(step, db_name, followersDir, port, followerCollectionTime, outputDir)
            
        step3 = False
        if step3:
            db_name = influencerScreenName
            from Visualization import vizUsingFollowerSnapshots
            vizUsingFollowerSnapshots(db_name, 50, 70, followersDir, outputDir, port)
        
    step4 = True
    if step4:
        print("Peak Cycle Analysis")
        step = 100
        outputDir2 = "peakAnalysis/"
        from PeakAnalysis import peakVisualization, cosineSimilarityBetweenPeaks 
        peakVisualization(userNames, followersDir, outputDir2, port, step)
        cosineSimilarityBetweenPeaks(userNames, followersDir, outputDir2, port, step)
        
