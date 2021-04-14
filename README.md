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
Twitter does not store information beyond message and user creation times i.e. there is no information on when user A followed user B. However, there is additional information in the order of followers because the order is such that most recent followers appear first. Focussing on x followers at a time and generating a time distribution (as discussed in project apanasyu/TwitterPeakCycleAnalysis).

Code for doing this:

We want to find the n that results in peak hour during each time distribution (see paper). Describe algrorithm 1 and show the 24 hour cycle.
Algorithm 1 code:

Step 3: Baselines based on Meeder approach

Step 4: Peak cycle analysis in general
MrBeast vs. NPR code

Step 5: Global vs. Local influencer via Peak analysis
Code for this

