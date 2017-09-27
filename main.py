from twython import Twython, TwythonError
import re
import configparser
from pathlib import Path

victims = open(file='victims.txt')
config = configparser.RawConfigParser()
config.read('twitter.cfg')
twitter = Twython(config.get('twitter', 'app_key'), config.get('twitter', 'app_secret'),
                  config.get('twitter', 'oauth_token'), config.get('twitter', 'oauth_token_secret'))
for victim in victims:
    user_timeline = None
    lasttweet = None
    twitter_handle = re.sub(r'\W', '', victim)
    try:
        lasttweet = config.get('lasttweets', twitter_handle)
    except configparser.Error:
        print('No last tweet saved for ' + twitter_handle)
    try:
        user_timeline = twitter.get_user_timeline(screen_name=twitter_handle, count=10, include_rts=False, since_id=lasttweet)
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
                    user_timeline = twitter.get_user_timeline(id_str=user_id, count=10, include_rts=False, since_id=lasttweet)
                except TwythonError as twython_exception:
                    print(twython_exception)
    if user_timeline:
        text = None
        for tweet in user_timeline:
            if len(tweet['text']) > 0:
                text = tweet['text']
        if text:
            text = re.sub(r'https:\/\/t.co\/\S*', '', text)
            text = re.sub(r'@', '%', (re.sub(r'(\w)\W*?(\w?)', lambda m: m.group(1).lower() + m.group(2).upper(), text)))
            text = '@' + twitter_handle + ' ' + text
            specialphoto = Path(twitter_handle + '.jpg')
            if specialphoto.is_file():
                photo = open(twitter_handle + '.jpg', 'rb')
                print('INFO: ' + twitter_handle + '.jpg exists')
            else:
                photo = open('mock.jpg', 'rb')
            response = twitter.upload_media(media=photo)
            try:
                print('INFO: Dropping tweet...')
                print(text)
                twitter.update_status(status=text, in_reply_to_status_id=tweet['id_str'], media_ids=[response['media_id']])
                config.set('lasttweets', twitter_handle, tweet['id_str'])
                user = tweet['user']
                config.set('victims', twitter_handle, user['id_str'])
            except TwythonError as twython_exception:
                print(twython_exception)
with open('twitter.cfg', 'w') as configfile:
    config.write(configfile)
