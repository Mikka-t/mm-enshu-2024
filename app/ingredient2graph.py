from graph2recipe_utils import *

def ingredient2graph(ingredient_list: list):
    """
    ex) ["牛乳", "卵", "小麦粉"] -> {"nodes":[{"id": "生地", "type":"intermediate"}] , "edges": []}
    ingredient_list: ノードIDのリスト
    TODO: 材料名のサジェスト
    TODO: 軽量化
    """

    nodes, edges = get_graph_str()

    reverse_edges = {}
    # [{target : [source, action]}, ...]
    create_reverse_edges_str(edges, reverse_edges)
    
    node_dict = {}
    create_node_dict_str(nodes, node_dict)



    # stack = ingredient_list.copy()
    stack = []
    for ingredient in ingredient_list:
        found = False
        for edge in edges:
            if ingredient == edge['source'] or ingredient == edge['target']:
                stack.append([ingredient, 1])
                found = True
                break
        if not found:
            print(f"WARNING: ingredient2graph.py: {ingredient} は存在しません。")

    visited = set()
    final_nodes = []
    print("検索を開始")

    while stack:
        current_node = stack.pop()
        if current_node[0] not in visited:
            visited.add(current_node[0])
            # sourceがcurrent_nodeなエッジをすべて取得
            nodes_to_check = []
            for edge in edges:
                if edge["source"] == current_node[0]:
                    score_sum = 0
                    score_pos = 0
                    for edge2 in edges:
                        if edge2["target"] == edge["target"]:
                            score_sum += 1
                            if edge2["source"] in ingredient_list:
                                score_pos += 1
                    if edge["target"] in node_dict:
                        if node_dict[edge["target"]]["type"] == "final":
                            final_nodes.append([edge["target"], score_pos/score_sum])
                        else:
                            nodes_to_check.append([edge["target"], score_pos/score_sum])
                    else:
                        nodes_to_check.append([edge["target"], score_pos/score_sum])

            stack.extend(nodes_to_check)

    final_nodes = sorted(final_nodes, key=lambda x: x[1], reverse=True)
    final_nodes = [x[0] for x in final_nodes]
    final_nodes = list(set(final_nodes))
    final_nodes = final_nodes[:5]

    print("final_nodes:", final_nodes)
    print("サブグラフ生成開始")

    # final_nodesをfinal_nodeとしたsubgraph5つを作成
    subgraphs = []
    for final_node in final_nodes:
        subgraph_nodes_set = set()
        subgraph_nodes = []
        subgraph_edges = []
        get_subgraph_dfs_str(final_node, reverse_edges, subgraph_nodes_set, subgraph_edges)
        for node in subgraph_nodes_set:
            if node in node_dict:
                subgraph_nodes.append(node_dict[node])
            else:
                error_node = {"id": node, "type": "misc"}
                subgraph_nodes.append(error_node)
        subgraph = {"nodes": subgraph_nodes, "edges": subgraph_edges}
        subgraphs.append(subgraph)
    # 重複が無いようにマージ
    answer_nodes = []
    answer_edges = []
    print("サブグラフ合成開始")
    for subgraph in subgraphs:
        for node in subgraph["nodes"]:
            # if node["id"] not in answer_nodes:
            #     answer_nodes.append(node)
            # nodeの重複判定はid, type, quantityが全て同じなら同じノードとして扱う
            is_same_node = False
            for answer_node in answer_nodes:
                # if node["id"] == answer_node["id"] and node["type"] == answer_node["type"] and node["quantity"] == answer_node["quantity"]:
                #     is_same_node = True
                #     break
                # ["quantity"]がない場合とある場合に対応する．quantityが両方にない場合は同一ノード、quantityが片方にしかないから異なるノード．
                if node["id"] == answer_node["id"] and node["type"] == answer_node["type"]:
                    if "quantity" in node and "quantity" in answer_node:
                        if node["quantity"] == answer_node["quantity"]:
                            is_same_node = True
                            break
                    elif "quantity" not in node and "quantity" not in answer_node:
                        is_same_node = True
                        break
            if not is_same_node:
                answer_nodes.append(node)

        # for edge in subgraph["edges"]:
        #     if edge not in answer_edges:
        #         answer_edges.append(edge)
        # edgeの重複判定はsource, target, actionが全て同じなら同じエッジとして扱う
        for edge in subgraph["edges"]:
            is_same_edge = False
            for answer_edge in answer_edges:
                if edge["source"] == answer_edge["source"] and edge["target"] == answer_edge["target"] and edge["action"] == answer_edge["action"]:
                    is_same_edge = True
                    break
            if not is_same_edge:
                answer_edges.append(edge) 
    print("処理完了")
    return {"nodes": answer_nodes, "edges": answer_edges}






