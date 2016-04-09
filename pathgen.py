#!/usr/bin/env python2

from Queue import PriorityQueue
from sys import maxint


def dijkstra(neighbors, start, end):
    """ Calculate shortest path between nodes.

    neighbors: map node_id -> array of neighbors
    start, end: node_id
    return: list of node_ids or None
    """
    distances = { start: 0, }  # no element = infinite
    path_from = { start: start, }
    visited = {}
    q = PriorityQueue()
    q.put((0, start))
    while not q.empty():
        (cur_dist, node) = q.get()
        if visited[node]:
            continue
        visited[node] = True
        if node == end:
            return rebuild_path(path_from, end)
        for neigh in neighbors.get(node, []):
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
