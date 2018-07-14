from __future__ import division
import codecs
import sys
import os
import pickle
import nltk
import collections
import operator
import sys
from nltk.corpus import stopwords
from gensim.utils import lemmatize
from subprocess import call
from nltk.stem.porter import *
from itertools import chain
from directed_graph import Graph
from amr import AMR

total_to_merge = 0
total_merged = 0
stop = set(stopwords.words('english'))


def resolve_corefereces_document(location_of_resolver='.',story=''):
	with open(location_of_resolver+'input','w'):
		f.write(story)
	reslover_command = 'python '+location_of_resolver+'demo.py final '+location_of_resolver+'/input'
	call(reslover_command.split())

# assumes that coreference resolution has already been done.
# input - location of file where we have the resolved story and location of this story in the file
# returns - the clusters and stories
def get_resolved_clusters(location_of_resolved_story='',location_of_story_in_file=0):
	with open(location_of_resolved_story,'r') as f:
		resolved_stories = pickle.load(f)
	print 'len(resolved_stories)', len(resolved_stories), 'location_of_resolved_story ', location_of_resolved_story
	clusters, story, attention_weights = resolved_stories[location_of_story_in_file]
	attention_weights = [x[0] for x in attention_weights]
	return clusters, story, attention_weights

def word_to_alignment(amr,word='',sentence='',location_of_word=0):
	return amr.word_to_alignment(word,sentence,location_of_word)

def words_corresponding_to_clusteres(story=[],clusters=[],attention_weights=[],highlight_attention=False):
	# give clusters (indices) - finds the 'words' corresponding to it
	for cluster in clusters:
		print '\n',
		for reference in cluster:
			if highlight_attention:
				index_word_max_weight_attention, _=max(enumerate(attention_weights[reference[0]:reference[1]+1]),
														 key=operator.itemgetter(1))
				index_word_max_weight_attention += reference[0]
				word_max_weight_attention = story[index_word_max_weight_attention]
				print '[' , word_max_weight_attention, '] ',attention_weights[reference[0]:reference[1]+1],

			for i in range(reference[0],reference[1]+1):
				print story[i], ' ',
			print ',',
	print ''

def get_phrases(amr,story=[],clusters=[],attention_weights=[]):
	# give clusters (indices) - finds the 'words' corresponding to it
	phrases = []
	for cluster in clusters:
		for reference in cluster:
			index_word_max_weight_attention, _=max(enumerate(attention_weights[reference[0]:reference[1]+1]),
													 key=operator.itemgetter(1))
			index_word_max_weight_attention += reference[0]

			new_pharse_indices = [x for x in range(reference[0],reference[1]+1)]
			new_pharse_vars = []
			current_sent = story[:reference[0]].count('.')

			sent_start_index = -1
			try:	sent_start_index = len(story[:reference[0]])-list(reversed(story[:reference[0]])).index('.')
			except:	pass
			sent_start_index += 1

			sent_end_index = reference[0]
			try:	sent_end_index += story[reference[0]:].index('.')
			except:	pass

			sent_indices = [x for x in range(sent_start_index ,sent_end_index)]
			new_pharse = []
			new_pharse.append(index_word_max_weight_attention)
			new_pharse.append(new_pharse_indices)
			new_pharse.append(current_sent)
			new_pharse.append(sent_indices)
			phrases.append(new_pharse)

	return phrases

def resolve_coref_doc_AMR(amr,resolved=True,story='',
							location_of_resolved_story='',
							location_of_story_in_file=0,
							location_of_resolver='.',
							idf={},
							debug=False):
	global stop
	global total_to_merge
	global total_merged
	idf_dict = {} 

	if not resolved:
		resolve_corefereces_document(location_of_resolver='.',story=story)
	clusters, story, attention_weights = get_resolved_clusters(
										location_of_resolved_story=location_of_resolved_story,
										location_of_story_in_file=location_of_story_in_file)
	lStory = [word.lower() for word in story]

	highlight_attention = True
	if debug:	words_corresponding_to_clusteres(story=story,clusters=clusters,attention_weights=attention_weights
											,highlight_attention=highlight_attention)
	# Hardcoded merging - 
	# Maintain a list of alignments that are no longer useful and update them to point to the correct location
	stemmer = PorterStemmer()

	while amr.merge_named_entities_graph():
		total_merged += 1
		total_to_merge += 1

	if debug:	print '\n'*7
	# return amr, [], idf_dict
	for cluster in clusters:
		words_max_weight_attention =[]
		for reference in cluster:
			index_word_max_weight_attention, _ = max(enumerate(attention_weights[reference[0]:reference[1]+1]),
													 key=operator.itemgetter(1))
			index_word_max_weight_attention += reference[0]

			word_max_weight_attention = lStory[index_word_max_weight_attention]
			words_max_weight_attention.append(word_max_weight_attention)
		most_common_key_word_in_cluster=max(set(words_max_weight_attention),key=words_max_weight_attention.count)
		# try to use the most common word
		# if it doesn't exist use the one with highest attention weight

		# find the largest cluster
		largest_reference = []
		largest_reference_size = 0 
		indices_word_to_use = []

		for index, reference in enumerate(cluster):
			if largest_reference_size < (reference[1]-reference[0]):
				 largest_reference = lStory[reference[0]:reference[1]+1]
				 largest_reference_size = reference[1]-reference[0] 
			if reference[0] == reference[1]: index_word_to_use = 0 
			else:
				try:index_word_to_use=lStory[reference[0]:reference[1]+1].index(most_common_key_word_in_cluster)
				except ValueError: index_word_to_use = -1
			if index_word_to_use == -1:
				index_word_to_use, _ = max(enumerate(attention_weights[reference[0]:reference[1]+1]),
													 key=operator.itemgetter(1))
			index_word_to_use += reference[0]
			indices_word_to_use.append(index_word_to_use)

		index_word_to_use = indices_word_to_use[0]
		try:	first_var = amr.directed_graph.text_index_to_var[str(index_word_to_use)][0]
		except:	first_var = ''

		first_index_word_to_use = index_word_to_use
		temp_index = 1
		while first_var == '' and temp_index < len(indices_word_to_use):
			index_word_to_use = indices_word_to_use[temp_index]
			first_index_word_to_use = index_word_to_use
			try:	first_var = amr.directed_graph.text_index_to_var[str(index_word_to_use)][0]
			except:	first_var = ''
			total_to_merge += 1
			temp_index += 1

		if first_var != '':
			try:
				idf_dict[first_var] = idf[' '.join([word.split('/')[0] for word in lemmatize(' '.join(largest_reference))])]
			except KeyError:
				idf_dict[first_var] = 5.477 

		for index_word_to_use in indices_word_to_use[temp_index:]:
			try:
				new_var = amr.directed_graph.text_index_to_var[str(index_word_to_use)][0]
			except:	new_var = ''
			if debug:
				print 'first_var-', first_var, 'new_var-', new_var,  first_index_word_to_use, story[first_index_word_to_use],
				print index_word_to_use, story[index_word_to_use]
			total_to_merge += 1
			if first_var != '' and new_var != '':

				merged = amr.merge_nodes(first_var=first_var,second_var=new_var,debug=debug)
				if debug:
					print 'merged -', bool(merged)
				if merged:
					total_merged += 1
			elif debug: print 'Can not merge - No alignment found for atleast one of the cases'

	amr.reconstruct_amr()
	phrases = get_phrases(amr=amr,story=story,clusters=clusters,attention_weights=attention_weights)

	if debug:
		print 'total_merged:', total_merged, 'total_to_merge:', total_to_merge
		print 'Ratio:', total_merged/total_to_merge
	return amr, phrases, idf_dict
