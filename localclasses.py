# utf-8
import re
import configparser
from pathlib import Path
from twython import Twython, TwythonError


class TweetProvider:
    is_text_empty = True
    photo = None
    text = None

    def __init__(self, twitter, tweet):
        assert isinstance(twitter, Twython)
        self.twitter = twitter
        self.tweet = tweet
        if self.tweet:
            self.user = self.tweet['user']
            self.screen_name = self.user['screen_name']
            self.user_id_str = self.user['id_str']
            self.tweet_id_str = tweet['id_str']
        if self.twitter and self.tweet:
            self.set_text()

    def set_text(self):
        text = self.tweet['text']
        mentions = re.match('(^(@\w+\s)*)', text).group(0)
        text = re.sub(r'&lt;', '<', re.sub(r'&gt;', '>', text))
        text = re.sub(r'@', 'ҩ', re.sub(r'^(@\w+\s)*', '', re.sub(r'https://t.co/\S*', '', text)))
        text = re.sub(r'(\w)\W*?(\w?)', lambda m: m.group(1).lower() + m.group(2).upper(), text)
        self.text = '@' + self.screen_name + ' ' + mentions + text
        text = re.sub(r'\W', '', text)
        if len(text) > 0:
            self.is_text_empty = False

    def set_mock_image(self):
        special_photo = Path(self.screen_name + '.jpg')
        if special_photo.is_file():
            self.photo = open(self.screen_name + '.jpg', 'rb')
            print('INFO: ' + self.screen_name + '.jpg exists')
        else:
            self.photo = open('mock.jpg', 'rb')

    def fire_tweet(self):
        self.set_mock_image()
        uploaded_photo = self.twitter.upload_media(media=self.photo)
        print('INFO: Dropping tweet with text...')
        print(self.text)
        try:
            self.twitter.update_status(status=self.text,
                                       in_reply_to_status_id=self.tweet_id_str,
                                       media_ids=[uploaded_photo['media_id']])
        except TwythonError as twython_exception:
            print(twython_exception)


class TimelineProvider:

    user_tl = None

    def __init__(self, twitter, screen_name, config):
        assert isinstance(twitter, Twython)
        assert isinstance(screen_name, str)
        assert isinstance(config, configparser.RawConfigParser)
        self.twitter = twitter
        self.screen_name = screen_name
        self.config = config

        self.get_user_tl()

    def get_user_tl(self):
        last_tweet = ''
        try:
            last_tweet = self.config.get('lasttweets', self.screen_name)
        except configparser.Error:
            print('No last tweet saved for ' + self.screen_name)
        try:
            self.user_tl = self.twitter.get_user_timeline(screen_name=self.screen_name, count=10,
                                                          include_rts=False, since_id=last_tweet)
        except TwythonError as twython_exception:
            error_str = str(twython_exception.error_code)
            print('ERROR ' + error_str + ' for ' + self.screen_name)
            if twython_exception.error_code == 404:
                print('Screen name does not exist (anymore)')
                user_id = None
                try:
                    user_id = self.config.get('victims', self.screen_name)
                except configparser.Error:
                    print('No user id saved')
                if user_id:
                    print('Trying with user id: ' + user_id)
                    try:
                        self.user_tl = self.twitter.get_user_timeline(id_str=user_id, count=10,
                                                                      include_rts=False, since_id=last_tweet)
                    except TwythonError as twython_exception:
                        print(twython_exception)

    def return_user_tl(self):
        return self.user_tl



