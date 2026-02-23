# Pruned Landmark Labeling (Python)

A simple Python implementation of exact shortest-path distance queries using Pruned Landmark Labeling, as described in [Akiba et al. (2013)](https://arxiv.org/abs/1304.4661).

This repository provides an educational, fully functional index that compresses the shortest-path knowledge of an unweighted, undirected network to allow for efficient distance queries.

## Key Optimizations Included
* **Degree-based Ordering:** Processes highly central "hub" vertices first to maximize BFS pruning.
* **Implicit Label Sorting:** Eliminates $O(N \log N)$ sorting overhead by indexing hubs by their topological rank.
* **$O(1)$ Array Cleanup:** Avoids massive $O(V)$ initialization penalties during the BFS phase.
* **Merge-Join Queries:** Resolves distance queries in microseconds using a two-pointer merge across pre-sorted labels.

## Quick Start

```python
from pll import PrunedLandmarkLabeling

# 1. Define an undirected, unweighted graph as an adjacency list
graph = [
    [1, 3],       # Neighbors of Node 0
    [0, 2, 4],    # Neighbors of Node 1
    [1],          # Neighbors of Node 2
    [0, 4],       # Neighbors of Node 3
    [1, 3]        # Neighbors of Node 4
]

# 2. Build the index
pll = PrunedLandmarkLabeling(graph)
pll.build_index()

# 3. Query exact shortest-path distances
distance = pll.query(2, 3)
print(f"Shortest path distance: {distance}") 
# Output: 3
