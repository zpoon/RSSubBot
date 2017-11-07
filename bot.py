"""Python reddit bot that automates an assortment of RuneScape-related tasks"""
import re
import HTMLParser
from datetime import datetime
import json
import argparse
import praw
import tweepy
import feedparser
from dateutil.relativedelta import relativedelta
from dateutil import parser

def get_config():
    """Load the config from config.json"""
    try:
        with open('config.json') as json_data_file:
            config = json.load(json_data_file)
            return config
    except IOError:
        raise IOError("Missing or unreadable config.json file")

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
    if news.bozo:
        raise news.bozo_exception
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


def get_dxp(start, end, news_url, portables_url):
    """Calculate the time until the start or end of a Double XP Weekend"""
    utc_time = datetime.utcnow()
    start_date = parser.parse(start)
    end_date = parser.parse(end)
    if utc_time < start_date:
        delta = relativedelta(start_date, utc_time)
        if delta.days >= 1:
            return '1. [DXP Weekend starts in: **%(days)d day, %(hours)d hours**](' \
                    % delta.__dict__ + news_url + \
                    '#dxp) \n \n 2. [Portables & Boxes FC Information](' + portables_url + ') \n'
        return '1. [DXP Weekend starts in: **%(hours)d hours**](' \
                % delta.__dict__ + news_url + \
                '#dxp) \n \n2. [Portables & Boxes FC Information](' + portables_url + ') \n'
    elif utc_time > end_date:
        return '1. DXP Weekend has ended.'
    else:
        delta = relativedelta(end_date, utc_time)
        if delta.days > 1:
            return '1. [DXP Weekend is LIVE: **%(days)d days, %(hours)d hours to go**]('  \
                    % delta.__dict__ + news_url + \
                    '#dxp) \n \n2. [Portables & Boxes FC Information](' + portables_url + ') \n'
        elif delta.days == 1:
            return '1. [DXP Weekend is LIVE: **%(days)d day, %(hours)d hours to go**](' \
                    % delta.__dict__ + news_url + \
                    '#dxp) \n \n2. [Portables & Boxes FC Information](' + portables_url + ') \n'
        return '1. [DXP Weekend is LIVE: **%(hours)d hours to go**](' \
                % delta.__dict__ + news_url + \
                '#dxp) \n \n2. [Portables & Boxes FC Information](' + portables_url + ') \n'

def main():
    """Main function"""
    config = get_config()
    reddit = init_reddit(config)
    subreddit = config['reddit']['subreddit']
    arg = argparse.ArgumentParser()
    arg.add_argument("--clock", help="set sidebar with the current time (utc)",
                     action="store_true")
    arg.add_argument("--vos", help="set sidebar with the current Voice of Seren",
                     action="store_true")
    arg.add_argument("--dxp", help="set sidebar with time until the end of dxp",
                     action="store_true")
    arg.add_argument("--news", help="set sidebar with the last 3 RuneScape news",
                     action="store_true")
    args = arg.parse_args()

    if args.clock:
        try:
            push_sidebar_update(reddit,
                                'clock',
                                get_time(),
                                subreddit)
        except ValueError:
            raise ValueError
        else:
            print "'clock' completed and pushed to %s" % subreddit
    if args.vos:
        try:
            push_sidebar_update(reddit,
                                'vos',
                                get_active_vos(config['twitter']['consumer_key'],
                                               config['twitter']['consumer_secret'],
                                               config['twitter']['access_token'],
                                               config['twitter']['access_token_secret']),
                                subreddit)
        except ValueError:
            raise ValueError
        else:
            print "'vos' completed and pushed to %s" % subreddit
    if args.news:
        try:
            push_sidebar_update(reddit,
                                'news',
                                get_latest_news(),
                                subreddit)
        except ValueError:
            raise ValueError
        else:
            print "'news' completed and pushed to %s" % subreddit
    if args.dxp:
        try:
            push_sidebar_update(reddit,
                                'dxp',
                                get_dxp(config['dxp']['start'],
                                        config['dxp']['end'],
                                        config['dxp']['news_url'],
                                        config['dxp']['portables_url']),
                                subreddit)
        except ValueError:
            raise ValueError
        else:
            print "'dxp' completed and pushed to %s" % subreddit

if __name__ == "__main__":
    main()
