#!/usr/bin/python

import graphviz
import sys



def read_data (filepath="data"):  #odczyt alfabetu, funkcji liczników oraz słowa z pliku o z góry określonym formacie
    f = open (filepath)
    text = f.read()
    f.close()
    lines = text.split('\n')
    alphabet = lines[0].split()
    size = len(alphabet)
    functions = [line.split('=') for line in lines[1:1+size]]
    word = lines[size+1]
    return alphabet, functions, word

def add_rel (a, b, S):  #dodanie relacji symetrycznej
    if not (a, b) in S:
        S.add((a, b))
        S.add((b, a))

def make_sets (alphabet, functions):  #tworzy relację zależności i niezależności
    D = set()
    I = set()
    for i, letter in enumerate(alphabet):
        D.add((letter, letter)) #relacja identycznościowa
        eq = functions[i][1]
        changing = functions[i][0]
        for l, equat in zip(alphabet[i+1:], functions[i+1:]): #porównujemy każdą funkcję z każdą pod nią
            if changing in equat[1] or equat[0] in eq or changing == equat[0]: #licznik zmieniany jest w drugim rówaniu po prawej i na odwrót lub te same liczniki są zamieniane
                add_rel (letter, l, D)
            else:
                add_rel (letter, l, I)  #nie jest zależne więc jest niezależne
    return D, I

def make_graph (word, D):  #budowa grafu jako lista sąsiedztwa
    graph = [set() for _ in range(len(word))]
    for i, letter in enumerate(word):
        for j, l in enumerate(word[i+1:]):
            if (letter, l) in D:
                graph[i].add(j+i+1)
    return graph

def minimize_graph (graph):  #minimalizacja grafu zgodnie z algorytmem z zajęć z wykorzystaniem DFS
    def _DFS (v, visited, not_use):
        if v == not_use[1]:
            return True
        visited[v] = 1
        for u in graph[v]:
            if visited[u]:
                continue
            if (v,u) == not_use:
                continue
            if _DFS (u, visited, not_use):
                return True
        return False
    
    new_graph = [set() for _ in range(len(graph))]
    
    for v, S in enumerate (graph):
        for u in S:
            visited = [0] * len(graph)
            if not _DFS (v, visited, (v,u)):
                new_graph[v].add(u)
    return new_graph

def make_FNF_from_word (word, D, alphabet):  #FNF z algorytmu z książki
    FNF = ""
    stacks = {letter : [] for letter in alphabet}
    for letter in word[::-1]:
        stacks[letter].append(letter)
        for l in alphabet:
            if l == letter:
                continue
            if (letter, l) in D:
                stacks[l].append('##')
    flag = True
    while flag:
        flag = False
        line = ""
        for stack in stacks.values():
            if len(stack) > 0:
                flag = True
                el = stack[-1]
                if el != '##':
                    del stack[-1]
                    line += el
        for letter in line:
            for l in alphabet:
                if l == letter:
                    continue
                if (l, letter) in D:
                    del stacks[l][-1]        
        if line:
            FNF += ("[" + line + "]")
    return FNF

def make_FNF_from_word_alternate (word, D):  #FNF napisane samodzielnie sprawdzające możliwości wszystkie
    FNF = ""
    used = [0] * len(word)
    for i, letter in enumerate (word):
        if used[i]:
            continue
        FNF += "[" + letter
        used[i] = i+1
        for j, l in enumerate (word[i+1:]):
            if used[j+i+1]:
                continue
            if (letter, l) in D:
                continue
            for k, let in enumerate(word[i+1:i+1+j]):
                if (l, let) in D and (used[i+1+k] == i+1 or not used[i+1+k]):
                    break
            else:
                used[j+i+1] = i+1
                FNF += l
        FNF += "]"
    return FNF

def make_FNF_from_graph (graph, word):  #odczyt FNF z grafu z wykorzystaniem zmienionego DFS
	#kolejny wierzchołek trafia do klasy dalej niż ten wcześniejszy, ważna rzecz nalezy usunąć, jeśli któryś trafił do wcześniejszej klasy i nie dodawać jeśli jest w dalszej
    def _DFS (v, idx, used, FNF):
        if used[v]:
            for s in FNF[:idx]:
                if v in s:
                    used[v] = 0
                    s.remove(v)
                    break
        if used[v]:
            return
        if idx >= len(FNF):
            FNF.append(set())
        FNF[idx].add(v)
        used[v] = 1
        for u in graph[v]:
            _DFS(u, idx+1, used, FNF)
    
    FNF = []
    used = [0] * len(graph)
    for v, S in enumerate(graph):
        if used[v]:
            continue
        _DFS (v, 0, used, FNF)
    FNF_str = ""
    for c in FNF:
        FNF_str += "["
        for i in c:
            FNF_str += word[i]
        FNF_str += "]"
    return FNF_str

def draw_graph (graph, word, filepath="graph.gv"):  #rysowanie grafu z wykorzystaniem graphviz
    dot = graphviz.Digraph()
    for i, label in enumerate (word):
        dot.node(str(i), label)
    for v, S in enumerate (graph):
        for u in S:
            dot.edge(str(v), str(u))
    print (dot.source)
    dot.render(filepath, view=True)

def main (filepath):  #wykonanie programu
	alphabet, functions, word = read_data(filepath)
	D, I = make_sets(alphabet, functions)
	graph = make_graph(word, D)
	graph = minimize_graph(graph)
	FNF = make_FNF_from_word_alternate(word, D)
	FNF1 = make_FNF_from_word(word, D, alphabet)
	FNF2 = make_FNF_from_graph (graph, word)
	print ("D =", D)
	print ("I =", I)
	print ("FNF proste ze słowa:", FNF)
	print ("FNF odczytane ze słowa:", FNF1)
	print ("FNF odczytane z grafu:", FNF2)
	graphpath = ""
	if '.' in filepath:
		graphpath = filepath.split(".")[0]
	else:
		graphpath = filepath
	graphpath += ".gv"
	draw_graph (graph, word, graphpath)


if __name__ == '__main__':

	if len(sys.argv) > 1:
		main (sys.argv[1])  #wywołanie z ścieżką do pliku podaną w argumencie wywołania
	else:                   #wywołanie dla dostarczonych danych testowych
		print ("Test automatyczny")
		main ("data.txt")
		main ("ndata.txt")
		main ("cdata.txt")
		main ("bigdata.txt")
