"""Python reddit bot that automates an assortment of RuneScape-related tasks"""
import re
import HTMLParser
from datetime import datetime
import os
import json
import argparse
import praw
import tweepy
import feedparser
from dateutil.relativedelta import relativedelta

def get_config():
    """Load the config from config.json"""
    if not os.path.isfile('config.json'):
        print "Error: Missing config.json file"
    else:
        with open('config.json') as json_data_file:
            config = json.load(json_data_file)
            return config

def init_reddit(config):
    """Initialize the Reddit praw object"""
    return praw.Reddit(
        client_id=config['reddit']['client_id'],
        client_secret=config['reddit']['secret'],
        password=config['reddit']['password'],
        username=config['reddit']['username'],
        user_agent=config['reddit']['user_agent']
    )

def push_sidebar_update(reddit, section, content, target_subreddit):
    """Retrieve a subreddit's current sidebar, and insert new content"""
    subreddit = reddit.subreddit(target_subreddit)
    current_sidebar = subreddit.description
    current_sidebar = HTMLParser.HTMLParser().unescape(current_sidebar)
    replace_pattern = re.compile(
        '%s.*?%s' %
        (re.escape(
            '[](/' +
            section +
            ')'),
         re.escape(
             '[](/' +
             section +
             '-end)')),
        re.IGNORECASE | re.DOTALL | re.UNICODE)
    new_sidebar = re.sub(
        replace_pattern, '%s\\n\\n%s\\n%s' %
        ('[](/' + section + ')', content, '[](/' + section + '-end)'), current_sidebar)
    reddit.subreddit(target_subreddit).mod.update(
        description=new_sidebar, spoilers_enabled=True)


def get_time():
    """Get the current UTC time"""
    utc_time = datetime.utcnow()
    return '## ' + utc_time.strftime("%H:%M") + '\n'


def get_active_vos(consumer_key, consumer_secret, access_token, access_token_secret):
    """Initialize a tweepy object, and access @JagexClock to find the most recent VoS tweet"""
    auth = tweepy.OAuthHandler(
        consumer_key,
        consumer_secret)
    auth.set_access_token(
        access_token,
        access_token_secret)
    api = tweepy.API(auth)
    vos_list = [
        'Amlodd',
        'Cadarn',
        'Crwys',
        'Hefin',
        'Iorwerth',
        'Ithell',
        'Meilyr',
        'Trahaearn']
    matches = []
    found = False
    for tweet in api.user_timeline('JagexClock', count=5):
        if found:
            break
        for vos in vos_list:
            if vos in tweet.text and vos not in matches:
                matches.append(vos)
                found = True
    return '## Voice of Seren \n \n 1. [' +  \
            matches[0] + '](https://twitter.com/JagexClock#' + \
            matches[0].lower() + ') \n 2. [' + \
            matches[1] + '](https://twitter.com/JagexClock#' + \
            matches[1].lower() + ') \n \n'


def get_latest_news():
    """Access the RuneScape News RSS feed and retrieve the 3 most recent news articles"""
    news = feedparser.parse(
        'http://services.runescape.com/m=news/latest_news.rss')
    matches = []
    if news:
        for item in news.entries:
            if item.category == 'Game Update News':
                matches.append(item)
        for item in matches:
            item.published = item.published.replace('00:00:00 GMT', '')

        if len(matches) >= 3:
            return '## Game updates  \n \n 1. [' + \
                    matches[0].title +'](' + \
                    matches[0].link + '#news) ' + \
                    matches[0].published + '\n 2. [' + \
                    matches[1].title + '](' + \
                    matches[1].link + '#news) ' + \
                    matches[1].published + '\n 3. [' +  \
                    matches[2].title + '](' + \
                    matches[2].link + '#news) ' + \
                    matches[2].published + '\n \n'
        elif len(matches) == 2:
            return '## Game updates  \n \n 1. [' + \
                    matches[0].title + '](' + \
                    matches[0].link + '#news) ' + \
                    matches[0].published + '\n 2. [' + \
                    matches[1].title + '](' + \
                    matches[1].link + '#news) ' + \
                    matches[1].published + '\n \n'
        return '## Game updates  \n \n 1. [' + \
                matches[0].title + '](' + \
                matches[0].link + '#news) ' + \
                matches[0].published + '\n \n'


def get_dxp(start, end, url):
    """Calculate the time until the start or end of a Double XP Weekend"""
    utc_time = datetime.utcnow()
    if utc_time < datetime(start):
        delta = relativedelta(datetime(start), utc_time)
        if delta.days >= 1:
            return '1. [DXP Weekend starts in: **%(days)d day, %(hours)d hours**](' + url + \
                    '#dxp) \n \n 2. [Portables & Boxes FC Information](https://redd.it/5uf7rt#dxp) \n' \
                    % delta.__dict__
        return '1. [DXP Weekend starts in: **%(hours)d hours**](' + url + \
                '#dxp) \n \n2. [Portables & Boxes FC Information](https://redd.it/5uf7rt#dxp) \n' \
                % delta.__dict__
    elif utc_time > datetime(end):
        return '1. DXP Weekend has ended.'
    else:
        delta = relativedelta(datetime(end), utc_time)
        if delta.days > 1:
            return '1. [DXP Weekend is LIVE: **%(days)d days, %(hours)d hours to go**](' + url + \
                    '#dxp) \n \n2. [Portables & Boxes FC Information](https://redd.it/5uf7rt#dxp) \n' \
                    % delta.__dict__
        elif delta.days == 1:
            return '1. [DXP Weekend is LIVE: **%(days)d day, %(hours)d hours to go**](' + url + \
                    '#dxp) \n \n2. [Portables & Boxes FC Information](https://redd.it/5uf7rt#dxp) \n' \
                    % delta.__dict__
        return '1. [DXP Weekend is LIVE: **%(hours)d hours to go**](' + url + \
                '#dxp) \n \n2. [Portables & Boxes FC Information](https://redd.it/5uf7rt#dxp) \n' \
                % delta.__dict__

def main():
    """Main function"""
    config = get_config()
    subreddit = config['reddit']['subreddit']
    parser = argparse.ArgumentParser()
    parser.add_argument("--clock", help="set sidebar with the current time (utc)",
                        action="store_true")
    parser.add_argument("--vos", help="set sidebar with the current Voice of Seren",
                        action="store_true")
    parser.add_argument("--dxp", help="set sidebar with time until the end of dxp",
                        action="store_true")
    parser.add_argument("--news", help="set sidebar with the last 3 RuneScape news",
                        action="store_true")
    parser.add_argument("-q", "--quiet", help="run with no outputs",
                        action="store_true")
    args = parser.parse_args()

    if args.clock:
        push_sidebar_update(init_reddit(config),
                            'clock',
                            get_time(),
                            subreddit)
        print "Successfully ran --clock"
    if args.vos:
        push_sidebar_update(init_reddit(config), 'vos',
                            get_active_vos(config['twitter']['consumer_key'],
                                           config['twitter']['consumer_secret'],
                                           config['twitter']['access_token'],
                                           config['twitter']['access_token_secret']),
                            subreddit)
        print "Successfully ran --vos"
    if args.news:
        push_sidebar_update(init_reddit(config),
                            'news',
                            get_latest_news(),
                            subreddit)
        print "Successfully ran --news"

if __name__ == "__main__":
    main()
