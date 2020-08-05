import pandas as pd
import os

def edgesToCsv(graph, path, fileName, index = False, thickness = True,\
               undirected = True):
	'''
	Generates a comma separated value file (.csv) with edges and their attributes from a Graph object.

	Parameters:
		graph (Graph): The object which represents a graph.
		path (str): The local where the .csv will be recorded.
		fileName (str): The name of the .csv.
		index (bool): Sets if the .csv will have an index.
		thickness (bool): Sets if the .csv will have a column for edges' thickness.
		undirected (bool): Sets if the graph is undirected.
	'''
	local = f'{str(path)}/{str(fileName)}.csv'
	if os.path.isfile(local):
		x = 0
		while os.path.isfile(local):
			x += 1
			local = f'{str(path)}/{str(fileName)}({x}).csv'

	edges = graph.get_edgelist()
	source = [edge[0] for edge in edges]
	target = [edge[1] for edge in edges]
	if undirected:
		form = ['Undirected' for i in range(graph.ecount())]
	else:
		form = ['Directed' for i in range(graph.ecount())]
	if thickness:
		weight = graph.es['Weight']
	else:
		weight = [None]*graph.ecount()
	tableEdge = pd.DataFrame({'Source': source, 'Target': target,
							  'Weight': weight, 'Type': form})
	tableEdge.to_csv(local, index = index, index_label = 'Id')

def verticesToCsv(graph, path, fileName, index = True,
                  size = True, community = True):
	'''
	Generates a comma separated value file (.csv) with vertices and their attributes from a Graph object.

	Parameters:
		graph (Graph): The object which represents a graph.
		path (str): Local where the .csv will be recorded.
		fileName (str): Name of the .csv.
		index (bool): Sets if the .csv will have an index.
		size (bool): Sets if the .csv will have a column for vertices' size.
		community (bool): Sets if the .csv file will have a column for vertices' community.
	'''
	local = f'{str(path)}/{str(fileName)}.csv'
	if os.path.isfile(local):
		x = 0
		while os.path.isfile(local):
			x += 1
			local = f'{str(path)}/{str(fileName)}({x}).csv'

	idxNodes = [num for num in range(graph.vcount())]
	if size:
		size = graph.vs['Size']
	else:
		size = [None]*graph.vcount()
	if community:
		members = graph.vs['Community']
	else:
		members = [None]*graph.vcount()
	table_vertice = pd.DataFrame({'Label': graph.vs['Name'],
	                              'Size': size, 'Community': members})
	table_vertice.to_csv(local, index = index, index_label = 'Id')