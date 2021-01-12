import tweepy
import pandas as pd
import numpy as np
import re
from time import sleep
from credentials import *

#Authenticate to twitter
auth = tweepy.OAuthHandler(consumer_key,consumer_secret_key)
auth.set_access_token(access_token,access_token_secret)

#Create Api Object
api = tweepy.API(auth,wait_on_rate_limit=True)

def getHashTags(tweet):
    hashArr = re.findall(r"#(\w+)",tweet)
    return hashArr
def tweetFunc(name,tagName):
    friendsTweet = []
    tweetID = []
    tagName = tagName.lower()
    for follower in api.friends(screen_name = name):
        userID = follower.screen_name
        tweets = tweepy.Cursor(api.user_timeline,screen_name=userID,include_rts=False,tweet_mode='extended').items()
        tweets_arr = [[tweet.user.screen_name, tweet.full_text, tweet.id] for tweet in tweets]
        tweet_df = pd.DataFrame(data=tweets_arr,columns=['User','Tweet','ID'])
        for i in range(0,len(tweet_df['Tweet'])):
            hashArr = getHashTags(tweet_df.iloc[i,1])
            hashArr = [x.lower() for x in hashArr]
            t_id = tweet_df.iloc[i,2]
            if t_id not in tweetID:    
                tweetID.append(t_id)
                if tagName in hashArr:
                    friendsTweet.append([tweet_df.iloc[i,0],tweet_df.iloc[i,1]])  
                
    #df = pd.DataFrame(data = friendsTweet,columns=['ID','UserName','Time','Tweet'])
    return friendsTweet

def retrieve_last_id(file_name):
    f_read = open(file_name,'r')
    last_id = int(f_read.read().strip())
    f_read.close()
    return last_id
def store_last_id(last_id,file_name):
    f_write = open(file_name,'w')
    f_write.write(str(last_id))
    f_write.close()
    return

FILE_NAME = 'last_id.txt'

def feed_tweets():    
    last_id = retrieve_last_id(FILE_NAME)
    mentions = api.mentions_timeline(since_id = last_id)  #last_id is removed
    for mention in reversed(mentions):
        print(str(mention.id) + " - " +mention.text + " - "+mention.user.screen_name)
        last_id = mention.id
        store_last_id(last_id,FILE_NAME)
        userName = mention.user.screen_name
        hashArr = getHashTags(mention.text)
        for tagName in hashArr:
            tweetsPerTag = tweetFunc(userName,tagName)
            #totalTweets.append([tagName,tweetsPerTag])
            for tweet in tweetsPerTag:
                x = ' '.join([str(item) for item in tweet])
                try:
                    api.update_status(' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",x).split())+" "+"@"+mention.user.screen_name,mention.id)
                except tweepy.TweepError as e:
                    print(e.reason)


if __name__ == "__main__":
    while True:
        feed_tweets()
        sleep(10)