import codecs
import sys
import os
import pickle
import nltk
from nltk.corpus import stopwords
import collections
import operator
import sys
reload(sys)  
sys.setdefaultencoding('utf8')
sys.path.append('/home/shibhansh/UGP-2/src/preprocessing')
sys.path.append('/home/shibhansh/UGP-2/src/extractive_summarization')
from concept import Concept

trivial_output = 0

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class concept_relation_list(object):

	def __init__(self,graph,index_to_var={},story_index=0,var_list=[],aligned_vars=[],text=[]):
		# self.var_list = var_list

		self.index_to_var = index_to_var
		self.var_list = var_list
		self.aligned_vars = set(aligned_vars)
		self.graph = graph
		self.text = ' '.join(text)

		self.sent_to_concept_indices = {}
		self.sent_to_partner_indices = {}
		for i in range(100):	self.sent_to_partner_indices[i] = []
		for i in range(100):	self.sent_to_partner_indices[i] = []
		self.concept_list = []
		self.concept_names = []
		self.partners = []

		self.get_concepts_story(story_index=story_index)
		self.concepts_to_vars()

	# Creating var sets corresponding to Concepts set
	def get_var_set(self,start_index=0,end_index=-1):
		# return var_set given the index range to search from
		var_set = []
		# print self.index_to_var.keys()
		for index in range(start_index,end_index):
			try:	new_var_set = self.index_to_var[str(index)]
			except:	continue
			var_set.extend(new_var_set)
		var_set = list(set(var_set))
		return var_set

	def concepts_to_vars(self):
		concept_num = 0
		for sent_index, sent_tuple_list in enumerate(self.tuples):
			# print sent_tuple_list
			# saves the concepts inside of each tuple
			current_tuple_concept_list = []
			# add concept object in concepts list
			for _tuple in sent_tuple_list:
				for key in _tuple.keys():
					if key in ['text','confidence']:
						# print _tuple[key]
						continue
					for pair in _tuple[key]:
						start_index = pair[0]
						end_index = pair[1]

						# get var set from the given range of words
						var_set = self.get_var_set(start_index=start_index,end_index=end_index)
						# print 'var_set', var_set

						# connect un-connected componets of the concept
						relevant_text = self.text.split()[pair[0]:pair[1]]
						# print relevant_text

						var_set, _ = self.graph.connect_unconnected_components(nodes=var_set)
						var_set = set(var_set)
						# print 'var_set ', var_set
						# create the concept
						self.concept_list.append(Concept(name='concept'+str(concept_num),var_set=var_set,
													sent_index=sent_index,lable=key))
						current_tuple_concept_list.append(concept_num)
						# add in sent_to_concept_indices list
						try:	self.sent_to_concept_indices[sent_index].append(concept_num)
						except:	self.sent_to_concept_indices[sent_index] = [concept_num]
						concept_num += 1
				# updating the full partners list
				self.partners.append(current_tuple_concept_list)
				self.concept_names.extend(current_tuple_concept_list)
				# updating sent_to_partner_indices list
				try:	self.sent_to_partner_indices[sent_index].append(current_tuple_concept_list)
				except:	self.sent_to_partner_indices[sent_index] = [current_tuple_concept_list]

				# set partners for each concept in the concept list
				for concept in self.concept_list:
					if concept.name in current_tuple_concept_list:
						concept.add_partners(current_tuple_concept_list)

	def get_concepts_story(self,story_index=0,concept_file_path='auxiliary/open_ie_std_output'):
		with open(concept_file_path,'r') as f:
			concepts = pickle.load(f)
		relevant_tuples = []
		try:	relevant_tuples = concepts[story_index]
		except:	pass
		# relevant_tuples is a list
		# each element of this list has list of tuples corresponding to each sentence
		# each element of sentence list is a tuple
		# Format of tuple - dict {Label - [[start,end],..]} ex. - {'Relation'-[0,5]..}; 
		# indices correspond to word location in story - story.split()[start_index:end_index], will be the text
		self.tuples = relevant_tuples
		# print self.tuples
		return relevant_tuples

	# Return tuples given path
	def get_concepts_given_path(self,path=[],sent_index=-1):
		list_var_set = self.get_list_var_sets(sent_index)
		# don't look for vars that have no alignments
		original_path = list(path)
		path = set(path).intersection(self.aligned_vars)
		# print 'list_var_set', list_var_set, len(list_var_set)
		possible_var_sets = []
		# print path
		for var_set in list_var_set:
			# print var_set, path - var_set
			if set(path).issubset(var_set):
				# print 'yes!', var_set
				var_set, _ = self.graph.connect_unconnected_components(nodes=list(set( list(var_set)+original_path) ))
				var_set = set(var_set)
				possible_var_sets.append(var_set)
				# print 'new -', var_set
				# return list(var_set)
		# print bcolors.HEADER, 'possible_var_sets', possible_var_sets, len(possible_var_sets), bcolors.ENDC
		# if len(possible_var_sets):	print 'largest var set-', max(possible_var_sets, key=lambda coll: len(coll))
		if len(possible_var_sets):	return max(possible_var_sets, key=lambda coll: len(coll))

		temp = []
		for key in self.index_to_var:
			temp.extend(self.index_to_var[key])

		global trivial_output
		trivial_output += 1
		print 'num cases where no concept found - ', trivial_output
		# return the full sentence AMR
		return -1
		print 'returning trivial'
		return set(self.graph.connect_unconnected_components( nodes=list(set(original_path)) ))

	def get_list_var_sets(self,sent_index=-1):
		# given sent index, return a list of var sets, element in var set corresponds to set of all vars in a tuple 
		list_var_set = []
		for concept_indices in self.sent_to_partner_indices[sent_index]:
			new_set = set()
			for concept_index in concept_indices:
				new_set = new_set.union(self.concept_list[concept_index].var_set)
			list_var_set.append(new_set)
		return list_var_set

	# Debug functions
	def print_tuples(self,):
		# with open('stories.txt','r') as f:
		# 	stories = f.readlines()
		for sent_index, sent_tuple_list in enumerate(self.tuples):
			for _tuple in sent_tuple_list:
				for key in _tuple.keys():
					if key in ['text','confidence']:
						print _tuple[key]
						continue
					for pair in _tuple[key]:
						print key, 
						relevant_text = self.text.split()[pair[0]:pair[1]]
						print relevant_text
				print ''
