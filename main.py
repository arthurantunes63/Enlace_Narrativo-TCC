from argparse import ArgumentParser
import os

from igraph import Graph
import pandas as pd
import spacy

from text.text import Book
from text.processedText import BookDoc
from text.utils.network import verticesToCsv, edgesToCsv
from text.utils.emotion import emotionGraphic

def main(args):
	if args.command == 'emotionAnalysis':
		nlp = spacy.load(args.spacyModel, disable = ["ner"])
	else:
		nlp = spacy.load(args.spacyModel)
	path = args.file
	book = Book(args.bookTitle)
	book.openBook(path = path).lowercaseBook().sliceBook('#######')
	bookDoc = BookDoc(book, nlp)

	if args.command == 'network':
		book.characters = bookDoc.extractCharacters()

		links, strength = bookDoc.buildNetwork()
		network = Graph(n = len(book.characters), edges = links, directed = False,
		                vertex_attrs = {'Name':book.characters},
		                edge_attrs = {'Weight':strength})
		mainNetwork = network.components().giant()

		mainNetworkCommunities = getattr(mainNetwork, args.communityAlg)(weights = mainNetwork.es['Weight'])

		mainNetworkNodeSize = getattr(mainNetwork, args.centralityMeasure)(directed = False)
		mainNetwork.vs['Size'] = mainNetworkNodeSize

		communityMembers = mainNetworkCommunities.as_clustering().membership
		mainNetwork.vs['Community'] = communityMembers

		verticesToCsv(mainNetwork, path = args.pathSave, fileName = f'{book.title} - vertices')
		edgesToCsv(mainNetwork, path = args.pathSave, fileName = f'{book.title} - edges')
		
	elif args.command == 'emotionAnalysis':
		lexiconPath = f'./data/lexicon/{args.lexicon}.txt'

		columns = ['Word', 'Emotion', 'Value']
		lexicon = pd.read_csv(lexiconPath, delim_whitespace = True, header = None, names = columns)
		y = bookDoc.analysisEmotion(lexicon, emotionPerChapter = args.perChapter)

		maxAxisX = book.chapterTotal
		emotionGraphic(book.title, args.pathSave, args.showEmotion, y, maxAxisX,
					   all = args.all, barGraph = args.bar,
					   extension = args.ext, perChapter = args.perChapter)

if __name__ == '__main__':
	# Main parser
	parser = ArgumentParser(prog = 'TCCAme', description = 'Enlace Narrativo: \
														TCC 4º INF - 2020 - IFPR Campus Cascavel\
									 			  		Arthur Antunes and Maria Edwarda.')

	parser.add_argument('-bt', '--bookTitle', type = str, help = 'The book Title.', required = True)
	parser.add_argument('-f', '--file', type = str, help = 'The book .txt path.',
						required = True)
	parser.add_argument('-sm', '--spacyModel', help = 'The english model of the library spaCy.',
						type = str, default = "en_core_web_lg")

	parser.add_argument('-ps', '--pathSave', help = 'Path to save the files.',
						type = str, required = True)


	subparsers = parser.add_subparsers(title = 'subcommands', description = "Commands for generate\
									    								 	 information extracted\
									    								 	 from the book",
									   dest = 'command', required = True)

	# Create the parser for the "network" command
	networkParser = subparsers.add_parser('network', help = 'Generates the network of the book.')
	networkParser.add_argument('-cm', '--centralityMeasure', help = 'The centrality measure.',
							   choices = ["betweenness", "page_rank"], default = "betweenness")
	networkParser.add_argument('-ca', '--communityAlg', help = 'The community detection algorithm.',
							   choices = ["community_walktrap", "community_edge_betweenness"],
							   default = "community_walktrap")
	networkParser.set_defaults(command = "network")

	# Create the parser for the "emotionAnalysis" command
	emotionParser = subparsers.add_parser('emotionAnalysis', help = 'Calculates the percentage of emotions of the book.')
	emotionParser.add_argument('-lex', '--lexicon', help = 'The lexicon to do the analysis.',
							   type = str, default = 'Emolex')
	emotionParser.add_argument('-perChapter', help = 'Emotion Analysis for each chapter.',
							   action = 'store_true', default = False)
	emotionParser.add_argument('-bar', help = 'Bar graph.', action = 'store_true',
							   default = False)
	emotionParser.add_argument('-all', help = 'One graph with all emotions.',
							   action = 'store_true', default = False)
	emotionParser.add_argument('-ext', help = 'Extension of the generated graph.',
						 	   type = str, choices = ['png', 'pdf'], default = 'png')
	emotionParser.add_argument('-se', '--showEmotion', help = 'Set list of emotions in the final graphic',
							   choices = ['joy', 'trust', 'disgust', 'fear', 'anger',
							   			  'surprise', 'anticipation', 'sadness',
							   			  'positive', 'negative'],
							   default = ['joy', 'trust', 'disgust', 'fear',
							   			  'anger', 'surprise', 'anticipation',
							   			  'sadness'], nargs = '+')

	emotionParser.set_defaults(command = "emotionAnalysis")

	# Executes the program with the arguments from command line.
	args = parser.parse_args()
	main(args)