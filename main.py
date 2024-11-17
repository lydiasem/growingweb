import networkx as nx
import matplotlib.pyplot as plt
import csv
import textwrap


try:
    with open('netflix_titles_nov_2019.csv') as csvfile:
        extractor = list(csv.reader(csvfile, delimiter=','))
except FileNotFoundError:
    print("Error: Dataset file 'netflix_titles_nov_2019.csv' not found.")
    exit()

header = extractor[0]
data_rows = extractor[1:]
director_index = header.index("director")
country_index = header.index("country")
genre_index = header.index("listed_in")
title_index = header.index("title")


def build_concept_tree(concept_name):
    """Build a tree structure for a given concept."""
    director_name = None
    country_name = None
    genre_name = None

    
    for row in data_rows:
        if row[title_index] == concept_name:
            director_name = row[director_index]
            country_name = row[country_index]
            genre_name = row[genre_index]
            break

    # Find related titles based on attributes
    related_titles_d = [
        row[title_index]
        for row in data_rows
        if director_name and row[director_index] == director_name and row[title_index] != concept_name
    ]

    related_titles_c = [
        row[title_index]
        for row in data_rows
        if country_name and row[country_index] == country_name and row[title_index] != concept_name
    ]

    related_titles_g = []
    if genre_name:
        related_titles_g = [
            row[title_index]
            for row in data_rows
            if any(genre.strip() in row[genre_index] for genre in genre_name.split(","))
            and row[title_index] != concept_name
        ]

    return {
        concept_name: {
            "Director": related_titles_d[:3],
            "Country": related_titles_c[:3],
            "Genre": related_titles_g[:3],
        }
    }


def add_nodes_edges(graph, root, tree_data):
    """Add nodes and edges for a concept tree."""
    for category, related_concepts in tree_data.items():
        graph.add_node(category)  
        graph.add_edge(root, category, label=category)  
        for concept in related_concepts:
            graph.add_node(concept)  
            graph.add_edge(category, concept)  


def create_positions(graph, root, categories, vertical_spacing=1.5, horizontal_spacing=1.2, positions=None):
    if positions is None:
        positions = {}

   
    if root in positions:
        root_x, root_y = positions[root]  
    else:
        root_x, root_y = 0, 0
        positions[root] = (root_x, root_y)

    
    num_categories = len(categories)
    category_spacing = 3.5 / max(num_categories, 1)

    for idx, category in enumerate(categories):
        if category not in positions:
           
            positions[category] = (
                root_x + (idx - num_categories / 2) * category_spacing,
                root_y - vertical_spacing,
            )

        
        related_concepts = concept_tree[root][category]
        num_concepts = len(related_concepts)
        if num_concepts > 0:
            concept_spacing = horizontal_spacing / max(num_concepts, 1)
            for i, concept in enumerate(related_concepts):
                if concept not in positions:
                    
                    positions[concept] = (
                        positions[category][0] + (i - num_concepts / 2) * concept_spacing,
                        positions[category][1] - vertical_spacing,
                    )
    return positions


def wrap_text(text, width=15):
    """Wrap text to fit in nodes."""
    return "\n".join(textwrap.wrap(text, width))


def visualize_tree(graph, concept_tree, concept_name):
    """Visualize the concept tree."""
    
    add_nodes_edges(graph, concept_name, concept_tree[concept_name])

    
    categories = list(concept_tree[concept_name].keys())
    positions = create_positions(graph, concept_name, categories)

    
    nx.set_node_attributes(graph, positions, "pos")

    
    plt.figure(figsize=(14, 9))
    nx.draw(
        graph,
        pos=positions,
        with_labels=False,
        node_size=5000,
        node_color="lightblue",
        font_size=10,
        font_weight="bold",
    )

    for node, (x, y) in positions.items():
        wrapped_label = wrap_text(node, width=15)
        plt.text(
            x,
            y,
            wrapped_label,
            fontsize=10,
            ha="center",
            va="center",
            bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3"),
        )

    edge_labels = nx.get_edge_attributes(graph, "label")
    nx.draw_networkx_edge_labels(graph, pos=positions, edge_labels=edge_labels, font_color="red")

    plt.show()



if __name__ == "__main__":
    G = nx.DiGraph()


    concept_name = input("Enter a movie title: ")
    concept_tree = build_concept_tree(concept_name)
    visualize_tree(G, concept_tree, concept_name)
