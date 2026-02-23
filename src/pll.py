from collections import deque

class PrunedLandmarkLabeling:
    def __init__(self, graph):
        """
        Initialises the 2-hop cover structure. Sorts vertices by degree (highest first) 
        to ensure highly connected hubs are processed early, maximising pruning efficiency.
        """
        # graph is adjacency list of [v: [neighbours]]
        self.graph = graph
        self.n = len(graph)
        self.vertex_order = list(range(self.n))
        
        # Degree sorting strategy
        self.vertex_order.sort(key=lambda v: len(graph[v]), reverse=True)
        # tuple of (vertex, dist)
        self.L = [[] for _ in range(self.n)]
        
        
    def build_index(self):
        """
        Constructs the index by executing a pruned Breadth-First Search 
        from every vertex sequentially, strictly following the computed rank order.
        """
        P = [float('inf') for _ in range(self.n)]
        for rank, v in enumerate(self.vertex_order):
            self.pruned_bfs(v, rank, P)    
        
    
    def pruned_bfs(self, v, rank_v, P):
        """
        Explores the graph from root 'v'. Uses a dense T-array to check existing 
        labels in O(|L(u)|) time, pruning the branch if a known optimal path already exists.
        """
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
        """
        Calculates the exact shortest distance in linear O(|L(u)| + |L(v)|) time 
        by performing a two-pointer merge-join across the implicitly sorted label lists.
        """
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

