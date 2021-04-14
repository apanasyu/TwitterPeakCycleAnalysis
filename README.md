# TwitterPeakCycleAnalysis

It is important to understand how an individual's influence changes with time; this can help predict future influence as well. In the context of Twitter, the corresponding problem involves estimating the rate at which an influencer has gained their existing followers over a given time period. We propose a novel algorithm to address this problem, using the creation times of an influencer's followers. We also illustrate how the method can be used to understand whether influencer's followers are contentrated in a single timezone.

# Preliminaries:

Utilizing Ubuntu operating system, MongoDB for storing Tweets, Python 3.x as the programming language.

Python interfaces with MongoDB using pymongo (pip install pymongo), with Twitter using tweepy (pip install tweepy). Other library dependencies: numpy, jsonpickle.

Important:
Before using the Twitter API you are required to create and register your app (this is free), see:

https://developer.twitter.com/en/docs/twitter-api/getting-started/guide

(By registering an app you will obtain four tokens: consumer key, consumer secret, access token, and access secret. Go inside TwitterAPI.py and put these keys inside getAPI method).


Step 1: Twitter API is utilized to collect followers of an influencer
For example, this code collects the first 100K followers of @NPR (the follower ids are initially stored as a pickle file, then once the followers ids are collected each id is used to obtain follower information that is then stored in MongoDB):

        port = 27021
        from MainDBSetup import setupDBUsingSingleUser
        from TwitterAPI import getAPI
        twitterAPI1 = getAPI()
        influencerScreenName = 'npr'
        maxFollowerToCollect = 100000
        setupDBUsingSingleUser(twitterAPI1, influencerScreenName, maxFollowerToCollect, followersDir, port)

Step 2: Focus on the account creation time of each follower
Twitter does not store information beyond message and user creation times i.e. there is no information on when user A followed user B. However, there is additional information in the order of followers because the order is such that most recent followers appear first. We utilize four separate methods for estimating number of followers gained on daily basis applied over the collected followers (each method is described in APPENDIX further below). 

        import os.path, time, datetime
        ctimeCreatedAt = time.ctime(os.path.getctime(filePath))
        followerCollectionTime = datetime.datetime.strptime(time.ctime(os.path.getctime(followersDir+'npr.pickle')), "%a %b %d %H:%M:%S %Y")
        db_name = 'npr'
        step = 20000 #number of followers to consider
        from EvolvingPopularity import calculateDailyFollowerGain
        calculateDailyFollowerGain(step, db_name, followersDir, port, followerCollectionTime, outputDir)

The code results in a CSV file that contains the number of followers gained on a daily basis.

![image](https://user-images.githubusercontent.com/80060152/114786655-7c18af80-9d4c-11eb-876c-11b7ba5ec905.png)

The following Figure shows the estimates for different days going back in time. For @NPR the estimates are close, but for other influencers it may not work as well. Method is expected to work well on influencers that have a large stable following and that are continuing to increase their follower base. There will be periods during which an influencer gains no followers and even loses followers. We can reason only about followers that the influencer currently has, i.e., we cannot know which followers an influencer might have had in the past. If the influencer has lost many original followers, then the signal in the data will be obscured by considerable noise.

![image](https://user-images.githubusercontent.com/80060152/114788040-cbf87600-9d4e-11eb-98a8-aaaba587b6d5.png)

Step 3: Peak cycle analysis in general
MrBeast vs. NPR code

Step 4: Global vs. Local influencer via Peak analysis
Code for this


APPENDIX: Four Methods for Inferring number of followers



