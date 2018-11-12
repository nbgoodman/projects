import os
import sys
sys.path.append('..')
sys.path.append('../..')
import argparse
import utils
from student_utils_sp18 import *

import time

"""
======================================================================
  Complete the following function.
======================================================================
"""
def floydWarshall(graph):
	dist = map(lambda i : map(lambda j : j , i) , graph)
	for k in range(len(graph)):

		# pick all vertices as source one by one
		for i in range(len(graph)):

			# Pick all vertices as destination for the
			# above picked source
			for j in range(len(graph)):

				# If vertex k is on the shortest path from
				# i to j, then update the value of dist[i][j]
				dist[i][j] = min(dist[i][j], dist[i][k]+ dist[k][j])
	return dist


def min_weight_set_cover_approx_algo(tuple_list, num_kingdoms, adj_matrix):
	# our resulting set of kingdoms (by their indices) to conquer
	result = list([])

	# create and populate an ORIGINAL array of size num_kingdoms, starting from 0 to num_kingdoms-1
	ORIGINAL = set([])
	for i in range(num_kingdoms):
		ORIGINAL.add(i)

	# initilize an empty NEW set
	NEW = set([])
	# keep adding set_covers until there is no difference between NEW and ORIGINAL
	while len(ORIGINAL.difference(NEW)) != 0:
		efficient_tuple = ()
		efficient_cost = float('inf')

		# look for the minimum efficient set to add to NEW
		for t in tuple_list:
			set_cover = t[0]
			kingdom_index = t[1]
			kingdom_efficiency = calc_efficiency(NEW, set_cover, kingdom_index, adj_matrix)

			if kingdom_efficiency < efficient_cost:
				efficient_tuple = t
				efficient_cost = kingdom_efficiency

		# if NEW != ORIGINAL but there are no more valid (contributing at least 1 new vertex) set_covers to add, then error
		if not efficient_tuple:
			raise ValueError("efficient_tuple in min_weight_set_cover_approx_algo is empty!")

		# TODO: optimization; if conquering a kingdom yields 0 new vertices, can remove from tuple_list immediately

		# add the most efficient set to the NEW set
		NEW = NEW.union(efficient_tuple[0])
		# add the kingdom to the set of kingdoms to conquer
		result.append(efficient_tuple[1])
		# remove the corresponding tuple from the list we're scanning
		tuple_list.remove(efficient_tuple)

	return result

# original_set = the set of all kingdoms in our problem
# candidate_set = the set that we may want to add to our NEW set above
# candidate_index = the candidate kinggdom's index
# adj_matrix = the adjacency matrix of all kingdoms in original_set
#
# returns the cost of conquering the candidate divided by the number of newly-added vertices
#	in decimal form
def calc_efficiency(original_set, candidate_set, candidate_index, adj_matrix):
	# candidate_set starts off as a list, convert it to a set
	candidate_set = set(candidate_set)
	# cost is found at c_ii of the adj_matrix
	conquering_cost = adj_matrix[candidate_index][candidate_index]
	# find the length of the number of newly-added vertices (take the vertices IN candidate_set but NOT in original_set)
	difference_set = candidate_set.difference(original_set)
	num_new_vertices = len(difference_set)

	# every value will be > 0, so a val of 0 means you conquer for free and gain vertices
	if conquering_cost == 0 and num_new_vertices != 0:
		return 0
	# if the candidate does not add any new vertices, return an efficiency of inf
	if num_new_vertices == 0:
		return float('inf')
	return float(conquering_cost)/float(num_new_vertices)


# # the original adjacency matrix
# matrix = None
# # visited array
# visited = list()
# # the resulting traversal list
# traversal = list()
# # length of the matrix
# length = 0

# adj_matrix = the original matrix that we run DFS on
# start_index = the index we start DFS on
#
# return the DFS traversal on the corresponding graph
def DFS(adj_matrix, start_index):
	visited = list()
	traversal = list()
	length = len(adj_matrix)
	lastunique = [start_index]

	# initialize the visited array to all false
	for i in range(length):
		visited.append(False)

	def DFS_helper(i):
		# visit the vertex
		visited[i] = True
		# add this vertex to the traversal list
		traversal.append(i)
		lastunique[0] = i

		for j in range(length):
			# if we haven't visited this neighbor j AND if there's an edge between i and j (it can't be an 'x')
			if not visited[j] and not isinstance(adj_matrix[i][j], str):
				DFS_helper(j)
				# when coming back, add the parent vertex to the traversal list (have to backtrack)
				traversal.append(i)

	# run DFS
	DFS_helper(start_index)

	return traversal, lastunique





def Dijkstra(adjmatrix, source, target):
	i = 0
	#vertexlist is list of nodes (0 to n)
	vertexlist = []
	while i < len(adjmatrix):
		vertexlist.append(i)
		i+=1
	#unchangedlist is original vertexlist
	unchangedlist = vertexlist
	#dist is distances from source to each vertex (infinity at first)
	dist = [float("inf") for x in range(len(adjmatrix))]
	#prev is the previous vertex visited to get to indexed vertex (if prev[4] = 0 then 0 -> 4)
	prev = [-1 for y in range(len(adjmatrix))]
	dist[source] = 0 #update source -> source distance is 0
	while vertexlist:
		minvert = None
		minval = float("inf")
		for x in vertexlist:
			if dist[x] < minval:
				minvert = x
				minval = dist[x]
		vertexlist.remove(minvert) #delete minvert because we are processing it
		if minvert == target: #triggers if we found target
			break
		k = 0
		while k < len(adjmatrix): #go through all neighbors of minvert
			if adjmatrix[minvert][k] == "x": #if no connection, do nothing
				pass
			else: #update lowest distance to others from minvert
				alt = dist[minvert] + adjmatrix[minvert][k]
				if alt < dist[k]:
					dist[k] = alt
					prev[k] = minvert
			k+=1
	s = [] #eventually the full path from source -> target
	u = target
	s.insert(0, u) #insert target
	while prev[u] != -1: #while there is a valid prev
		s.insert(0,prev[u])
		u = prev[u]
	#s.insert(0, u) #u is now the source
	#not really sure why I did this START
	distances = []
	distsum = 0
	for vert in s:
		distances.append(dist[vert] - distsum)
		distsum += dist[vert]
	#not really sure why I did this END
	return s, dist[target]


def solve(list_of_kingdom_names, starting_kingdom, adjacency_matrix, params=[]):
	startingnode = list_of_kingdom_names.index(starting_kingdom)
	setlist = [] #setlist eventually a list of ([non-"x" entries in adj[i] (not distances but indexes)], i)
	i = 0
	while i < len(adjacency_matrix):
		vertlist = []
		j = 0
		minedge = float("inf")
		while j < len(adjacency_matrix[i]):
			if isinstance(adjacency_matrix[i][j], str):
				pass
			else:
				vertlist.append(j)
				if adjacency_matrix[i][j] < minedge and i != j:
					minedge = adjacency_matrix[i][j]
			j += 1
		adjacency_matrix[i][i] += minedge
		setlist.append((vertlist, i))
		i += 1
	terminal_nodes = min_weight_set_cover_approx_algo(setlist, len(list_of_kingdom_names), adjacency_matrix)
	terminalcopy = terminal_nodes.copy() #original set of dominated nodes
	if startingnode not in terminal_nodes:
		terminal_nodes.append(startingnode)
	#subgraph is same size as adjacency matrix, originally all "x"
	subgraph = [["x" for elem1 in range(len(adjacency_matrix))] for elem2 in range(len(adjacency_matrix))]
	starting = [terminal_nodes[0]] #nodes we can start from for steiner tree creation
	if len(terminal_nodes) == 1:
		realthing = list_of_kingdom_names[terminal_nodes[0]]
		return [realthing], [realthing]
	terminal_nodes.remove(terminal_nodes[0])
	optimizedict = {}
	while terminal_nodes:
		wtf = [] #list of (path, distance)
		for startnode in starting:
			for endnode in terminal_nodes:
				found = 0
				for key, item in optimizedict.items():
					if key[0] == startnode and key[len(key) - 1] == endnode:
						wtf.append((key, distance))
						found = 1
						break
				if found == 0:
					#find distance from startnode to endnode for all pairs
					path, distance = Dijkstra(adjacency_matrix, startnode, endnode)
					wtf.append((path, distance))
					optimizedict[tuple(path)] = distance
		#find min path, distance in wtf
		newpath = wtf[0][0]
		mindist = wtf[0][1]
		for (pathway, dista) in wtf:
			if dista < mindist:
				mindist = dista
				newpath = pathway
		starting.append(newpath[len(newpath) - 1]) #append endnode
		terminal_nodes.remove(newpath[len(newpath) - 1]) #remove endnode
		blah = 0

		#utils.write_to_file("test.out", "length: " + str(len(terminal_nodes)) + "time: " + str(time.time()) + "\n", append=True)

		#add path to adjacency matrix (not sure if this is correct)
		while blah < (len(newpath) - 1):
			subgraph[newpath[blah]][newpath[blah + 1]] = adjacency_matrix[newpath[blah]][newpath[blah + 1]]
			subgraph[newpath[blah + 1]][newpath[blah]] = adjacency_matrix[newpath[blah + 1]][newpath[blah]]
			blah += 1
	let1 = 0
	offset = 0
	#reducing the matrix to all numbers (no "x")
	realindexes = []
	while let1 < len(adjacency_matrix):
		if all(isinstance(h, str) for h in subgraph[let1 - offset]):
			for vertrow in subgraph:
				del vertrow[let1 - offset]
			del subgraph[let1 - offset]
			offset += 1
		else:
			realindexes.append(let1)
		let1+=1
	#run DFS
	traversal, lastnum = DFS(subgraph, realindexes.index(startingnode))
	lastindex = max(loc for loc, val in enumerate(traversal) if val == lastnum[0])
	traversal = traversal[0:lastindex+1]
	last_kingdom_real = realindexes[traversal[len(traversal)-1]]
	starting_kingdom_real = startingnode
	path = Dijkstra(adjacency_matrix, last_kingdom_real, starting_kingdom_real)[0]
	realtraversal= []
	for node in traversal:
		realtraversal.append(realindexes[node])
	#print (realtraversal)
	# delete the first node in the path because itll repeat the last_kingdom, then add to traversal
	del path[0]
	for i in path:
		realtraversal.append(i)

	namedtraversal = []
	nameddominate = []

	for b in realtraversal:
		namedtraversal.append(list_of_kingdom_names[b])
	for c in terminalcopy:
		nameddominate.append(list_of_kingdom_names[c])
	return namedtraversal, nameddominate

	#raise Exception('"solve" function not defined')
	# return closed_walk, conquered_kingdoms


"""
======================================================================
   No need to change any code below this line
======================================================================
"""


def solve_from_file(input_file, output_directory, params=[]):
	print('Processing', input_file)

	input_data = utils.read_file(input_file)
	number_of_kingdoms, list_of_kingdom_names, starting_kingdom, adjacency_matrix = data_parser(input_data)
	closed_walk, conquered_kingdoms = solve(list_of_kingdom_names, starting_kingdom, adjacency_matrix, params=params)

	basename, filename = os.path.split(input_file)
	output_filename = utils.input_to_output(filename)
	output_file = f'{output_directory}/{output_filename}'
	if not os.path.exists(output_directory):
		os.makedirs(output_directory)
	utils.write_data_to_file(output_file, closed_walk, ' ')
	utils.write_to_file(output_file, '\n', append=True)
	utils.write_data_to_file(output_file, conquered_kingdoms, ' ', append=True)


def solve_all(input_directory, output_directory, params=[]):
	input_files = utils.get_files_with_extension(input_directory, 'in')

	for input_file in input_files:
		solve_from_file(input_file, output_directory, params=params)


if __name__=="__main__":
	parser = argparse.ArgumentParser(description='Parsing arguments')
	parser.add_argument('--all', action='store_true', help='If specified, the solver is run on all files in the input directory. Else, it is run on just the given input file')
	parser.add_argument('input', type=str, help='The path to the input file or directory')
	parser.add_argument('output_directory', type=str, nargs='?', default='.', help='The path to the directory where the output should be written')
	parser.add_argument('params', nargs=argparse.REMAINDER, help='Extra arguments passed in')
	args = parser.parse_args()
	output_directory = args.output_directory
	if args.all:
		input_directory = args.input
		solve_all(input_directory, output_directory, params=args.params)
	else:
		input_file = args.input
		solve_from_file(input_file, output_directory, params=args.params)
