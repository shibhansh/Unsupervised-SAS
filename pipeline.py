from __future__ import division
import codecs
import os
import pickle
import nltk
import collections
import operator
import sys
import copy
from matplotlib import pylab
from nltk.corpus import stopwords
import networkx as nx
import matplotlib.pyplot as plt

from read_data import *
from resolve_coref import *
from generate_document_graph import *
from tok_std_format_conversion import *
from directed_graph import Graph
from amr import AMR

def save_stories(stories,path=''):
	if path == '':
		path = dataset+"/stories_"+dataset+".txt"
	os.system("touch "+path)
	f = codecs.open(path,'w')
	for i in range(0,len(stories)):
		f.write(stories[i])
		f.write('\n')
	f.close()


def main(arguments):
	parser = argparse.ArgumentParser(
		description=__doc__,
		formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--input_file', help="Path of the file containing AMRs of each sentence", type=str, 
				default='/home/shibhansh/UGP-2/data/LDC2015E86_DEFT_Phase_2_AMR_Annotation_R1/' + \
				'data/amrs/split/test/deft-p2-amr-r1-amrs-test-alignments-proxy.txt')
	parser.add_argument('--dataset', help="Name of dataset",
				type=str, default='')
	parser.add_argument('--display', help="Path of the file containing AMRs of each sentence",
				type=bool, default=False)

	args = parser.parse_args(arguments)

	input_file = args.input_file
	dataset = args.dataset

	'''
	'docs' is a list of 'documents', each 'document' is list a dictionary. Each dictionary contains
	information about a sentence. Each dicitonary has 'alignments', 'amr' etc. keys. Corresponding
	to each key we have the relevant information like the amr, text, alignment etc.
	'''

	# Remove alignments from the new file
	os.system('cp '+ input_file +' auxiliary/temp')
	with codecs.open('auxiliary/temp', 'r') as data_file:
		original_data = data_file.readlines()

	os.system('sed -i \'s/~e.[	0-9]*//g\' auxiliary/temp')
	os.system('sed -i \'s/,[	0-9]*//g\' auxiliary/temp')

	with codecs.open('auxiliary/temp', 'r') as data_file:
		data = data_file.readlines()
	for index_line,line in enumerate(data):
		if line.startswith('#'):
			data[index_line] = original_data[index_line]

	with codecs.open('auxiliary/temp', 'w') as data_file:
		for line in data:
			data_file.write(line)

	input_file = 'auxiliary/temp'

	docs, target_summaries, stories = read_data(input_file)

	os.system('rm auxiliary/temp')
	save_stories(stories,'auxiliary/stories.txt')

	with open('auxiliary/target_summaries.txt','w') as f:
		for summary in target_summaries:
			f.write(tok_to_std_format_convertor(summary)+'\n')
	idf = {}
	with open('auxiliary/'+dataset+'_idf.txt','r') as f:
		idf = pickle.load(f) 

	f = open('auxiliary/predicted_summaries.txt','w')
	summary_sentences_per_story = []
	# currently all the information of a node is stored as a list, changing it to a dictionary
	debug = False
	# 'document_amrs' is the list of document amrs formed after joining nodes and collapsing same entities etc.
	target_summaries_amrs = []
	predicted_summaries_amrs = []
	document_amrs = []
	selected_sents = []
	for index_doc, doc in enumerate(docs):
		current_doc_sent_amr_list = []
		current_target_summary_sent_amr_list = []
		for index_dict, dict_sentence in enumerate(doc):
			if dict_sentence['amr'] != []:
				if dict_sentence['tok'].strip()[-1] != '.': dict_sentence['tok'] = dict_sentence['tok'] + ' .' 
				# Get the AMR class for each sentence using just the text
				if dict_sentence['snt-type'] == 'summary':
					current_target_summary_sent_amr_list.append(AMR(dict_sentence['amr'],
													amr_with_attributes=False,
													text=dict_sentence['tok'],
													alignments=dict_sentence['alignments']))
				if dict_sentence['snt-type'] == 'body':
					docs[index_doc][index_dict]['amr'] = AMR(dict_sentence['amr'],
														amr_with_attributes=False,
														text=dict_sentence['tok'],
														alignments=dict_sentence['alignments'])
					current_doc_sent_amr_list.append(docs[index_doc][index_dict]['amr'])
		# merging the sentence AMRs to form a single AMR
		amr_as_list, document_text, document_alignments,var_to_sent = \
												merge_sentence_amrs(current_doc_sent_amr_list,debug=False)
		new_document_amr = AMR(text_list=amr_as_list,
							text=document_text,
							alignments=document_alignments,
							amr_with_attributes=True,
							var_to_sent=var_to_sent)
		document_amrs.append(new_document_amr)
		target_summaries_amrs.append(current_target_summary_sent_amr_list)

		# number of nodes required in summary

		imp_doc = index_doc
		# imp_doc = 1000
		if imp_doc == 1000:
			# just the first sentence of the story is the summary
			predicted_summaries_amrs.append([current_doc_sent_amr_list[0]])
		if imp_doc == 2000:
			# just the first two sentences of the story is the summary
			predicted_summaries_amrs.append([current_doc_sent_amr_list[0],current_doc_sent_amr_list[1]])
		if imp_doc == 3000:
			# just the first two sentences of the story is the summary
			predicted_summaries_amrs.append([current_doc_sent_amr_list[0],current_doc_sent_amr_list[1]\
												,current_doc_sent_amr_list[2]])
		if imp_doc == -1:
			# all sentences of the story is the summary
			predicted_summaries_amrs.append(current_doc_sent_amr_list)
		if index_doc == imp_doc:
			document_amrs[index_doc], phrases,idf_vars = resolve_coref_doc_AMR(amr=document_amrs[index_doc], 
									resolved=True,story=' '.join(document_amrs[index_doc].text),
									location_of_resolved_story='auxiliary/'+dataset+'_predicted_resolutions.txt',
									location_of_story_in_file=index_doc,
									location_of_resolver='.',
									idf=idf,
									debug=False)

			cn_freq_dict,cn_sent_lists,cn_var_lists=document_amrs[index_doc].get_common_nouns(phrases=phrases)
			idf_vars = document_amrs[index_doc].get_idf_vars(idf_vars=idf_vars,idf=idf)
		
			# range equal to the std_deviation of the summary size in the dataset
			if dataset == '':
				current_summary_nodes = []
				for target_summary_amr in current_target_summary_sent_amr_list:
					current_summary_nodes.extend(target_summary_amr.get_nodes() )

				num_summary_nodes = len(current_summary_nodes)
				range_num_nodes = 0
				range_num_nodes = int((len(document_amrs[index_doc].get_nodes())*4)/100)

			document_amrs[index_doc].get_concept_relation_list(story_index=index_doc,debug=False)

			pr = document_amrs[index_doc].directed_graph.rank_sent_in_degree()

			# rank the nodes with the 'meta_nodes'
			pr = document_amrs[index_doc].directed_graph.rank_with_meta_nodes(var_freq_list=pr,
																			cn_freq_dict=cn_freq_dict,
																			cn_sent_lists=cn_sent_lists,
																			cn_var_dict=cn_var_lists)
			ranks, weights, _ = zip(*pr)
			print ranks
			print weights

			pr = document_amrs[index_doc].directed_graph.add_idf_ranking(var_freq_list=pr,
																		default_idf=5.477,
																		idf_vars=idf_vars,
																		num_vars_to_add=5)

			ranks, weights, _ = zip(*pr)
			print ranks
			print weights

			new_graph = document_amrs[index_doc].directed_graph.construct_greedily_first(ranks=ranks,weights=weights,
							concept_relation_list=document_amrs[index_doc].concept_relation_list,
							use_true_sent_rank=False,num_nodes=num_summary_nodes,range_num_nodes=range_num_nodes)

			# generate AMR from the graphical representation
			new_amr_graph = document_amrs[index_doc].get_AMR_from_directed_graph(sub_graph=new_graph)
			new_amr_graph.print_amr()
			predicted_summaries_amrs.append([new_amr_graph])

	with open('auxiliary/'+dataset+'_eos_stories.txt','w') as f:
		for document_amr in document_amrs:
			f.write(' <eos> '.join(document_amr.text)+'\n')

	f.close()
	with open('auxiliary/num_sent_per_story.txt','w') as f3:
		pickle.dump(summary_sentences_per_story,f3)
	# save document AMR in file
	with open('auxiliary/text_amr.txt','w') as f2:
		f2.write('# :id PROXY_AFP_ENG_20050317_010.10 ::amr-annotator SDL-AMR-09  ::preferred ::snt-type body\n')
		f2.write('# ::snt On 21 March 2005\n')
		f2.write('# ::tok On 21 March 2005\n')
		if imp_doc >= 0 and imp_doc < len(document_amrs):
			for index_node, node in enumerate(document_amrs[imp_doc].amr):
				f2.write('\t'*node['depth']+node['text']+'\n')

	target_summaries_nodes = []
	for target_summary_amrs in target_summaries_amrs:
		current_summary_nodes = []
		for target_summary_amr in target_summary_amrs:
			# current_summary_nodes.extend(target_summary_amr.get_edge_tuples() )
			current_summary_nodes.extend(target_summary_amr.get_nodes() )
		target_summaries_nodes.append(current_summary_nodes)

	target_summary_lengths = [len(i) for i in target_summaries_nodes]
	document_lengths = [len(i.get_nodes()) for i in document_amrs]

	ratios = []
	for i in range(len(document_lengths)):
		ratios.append(float(target_summary_lengths[i]/document_lengths[i])*100)

	average_ratio = (float(sum(ratios)) / len(ratios))
	deviations = [abs(ratio - average_ratio) for ratio in ratios]

	mean_deviation = (float(sum(deviations)) / len(deviations))

	# average ratio in 'gold' dataset is 9%, and deviation is 4%
	print 'average_ratio', average_ratio, 'mean_deviation', mean_deviation

	with open('auxiliary/target_summary_nodes.txt','w') as f6:
		for node_list in target_summaries_nodes:
			f6.write(' '.join([node for node in node_list]) + '\n')

	predicted_summaries_nodes = []
	for predicted_summary_amrs in predicted_summaries_amrs:
		current_summary_nodes = []
		for predicted_summary_amr in predicted_summary_amrs:
			# current_summary_nodes.extend(predicted_summary_amr.get_edge_tuples() )
			current_summary_nodes.extend(predicted_summary_amr.get_nodes() )
		predicted_summaries_nodes.append(current_summary_nodes)

	with open('auxiliary/predicted_summary_nodes.txt','w') as f7:
		for node_list in predicted_summaries_nodes:
			f7.write(' '.join([node for node in node_list]) + '\n')

if __name__ == '__main__':
	sys.exit(main(sys.argv[1:]))
