#!/usr/bin/python

import graphviz
import sys


def node_name (letter, *args):
    return letter + str(args)


def draw_graph (N, filepath="graph.gv"):
    dot = graphviz.Digraph()
    for i in range (1, N):
        for k in range (i+1, N+1):
            label = node_name ("A", i, k)
            dot.node(label)
            for j in range (i, N+2):
                label = node_name ("B", i, j, k)
                dot.node(label)
                label = node_name ("C", i, j, k)
                dot.node(label)
    for i in range (1, N):
        for k in range (i+1, N+1):
            for j in range (i, N+2):
                label1 = node_name ("A", i, k)
                label2 = node_name ("B", i, j, k)
                dot.edge(label1, label2)
                label1 = node_name ("B", i, j, k)
                label2 = node_name ("C", i, j, k)
                dot.edge(label1, label2)
    for i in range (1, N-1):
        for k in range (i+2, N+1):
            label1 = node_name ("C", i, i+1, i+1)
            label2 = node_name ("A", i+1, k)
            dot.edge(label1, label2)
            label1 = node_name ("C", i, i+1, k)
            label2 = node_name ("A", i+1, k)
            dot.edge(label1, label2)
            for j in range (i+2, N+2):
                label1 = node_name ("C", i, j, i+1)
                label2 = node_name ("B", i+1, j, k)
                dot.edge(label1, label2)
                label1 = node_name ("C", i, j, k)
                label2 = node_name ("C", i+1, j, k)
                dot.edge(label1, label2)
    #print (dot.source)
    dot.render(filepath, view=True)


if __name__ == '__main__':
	N = 3 if len(sys.argv) <= 1 else int(sys.argv[1])
	draw_graph(N)
