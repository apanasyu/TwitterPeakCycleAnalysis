# TwitterPeakCycleAnalysis

It is important to understand how an individual's influence changes with time; this can help predict future influence as well. In the context of Twitter, the corresponding problem involves estimating the rate at which an influencer has gained their existing followers over a given time period. We propose a novel algorithm to address this problem, using the creation times of an influencer's followers. We also illustrate how the method can be used to understand whether influencer's followers are contentrated in a single timezone.

# Preliminaries:

Utilizing Ubuntu operating system, MongoDB for storing Tweets, Python 3.x as the programming language.

Python interfaces with MongoDB using pymongo (pip install pymongo), with Twitter using tweepy (pip install tweepy). Other library dependencies: numpy, jsonpickle.

Important:
Before using the Twitter API you are required to create and register your app (this is free), see:

https://developer.twitter.com/en/docs/twitter-api/getting-started/guide

(By registering an app you will obtain four tokens: consumer key, consumer secret, access token, and access secret. Go inside TwitterAPI.py and put these keys inside getAPI method).


