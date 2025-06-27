#!/usr/bin/env python3
"""
GraphRAG关系类型数据质量检查报告
"""

import pandas as pd
import re
from collections import Counter

def extract_relationship_type(description):
    """从描述中提取关系类型"""
    # 预定义的关系类型列表
    relation_types = [
        'BELONGS_TO', 'IS_A', 'RELATED_TO', 'TEACHES', 'PREREQUISITE_OF',
        'PART_OF', 'CAUSES', 'LOCATED_IN', 'MENTIONED_IN', 'WORKS_FOR',
        'MANAGES', 'CONTAINS', 'OCCURS_BEFORE', 'LEADS_TO', 'COLLABORATES_WITH',
        'OPPOSES', 'SIMILAR_TO', 'MENTIONS', 'CITES', 'AUTHORED_BY', 'PUBLISHED_IN',
        'DERIVED_FROM', 'HAS_TOPIC', 'USES', 'EXTENDS', 'HAS_PROPERTY'
    ]
    
    # 检查是否是纯关系类型
    if description.strip() in relation_types:
        return description.strip()
    
    # 在描述中查找关系类型
    for rel_type in relation_types:
        if rel_type in description:
            return rel_type
    
    return "UNKNOWN"

def generate_quality_report():
    """生成数据质量报告"""
    
    # 读取数据
    df = pd.read_parquet('output/relationships.parquet')
    
    print("📊 GraphRAG关系类型数据质量报告")
    print("=" * 60)
    
    # 基本统计
    print(f"\n📈 基本统计:")
    print(f"  总关系数: {len(df)}")
    print(f"  唯一源节点: {df['source'].nunique()}")
    print(f"  唯一目标节点: {df['target'].nunique()}")
    print(f"  平均权重: {df['weight'].mean():.2f}")
    print(f"  权重范围: {df['weight'].min():.1f} - {df['weight'].max():.1f}")
    
    # 提取关系类型
    df['relationship_type'] = df['description'].apply(extract_relationship_type)
    
    # 关系类型统计
    type_counts = df['relationship_type'].value_counts()
    print(f"\n🎯 关系类型分布:")
    print(f"  识别出的关系类型数: {len(type_counts)}")
    print(f"  成功识别率: {(len(df) - type_counts.get('UNKNOWN', 0)) / len(df) * 100:.1f}%")
    
    print(f"\n📋 详细关系类型统计:")
    for rel_type, count in type_counts.items():
        percentage = count / len(df) * 100
        print(f"  {rel_type:20s}: {count:2d} ({percentage:5.1f}%)")
    
    # 质量评估
    print(f"\n✅ 质量评估:")
    
    # 1. 关系类型覆盖度
    predefined_types = [
        'BELONGS_TO', 'IS_A', 'RELATED_TO', 'TEACHES', 'PREREQUISITE_OF',
        'PART_OF', 'CAUSES', 'LOCATED_IN', 'MENTIONED_IN', 'WORKS_FOR',
        'MANAGES', 'CONTAINS', 'OCCURS_BEFORE', 'LEADS_TO', 'COLLABORATES_WITH',
        'OPPOSES', 'SIMILAR_TO', 'MENTIONS', 'CITES', 'AUTHORED_BY', 'PUBLISHED_IN',
        'DERIVED_FROM', 'HAS_TOPIC', 'USES', 'EXTENDS', 'HAS_PROPERTY'
    ]
    
    found_types = set(type_counts.keys()) - {'UNKNOWN'}
    coverage = len(found_types) / len(predefined_types) * 100
    print(f"  关系类型覆盖度: {len(found_types)}/{len(predefined_types)} ({coverage:.1f}%)")
    
    # 2. 数据完整性
    missing_source = df['source'].isna().sum()
    missing_target = df['target'].isna().sum()
    missing_desc = df['description'].isna().sum()
    print(f"  数据完整性: 源节点缺失{missing_source}个, 目标节点缺失{missing_target}个, 描述缺失{missing_desc}个")
    
    # 3. 关系方向性
    bidirectional_count = 0
    for _, row in df.iterrows():
        reverse_exists = ((df['source'] == row['target']) & (df['target'] == row['source'])).any()
        if reverse_exists:
            bidirectional_count += 1
    print(f"  双向关系数: {bidirectional_count // 2} 对")
    
    # 4. 节点连接度分析
    source_counts = df['source'].value_counts()
    target_counts = df['target'].value_counts()
    
    print(f"\n🔗 节点连接度分析:")
    print(f"  最活跃源节点: {source_counts.index[0]} ({source_counts.iloc[0]} 个出度)")
    print(f"  最活跃目标节点: {target_counts.index[0]} ({target_counts.iloc[0]} 个入度)")
    
    # 5. 关系类型语义分析
    print(f"\n🧠 关系类型语义分析:")
    
    # 按语义分组
    semantic_groups = {
        '分类关系': ['IS_A', 'BELONGS_TO', 'PART_OF'],
        '使用关系': ['USES', 'CONTAINS'],
        '属性关系': ['HAS_PROPERTY'],
        '时间关系': ['OCCURS_BEFORE', 'LEADS_TO'],
        '对立关系': ['OPPOSES'],
        '协作关系': ['COLLABORATES_WITH'],
        '相似关系': ['SIMILAR_TO'],
        '引用关系': ['MENTIONS'],
        '通用关系': ['RELATED_TO']
    }
    
    for group_name, types in semantic_groups.items():
        group_count = sum(type_counts.get(t, 0) for t in types)
        if group_count > 0:
            print(f"  {group_name}: {group_count} 个关系")
            for t in types:
                if t in type_counts:
                    print(f"    - {t}: {type_counts[t]}")
    
    # 6. 生成改进建议
    print(f"\n💡 改进建议:")
    
    unknown_count = type_counts.get('UNKNOWN', 0)
    if unknown_count > 0:
        print(f"  - 有 {unknown_count} 个关系未能识别类型，建议优化提示词")
    
    if coverage < 50:
        print(f"  - 关系类型覆盖度较低({coverage:.1f}%)，建议增加更多样化的训练数据")
    
    if len(found_types) < 10:
        print(f"  - 关系类型多样性不足，建议调整实体类型和文档内容")
    
    # 保存增强的数据
    df_enhanced = df.copy()
    df_enhanced['extracted_relationship_type'] = df['relationship_type']
    df_enhanced.to_parquet('output/relationships_with_types.parquet', index=False)
    print(f"\n💾 已保存增强数据到: output/relationships_with_types.parquet")
    
    return df_enhanced

if __name__ == "__main__":
    enhanced_df = generate_quality_report()
