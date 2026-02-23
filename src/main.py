import urllib.request
import gzip
import time
import random
from collections import deque

class PrunedLandmarkLabeling:
    def __init__(self, graph):
        # graph is adjacency list of [v: [neighbours]]
        self.graph = graph
        self.n = len(graph)
        self.vertex_order = list(range(self.n))
        
        # Degree sorting strategy
        self.vertex_order.sort(key=lambda v: len(graph[v]), reverse=True)
        # tuple of (vertex, dist)
        self.L = [[] for _ in range(self.n)]
        
        
    def build_index(self):
        P = [float('inf') for _ in range(self.n)]
        for rank, v in enumerate(self.vertex_order):
            self.pruned_bfs(v, rank, P)    
        
    
    def pruned_bfs(self, v, rank_v, P):
        queue = deque([(v, 0)])
        visited = [v]
        
        T = [float('inf') for _ in range(self.n)]
        for w, dist in self.L[v]:
            T[w] = dist
        T[rank_v] = 0
        P[v] = 0
        
        while len(queue) > 0:
            u, cur_dist = queue.popleft()
            min_query_dist = float('inf')
            for w, dist in self.L[u]:
                min_query_dist = min(min_query_dist, dist + T[w])
                
            if min_query_dist <= cur_dist:
                continue
            
            self.L[u].append((rank_v, cur_dist))
            
            for w in self.graph[u]:
                if P[w] == float('inf'):
                    P[w] = P[u] + 1
                    queue.append((w, cur_dist + 1))
                    visited.append(w)
                    
        for w in visited:
            P[w] = float('inf')
         
            
    def query(self, u, v):
        if u >= self.n or v >= self.n:
            return float('inf')
        
        L_u = self.L[u]
        L_v = self.L[v]
        
        i = 0
        j = 0
        min_dist = float('inf')
        
        while i < len(L_u) and j < len(L_v):
            hub_u, dist_u = L_u[i]
            hub_v, dist_v = L_v[j]
            
            if hub_u > hub_v:
                j += 1
            elif hub_v > hub_u:
                i += 1
            else:
                min_dist = min(min_dist, dist_u + dist_v)
                i += 1
                j += 1
                
        return min_dist


def load_snap_dataset(url):
    print(f"Downloading dataset from {url}...")
    # Using a User-Agent to ensure the download is accepted
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req) as response:
        with gzip.GzipFile(fileobj=response) as uncompressed:
            file_content = uncompressed.read().decode('utf-8')

    print("Parsing edge list and mapping nodes...")
    node_map = {}
    edges = []
    
    for line in file_content.split('\n'):
        # Skip comments and empty lines
        if line.startswith('#') or not line.strip():
            continue
        
        u, v = map(int, line.split())
        
        # Map raw IDs to consecutive integers 0 to N-1
        if u not in node_map:
            node_map[u] = len(node_map)
        if v not in node_map:
            node_map[v] = len(node_map)
            
        edges.append((node_map[u], node_map[v]))
        
    n = len(node_map)
    
    # The paper treats these as undirected, unweighted graphs
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
        
    # Remove duplicates if the dataset had duplicate edges
    graph = [list(set(neighbors)) for neighbors in graph]
    
    print(f"Loaded graph with {n} nodes and {len(edges)} edges.")
    return graph

if __name__ == "__main__":
    # URL for p2p-Gnutella08 (Smaller dataset: ~6,300 nodes, ~20,000 edges)
    # For the larger 62,000 node dataset, use: 
    # 'https://snap.stanford.edu/data/p2p-Gnutella31.txt.gz'
    gnutella_url = 'https://snap.stanford.edu/data/p2p-Gnutella08.txt.gz'
    
    graph = load_snap_dataset(gnutella_url)
    
    print("\nInitializing Pruned Landmark Labeling...")
    start_time = time.time()
    pll = PrunedLandmarkLabeling(graph)
    
    print("Building index (this may take a minute in Python)...")
    pll.build_index()
    end_time = time.time()
    print(f"Index built in {end_time - start_time:.2f} seconds.")
    
    # Calculate average label size to see the pruning in action!
    total_label_entries = sum(len(label) for label in pll.L)
    avg_label_size = total_label_entries / pll.n
    print(f"Average label size: {avg_label_size:.2f} entries per node.")
    
    # Run 5 random distance queries
    print("\nRunning random queries:")
    for _ in range(5):
        u = random.randint(0, pll.n - 1)
        v = random.randint(0, pll.n - 1)
        
        query_start = time.time()
        distance = pll.query(u, v)
        query_time = (time.time() - query_start) * 1000000 # convert to microseconds
        
        print(f"Distance between {u} and {v}: {distance} (took {query_time:.2f} µs)")