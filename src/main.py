from collections import deque, defaultdict

class PrunedLandmarkLabeling:
    def __init__(self, graph):
        # graph is adjacency list of [v: [neighbours]]
        self.graph = graph
        self.vertices = graph.copy()
        self.n = len(graph)
        
        # Degree sorting strategy
        self.vertices.sort(key=lambda v: len(v), reverse=True)
        # tuple of (vertex, dist)
        self.L = [[] for _ in range(self.n)]
        
    def construct_index(self):
        P = [float('inf') for _ in range(self.n)]
        pass
    
    def pruned_bfs(self, v, P):
        queue = deque()
        queue.append(v)
        visited = []
        
        T = [float('inf') for _ in range(self.n)]
        for _, w in self.L[v]:
            T[w] = w
        T[v] = 0
        
        while len(queue) > 0:
            u, cur_dist = queue.pop()
            min_query_dist = float('inf')
            for w, dist in self.L[u]:
                min_query_dist = min(min_query_dist, dist + T[w])
                
            if min_query_dist <= cur_dist:
                continue
            
            self.L[u].append((v, cur_dist))
            
            for w in self.graph[u]:
                if P[w] != float('inf'):
                    P[w] = P[u] + 1
                    queue.append(w)
                    visited.append(w)
                    
        for w in visited:
            P[w] = float('inf')
            