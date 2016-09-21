import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame, Series
import networkx as nx
import itertools
import sqlite3

con = sqlite3.connect("data.sqlite")

auth_docu_mod ='''
select authors_id, documents_id, full_name, title
from authors a, documents b, documents_authors c
where a.id=c.authors_id and c.documents_id=b.id;
'''

X = pd.read_sql(auth_docu_mod, con)

Documents = X.documents_id.groupby(by = X.documents_id).size()

Authors = X.groupby(by = X.authors_id).size()

Y = X["documents_id"].unique()
all_authors = set(X.authors_id)

x = []
y = {}
uniq = Y

for article in uniq:
    y[article] = X.loc[X['documents_id'] == article]['authors_id']

combinations = []
for article in y:
    g = list(itertools.combinations(y[article], 2))
    for sub in g:
        combinations.append(sub)

suc_authors = set()
for edge in combinations:
    for auth in edge:
        suc_authors.add(auth)

single_dogs= all_authors - suc_authors

A_N = X[['authors_id', 'full_name']]
A_N = A_N.drop_duplicates()
A_N.index = A_N.authors_id


SA_paper_num = Authors.ix[single_dogs]
Single_Auth = A_N[A_N.authors_id.isin(single_dogs)]
Single_Auth['paper_num'] = SA_paper_num

SuA_paper_num = Authors.ix[suc_authors]
Success_Auth = A_N[A_N.authors_id.isin(suc_authors)]
Success_Auth['paper_num'] = SuA_paper_num

Edges = Series(combinations)
Edges = Edges.groupby(Edges).size().reset_index()
Edges.rename(columns = {0: 'frequency', "index" : 'Edge'}, inplace = True)


First_Blood = nx.Graph()
for i in range(len(Single_Auth)):
    a = Single_Auth.iloc[i]
    First_Blood.add_node(a.authors_id, full_name =a.full_name, paper_num = a.paper_num)

G = nx.Graph()
for i in range(len(Success_Auth)):
    a = Success_Auth.iloc[i]
    G.add_node(a.authors_id, full_name =a.full_name, paper_num = a.paper_num)

for i in range(len(Edges)):
    edge = Edges.iloc[i]
    G.add_edge(edge.Edge[0], edge.Edge[1], freq = edge.frequency)

subgraphs = list(nx.connected_component_subgraphs(G))

subgraphs_size = Series()
length = len(subgraphs)
for i in range(length):
    subgraphs_size.loc[i] = len(subgraphs[i].nodes())


double_kill = [ subg for subg in subgraphs if len(subg.nodes()) == 2 ]
triple_kill = [ subg for subg in subgraphs if len(subg.nodes()) == 3 ]
quadra_kill = [ subg for subg in subgraphs if len(subg.nodes()) == 4 ]

penta_kill  = [ subg for subg in subgraphs
               if len(subg.nodes()) == 5  or len(subg.nodes()) == 6 ]

rampage     = [ subg for subg in subgraphs
               if len(subg.nodes()) == 7  or len(subg.nodes()) == 8 ]

godlike     = [ subg for subg in subgraphs
               if len(subg.nodes()) >= 10 and len(subg.nodes()) < 14]

legendary   = [ subg for subg in subgraphs
               if len(subg.nodes()) >= 14 ]


Double_Kill = nx.Graph()
for subg in double_kill:
    Double_Kill.add_edges_from(subg.edges(data = True))
    Double_Kill.add_nodes_from(subg.nodes(data = True))


Triple_Kill = nx.Graph()
for subg in triple_kill:
    Triple_Kill.add_edges_from(subg.edges(data = True))
    Triple_Kill.add_nodes_from(subg.nodes(data = True))

Quadra_Kill = nx.Graph()
for subg in quadra_kill:
    Quadra_Kill.add_edges_from(subg.edges(data = True))
    Quadra_Kill.add_nodes_from(subg.nodes(data = True))

Penta_Kill = nx.Graph()
for subg in penta_kill:
    Penta_Kill.add_edges_from(subg.edges(data = True))
    Penta_Kill.add_nodes_from(subg.nodes(data = True))

Rampage = nx.Graph()
for subg in rampage:
    Rampage.add_edges_from(subg.edges(data = True))
    Rampage.add_nodes_from(subg.nodes(data = True))

Godlike = nx.Graph()
for subg in godlike:
    Godlike.add_edges_from(subg.edges(data = True))
    Godlike.add_nodes_from(subg.nodes(data = True))

Legendary = nx.Graph()
for subg in legendary:
    Legendary.add_edges_from(subg.edges(data = True))
    Legendary.add_nodes_from(subg.nodes(data = True))

def DrawGraph(Achievement, layout = "random"):
    if layout == "random":
        pos = nx.random_layout(Achievement)
    if layout == "shell":
        pos = nx.shell_layout(Achievement)
    if layout == "spring":
        pos = nx.spring_layout(Achievement)
    if layout == "spectral":
        pos = nx.spectral_layout(Achievement)

    # for nodes
    auth1 = [ auth for (auth, d) in Achievement.nodes(data = True) if d["paper_num"] ==1]
    auth2 = [ auth for (auth, d) in Achievement.nodes(data = True) if d["paper_num"] ==2]
    auth3 = [ auth for (auth, d) in Achievement.nodes(data = True) if d["paper_num"] ==3]
    auth4 = [ auth for (auth, d) in Achievement.nodes(data = True) if d["paper_num"] ==4]


    auth5_10  = [ auth for (auth, d) in Achievement.nodes(data = True) if d["paper_num"] >=5  and d["paper_num"] < 11 ]
    auth11_20 = [ auth for (auth, d) in Achievement.nodes(data = True) if d["paper_num"] >=11 and d["paper_num"] < 21 ]
    auth21_30 = [ auth for (auth, d) in Achievement.nodes(data = True) if d["paper_num"] >=21 and d["paper_num"] < 31 ]

    auth31_   =  [ auth for (auth, d) in Achievement.nodes(data = True) if d["paper_num"] >=31]


    nx.draw_networkx_nodes(Achievement,pos,nodelist = auth1, node_size=50)
    nx.draw_networkx_nodes(Achievement,pos,nodelist = auth2, node_size=100, node_color = 'g')
    nx.draw_networkx_nodes(Achievement,pos,nodelist = auth3, node_size=200, node_color = 'y')
    nx.draw_networkx_nodes(Achievement,pos,nodelist = auth4, node_size=300, node_color = 'b')


    nx.draw_networkx_nodes(Achievement,pos,nodelist = auth5_10,  node_size=400, node_color = 'c')
    nx.draw_networkx_nodes(Achievement,pos,nodelist = auth11_20, node_size=600, node_color = 'm')
    nx.draw_networkx_nodes(Achievement,pos,nodelist = auth21_30, node_size=800, node_color = 'k')

    nx.draw_networkx_nodes(Achievement,pos,nodelist = auth31_, node_size=1000, node_color = 'k')


    # for edges
    edge1 = [ (u,v) for (u,v,d) in Achievement.edges(data = True) if d["freq"] == 1]
    edge2 = [ (u,v) for (u,v,d) in Achievement.edges(data = True) if d["freq"] == 2]
    edge3 = [ (u,v) for (u,v,d) in Achievement.edges(data = True) if d["freq"] == 3]


    nx.draw_networkx_edges(Achievement, pos, edgelist = edge1, width = 1, edge_color = "grey")
    nx.draw_networkx_edges(Achievement, pos, edgelist = edge2, width = 3,  edge_color = 'b')
    nx.draw_networkx_edges(Achievement, pos, edgelist = edge3, width = 10, edge_color = "m")

    # for labels
    names = {}
    for v, d in Achievement.nodes(data = True):
        names[v] = d["full_name"]
    nx.draw_networkx_labels(Achievement,pos,names,font_size=2, color ="w")




# first blood
DrawGraph(First_Blood)
plt.savefig("First_Blood1", dpi = 700)
plt.clf()

DrawGraph(First_Blood, layout = "spring")
plt.savefig("First_Blood2", dpi = 700)
plt.clf()

# double kill
DrawGraph(Double_Kill)
plt.savefig("Double_Kill1", dpi = 700)
plt.clf()

DrawGraph(Double_Kill, layout = "spring")
plt.savefig("Double_Kill2", dpi = 700)
plt.clf()



# triple kill
DrawGraph(Triple_Kill)
plt.savefig("Triple_Kill1", dpi = 700)
plt.clf()

DrawGraph(Triple_Kill, layout = "spring")
plt.savefig("Triple_Kill2", dpi = 700)
plt.clf()



# quadra kill
DrawGraph(Quadra_Kill)
plt.savefig("Quadra_Kill1", dpi = 700)
plt.clf()

DrawGraph(Quadra_Kill, layout = "spring")
plt.savefig("Quadra_Kill2", dpi = 700)
plt.clf()

# penta kill
DrawGraph(Penta_Kill)
plt.savefig("Penta_Kill1", dpi = 700)
plt.clf()

DrawGraph(Penta_Kill, layout = "spring")
plt.savefig("Penta_Kill2", dpi = 700)
plt.clf()


# rampage
DrawGraph(Rampage)
plt.savefig("Rampage1", dpi = 700)
plt.clf()

DrawGraph(Rampage, layout = "spring")
plt.savefig("Rampage2", dpi = 700)
plt.clf()


# godlike
DrawGraph(Godlike)
plt.savefig("Godlike1", dpi = 700)
plt.clf()

DrawGraph(Godlike, layout = "spring")
plt.savefig("Godlike2", dpi = 700)
plt.clf()


# legendary
DrawGraph(Legendary)
plt.savefig("Legendary1", dpi = 700)
plt.clf()

DrawGraph(Legendary, layout = "spring")
plt.savefig("Legendary2", dpi = 700)
plt.clf()
