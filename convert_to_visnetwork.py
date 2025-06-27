#!/usr/bin/env python3
"""
GraphRAG到vis-network数据转换脚本

该脚本将GraphRAG生成的parquet文件转换为vis-network可视化库所需的JSON格式。

作者: AI Assistant
日期: 2025-06-27
"""

import pandas as pd
import json
import os
from typing import Dict, List, Any, Tuple
import hashlib


def load_parquet_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    加载GraphRAG生成的parquet文件
    
    Returns:
        entities, relationships, communities数据框
    """
    try:
        entities_df = pd.read_parquet("output/entities.parquet")
        relationships_df = pd.read_parquet("output/relationships_with_types.parquet")
        communities_df = pd.read_parquet("output/communities.parquet")
        
        print(f"✅ 数据加载成功:")
        print(f"  - 实体数量: {len(entities_df)}")
        print(f"  - 关系数量: {len(relationships_df)}")
        print(f"  - 社区数量: {len(communities_df)}")
        
        return entities_df, relationships_df, communities_df
        
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        raise


def get_node_color_by_type(entity_type: str) -> Dict[str, str]:
    """
    根据实体类型返回节点颜色配置
    
    Args:
        entity_type: 实体类型
        
    Returns:
        颜色配置字典
    """
    color_map = {
        "person": {
            "background": "#FFA500",
            "border": "#FF8C00",
            "highlight": {"background": "#FFD700", "border": "#FF8C00"}
        },
        "organization": {
            "background": "#7BE141",
            "border": "#4AD63A",
            "highlight": {"background": "#90EE90", "border": "#4AD63A"}
        },
        "concept": {
            "background": "#FB7E81",
            "border": "#FA0A10",
            "highlight": {"background": "#FFB6C1", "border": "#FA0A10"}
        },
        "location": {
            "background": "#87CEEB",
            "border": "#4682B4",
            "highlight": {"background": "#B0E0E6", "border": "#4682B4"}
        },
        "event": {
            "background": "#DDA0DD",
            "border": "#9370DB",
            "highlight": {"background": "#E6E6FA", "border": "#9370DB"}
        },
        "default": {
            "background": "#97C2FC",
            "border": "#2B7CE9",
            "highlight": {"background": "#D2E5FF", "border": "#2B7CE9"}
        }
    }
    
    return color_map.get(entity_type.lower(), color_map["default"])


def get_edge_style_by_type(relationship_type: str) -> Dict[str, Any]:
    """
    根据关系类型返回边样式配置
    
    Args:
        relationship_type: 关系类型
        
    Returns:
        边样式配置字典
    """
    style_map = {
        "IS_A": {
            "color": {"color": "#2B7CE9", "highlight": "#2B7CE9"},
            "arrows": {"to": {"enabled": True, "type": "arrow"}},
            "dashes": False,
            "width": 2
        },
        "PART_OF": {
            "color": {"color": "#4AD63A", "highlight": "#4AD63A"},
            "arrows": {"to": {"enabled": True, "type": "arrow"}},
            "dashes": False,
            "width": 3
        },
        "MENTIONS": {
            "color": {"color": "#848484", "highlight": "#848484"},
            "arrows": {"to": {"enabled": True, "type": "arrow"}},
            "dashes": [5, 5],
            "width": 1
        },
        "TEACHES": {
            "color": {"color": "#FFA500", "highlight": "#FFA500"},
            "arrows": {"to": {"enabled": True, "type": "arrow"}},
            "dashes": False,
            "width": 2
        },
        "COLLABORATES_WITH": {
            "color": {"color": "#9A4DFF", "highlight": "#9A4DFF"},
            "arrows": {"to": {"enabled": True, "type": "circle"}},
            "dashes": False,
            "width": 2
        },
        "CAUSES": {
            "color": {"color": "#FA0A10", "highlight": "#FA0A10"},
            "arrows": {"to": {"enabled": True, "type": "arrow"}},
            "dashes": False,
            "width": 3
        },
        "USES": {
            "color": {"color": "#00CED1", "highlight": "#00CED1"},
            "arrows": {"to": {"enabled": True, "type": "bar"}},
            "dashes": False,
            "width": 2
        },
        "CONTAINS": {
            "color": {"color": "#32CD32", "highlight": "#32CD32"},
            "arrows": {"to": {"enabled": True, "type": "box"}},
            "dashes": False,
            "width": 2
        },
        "BELONGS_TO": {
            "color": {"color": "#FF69B4", "highlight": "#FF69B4"},
            "arrows": {"to": {"enabled": True, "type": "arrow"}},
            "dashes": [10, 5],
            "width": 2
        },
        "RELATED_TO": {
            "color": {"color": "#808080", "highlight": "#808080"},
            "arrows": {"to": {"enabled": True, "type": "arrow"}},
            "dashes": [3, 3],
            "width": 1
        },
        "UNKNOWN": {
            "color": {"color": "#C0C0C0", "highlight": "#C0C0C0"},
            "arrows": {"to": {"enabled": True, "type": "arrow"}},
            "dashes": [2, 2],
            "width": 1
        }
    }
    
    return style_map.get(relationship_type, style_map["UNKNOWN"])


def calculate_edge_width(weight: float) -> int:
    """
    根据关系权重计算边宽度
    
    Args:
        weight: 关系权重
        
    Returns:
        边宽度
    """
    if pd.isna(weight):
        return 1
    
    # 将权重映射到1-5的宽度范围
    min_width, max_width = 1, 5
    normalized_weight = max(0, min(1, weight))  # 确保在0-1范围内
    return int(min_width + (max_width - min_width) * normalized_weight)


def entity_to_node(entity_row: pd.Series) -> Dict[str, Any]:
    """
    将实体数据转换为vis-network节点格式
    
    Args:
        entity_row: 实体数据行
        
    Returns:
        vis-network节点字典
    """
    entity_title = str(entity_row["title"])
    entity_desc = str(entity_row.get("description", ""))
    entity_type = str(entity_row.get("type", "default"))
    
    # 创建悬停提示
    title_html = f"<b>{entity_title}</b>"
    if entity_desc and entity_desc != "nan":
        title_html += f"<br/>{entity_desc[:200]}..."
    
    return {
        "id": entity_title,
        "label": entity_title,
        "title": title_html,
        "group": entity_type,
        "color": get_node_color_by_type(entity_type),
        "shape": "dot",
        "size": 25,
        "font": {"size": 14, "color": "#000000"},
        "physics": True
    }


def relationship_to_edge(rel_row: pd.Series, edge_id: str) -> Dict[str, Any]:
    """
    将关系数据转换为vis-network边格式
    
    Args:
        rel_row: 关系数据行
        edge_id: 边ID
        
    Returns:
        vis-network边字典
    """
    source = str(rel_row["source"])
    target = str(rel_row["target"])
    rel_type = str(rel_row.get("relationship_type", "UNKNOWN"))
    description = str(rel_row.get("description", ""))
    weight = rel_row.get("weight", 1.0)
    
    # 创建悬停提示
    title_html = f"<b>{rel_type}</b><br/>{source} → {target}"
    if description and description != "nan":
        title_html += f"<br/>{description[:200]}..."
    
    # 获取样式配置
    style = get_edge_style_by_type(rel_type)
    
    return {
        "id": edge_id,
        "from": source,
        "to": target,
        "label": rel_type,
        "title": title_html,
        "color": style["color"],
        "width": calculate_edge_width(weight),
        "arrows": style["arrows"],
        "dashes": style["dashes"],
        "smooth": {"enabled": True, "type": "dynamic"},
        "physics": True
    }


def convert_data_to_visnetwork(entities_df: pd.DataFrame, 
                              relationships_df: pd.DataFrame) -> Tuple[List[Dict], List[Dict]]:
    """
    将GraphRAG数据转换为vis-network格式
    
    Args:
        entities_df: 实体数据框
        relationships_df: 关系数据框
        
    Returns:
        (nodes, edges)元组
    """
    print("🔄 开始数据转换...")
    
    # 转换实体为节点
    nodes = []
    entity_set = set()
    
    for _, entity_row in entities_df.iterrows():
        node = entity_to_node(entity_row)
        if node["id"] not in entity_set:
            nodes.append(node)
            entity_set.add(node["id"])
    
    # 从关系中提取额外的实体（确保所有实体都有节点）
    for _, rel_row in relationships_df.iterrows():
        for entity_name in [rel_row["source"], rel_row["target"]]:
            entity_name = str(entity_name)
            if entity_name not in entity_set:
                # 创建默认节点
                node = {
                    "id": entity_name,
                    "label": entity_name,
                    "title": f"<b>{entity_name}</b>",
                    "group": "default",
                    "color": get_node_color_by_type("default"),
                    "shape": "dot",
                    "size": 20,
                    "font": {"size": 12, "color": "#000000"},
                    "physics": True
                }
                nodes.append(node)
                entity_set.add(entity_name)
    
    # 转换关系为边
    edges = []
    edge_set = set()
    
    for idx, rel_row in relationships_df.iterrows():
        source = str(rel_row["source"])
        target = str(rel_row["target"])
        
        # 创建边ID（避免重复）
        edge_key = f"{source}-{target}"
        edge_id = hashlib.md5(edge_key.encode()).hexdigest()[:8]
        
        if edge_key not in edge_set:
            edge = relationship_to_edge(rel_row, edge_id)
            edges.append(edge)
            edge_set.add(edge_key)
    
    print(f"✅ 转换完成:")
    print(f"  - 节点数量: {len(nodes)}")
    print(f"  - 边数量: {len(edges)}")
    
    return nodes, edges


def save_json_data(nodes: List[Dict], edges: List[Dict]) -> None:
    """
    保存数据为JSON文件
    
    Args:
        nodes: 节点列表
        edges: 边列表
    """
    # 保存节点数据
    with open("nodes.json", "w", encoding="utf-8") as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)
    
    # 保存边数据
    with open("edges.json", "w", encoding="utf-8") as f:
        json.dump(edges, f, ensure_ascii=False, indent=2)
    
    # 保存完整数据
    complete_data = {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "generated_at": pd.Timestamp.now().isoformat()
        }
    }
    
    with open("graph_data.json", "w", encoding="utf-8") as f:
        json.dump(complete_data, f, ensure_ascii=False, indent=2)
    
    print(f"📁 数据已保存:")
    print(f"  - nodes.json: {len(nodes)} 个节点")
    print(f"  - edges.json: {len(edges)} 个边")
    print(f"  - graph_data.json: 完整图数据")


def generate_statistics(nodes: List[Dict], edges: List[Dict]) -> None:
    """
    生成数据统计信息
    
    Args:
        nodes: 节点列表
        edges: 边列表
    """
    print("\n📊 数据统计:")
    print("-" * 40)
    
    # 节点统计
    node_groups = {}
    for node in nodes:
        group = node.get("group", "default")
        node_groups[group] = node_groups.get(group, 0) + 1
    
    print("节点分组统计:")
    for group, count in sorted(node_groups.items()):
        print(f"  {group}: {count}")
    
    # 边统计
    edge_types = {}
    for edge in edges:
        edge_type = edge.get("label", "UNKNOWN")
        edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
    
    print("\n关系类型统计:")
    for rel_type, count in sorted(edge_types.items()):
        print(f"  {rel_type}: {count}")


def main():
    """主函数"""
    print("🚀 开始GraphRAG到vis-network数据转换...")
    
    try:
        # 加载数据
        entities_df, relationships_df, communities_df = load_parquet_data()
        
        # 转换数据
        nodes, edges = convert_data_to_visnetwork(entities_df, relationships_df)
        
        # 保存数据
        save_json_data(nodes, edges)
        
        # 生成统计
        generate_statistics(nodes, edges)
        
        print("\n✅ 转换完成! 可以使用生成的JSON文件进行vis-network可视化。")
        
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        raise


if __name__ == "__main__":
    main()
