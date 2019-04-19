#! /usr/bin/env python
# -*- coding: utf-8 -*-


import vk_api
import requests
import json
import time
import urllib

def get(url):
	try:
		return requests.get(url)
	except Exception:
		time.sleep(1)
		return get(url)

def get_hashtag():
	string = ''
	r=requests.get('https://hmtpk.ru/api/getnews.php?type=all&limit=1')
	obj = json.loads(r.text)
	tags = ['ХМТПК@hmtpk'] + obj[0]['tags'].split(', ')
	i = 0
	for tag in tags:
		tags[i] = '#'+tag + ' '
		string = string + tags[i]
		i+=1
	return string

def get_site_news(): # Получение последней новости с сайта
	r=requests.get('https://hmtpk.ru/api/getnews.php?type=all&limit=1')
	obj = json.loads(r.text)

	id = obj[0]['id']
	date = obj[0]['date'] 
	name = obj[0]['name']
	text = obj[0]['text']
	url = 'https://hmtpk.ru'+obj[0]['link'][0:-9]
	media_url = 'https://hmtpk.ru/'+obj[0]['picture']
	return id,date,name,text,url,media_url

def clear_from_hashtag(text):
	clear_hashtag = text.split('Подробности по ссылке ниже')
	return clear_hashtag[0]

def short_url(url):
	short_url = vk_group.method('utils.getShortLink',{'url':url})['short_url']
	return short_url

def upload_image(url):
	img = urllib.request.urlopen(url).read()
	out = open("img.jpg", "wb")
	out.write(img)
	out.close()
	img = vk_group.method('photos.getMessagesUploadServer')
	data_upload_server = img['upload_url']
	r = requests.post(data_upload_server, files = {'photo': open('img.jpg', 'rb')})
	answer = r.json()
	server = answer['server']
	photo = answer['photo']
	hash = answer['hash']
	upload_results = vk_group.method('photos.saveMessagesPhoto',{'photo':photo,'server':server,'hash':hash})

	attachment = 'photo{}_{}'.format(upload_results[0]['owner_id'], upload_results[0]['id'])
	return attachment

def write_msg(user_id, message,attachment):  # Функция отправки сообщений
	vk_group.method('messages.send', {'user_id':user_id,'message':message,'attachment':attachment,'dont_parse_links':1})

def send_post_from_group(vk_group_id,offset,user_id):
	post = vk_service.method('wall.get', {'owner_id': vk_group_id,"type": "text",'offset':offset,'count':1})
	text = clear_from_hashtag(post['items'][0]['text'])
	url = short_url(post['items'][0]['attachments'][0]['link']['url'])
	media_url = post['items'][0]['attachments'][0]['link']['photo']['sizes'][0]['url']
	message = text+'\n'+'Подробности по ссылке ниже.'+'\n'+'\n'+url
	attachment = upload_image(media_url)
	write_msg(user_id,message,attachment)

def send_post_from_site(user_id):
	id,date,name,text,url,media_url = get_site_news()
	attachment = upload_image(media_url)
	url = short_url(url)
	message = name+'\n'+'\n'+text+'\n'+'\n'+'Подробности по ссылке ниже.'+'\n'+'\n'+url
	write_msg(user_id,message,attachment)

def wall_post(owner_id):
	id,date,name,text,url,media_url = get_site_news()
	attachment = upload_image(media_url)
	tags = get_hashtag()
	message = name+'\n'+'\n'+text+'\n'+'\n'+'Подробности по ссылке ниже.'+'\n'+'\n'+tags
	vk_group_user.method('wall.post',{'owner_id':owner_id,'message':message,'from_group':1,'attachments':url})

def get_user_from_file():
	f = open('test.txt')
	l = [line.strip() for line in f]
	f.close()
	return l


access_token = 'Здесь должен быть токен'
service_token = 'И тут'
user_access_token = 'Тут тоже'

vk_group = vk_api.VkApi(token = access_token) # Авторизация группы
vk_service = vk_api.VkApi(token = service_token) # Авторизация приложения
vk_group_user = vk_api.VkApi(token = user_access_token) # Работа с группой от имени моего аккаунта


r=requests.get('https://hmtpk.ru/api/getnews.php?type=all&limit=1')
obj = json.loads(r.text)
id = obj[0]['id']


while True:
	print('New iteration')
	try:
		r=get('https://hmtpk.ru/api/getnews.php?type=all&limit=1')
		obj = json.loads(r.text)
		id_change = obj[0]['id']

		if id_change != id: # Если он изменился
			print('find new news')
			f = open('old_news.txt','r')

			for line in f:
				old_news_id = [line.strip() for line in f]
			f.close()

			if id_change not in old_news_id:
				try:
					print('posting...')
					wall_post(-122421776)
					user_list = get_user_from_file()

					for user in user_list:
						try:
							print('send post to user...')
							send_post_from_site(user)
					
						except Exception:
							print('error: cant sand post to user')
							continue

						finally:
							time.sleep(0.3)

					old_news_id.append(id_change)
					f = open('old_news.txt','w')
					print('write new news_id')
					for i in old_news_id:
						f.write(str(i)+'\n')

					f.close()

				except Exception:
					print('error: to try post and send')
					continue

				finally:
					id = id_change # Запомнить новый id поста
	except Exception:
		print('global error')
		continue
	time.sleep(60)