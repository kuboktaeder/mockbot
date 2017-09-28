#!/usr/bin/env python3
# utf-8
from twython import Twython, TwythonError
import re
import configparser
import localclasses

victims = open(file='victims.txt')
config = configparser.RawConfigParser()
config.read('twitter.cfg')
twitter = Twython(config.get('twitter', 'app_key'), config.get('twitter', 'app_secret'),
                  config.get('twitter', 'oauth_token'), config.get('twitter', 'oauth_token_secret'))
for victim in victims:
    user_tl = None
    last_tweet = None
    twitter_handle = re.sub(r'\W', '', victim)
    try:
        last_tweet = config.get('lasttweets', twitter_handle)
    except configparser.Error:
        print('No last tweet saved for ' + twitter_handle)
    try:
        user_tl = twitter.get_user_timeline(screen_name=twitter_handle, count=10,
                                            include_rts=False, since_id=last_tweet)
    except TwythonError as twython_exception:
        error_str = str(twython_exception.error_code)
        print('ERROR ' + error_str + ' for ' + twitter_handle)
        if twython_exception.error_code == 404:
            print('Screen name does not exist (anymore)')
            user_id = None
            try:
                user_id = config.get('victims', twitter_handle)
            except configparser.Error:
                print('No user id saved')
            if user_id:
                print('Trying with user id: ' + user_id)
                try:
                    user_tl = twitter.get_user_timeline(id_str=user_id, count=10,
                                                        include_rts=False, since_id=last_tweet)
                except TwythonError as twython_exception:
                    print(twython_exception)
    if user_tl:
        final_tweet = None
        for tweet in user_tl:
            tweet_candidate = localclasses.TweetProvider(twitter=twitter, tweet=tweet)
            if not tweet_candidate.is_text_empty:
                final_tweet = tweet_candidate
        if final_tweet:
            final_tweet.fire_tweet()
            config.set('lasttweets', final_tweet.screen_name, final_tweet.tweet_id_str)
            config.set('victims', twitter_handle, final_tweet.user_id_str)

with open('twitter.cfg', 'w') as configfile:
    config.write(configfile)
