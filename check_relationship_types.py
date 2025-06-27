#!/usr/bin/env python3
"""
检查GraphRAG生成的关系数据中的关系类型信息
"""

import pandas as pd
import json

def analyze_relationships():
    """分析关系数据中的关系类型"""
    
    # 读取关系数据
    df = pd.read_parquet('output/relationships.parquet')
    
    print("🔍 分析关系类型信息")
    print("=" * 50)
    
    # 检查描述字段中的关系类型
    print("\n📋 关系描述分析:")
    print(f"总关系数: {len(df)}")
    
    # 查看所有描述
    print("\n📝 所有关系描述:")
    for i, row in df.iterrows():
        desc = row['description']
        print(f"{i+1:2d}. {row['source']} -> {row['target']}")
        print(f"    描述: {desc}")
        print(f"    权重: {row['weight']}")
        print()
    
    # 检查是否有简短的关系类型描述
    short_descriptions = df[df['description'].str.len() < 50]
    if len(short_descriptions) > 0:
        print(f"\n🎯 发现 {len(short_descriptions)} 个可能的关系类型:")
        for _, row in short_descriptions.iterrows():
            print(f"  {row['source']} -> {row['target']}: {row['description']}")
    
    # 统计描述长度分布
    desc_lengths = df['description'].str.len()
    print(f"\n📊 描述长度统计:")
    print(f"  最短: {desc_lengths.min()} 字符")
    print(f"  最长: {desc_lengths.max()} 字符")
    print(f"  平均: {desc_lengths.mean():.1f} 字符")
    print(f"  中位数: {desc_lengths.median():.1f} 字符")
    
    # 查找可能的关系类型模式
    print(f"\n🔍 查找关系类型模式:")
    
    # 预定义的关系类型列表
    relation_types = [
        'BELONGS_TO', 'IS_A', 'RELATED_TO', 'TEACHES', 'PREREQUISITE_OF',
        'PART_OF', 'CAUSES', 'LOCATED_IN', 'MENTIONED_IN', 'WORKS_FOR',
        'MANAGES', 'CONTAINS', 'OCCURS_BEFORE', 'LEADS_TO', 'COLLABORATES_WITH',
        'OPPOSES', 'SIMILAR_TO', 'MENTIONS', 'CITES', 'AUTHORED_BY', 'PUBLISHED_IN',
        'DERIVED_FROM', 'HAS_TOPIC', 'USES', 'EXTENDS', 'HAS_PROPERTY'
    ]
    
    found_types = {}
    for rel_type in relation_types:
        matches = df[df['description'].str.contains(rel_type, case=False, na=False)]
        if len(matches) > 0:
            found_types[rel_type] = len(matches)
            print(f"  ✅ {rel_type}: {len(matches)} 个关系")
            for _, row in matches.iterrows():
                print(f"     {row['source']} -> {row['target']}")
    
    if not found_types:
        print("  ❌ 未找到预定义的关系类型")
    
    print(f"\n📈 关系类型统计:")
    for rel_type, count in sorted(found_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {rel_type}: {count}")

if __name__ == "__main__":
    analyze_relationships()
