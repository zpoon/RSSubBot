import time
import praw
import tweepy
import feedparser
import re
import HTMLParser
from datetime import datetime
import os
import json
import argparse
 
def get_config():
    if not os.path.isfile('config.json'):
        print "Error: Missing config.json file"
    else:
        with open('config.json') as json_data_file:
            config = json.load(json_data_file)
            return config

def pushSidebarUpdate(section, content, target_subreddit):
    subreddit = r.subreddit(target_subreddit)
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
    r.subreddit(target_subreddit).mod.update(
        description=new_sidebar, spoilers_enabled=True)


def getTime():
    utc_time = datetime.utcnow()
    return '## ' + utc_time.strftime("%H:%M") + '\n'


def getActiveVos(consumer_key, consumer_secret, access_token, access_token_secret):
    auth = tweepy.OAuthHandler(
        consumer_key,
        consumer_secret)
    auth.set_access_token(
        access_token,
        access_token_secret)
    api = tweepy.API(auth)
    VosList = [
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
        for x in VosList:
            if x in tweet.text and x not in matches:
                matches.append(x)
                found = True
    return '## Voice of Seren \n \n 1. [' + matches[0] + '](https://twitter.com/JagexClock#' + matches[0].lower(
    ) + ') \n 2. [' + matches[1] + '](https://twitter.com/JagexClock#' + matches[1].lower() + ') \n \n'


def getLatestNews():
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
            return '## Game updates  \n \n 1. [' + matches[0].title + '](' + matches[0].link + '#news) ' + matches[0].published + '\n 2. [' + matches[1].title + '](' + matches[
                1].link + '#news) ' + matches[1].published + '\n 3. [' + matches[2].title + '](' + matches[2].link + '#news) ' + matches[2].published + '\n \n'
        elif len(matches) == 2:
            return '## Game updates  \n \n 1. [' + matches[0].title + '](' + matches[0].link + '#news) ' + matches[
                0].published + '\n 2. [' + matches[1].title + '](' + matches[1].link + '#news) ' + matches[1].published + '\n \n'
        else:
            return '## Game updates  \n \n 1. [' + matches[
                0].title + '](' + matches[0].link + '#news) ' + matches[0].published + '\n \n'


def getDxp(start, end, url):
    utc_time = datetime.utcnow()
    if utc_time < datetime(start):
        rd = relativedelta(datetime(start), utc_time)
        if rd.days >= 1:
            return '1. [DXP Weekend starts in: **%(days)d day, %(hours)d hours**](' + url + \
                '#dxp) \n \n2. [Portables & Boxes FC Information](https://redd.it/5uf7rt#dxp) \n' % rd.__dict__
        else:
            return '1. [DXP Weekend starts in: **%(hours)d hours**](' + url + \
                '#dxp) \n \n2. [Portables & Boxes FC Information](https://redd.it/5uf7rt#dxp) \n' % rd.__dict__
    elif utc_time > datetime(end):
        return '1. DXP Weekend has ended.'
    else:
        rd = relativedelta(datetime(end), utc_time)
        if rd.days > 1:
            return '1. [DXP Weekend is LIVE: **%(days)d days, %(hours)d hours to go**](' + url + \
                '#dxp) \n \n2. [Portables & Boxes FC Information](https://redd.it/5uf7rt#dxp) \n' % rd.__dict__
        elif rd.days == 1:
            return '1. [DXP Weekend is LIVE: **%(days)d day, %(hours)d hours to go**](' + url + \
                '#dxp) \n \n2. [Portables & Boxes FC Information](https://redd.it/5uf7rt#dxp) \n' % rd.__dict__
        else:
            return '1. [DXP Weekend is LIVE: **%(hours)d hours to go**](' + url + \
                '#dxp) \n \n2. [Portables & Boxes FC Information](https://redd.it/5uf7rt#dxp) \n' % rd.__dict__

def main():
    config = get_config()
    subreddit = config['reddit']['subreddit']
    global r 
    r = praw.Reddit(
        client_id=config['reddit']['client_id'],
        client_secret=config['reddit']['secret'],
        password=config['reddit']['password'],
        username=config['reddit']['username'],
        user_agent=config['reddit']['user_agent']
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--clock", help="set sidebar with the current time (utc)", action="store_true")
    parser.add_argument("--vos", help="set sidebar with the current Voice of Seren", action="store_true")
    parser.add_argument("--dxp", help="set sidebar with time until the end of dxp", action="store_true")
    parser.add_argument("--news", help="set sidebar with the last 3 RuneScape news", action="store_true")
    parser.add_argument("-q", "--quiet", help="run with no outputs",
                    action="store_true")
    args = parser.parse_args()

    if args.clock:
        pushSidebarUpdate('clock', getTime(), subreddit)
        print "Successfully ran --clock"
    if args.vos:
        pushSidebarUpdate('vos', getActiveVos(config['twitter']['consumer_key'], config['twitter']['consumer_secret'], config['twitter']['access_token'], config['twitter']['access_token_secret']), subreddit)
        print "Successfully ran --vos"
    if args.news:
        pushSidebarUpdate('news', getLatestNews(), subreddit)
        print "Successfully ran --news"

if __name__ == "__main__":
   main()
