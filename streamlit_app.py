import streamlit as st
import networkx as nx
import plotly.graph_objects as go

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

@st.cache_data
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
    
    return edge_x, edge_y, edge_z, node_x, node_y, node_z, node_text, H.nodes(), distances

def plot_graph(edge_x, edge_y, edge_z, node_x, node_y, node_z, node_text, node_of_interest, nodes, size, color_of_interest, color_others):
    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        line=dict(width=0.5, color='#888'),
        mode='lines'
    )

    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text',  
        marker=dict(
            size=size * 1.5, 
            color=[color_of_interest if node == node_of_interest else color_others for node in nodes],
            line=dict(width=0.5, color='#888')
        ),
        text=node_text,
        textposition="top center",  # Position the text above the node
        hoverinfo='text'
    )

    layout = go.Layout(
        title=dict(text=f'3D Sub-Network of pathways centering: {node_of_interest}', x=0.5),
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
            eye=dict(x=1.5, y=1.5, z=1.5)
        ),
        dragmode='orbit',
        hovermode='closest',
        template='plotly_dark'
    )

    fig = go.Figure(data=[edge_trace, node_trace], layout=layout)
    return fig
######SStreamlit appo:
st.set_page_config(page_title="3D TF-Network Visualization", layout="wide")

st.title("3D TF-Network Visualization")
st.sidebar.header("Settings")

tfs = extract_tfs()
node_of_interest = st.sidebar.selectbox("Select a 'node(meaning: transcription factor)' of interest:", tfs)

st.sidebar.markdown("**Graph Customization**")
size = st.sidebar.slider('Node size:', min_value=5, max_value=15, value=8)
color_of_interest = st.sidebar.color_picker('Color for selected TF:', '#FF6347')
color_others = st.sidebar.color_picker('Color for neighboring TFs:', '#87CEFA')

if st.sidebar.button('Generate Subgraph'):
    G = create_graph()
    
    edge_x, edge_y, edge_z, node_x, node_y, node_z, node_text, nodes, distances = create_subgraph(G, node_of_interest)
    fig = plot_graph(edge_x, edge_y, edge_z, node_x, node_y, node_z, node_text, node_of_interest, nodes, size, color_of_interest, color_others)
    st.subheader(f"'{node_of_interest}' relations to neigboring TFs: (negative means: downregulation)")
    for neighbor, distance in distances.items():
        color = 'green' if distance >= 0 else 'red'
        st.markdown(f"<span style='color:{color}'>{neighbor}: {distance:.2f}</span>", unsafe_allow_html=True)

    st.plotly_chart(fig, use_container_width=True)
