# TwitterPeakCycleAnalysis

It is important to understand how an individual's influence changes with time; this can help predict future influence as well. In the context of Twitter, the corresponding problem involves estimating the rate at which an influencer has gained their existing followers over a given time period. We propose a novel algorithm to address this problem, using the creation times of an influencer's followers. This problem is related to inferring link creation times (in this case when a follower has followed the influencer). We also illustrate how the method can be used to understand whether influencer's followers are contentrated in a single timezone.

# Preliminaries:

Utilizing Ubuntu operating system, MongoDB for storing Tweets, Python 3.x as the programming language.

Python interfaces with MongoDB using pymongo (pip install pymongo), with Twitter using tweepy (pip install tweepy). Other library dependencies: numpy, jsonpickle.

Important:
Before using the Twitter API you are required to create and register your app (this is free), see:

https://developer.twitter.com/en/docs/twitter-api/getting-started/guide

(By registering an app you will obtain four tokens: consumer key, consumer secret, access token, and access secret. Go inside TwitterAPI.py and put these keys inside getAPI method).

# Approach:
Step 1: Twitter API is utilized to collect followers of an influencer
For example, this code collects the first 100K followers of @NPR (the follower ids are initially stored as a pickle file (npr.pickle in folder followersDir), then once the followers ids are collected each id is used to obtain follower information that is then stored in MongoDB in database using influencer screenname (npr)):

        port = 27021
        from MainDBSetup import setupDBUsingSingleUser
        from TwitterAPI import getAPI
        twitterAPI1 = getAPI()
        influencerScreenName = 'npr'
        maxFollowerToCollect = 100000
        setupDBUsingSingleUser(twitterAPI1, influencerScreenName, maxFollowerToCollect, followersDir, port)

Step 2: Focus on the account creation time of each follower

Twitter does not store information beyond message and user creation times i.e. there is no information on when user A followed user B. However, there is additional information in the order of followers because the order is such that most recent followers appear first. 

For a specific influencer i,  let F(i) = [f0, f1, f2, ..., fc]  be the list of account creation times of its followers. We select the first m*n values from this list for generating the matrix A. In matrix A, there are m rows where each row consists of n followers (A_{i,j} refers to follower f_{i*n+j}). As an illustration the following code generates a visualization for influencer @NPR where m=50 and n=70 (visualization stored as .PNG in folder specified by outputDir). 

        db_name = 'npr'
        from Visualization import vizUsingFollowerSnapshots
        vizUsingFollowerSnapshots(db_name, 50, 70, followersDir, outputDir, port)

The n followers at a time are utilized to form a time distribution (see apanasyu/TwitterMining and reference [1]). Figure illustrates m time distributions drawn one on top of the other. In this figure, for each distribution, the hour during which the frequency peaks is highlighted in red. We observe that each distribution has a peak and the peak shifts by about an hour. 

<img src="https://user-images.githubusercontent.com/80060152/114931206-ee989680-9e03-11eb-87f0-c48955ca4e39.png" width="600">

If we compute and plot the vector of cosine similarities between (sine, cosine) representations of these hours with the representation of hour 16 (where the peak occurs in the first distribution), we obtain the curve shown below. The curve has a periodicity in that it starts at 1 goes to -1 and back up to 1 (starts at hour 16 and back to 16).

<img src="https://user-images.githubusercontent.com/80060152/114931032-ae391880-9e03-11eb-84de-e20a3d5f77c9.png" width="500">

We utilize four separate methods for estimating number of followers gained on daily basis applied over the collected followers. We are interested in the size of $n$ that results in temporal distributions that peak exactly one hour apart for all 24 hours (or as close to it as possible). Thus the methods based on time distribution utilize m=24:

A. The first method uses Pearson Correlation between the vector of cosine similarities using peaks vs. cosine similarity for hours that are in order (that is the cosine similarities of (sine, cosine) representation of a specific hour A, with  (sine, cosine) representations of hours A, (A+1), (A+2), ...). The n that results in higher Pearson Correlation coefficient is recorded.

B. The second method uses peaks across the 24 time distributions and records n that results in a slope as close to -1 as possible.

C and D. The final two methods (baseline 1 and baseline 2) are modified versions of approach first proposed by Meeder et al. [2]. Let Lm be the list of (t ??? account creation time of the jth follower in seconds) where t is the datetime when the followers were collected. For our problem we are interested in the index where the account creation datetime for the follower is as close to the datetime that is 24 hours before the follower collection took place. Here is the mathematical formulation (see source code and [1] for more details).

<img src="https://user-images.githubusercontent.com/80060152/114945140-ce260780-9e16-11eb-8841-817bfd4b1d76.png" width="500">

This code results in a CSV file that contains the number of followers gained on a daily basis using each method.

        import os.path, time, datetime
        followerCollectionTime = datetime.datetime.strptime(time.ctime(os.path.getctime(followersDir+'npr.pickle')), "%a %b %d %H:%M:%S %Y")
        db_name = 'npr'
        step = 20000 #number of followers to consider
        from EvolvingPopularity import calculateDailyFollowerGain
        calculateDailyFollowerGain(step, db_name, followersDir, port, followerCollectionTime, outputDir)

Here is a snapshot of the CSV:

<img src="https://user-images.githubusercontent.com/80060152/114786655-7c18af80-9d4c-11eb-876c-11b7ba5ec905.png" width="300">

The following Figure shows the estimates for different days going back in time. For @NPR the estimates are close, indicating that @NPR is gaining around 1200-2000 new followers on a daily basis. Method is expected to work well on influencers that have a large stable following and that are continuing to increase their follower base. There will be periods during which an influencer gains no followers and even loses followers. We can reason only about followers that the influencer currently has, i.e., we cannot know which followers an influencer might have had in the past. If the influencer has lost many original followers, then the signal in the data will be obscured by considerable noise.

![image](https://user-images.githubusercontent.com/80060152/114788040-cbf87600-9d4e-11eb-98a8-aaaba587b6d5.png)

# Peak Cycle Analysis in General

Previous section showed how peak cycle analysis can be used to infer number of followers gained on a daily basis. This is useful for understanding how the influencer's popularity is evolving and can be used to identify rising stars (those influencers that have a large ratio of new vs. old followers). Peak analysis can also reveal whether an influencer has a more global like following and can be used to compare two influencers.

The following code takes the followers of two influencers. For each influencer n=100 (specified via step) i.e. 100 followers at a time used to generate a time distribution and the peak of the time distribution is recorded. 

        step = 100
        userNames = ['npr', 'bbcworld']
        outputDir2 = "peakAnalysis/"
        from PeakAnalysis import peakVisualization, cosineSimilarityBetweenPeaks 
        peakVisualization(userNames, followersDir, outputDir2, port, step)
        cosineSimilarityBetweenPeaks(userNames, followersDir, outputDir2, port, step)
        
The peakVisualization() function generates the following Figure. 100K followers of NPR and 100K follower of BBCWorld used to generate figure. There are a total of 100K/100=1000 points plotted for each. From Figure we see a period of inactivity for NPR around hours 5-10 whereas BBCWorld has peaks during all hours (this visually indicates that BBCWorld is more global, see [1] for more details).

![image](https://user-images.githubusercontent.com/80060152/115067852-77c0d380-9ebf-11eb-9dc6-c929b32d5672.png)

The cosineSimilarityBetweenPeaks() function generates Figure below which illustrates a larger number of followers attracted on a daily basis by BBCWorld. 

![image](https://user-images.githubusercontent.com/80060152/115084672-33d9c880-9ed7-11eb-8d5d-61165858ef96.png)

Global vs. Local influencer identification via peak cycle analysis is described in [1]. Additional signal processing methods may yield additional insights. This code serves as a means for collecting and visualizing this data.

# REFERENCES: 

[1] Panasyuk, Aleksey, Kishan G. Mehrotra, Edmund Szu-Li Yu, and Chilukuri K. Mohan. "Inferring Degree of Localization and Popularity of Twitter Topics and Persons using Temporal Features." Lecture Notes in Computer Science, Springer 2021.

[2] Meeder, Brendan, et al. "We know who you followed last summer: inferring social link creation times in twitter." Proceedings of the 20th international conference on World wide web. 2011.
