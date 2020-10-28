# Kitty Bot
These are the sources of Kitty Bot, a discontinued project of mine.

## Note
I will NOT be accepting pull requests, I'm no longer interested in maintaining the bot.

## Contributors
### Programmers
 - omame (me) - Main Programmer
 - KittyLe - Lead Programmer

### FFmpeg magicians
 - dengr1065 - made FFmpeg command line switches for `k.mutalaugh`

## How to set this up?
To run Kitty Bot, you need:
 - Python 3.8+ (or lower, idk)
 - pip
 - Chrome/Chromium (with chromedriver)
 - ImageMagick
 - possibly something else, i forgot (tell me in the Issues tab if i'm missing smth pls)

Install the dependencies:
```sh
$ pip3 install -r requirements.txt
```

Create `config.py` in the root directory with the following content:
```py
token = "YOUR_TOKEN_HERE"
prefix = "k."
shards = 1
```
You can change the prefix.

Now, run `main.py`:
```sh
$ python3 ./main.py
```

# Where is Flex's source code?
I still have to dig it out.

# Updates
Last updated: 2020-10-28

## 2020-10-28
Initial upload.

# Licensing
I'm releasing **the code** into the public domain.

Assets, however, are released under the CC-BY 4.0 license. As such, they require attribution, and are not allowed to be restricted legally.

The images:
 - `/static/img/kittyRound.png`
 - `/static/img/kittySquare.png`

are photos of my cat, and as such, they're released under the CC-BY-NC-ND 4.0 license, which prohibits you from editing the images, and doesn't allow you to use them for commercial purposes. You must also give me appropriate credit for them.
