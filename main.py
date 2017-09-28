#!/usr/bin/env python3
# utf-8
from twython import Twython
import re
import configparser
import localclasses

victims = open(file='victims.txt')
config = configparser.RawConfigParser()
config.read('twitter.cfg')
twitter = Twython(config.get('twitter', 'app_key'), config.get('twitter', 'app_secret'),
                  config.get('twitter', 'oauth_token'), config.get('twitter', 'oauth_token_secret'))
for victim in victims:
    twitter_handle = re.sub(r'\W', '', victim)
    user_tl = localclasses.TimelineProvider(twitter=twitter, screen_name=twitter_handle, config=config).return_user_tl()
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
