import urllib.request
import gzip
import time
import random
from collections import deque
from pll import PrunedLandmarkLabeling


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

def verify_distance_bfs(graph, start, target):
    """A standard, brute-force BFS to serve as the ground truth."""
    if start == target:
        return 0
        
    queue = deque([(start, 0)])
    visited = {start}
    
    while queue:
        current, dist = queue.popleft()
        
        for neighbor in graph[current]:
            if neighbor == target:
                return dist + 1
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
                
    return float('inf') # No path exists


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
    print("\nRunning random queries and verifying...")
    for _ in range(5):
        u = random.randint(0, pll.n - 1)
        v = random.randint(0, pll.n - 1)
        
        # Get answer from PLL index
        query_start = time.time()
        pll_distance = pll.query(u, v)
        query_time = (time.time() - query_start) * 1000000 
        
        # Get answer from brute force BFS
        brute_force_start = time.time()
        bfs_distance = verify_distance_bfs(graph, u, v)
        brute_force_time = (time.time() - brute_force_start) * 1000000 
        
        # Check answer
        status = "PASS" if pll_distance == bfs_distance else "FAIL"
        
        print(f"[{status}] Dist({u}, {v}) = {pll_distance} (PLL took {query_time:.2f} µs)")
        print(f"Brute force BFS took {brute_force_time:.2f} µs")