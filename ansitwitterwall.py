#!/usr/bin/python

#
# ANSi Tweetboard designed for Raspberry Pi
# 
# Released as open source by NCC Group Plc - http://www.nccgroup.com/
# 
# Developed by Ollie Whitehouse, ollie dot whitehouse at nccgroup dot com
#
# http://www.github.com/olliencc/ansitwitterwall
#
# Released under AGPL see LICENSE for more information#
#

#
# Notes:
#    - Python 2.7
#    - If testing over SSH ensure you use a remote character set of CP437.
#    - Designed for Raspberry Pi native HDMI output resolution.
#    - Designed for the ANSi template included in the src repo, but it will give you an idea of how to build your own.
#


# https://github.com/sixohsix/twitter
from twitter import *
# General
import sys
import colorama
import time
import argparse
import os
from time import gmtime, strftime

# Twitter authentication stuff
twitter = Twitter(
      auth=OAuth('','','','')
	)

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("file", help="ANSi template file to use")
parser.add_argument("user", help="user's timeline to show, followers etc.")
parser.add_argument("--term", help="term or harshtag to show for instead of user's timeline")
args = parser.parse_args()
monuser = args.user

# Open the ANSi template (once)
try:
        with open(args.file) as f:
                content = f.readlines()
except:
        sys.stderr.write("[!] couldn't open " + args.file + "\n")
        sys.exit()

# Collect init stuff
colorama.init()

# Loop
while True:

	# Clear screen
    	os.system('clear')

	# Are we using a searchterm or watching a user's tweets?
	try:
		if args.term: # search term
			tweets = twitter.search.tweets(q=args.term,count=9)
			user = False
		else: # users tweets
			tweets = twitter.statuses.user_timeline(screen_name=monuser, count=9)
			user = True
	except: # again should probably be handled a little better
		user = True

	# Used for the loop
	count = 0

	# Our followers
	try:
		followers = twitter.users.show(screen_name=monuser)
	except:
		followers = 1337

	# Replace any template lines we need to	
	for ansiline in content:

		newline = ansiline
		padtitle = 18
		padtweet = 132
		padnfo = 88

		try:

			if "@tweet" in newline:		
				count+=1
				padtweet += len("@tweet"+str(count)+"@")
				if user:
					padtweet -= len(tweets[count-1]['text'].encode('ascii','ignore'))
					newline = newline.replace("@tweet"+str(count)+"@",tweets[count-1]['text'].encode('ascii','ignore').replace("\n", " ") + " "*padtweet)
				else:
					padtweet -= len(tweets['statuses'][count-1]['text'].encode('ascii','ignore'))
					newline = newline.replace("@tweet"+str(count)+"@",tweets['statuses'][count-1]['text'].encode('ascii','ignore').replace("\n", " ") + " "*padtweet)			
	
			if "@peep" in newline:
				if user:
					padnfo += len("@peep"+str(count)+"@")
					padnfo -= len(tweets[count-1]['user']['screen_name'].encode('ascii','ignore'))
					newline = newline.replace("@peep"+str(count)+"@",tweets[count-1]['user']['screen_name'].encode('ascii','ignore'))
				else:
					padnfo += len("@peep"+str(count)+"@")
					padnfo -= len(tweets['statuses'][count-1]['user']['screen_name'].encode('ascii','ignore'))
					newline = newline.replace("@peep"+str(count)+"@",tweets['statuses'][count-1]['user']['screen_name'].encode('ascii','ignore'))

			if "@when" in newline:
				if user:
					padnfo += len("@when"+str(count)+"@")
					padnfo -= len(tweets[count-1]['created_at'].encode('ascii','ignore'))
					newline = newline.replace("@when"+str(count)+"@",tweets[count-1]['created_at'].encode('ascii','ignore'))
				else:
					padnfo += len("@when"+str(count)+"@")
					padnfo -= len(tweets['statuses'][count-1]['created_at'].encode('ascii','ignore'))
					newline = newline.replace("@when"+str(count)+"@",tweets['statuses'][count-1]['created_at'].encode('ascii','ignore'))

			if "@re" in newline:
				if user:
					padnfo += len("@re"+str(count)+"@")
					padnfo -= len(str(tweets[count-1]['retweet_count']))
					newline = newline.replace("@re"+str(count)+"@",str(tweets[count-1]['retweet_count']))
				else:
					padnfo += len("@re"+str(count)+"@")
					padnfo -= len(str(tweets['statuses'][count-1]['retweet_count']))
					newline = newline.replace("@re"+str(count)+"@",str(tweets['statuses'][count-1]['retweet_count']))

			if "@fav" in newline:
				if user:
					padnfo += len("@fav"+str(count)+"@")
					padnfo -= len(str(tweets[count-1]['favorite_count']))
					newline = newline.replace("@fav"+str(count)+"@",str(tweets[count-1]['favorite_count']))
				else:
					padnfo += len("@fav"+str(count)+"@")
					padnfo -= len(str(tweets['statuses'][count-1]['favorite_count']))
					newline = newline.replace("@fav"+str(count)+"@",str(tweets['statuses'][count-1]['favorite_count']))

			if "favs" in newline:
				newline = newline.replace("favs","favs" + " "*padnfo)

			if "@follow@" in newline:
				pad = len("@follow@") - len(str(followers['followers_count'])) 
				newline = newline.replace("@follow@"," "*pad + str(followers['followers_count']))

			if "@update@" in newline:
				padtitle += len("@update@")
				padtitle -= len(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
				newline = newline.replace("@update@", strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " "*padtitle)

		except: # this should probably be made to make a liittle prettier
			pass
			
		# Output
		sys.stdout.write(newline)

	# Before the refresh - every 15 mins
	time.sleep(900)

