import pandas as pd
import numpy as np
import matplotlib
import sys
import http.client
import json
import re
import math
import difflib
from multiprocessing import Pool, Value, Lock, Process
from datetime import datetime
startTime = datetime.now()

def process_data(filename):
	# takes filename, returns cleaned dataframe
	fp = filename
	df = pd.read_table(fp)
	#unique.to_csv('unique.csv', sep='\t', encoding='utf-8')
	to_strip = ['+ Q&A', '+ Panel Discussion', "Director's Cut", "(Director's Cut)", "3D", 
				"MA15+", "M15+", "R18+", "15+", "18+", "(M)", "(G)", "(PG)", "(3D)" 
				"By Request >", "By Request>", "15", "18", "Director Q&A", "+ lecture", "+ short",
				"+ panel discussion", "#"]
	df.dropna(subset=['Title'], inplace=True)
	
	for movie in df.Title:
		for x in to_strip:
			if x in movie:
				#print(x)
				#print(movie)
				stripped = re.sub(re.escape(x), '', movie, flags=re.M)
				df['Title'] = df['Title'].replace(movie, stripped)
				#print(stripped)

	index = 0
	for movie in df.Title:
		if '+' in movie and movie not in ["Romeo + Juliet"]:
			#if format is "movie1 + movie2", split record & create another row with same date
			movie2 = movie.split("+", 1)[1]
			print(movie2)
			print(df.get_value(index, 'Day'))
			extra = pd.DataFrame(np.array([df.get_value(index, 'Day'), 
					df.get_value(index, 'Date'),
					df.get_value(index, 'Time'), 
					df.get_value(index, 'Place'), movie2, 
					df.get_value(index, 'Rating')]).reshape(1,6), 
					columns=['Day', 'Date', 'Time', 'Place', 'Title', 'Rating'])
			#print(extra)
			frames = [df, extra]
			df = pd.concat(frames, ignore_index=True)
		index += 1

	df.to_csv('final3.csv', sep='\t', encoding='utf-8')
	return df

def tmdb_query(query):
# takes string keyword/phrase to be queried (i.e. name of movie), returns matching TMDB movie ID
	conn = http.client.HTTPSConnection("api.themoviedb.org")
	payload = "{}"
	api_key = "ebe089b151a80b2e62133c729c577949"

	keyword = query.replace(' ', '+')

	conn.request("GET", "/3/search/movie?page=1&query={}&api_key={}".format(keyword, api_key), payload)

	res = conn.getresponse()
	data = res.read()
	data = data.decode("utf-8")
	data = json.loads(data)
	#print(data
	selection = []
	final = []
	if 'results' in data:
		selection = data['results']
	else:
		return final
	

	#ONLY ITERATE IF THERE IS MORE THAN ONE RECORD
	#iterating through movie json array to check for exact title matches 
	# USE get_close_matches instead!!!!!!
	#print(selection)

	if data['total_results'] > 1:
		for movie in selection:
			if movie['title'].lower() == query.lower():
				final.append(movie)
		if not final:
			return selection
		return final
	else:
		return selection
	#if there is more than one ~matching~ title: check release date with screening date
	#print(query)

	#POSSIBILITIES:
	#there is only one matching entry => return selection
	#there are multiple exact name matches => check release date => return final
	#there are no exact name matches => return selection


def get_credits(movieid):
# takes movie_id integer argument, returns json object of credits
# USE &append_to_response=credits FOR CREDITS ON A FILM
# or https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key=<<api_key>>
	conn = http.client.HTTPSConnection("api.themoviedb.org")
	payload = "{}"
	api_key = "ebe089b151a80b2e62133c729c577949"

	conn.request("GET", "/3/movie/{}?api_key={}&append_to_response=credits".format(movieid, api_key), payload)

	res = conn.getresponse()
	data = res.read()
	data = data.decode("utf-8")
	data = json.loads(data)
	#print(data)
	return data

from itertools import repeat, product

def check_attribute(ns, att_str, index, movieid):
	result = get_credits(movieid)
	if att_str in result.keys():
		att = result[att_str]
		ns.df = ns.df.set_value(index, att_str, att)
		print(att_str)

def process_query(movie, ns):
	print(movie)
	#print(tmdb_query(movie))
	#print(result)
	index = ns.df.index[ns.df['Title'] == movie].tolist()[0]
	print(index)
	movie = ''.join([i if ord(i) < 128 else ' ' for i in movie])
	if tmdb_query(movie) == [] or not movie: #if no results exist for the query
		print("no entry")
		return master
	try:
		result = tmdb_query(movie)[0]
	except IndexError:
		return master
	movie_id = result['id']
	info = get_credits(movie_id)
	check_attribute(ns, 'original_language', index, movie_id)
	check_attribute(ns, 'release_date', index, movie_id)
	check_attribute(ns, 'budget', index, movie_id)
	check_attribute(ns, 'revenue', index, movie_id)
	check_attribute(ns, 'runtime', index, movie_id)

	if 'genres' in info.keys():
		genres = []
		for genre in info['genres']:
			genres.append(genre['name'])
		ns.df = ns.df.set_value(index, 'genre', genres)

	print(movie_id)
	ns.df = ns.df.set_value(index, 'tmdb_id', movie_id)
	if 'credits' in info.keys():
		credits = info["credits"]
		crew = credits["crew"] 
		director = ''
		for person in crew:
			if person['job'] == 'Director':
				director = person['name']
		#cast_female = credits["cast"] # gender == 1
		#cast_male = len(list) - cast_female # gender == 0 or 2
		#crew_female =
		#crew_male =
		if director:
			ns.df = ns.df.set_value(index, 'director', director)
	ns.df.to_csv('final3.csv', sep='\t', encoding='utf-8')
	print(index)
	return master

print(get_credits(500))
df = process_data("acmi-historic-film-screenings-data.tsv")

df = df.Title.unique()
df = pd.DataFrame(df, columns=['Title'])

attributes = ['Day', 'Date', 'Time', 'Place', 'Title', 'Rating', 'tmdb_id', 
			'original_language', 'release_date',
			'budget', 'revenue', 'runtime', 'genre', 'director', 'cast']
df = df.reindex(columns=attributes)
df['director'] = df['director'].astype(str)
df['original_language'] = df['original_language'].astype(str)
df['release_date'] = df['release_date'].astype(str)
df['budget'] = df['budget'].astype(float)
df['revenue'] = df['revenue'].astype(float)
df['runtime'] = df['runtime'].astype(float)
df['genre'] = df['genre'].astype(list)

from multiprocessing import Manager
from itertools import repeat
master = df

mgr = Manager()
ns = mgr.Namespace()
ns.df = master

print(ns.df)

if __name__ == '__main__':
	p = Pool(5)
	length = list(range(len(master.index)+1))
	titles = ns.df['Title'].tolist()
	args = zip(ns.df['Title'].tolist(), repeat(ns))
	p.starmap(process_query, args)
	p.close()
	sys.exit()

'''
col = ['Day', 'Date', 'Time', 'Place']
df = process_data("acmi-historic-film-screenings-data.tsv")
df = df.drop_duplicates(subset='Title')
screening_data = pd.DataFrame(df, columns=col)
screening_data = screening_data.reset_index()
print(screening_data)
tmdb_data = pd.read_csv("final-unique.csv", sep='\t')
tmdb_data = tmdb_data.drop(tmdb_data.columns[0], axis=1)
tmdb_data = tmdb_data.drop(col, axis=1)
tmdb_data = pd.concat([screening_data, tmdb_data], axis=1)
#print(tmdb_data)
tmdb_data.to_csv('final_tmdb.csv', sep='\t', encoding='utf-8')
print(datetime.now() - startTime)

'''


