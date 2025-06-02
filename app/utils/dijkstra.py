from math import inf
from app.utils.jarak import calculate_distance

def create_graph(office, packages):
    """Membuat graph dari kantor dan semua paket"""
   
    nodes = [(office.lat, office.lng)] + [(p.lat, p.lng) for p in packages]
    n = len(nodes)
    
    
    graph = [[0 if i == j else calculate_distance(nodes[i][0], nodes[i][1], 
             nodes[j][0], nodes[j][1]) for j in range(n)] for i in range(n)]
    
    return graph, nodes

def dijkstra_shortest_path(graph, start=0):
    """Implementasi algoritma Dijkstra untuk mencari rute terpendek"""
    n = len(graph)
    distances = [inf] * n
    distances[start] = 0
    unvisited = set(range(n))
    previous = [None] * n
    
    while unvisited:
        
        current = min(unvisited, key=lambda x: distances[x])
        
        if distances[current] == inf:
            break
            
        unvisited.remove(current)
        
       
        for neighbor in range(n):
            if neighbor in unvisited:
                new_distance = distances[current] + graph[current][neighbor]
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current
    
    return distances, previous

def get_optimal_route(office, packages):
    """Mendapatkan rute optimal menggunakan Dijkstra"""
    if not packages:
        return [], 0
        
   
    graph, nodes = create_graph(office, packages)
    n = len(nodes)
    
    
    total_distance = 0
    ordered_packages = []
    current_pos = 0 
    
   
    unvisited = set(range(1, n))  
    
    
    while unvisited:
        
        distances, _ = dijkstra_shortest_path(graph, current_pos)
        
        
        next_pos = min(unvisited, key=lambda x: distances[x])
        
        
        total_distance += distances[next_pos]
        
        
        package = packages[next_pos - 1]  
        package.distance = distances[next_pos] 
        ordered_packages.append(package)
        
        
        current_pos = next_pos
        unvisited.remove(next_pos)
    
    return ordered_packages, total_distance