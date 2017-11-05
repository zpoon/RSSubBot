# RSSubBot (WIP)

A reddit CLI bot that handles an assortment of RuneScape-related tasks.

## Installation

Installation of the dependencies can be done with pip:

`pip install -r requirements.txt`

## Configs

A `config.json` file is required to run the bot which contains reddit and twitter keys. This is where you must set your reddit OAuth2 keys, Twitter API (if using `--vos`), target subreddit, and dxp weekend information.
```
{
    "reddit": {
        "client_id": "CLIENT_ID",
        "secret": "SECRET",
        "password": "PASSWORD",
        "username": "USERNAME",
        "user_agent": "USER_AGENT",
        "subreddit": "SUBREDDIT"
    },
    "twitter": {
        "consumer_key": "CONSUMER_KEY",
        "consumer_secret": "CONSUMER_SECRET",
        "access_token": "ACCESS_TOKEN",
        "access_token_secret": "ACCESS_TOKEN_SECRET"
    }
}
```
## Usage

The bot is designed to be run from a command-line interface taking arguments. Tasks are supposed to run periodically to push updates to a subreddit, however at this time there is no native scheduler or timer built into the bot. This allows you to utilize your own scheduler solutions (scripts, cron, services etc.)

### News

Get the latest RuneScape news from the website and update the sidebar.

`--news`

### Time

Get the current UTC (in-game) time and update the sidebar.

`--time`

### Voice of Seren

Get the current active Voice of Seren and update the sidebar.

`--vos`

### DXP (WIP)

Update the sidebar with the amount of time remaining (or to start) in a double XP weekend.

`--dxp`


## Credits

Author: Nicholas Torkos (@ZPUNS)

## License

MIT License

Copyright (c) 2017 Nicholas Torkos

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
