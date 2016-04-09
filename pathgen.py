#!/usr/bin/env python2

from Queue import PriorityQueue
from sys import maxint

from db_connection import DBWaypoint


def dijkstra(graph, start, end):
    """ Calculate shortest path between nodes.

    graph: map of node_id -> DBWaypoint
    start, end: node_id
    return: list of node_ids or None
    """
    distances = {start: 0, }  # no element = infinite
    path_from = {start: start, }
    visited = {}
    q = PriorityQueue()
    q.put((0, start))
    while not q.empty():
        (cur_dist, node) = q.get()
        if node in visited:
            continue
        visited[node] = True
        if node == end:
            return rebuild_path(path_from, end)
        for neigh in graph[node].connection_ids:
            if cur_dist + 1 < distances.get(neigh, maxint):
                neigh_dist = cur_dist+1
                distances[neigh] = neigh_dist
                path_from[neigh] = node
                q.put((neigh_dist, neigh))
    return None


def rebuild_path(path_from, end):
    """ Retrace the path that led Dijkstra to end and return it. """
    path = [end, ]
    node = end
    while node != path_from[node]:
        node = path_from[node]
        path.append(node)
    path.reverse()
    return path


def build_graph(node_list):
    """ Generate a graph lookup map.

    node_list: list of DBWaypoint
    return: map of node_id -> DBWaypoint
    """
    res_graph = {}
    for waypoint in node_list:
        res_graph[waypoint.node_id] = waypoint
    return res_graph


def dummy_test_graph():
    """ sample return value of Database.get_whole_graph() """
    return [
        DBWaypoint(1, "Room 3180", [2]),
        DBWaypoint(2, "Main hall", [1, 2, 3]),
        DBWaypoint(3, "North corridor", [2, 4]),
        DBWaypoint(4, "Toilet", [3]),
    ]


def gen_path_description(graph, path):
    """ Generate text description of a given path.

    graph: generated by build_graph
    path: array of node_ids. Assume path[0] is current location, path[-1] is target location.
    return: string with instructions.
    """
    if path is None or len(path) == 0:
        return "No route found."
    if len(path) == 1:
        return "You're already there."
    instrs = ["You're in " + graph[path[0]].name]
    for pos in xrange(1, len(path)):
        prefix = get_instruction_prefix(pos, len(path), graph[path[pos-1]], graph[path[pos]])
        instrs.append(prefix + graph[path[pos]].name)
    return ". ".join(instrs)


def get_instruction_prefix(pos, total, prev_wp, next_wp):
    if pos == 1:
        pname = prev_wp.name.lower()
        if pname.startswith('room') or 'toilet' in pname:
            return "Exit to"
        return "Go to "
    if pos == total-1:
        return "Finally, head to "
    options = [
        "Then head to ",
        "Continue to ",
        "Next, go to ",
    ]
    return options[(pos-1) % len(options)]


def get_node(graph, name):
    for node in graph.values():
        if node.name.lower() == name.lower():
            return node.node_id
    return None


def get_instructions(db_graph, start, end):
    graph = build_graph(db_graph)
    path = dijkstra(graph, start, end)
    return gen_path_description(graph, path)
