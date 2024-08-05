from flask import Flask, render_template, request, jsonify
import networkx as nx
import plotly.graph_objects as go
import plotly.utils
import json

app = Flask(__name__)

def create_graph():
    G = nx.DiGraph()
    with open('EDGES.csv', 'r') as file:
        next(file)  # Skip the header
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
        next(file)  # Skip the header
        for line in file:
            parts = line.strip().split(',')
            source = parts[0].strip('"')
            tfs.add(source)
    return sorted(tfs)

def create_subgraph(G, node_of_interest):
    H = nx.ego_graph(G, node_of_interest, radius=1)
    pos = nx.spring_layout(H, dim=3)
    
    edge_x, edge_y, edge_z = [], [], []
    for edge in H.edges():
        x0, y0, z0 = pos[edge[0]]
        x1, y1, z1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])
    
    node_x, node_y, node_z, node_text = [], [], [], []
    for node in H.nodes():
        x, y, z = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        node_text.append(node)
    
    return edge_x, edge_y, edge_z, node_x, node_y, node_z, node_text, H.nodes()

@app.route('/', methods=['GET', 'POST'])
def index():
    tfs = extract_tfs()
    if request.method == 'POST':
        node_of_interest = request.form['tf']
        G = create_graph()
        edge_x, edge_y, edge_z, node_x, node_y, node_z, node_text, nodes = create_subgraph(G, node_of_interest)
        
        edge_trace = go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z,
            line=dict(width=0.5, color='#888'),
            mode='lines'
        )
        
        node_trace = go.Scatter3d(
            x=node_x, y=node_y, z=node_z,
            mode='markers',
            marker=dict(
                size=5,
                color=['red' if node == node_of_interest else 'lightblue' for node in nodes],
                line=dict(width=0.5, color='#888')
            ),
            text=node_text,
            hoverinfo='text'
        )
        
        layout = go.Layout(
            title=f'3D Subgraph centered at {node_of_interest}',
            showlegend=False,
            scene=dict(
                xaxis=dict(showticklabels=False),
                yaxis=dict(showticklabels=False),
                zaxis=dict(showticklabels=False),
                aspectmode='data'
            ),
            margin=dict(l=0, r=0, b=0, t=40),
            scene_camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.2, y=1.2, z=1.2)
            ),
            dragmode='orbit',
            hovermode='closest'
        )
        
        fig = go.Figure(data=[edge_trace, node_trace], layout=layout)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('graph.html', graphJSON=graphJSON, tfs=tfs)
    
    return render_template('index.html', tfs=tfs)

if __name__ == '__main__':
    app.run(debug=True)
