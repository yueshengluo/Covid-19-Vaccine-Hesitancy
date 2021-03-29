from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import cursor
import json
import re
from datetime import datetime
from dateutil import tz
import pymongo
import sys, os
import time

import api_cred

## Handle the twitter api authentication for all functions
class twitterauthenticator():
    def authenticate_twitter_app(self):
        auth = OAuthHandler(api_cred.consumer_key, api_cred.consumer_secret)
        auth.set_access_token(api_cred.access_token, api_cred.access_token_secret)
        return auth
        

## main Twitter streaming function
class TwitterStreamer():

    def __init__(self):
        self.twitter_auth = twitterauthenticator()

    def stream_tweets(self, hash_tag_list):

        listener = tweetListner(hash_tag_list)
        auth = self.twitter_auth.authenticate_twitter_app()
        stream = Stream(auth, listener, tweet_mode='extended')
        stream.filter(languages=["en"], track = hash_tag_list)

## The callback function of stream
class tweetListner(StreamListener):
    ## track time and define connection to MongoDB

    tstamp1 = time.time()
    # myclient = pymongo.MongoClient("mongodb://Muzhgan:Muzhganpassword@54.212.88.30:27017/?retryWrites=true")
    # mydb = myclient["tempDB"]
    # tweetcol = mydb.tweet
    # usercol = mydb.tweet_user
    # ##delete stored documents
    # tweetcol.delete_many({})
    # usercol.delete_many({})

    ## define blank array for batch storing
    tweetobj = []
    userobj = []
    

    ## get filename here
    def __init__(self, hash_tag_list):
        self.hash_tag_list = hash_tag_list

    
    #print(tstamp1)
    def on_data(self,data):
        #from_zone = tz.gettz('UTC')
        #to_zone = tz.gettz('America/Los_Angeles')
        try:
            #print(data)
            ## load the data into json and save in db:
            ## save tweet data into tweet table
            dic = {}
            
            parsed = json.loads(data)
            
            # print(parsed)
            if "retweeted_status" in parsed:
                if "extended_tweet" in parsed['retweeted_status']:
                    dic["og_tweet_txt"] = parsed["retweeted_status"]["extended_tweet"]["full_text"]    
                else:
                    dic["og_tweet_txt"] = parsed["retweeted_status"]["text"]
                # print(dic['og_tweet_txt'])
                dic["og_tweet_time"] = parsed["retweeted_status"]["created_at"]
                dic["og_tweet_id"] = parsed["retweeted_status"]["id"]
                dic["og_tweet_user_id"] = parsed["retweeted_status"]["user"]["id"]
                dic["og_tweet_user_name"] = parsed["retweeted_status"]["user"]["screen_name"]
                dic["og_tweet_user_desc"] = parsed["retweeted_status"]["user"]["description"]
                dic["og_tweet_user_vrifd"] = parsed["retweeted_status"]["user"]["verified"]
                dic["og_tweet_user_loc"] = parsed["retweeted_status"]["user"]["location"]
                dic["og_tweet_time"] = datetime.strptime(parsed["retweeted_status"]["created_at"],'%a %b %d %H:%M:%S +0000 %Y').isoformat()
            else:
                dic["og_tweet_txt"] = ""
                dic["og_tweet_time"] = ""
                dic["og_tweet_id"] = ""
                dic["og_tweet_user_id"] = ""
                dic["og_tweet_user_name"] = ""
                dic["og_tweet_user_desc"] = ""
                dic["og_tweet_user_vrifd"] = ""
                dic["og_tweet_user_loc"] = ""
                dic["og_tweet_time"] = ""
            if "extended_tweet" in parsed:
                dic["tweet_txt"] = parsed["extended_tweet"]['full_text']
            else:
                dic["tweet_txt"] = parsed["text"]
            # dic["filter_word"] = [each for each in self.hash_tag_list if (each in dic["og_tweet_txt"].lower())]
            # if not dic["filter_word"]:
            #     dic["filter_word"] = [each for each in self.hash_tag_list if (each in dic["tweet_txt"].lower())]
            # dic["loc"] = {}
            # dic["loc"]["state"] = "CA"
            # dic["loc"]["city"] = ""
            ## We will disaseemble the location into city and county later, but now just put into county
            dic["user_loc"] = parsed["user"]["location"]
            dic["tweet_geo"] = parsed["geo"]
            dic["tweet_place"] = parsed["place"]

            #dic["coord"] = parsed["coordinates"]
            dic["tweet_time"] = {}
            # utc = t.replace(tzinfo=from_zone)
            #t_new = utc.astimezone(to_zone)
            dic["tweet_time"] = datetime.strptime(parsed["created_at"],'%a %b %d %H:%M:%S +0000 %Y').isoformat()
            #print(utc)
            dic["tweet_id"] = parsed["id"]
            # dic["user_info"] = {}
            dic["user_id"] = parsed["user"]["id"]
            dic["user_name"] = parsed["user"]["screen_name"]

            dic["tweet_likes"] = parsed["favorite_count"]
            dic["tweet_source"] = re.split("<|>",parsed["source"])[2]
            # dic["testing"] = parsed["entities"]
            if parsed["entities"]["hashtags"]:
            #if "text" in parsed["entities"]["hashtags"][0]:
                dic["hashtags"] = parsed["entities"]["hashtags"][0]["text"]
            else:
                dic["hashtags"] = ""
            ##save user data into user table
            dic["user_acc_cr_time"] = datetime.strptime(parsed["user"]["created_at"],'%a %b %d %H:%M:%S +0000 %Y').isoformat()
            dic["user_verified"] = parsed["user"]["verified"]
            dic["user_total_tweets"] = parsed["user"]["statuses_count"]
            # user_dic["total_likes"] = parsed["user"]["favourites_count"]
            # user_dic["profile_image"] = parsed["user"]["profile_image_url_https"]
            dic["user_followers"] = parsed["user"]["followers_count"]
            # dic["filter_word"] = self.fetched_tweets_filename.replace(".json", "")
            ## hard code in user_country for now because we only doing US for now
            # user_dic["user_country"] = "US"
            # json_obj = json.dumps(dic, indent=2)
            # user_obj = json.dumps(user_dic, indent=2)
            self.tweetobj.append(dic)
            # self.userobj.append(user_dic)
            
            ## Store it into mongoDB
            ## insert into MongoDB
            # print(dic)
            tstamp2 = time.time()

            # if tstamp2 - self.tstamp1 > 10:
            #     print("10s passed")
            #     tempinsert = self.tweetcol.insert_many(self.tweetobj)
            #     print(tempinsert.inserted_ids)
            #     tempinsert = self.usercol.insert_many(self.userobj)
            #     print(tempinsert.inserted_ids)
            #     self.tweetobj, self.userobj = [],[]
            #     self.tstamp1 = tstamp2
            
            # print(dic["tweet_id"],dic["txt"])
            # print(dic["tweet_time"])
            
            if tstamp2 - self.tstamp1 > 600:
                
                if dic:
                    # json_obj = json.dumps(dic, indent=2)
                    print("appending to doc",datetime.today().strftime('%m-%d-%Y')+".json")
                    with open(datetime.today().strftime('%m-%d-%Y')+".json", 'a', encoding = 'utf-16') as tf:
                        for d in self.tweetobj:
                            json.dump(d, tf)
                            tf.write('\n')
                        # tf.write(json_obj)
                    self.tweetobj = []
                    self.tstamp1 = tstamp2
            # with open(self.fetched_tweets_filename[1], 'a') as tf:
            #     tf.write(user_obj)
            # return True

        # except tweepy.TweepError:
        #     time.sleep(60 * 15)

        except BaseException as e:
            ##Debugging on where the error row is:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            #print("Error on_data: %s" % str(e))
            return True
    
    def on_error(self, status):
        if status == 420:
            ## Return false in case rate limit happens
            return False
        print(status)

## init it
if __name__ == "__main__":
    hash_tag_list = ["covid vaccine", "coronavirus vaccine","china virus vaccine", "covid injection", "covid shot", "kungflu vaccine", "wuhan virus vaccine", "pfizer covid"]
    # fetched_tweets_filename = re.sub('\s', '_',hash_tag_list[7])+".json"
    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets(hash_tag_list)