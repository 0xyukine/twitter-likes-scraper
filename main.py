import threading
import requests
import json
import time
import os

from dotenv import load_dotenv, find_dotenv

BEARER = os.getenv('TOKEN')
USERNAME = os.getenv('USERNAME')

def get_likes():
	session = requests.Session()
	session.headers.update({"Authorization": BEARER})

	test = session.get("https://api.twitter.com/2/users/by/username/{}".format(USERNAME)).json()
	user_id = test["data"]["id"]

	exp = "expansions=attachments.media_keys,author_id"
	mf = "media.fields=height,url,width"
	mr = "max_results=100"
	pt = ""

	data = []
	media = []
	users = []

	try:
		while True:
			liked_tweets = session.get("https://api.twitter.com/2/users/{}/liked_tweets?{}&{}&{}{}".format(user_id, exp, mf, mr, pt)).json()
			data.append(liked_tweets["data"])
			media.append(liked_tweets["includes"]["media"])
			users.append(liked_tweets["includes"]["users"])
			if liked_tweets["meta"]["next_token"]:
				pt = "&pagination_token=" + liked_tweets["meta"]["next_token"]
			else:
				print("end of pagination")
				break
	except Exception as e:
		print(liked_tweets, e)
	finally:
		formatted = {
			"data":data,
			"media":media,
			"users":users
		}
		
		with open("tweets.json", 'w') as x:
			json.dump(formatted, x, indent=4)

def get_media_keys():
	media = {}

	with open('tweets.json', 'r') as x:
		tweets = json.load(x)

	print(len(tweets["data"]))

	for page in tweets["media"]:
		for i in page:
			try:
				media[i["media_key"]] = {
				"height":i["height"],
				"width":i["width"],
				"url":i["url"],
				"type":i["type"]
				}
			except Exception as e:
				print(e)

	print(len(media))
	with open('media.json', 'w') as x:
		json.dump(media, x, indent=4)

def get_user_ids():
	users = {}

	with open('tweets.json', 'r') as x:
		tweets = json.load(x)

	for page in tweets["users"]:
		for i in page:
			try:
				users[i["id"]] = {
				"name":i["name"],
				"username":i["username"]
				}
			except Exception as e:
				print(e)

	print(len(users))
	with open('users.json', 'w') as x:
		json.dump(users, x, indent=4)

def get_complete_json():
	data = {}

	with open('media.json', 'r') as x:
		media = json.load(x)
	with open('users.json', 'r') as x:
		users = json.load(x)
	with open('tweets.json', 'r') as x:
		tweets = json.load(x)

	for page in tweets["data"]:
		for i in page:
			try:
				tweet_media = {}
				for mk in i["attachments"]["media_keys"]:
					tweet_media[mk] = media[mk].copy()

				data[i["id"]] = {
				"text":i["text"],
				"author_id":i["author_id"],
				"author_username":users[i["author_id"]]["username"],
				"media":tweet_media
				}
			except Exception as e:
				print(i["text"])
				print(e)

	with open('complete.json', 'w') as x:
		json.dump(data, x, indent=4)

def get_images():
	with open('complete.json', 'r') as x:
		complete = json.load(x)

	path = "/mnt/e/twitter/"

	for c_key, c_val in complete.items():
		for image_key, image_val in c_val["media"].items():
			while True:
				if threading.activeCount() >= 20:
					time.sleep(2)
				else:
					break
			print(image_key, image_val)
			#img = requests.get(image_val["url"] + "?name=large").content
			filename = '{}{} - {}/{}'.format(path,c_val["author_id"],c_val["author_username"], image_val["url"].split("/")[-1])
			#os.makedirs(os.path.dirname(filename), exist_ok=True)
			x = threading.Thread(target=download, args=(image_val["url"],filename,))
			x.start()
			#with open(filename, 'wb') as handler:
			#	handler.write(img)

def download(url, filename):
	img = requests.get(url + "?name=large").content
	os.makedirs(os.path.dirname(filename), exist_ok=True)
	with open(filename, 'wb') as handler:
		handler.write(img)

#get_media_keys()
#get_user_ids()
#get_complete_json()
get_images()