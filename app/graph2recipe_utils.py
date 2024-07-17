# 逆向きエッジをdictで作成，検索の計算量を削減
def create_reverse_edges(edges, reverse_edges):
    """
    reverse_edges(dict): 結果格納用の引数
        {nodeID2(int) : [[nodeID1a(int), edgeIDa(int)], [nodeID1b(int), edgeIDb(int)], ...]} nodeID1 -> nodeID2
    """
    for edge_id, edge in edges.items():
        node1, node2 = edge[0], edge[1]
        if node2 not in reverse_edges:
            reverse_edges[node2] = []
        reverse_edges[node2].append([node1, edge_id])

# 深さ優先探索で逆向きに探索，サブグラフを取得
def get_subgraph_dfs(target_node, reverse_edges, visited, subgraph_edges):
    stack = [target_node]

    while stack:
        current_node = stack.pop()
        if current_node not in visited:
            visited.add(current_node)
            if current_node in reverse_edges:
                for edge in reverse_edges[current_node]:
                    node1, edge_id = edge[0], edge[1]
                    subgraph_edges[edge_id] = [node1, current_node]
                    stack.append(node1)

# Output: edges: dict {edgeID:int : [nodeID1:int, nodeID2:int]}, 意味: nodeID1 -> nodeID2
def get_edges():
    # QUE君担当の関数を叩きます
    # 必要なら辞書型に直します
    # return edges
    pass

def get_node_info(node: int) -> str:
    """
    Input: nodeID(int)
    Returns: ノードの説明(str)
    """
    # QUE君担当の関数を叩きます
    # 必要なら文字列に直します
    # return node_info
    pass

def get_edge_info(node: int) -> str:
    """
    Input: edgeID(int)
    Returns: エッジの説明(str)
    """
    # QUE君担当の関数を叩きます
    # 必要なら文字列に直します
    # return edge_info
    pass