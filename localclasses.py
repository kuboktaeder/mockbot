# utf-8
import re
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
        print(self.text)
        print(self.is_text_empty)

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
        print('INFO: Dropping tweet...')
        print(self.text)
        try:
            self.twitter.update_status(status=self.text,
                                       in_reply_to_status_id=self.tweet_id_str,
                                       media_ids=[uploaded_photo['media_id']])
        except TwythonError as twython_exception:
            print(twython_exception)
