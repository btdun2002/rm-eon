def create_nsfnet_topology():
    nodes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

    edges = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 5), (3, 6), (4, 7), (5, 8), (6, 9), (7, 10),
             (8, 11), (9, 12), (10, 13), (11, 14), (12, 13), (13, 14), (4, 5),
             (6, 7), (8, 9), (10, 11), (12, 14), (1, 14)]
    adjacency_list = {node: [] for node in nodes}
    for u, v in edges:
        adjacency_list[u].append(v)
        adjacency_list[v].append(u)

    topology_data = {
        'nodes': nodes,
        'edges': edges,
        'adjacency_list': adjacency_list
    }
    return topology_data
