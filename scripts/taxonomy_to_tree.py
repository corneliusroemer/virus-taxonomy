"""
Run in this rule:
rule taxonomy_to_tree:
    input:
        tsv="results/vmr.tsv",
    output:
        tree="results/tree.nwk",
    shell:
        python scripts/taxonomy_to_tree.py {input.tsv} {output.tree}

TSV has following columns:
- Realm
- Subrealm
- Kingdom
- Subkingdom
- Phylum
- Subphylum
- Class
- Subclass
- Order
- Suborder
- Family
- Subfamily
- Genus
- Subgenus
- Species

Create a tree from first to last column, grouping by each column
"""
#%%
import networkx as nx
import pandas as pd
import sys
#%%
#%%
df = pd.read_csv("results/vmr.tsv", sep="\t", dtype="string").fillna("none")
df

ROOT = "root"

#%%
# def tree_to_newick(g, root=ROOT):
#     if root is None:
#         roots = list(filter(lambda p: p[1] == 0, g.in_degree()))
#         assert 1 == len(roots)
#         root = roots[0][0]
#     subgs = []
#     for child in g[root]:
#         if len(g[child]) > 0:
#             subgs.append(tree_to_newick(g, root=child))
#         else:
#             subgs.append(f"{child}:0.1")
#     return "(" + ','.join(subgs) + "):1"
def tree_to_newick(G: nx.DiGraph, root: nx.DiGraph):
    def _to_newick(node):
        children = list(G.successors(node))
        if len(children) == 0:  # Leaf node
            return str(node)
        else:
            return "(" + ",".join(_to_newick(child) for child in children) + f"){node}:1.0" + str(node)
    return _to_newick(root) + ";"

def write_nwk(G, path):
    if not nx.is_directed_acyclic_graph(G):
        print(nx.find_cycle(G))
        raise ValueError("Graph must be a tree")
    with open(path, "w") as f:
        f.write(tree_to_newick(G, ROOT))

#%%
def row_to_node(row, level):
    if level == 0:
        return ROOT
    return "|".join(row[:level])


row_to_node(df.iloc[0],7)
#%%
subset_df = df.iloc[:, list(range(2, 17)) + [18]]

#%%
def rename_node(node: str) -> str:
    # Take from end until first non-"none"
    split = node.split("|")
    idx = len(split) - 1
    while split[idx] == "none" and idx > 0:
        idx -= 1
    result = "|".join(split[idx:])
    print(f"{node} -> {result}")
    return result


#%%
# Create graph
G = nx.DiGraph()
G.add_node(ROOT)
renamed = set()
for level in range(1,17):
    for row in subset_df.iloc[:,:level].drop_duplicates().values:
        print(row)
        parent=row_to_node(row, level-1)
        child=row_to_node(row, level)
        print(f"{parent} -> {child}")
        # If parent has no children, add tip
        # if len(G[parent]) == 0:
            # tipname = parent.split("|")[-1]
            # if tipname != "none":
            #     G.add_edge(parent, tipname + "_tip")
            #     print(f"{parent} -> {tipname}")
        if rename_node(child) not in renamed:
            G.add_edge(parent, child)
            renamed.add(rename_node(child))
        else:
            print("Skipping self-edge: ", parent, child)

# nx.draw(G, with_labels=True)

# #%%
# for realm in df.Realm.unique():
#     G.add_edge("root", realm)

# # Visualize
# nx.draw(G, with_labels=True)
#%%
# Post-process tree
# Rename tips removing everything before the lasst non-"none" node
# Get list of nodes
H = nx.relabel_nodes(G, rename_node)

#%%
# # Add tips for named internal nodes (don't end in "none")
# nodes = list(H.nodes())
# for node in nodes:
#     if node.endswith("none"):
#         continue
#     H.add_edge(node, node + "_tip")



#%%
write_nwk(H, "results/tree.nwk")

