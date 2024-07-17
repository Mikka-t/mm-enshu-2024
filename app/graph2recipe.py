from graph2recipe_utils import *

def get_subgraph(target_node: int):
    """
    future work: cache recent subgraph

    get recipe subgraph from dataset

    Input: target_node(int)...完成料理ノードID
    Returns: 
        subgraph_nodes(dict) {nodeID(int) : node_info(dict)}, 
        node_info(dict) = {nodeID(int) : node_info(dict)}
        subgraph_edges(dict) {edgeID(int) : [nodeID1(int), nodeID2(int)]}
            意味: nodeID1 -> nodeID2
    """
    # edges: dict {edgeID:int : [nodeID1:int, nodeID2:int]}, 意味: nodeID1 -> nodeID2
    # get_edges: サーバーと通信する関数，edgesを取得
    edges = get_edges()

    reverse_edges = {}
    # エッジを逆向きにして計算量削減
    # {nodeID2(int) : [[nodeID1a(int), edgeIDa(int)], ...} nodeID1 -> nodeID2
    create_reverse_edges(edges, reverse_edges)

    # 結果を格納
    subgraph_nodes = set()
    subgraph_node_info = {}
    subgraph_edges = {}
    subgraph_edge_info = {}

    # 深さ優先探索で逆向きに探索，サブグラフを取得
    get_subgraph_dfs(target_node, reverse_edges, subgraph_nodes, subgraph_edges)

    # ノード説明文を取得
    for nodeID in subgraph_nodes:
        # サーバにノードIDを渡して説明文を取得
        node_info = get_node_info(nodeID)
        subgraph_node_info[nodeID] = node_info

    # エッジ説明文を取得
    for edgeID, edge in subgraph_edges.items():
        # サーバにノードIDを渡して説明文を取得
        edge_info = get_edge_info(edgeID)
        subgraph_edge_info[edgeID] = edge_info

    return subgraph_nodes, subgraph_edges, subgraph_node_info, subgraph_edge_info