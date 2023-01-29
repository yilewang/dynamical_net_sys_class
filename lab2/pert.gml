# This is a graph object in gml file format
# produced by the zen graph library

ZenCodec "basic"
ZenStringEncoder "encode_str"

graph [
	directed 1
	bipartite 0
	node [
		id 0
		name "Lead time"
	]
	node [
		id 1
		name "Move to site"
	]
	node [
		id 2
		name "Obtain pipes"
	]
	node [
		id 3
		name "Obtain valves"
	]
	node [
		id 4
		name "Lay out pipeline"
	]
	node [
		id 5
		name "Dig trench"
	]
	node [
		id 6
		name "Prepare valve chambers"
	]
	node [
		id 7
		name "Cut specials"
	]
	node [
		id 8
		name "Lay pipes"
	]
	node [
		id 9
		name "Fit valves"
	]
	node [
		id 10
		name "Concrete anchors"
	]
	node [
		id 11
		name "Finish valve chambers"
	]
	node [
		id 12
		name "Test pipeline"
	]
	node [
		id 13
		name "Backfill"
	]
	node [
		id 14
		name "Clean up"
	]
	node [
		id 15
		name "Leave site"
	]
	edge [
		source 0
		target 1
		weight 10.0
	]
	edge [
		source 0
		target 2
		weight 10.0
	]
	edge [
		source 0
		target 3
		weight 10.0
	]
	edge [
		source 1
		target 4
		weight 20.0
	]
	edge [
		source 4
		target 5
		weight 7.0
	]
	edge [
		source 2
		target 6
		weight 30.0
	]
	edge [
		source 5
		target 6
		weight 25.0
	]
	edge [
		source 2
		target 7
		weight 30.0
	]
	edge [
		source 2
		target 8
		weight 30.0
	]
	edge [
		source 5
		target 8
		weight 25.0
	]
	edge [
		source 3
		target 9
		weight 20.0
	]
	edge [
		source 6
		target 9
		weight 18.0
	]
	edge [
		source 7
		target 9
		weight 9.0
	]
	edge [
		source 8
		target 10
		weight 20.0
	]
	edge [
		source 9
		target 11
		weight 10.0
	]
	edge [
		source 10
		target 11
		weight 12.0
	]
	edge [
		source 9
		target 12
		weight 10.0
	]
	edge [
		source 10
		target 12
		weight 12.0
	]
	edge [
		source 10
		target 13
		weight 12.0
	]
	edge [
		source 12
		target 14
		weight 6.0
	]
	edge [
		source 13
		target 14
		weight 10.0
	]
	edge [
		source 11
		target 15
		weight 8.0
	]
	edge [
		source 14
		target 15
		weight 3.0
	]
]
