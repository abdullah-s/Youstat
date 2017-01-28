import json
import re
import urllib
import requests
import os
import sys

from HTMLParser import HTMLParser
htmlParser = HTMLParser()

# import ipdb; ipdb.set_trace()

API_KEY = os.environ['YOUTUBE_API_KEY']

# CHANNEL_NAME = "nigahiga" # CHANNEL WITHOUT AUTO SUBTITLES BUT WITH MANUAL SUBTITLES
# CHANNEL_NAME = "KSIOlajidebt" # CHANNEL WITHOUT MANUAL SUBTITLES BUT WITH AUTO SUBTITLES

PAGE_SIZE = 50 # get one vid only 50 max
TOP_WORDS_SIZE = 30 # the top 30 frequent words

stopwords = ['a', 'about', 'above', 'across', 'after', 'afterwards']
stopwords += ['again', 'against', 'all', 'almost', 'alone', 'along']
stopwords += ['already', 'also', 'although', 'always', 'am', 'among']
stopwords += ['amongst', 'amoungst', 'amount', 'an', 'and', 'another']
stopwords += ['any', 'anyhow', 'anyone', 'anything', 'anyway', 'anywhere']
stopwords += ['are', 'around', 'as', 'at', 'back', 'be', 'became']
stopwords += ['because', 'become', 'becomes', 'becoming', 'been']
stopwords += ['before', 'beforehand', 'behind', 'being', 'below']
stopwords += ['beside', 'besides', 'between', 'beyond', 'bill', 'both']
stopwords += ['bottom', 'but', 'by', 'call', 'can', 'cannot', 'cant']
stopwords += ['co', 'computer', 'con', 'could', 'couldnt', 'cry', 'de']
stopwords += ['describe', 'detail', 'did', 'do', 'done', 'dont', 'down', 'due']
stopwords += ['during', 'each', 'eg', 'eight', 'either', 'eleven', 'else']
stopwords += ['elsewhere', 'empty', 'enough', 'etc', 'even', 'ever']
stopwords += ['every', 'everyone', 'everything', 'everywhere', 'except']
stopwords += ['few', 'fifteen', 'fifty', 'fill', 'find', 'fire', 'first']
stopwords += ['five', 'for', 'former', 'formerly', 'forty', 'found']
stopwords += ['four', 'from', 'front', 'full', 'further', 'get', 'give']
stopwords += ['go', 'had', 'has', 'hasnt', 'have', 'he', 'hence', 'her']
stopwords += ['here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers']
stopwords += ['herself', 'him', 'himself', 'his', 'how', 'however']
stopwords += ['hundred', 'i', 'im', 'ive', 'ie', 'if', 'in', 'inc', 'indeed']
stopwords += ['interest', 'into', 'is', 'it', 'its', 'itself', 'just', 'keep']
stopwords += ['last', 'latter', 'latterly', 'least', 'less', 'ltd', 'made']
stopwords += ['many', 'may', 'me', 'meanwhile', 'might', 'mill', 'mine']
stopwords += ['more', 'moreover', 'most', 'mostly', 'move', 'much']
stopwords += ['must', 'my', 'myself', 'name', 'namely', 'neither', 'never']
stopwords += ['nevertheless', 'next', 'nine', 'no', 'nobody', 'none']
stopwords += ['noone', 'nor', 'not', 'nothing', 'now', 'nowhere', 'of']
stopwords += ['off', 'often', 'on','once', 'one', 'only', 'onto', 'or']
stopwords += ['other', 'others', 'otherwise', 'our', 'ours', 'ourselves']
stopwords += ['out', 'over', 'own', 'part', 'per', 'perhaps', 'please']
stopwords += ['put', 'rather', 're', 's', 'same', 'see', 'seem', 'seemed']
stopwords += ['seeming', 'seems', 'serious', 'several', 'she', 'should']
stopwords += ['show', 'side', 'since', 'sincere', 'six', 'sixty', 'so']
stopwords += ['some', 'somehow', 'someone', 'something', 'sometime']
stopwords += ['sometimes', 'somewhere', 'still', 'such', 'system', 'take']
stopwords += ['ten', 'than', 'that', 'the', 'their', 'them', 'themselves']
stopwords += ['then', 'thence', 'there', 'thereafter', 'thereby']
stopwords += ['therefore', 'therein', 'thereupon', 'these', 'they']
stopwords += ['thick', 'thin', 'third', 'this', 'those', 'though', 'three']
stopwords += ['three', 'through', 'throughout', 'thru', 'thus', 'to']
stopwords += ['together', 'too', 'top', 'toward', 'towards', 'twelve']
stopwords += ['twenty', 'two', 'un', 'under', 'until', 'up', 'upon']
stopwords += ['us', 'very', 'via', 'was', 'we', 'well', 'were', 'what']
stopwords += ['whatever', 'when', 'whence', 'whenever', 'where']
stopwords += ['whereafter', 'whereas', 'whereby', 'wherein', 'whereupon']
stopwords += ['wherever', 'whether', 'which', 'while', 'whither', 'who']
stopwords += ['whoever', 'whole', 'whom', 'whose', 'why', 'will', 'with']
stopwords += ['within', 'without', 'would', 'yet', 'you', 'your']
stopwords += ['yours', 'youre', 'yourself', 'yourselves']

def channel_url(name):
	return "https://www.googleapis.com/youtube/v3/channels?part=contentDetails&forUsername="+name+"&key="+API_KEY

def get_channel(name):
	return get_json(channel_url(name))

def playlist_url(id, token):
	url = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails&maxResults="+ str(PAGE_SIZE) +"&playlistId="+id+"&key="+API_KEY
	return url + (("&pageToken=" + token) if token else "")

def uploads_id(channel):
	return channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']

def latest_sub(videos_manual_subs, videos_auto_subs):
	if videos_manual_subs:
		return videos_manual_subs[0][1]
	if videos_auto_subs:
		return videos_auto_subs[0][1]

def video_id(vid):
	return vid['contentDetails']['videoId']

def is_video(vid):
	return ('videoId' in vid['contentDetails'])

def format_subtitles(subtitles):
	subtitles = htmlParser.unescape(htmlParser.unescape(subtitles))
	subtitles = subtitles.replace('</text>', '\n')
	subtitles = re.sub('<.*?>', '', subtitles)
	return subtitles

def get_json(url):
	page = requests.get(url) # gets the content of the url that fetches the videos
	return json.loads(page.text) # parses the content

def get_manual_sub(video_id):
	subtitle = requests.get('http://video.google.com/timedtext?lang=en&v='+video_id).text
	return (video_id, format_subtitles(subtitle) if subtitle else  None)

def sub_url(response):
	matches = re.findall("\"caption_tracks\".*?(https.*lang\%3D(..))", response)
	if matches:
		url, lang = matches[0]
		if lang == 'en':
			return urllib.unquote(url).decode('utf8')
	return None

def get_auto_sub(video_id):
	video_page = requests.get('http://youtube.com/watch?v='+video_id).text
	url = sub_url(video_page)
	if url:
		subtitle = requests.get(url).text
		return (video_id, format_subtitles(subtitle) if subtitle else None)
	return (video_id, None)

def split_results(results):
	oks = []
	errs = []
	for (id, result) in results:
		if result:
			oks += [(id, result)]
		else:
			errs += [id]
	return (oks, errs)


def get_subtitle_statistics(sub):
	r = requests.post(url = 'https://tone-analyzer-demo.mybluemix.net/api/tone',
		data = {'text': sub},
		headers={'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'})
	return json.loads(r.text)

def get_playlist(channel, token=None):
	playlist = get_json(playlist_url(uploads_id(channel), token))
	if 'nextPageToken' in playlist['items']:
		return playlist['items'] + get_playlist(playlist['nextPageToken'])
	else:
		return playlist['items']

def words_frequency(manual_subs, auto_subs):
	def sort_words_by_freq(words):
		return sorted(words.items(), key=lambda v: v[1], reverse=True)

	def rm_stop_words(subtitle):
		regex = r'\b('+'|'.join(stopwords)+r')\b'
		sub_clean_1 = re.sub('[?!,.\(\)\[\]]', ' ', subtitle)
		sub_clean_2 = re.sub('[\'"-]', '', sub_clean_1)
		clean_subtitle = re.sub(regex, '', sub_clean_2, flags=re.IGNORECASE)
		return clean_subtitle

	def count_words(subtitle, words=None):
		words = words if words else {}
		for word in subtitle.split():
			if word in words:
				words[word] += 1
			else:
				words[word] = 1
		return words

	def process_subs(subtitles):
		words = {}
		for id, subtitle in subtitles:
			clean_subtitle = rm_stop_words(subtitle)
			words = count_words(clean_subtitle, words)
		return words

	words = process_subs(manual_subs + auto_subs)
	return sort_words_by_freq(words)[0:TOP_WORDS_SIZE]

def beautify_stats(stats):
	def beautify_category(category):
		scores = map(lambda x: x['score'], category['tones'])
		scores_sum = reduce(lambda x,y: x+y, scores)
		tones = [ { tone['tone_name']: (tone['score'] / scores_sum) * 100
					} for tone in category['tones'] ]
		return { 'category_name': category['category_name'], 'tones': tones }
	return map(beautify_category, stats['document_tone']['tone_categories'])

def get_stats(channel_name):
	channel_name = channel_name
	channel = get_channel(channel_name)
	items = get_playlist(channel)
	video_ids = [video_id(item) for item in items if is_video(item)]

	manual_subs, video_ids_no_manual_subs = (
		split_results([get_manual_sub(i) for i in video_ids]) )

	auto_subs, video_ids_no_auto_subs = (
		split_results([get_auto_sub(i) for i in video_ids_no_manual_subs]) )

	if manual_subs or auto_subs:
		# frequent_words = words_frequency(manual_subs, auto_subs)
		sub = latest_sub(manual_subs, auto_subs)
		stats = get_subtitle_statistics(sub)
		beautiful_stats = beautify_stats(stats)
		return beautiful_stats
	else:
		return "No english subtitles in this channel: "+channel_name

def main():
	channel_name = sys.argv[1]
	print get_stats(channel_name)

if __name__ == '__main__':
	main()