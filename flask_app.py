from flask import Flask, render_template, jsonify, request
import networkx as nx
import json

app = Flask(__name__)

def create_graph():
    G = nx.DiGraph()
    with open('EDGES.csv', 'r') as file:
        next(file)
        for line in file:
            parts = line.strip().split(',')
            source = parts[0].strip('"')
            target = parts[2].strip('"')
            sign = int(parts[1])
            G.add_edge(source, target, sign=sign)
    return G

def extract_tfs():
    tfs = set()
    with open('EDGES.csv', 'r') as file:
        next(file)
        for line in file:
            parts = line.strip().split(',')
            source = parts[0].strip('"')
            tfs.add(source)
    return sorted(tfs)

def create_subgraph(G, node_of_interest):
    H = nx.ego_graph(G, node_of_interest, radius=1)
    pos = nx.spring_layout(H, dim=3)

    edge_x, edge_y, edge_z = [], [], []
    node_x, node_y, node_z, node_text = [], [], [], []
    distances = {}

    for edge in H.edges(data=True):
        x0, y0, z0 = pos[edge[0]]
        x1, y1, z1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])

        distance = ((x0-x1)**2 + (y0-y1)**2 + (z0-z1)**2) ** 0.5
        sign = edge[2]['sign']
        adjusted_distance = distance * sign

        if edge[0] == node_of_interest:
            distances[edge[1]] = adjusted_distance
        elif edge[1] == node_of_interest:
            distances[edge[0]] = adjusted_distance

    for node in H.nodes():
        x, y, z = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        node_text.append(node)

    return {
        'edge_x': edge_x, 'edge_y': edge_y, 'edge_z': edge_z,
        'node_x': node_x, 'node_y': node_y, 'node_z': node_z,
        'node_text': node_text, 'nodes': list(H.nodes()),
        'distances': distances
    }

@app.route('/')
def index():
    tfs = extract_tfs()
    return render_template('index.html', tfs=tfs)

@app.route('/get_graph_data', methods=['POST'])
def get_graph_data():
    data = request.json
    node_of_interest = data['node']
    G = create_graph()
    graph_data = create_subgraph(G, node_of_interest)
    return jsonify(graph_data)

if __name__ == '__main__':
    app.run(debug=True)