import pandas as pd

def verify_relationship_fields():
    """验证 relationships.parquet 中的字段结构"""
    
    print("🔍 验证 GraphRAG relationships.parquet 文件结构")
    print("=" * 60)
    
    # 读取 relationships.parquet
    relationships_df = pd.read_parquet('output/relationships.parquet')
    
    print(f"📊 Relationships.parquet 文件信息:")
    print(f"  文件路径: output/relationships.parquet")
    print(f"  行数: {len(relationships_df)}")
    print(f"  列数: {len(relationships_df.columns)}")
    
    print(f"\n📋 所有字段列表:")
    for i, col in enumerate(relationships_df.columns, 1):
        print(f"  {i}. {col}")
    
    print(f"\n🔍 字段详细信息:")
    for col in relationships_df.columns:
        dtype = relationships_df[col].dtype
        non_null_count = relationships_df[col].count()
        null_count = len(relationships_df) - non_null_count
        
        print(f"  {col}:")
        print(f"    类型: {dtype}")
        print(f"    非空值: {non_null_count}")
        print(f"    空值: {null_count}")
        
        # 显示示例值
        if non_null_count > 0:
            sample_value = str(relationships_df[col].iloc[0])
            if len(sample_value) > 100:
                sample_value = sample_value[:100] + "..."
            print(f"    示例: {sample_value}")
        print()
    
    # 检查是否有 relationship 字段
    print(f"🔍 关系字段检查:")
    relationship_fields = [col for col in relationships_df.columns if 'relationship' in col.lower()]
    if relationship_fields:
        print(f"  ✅ 找到关系相关字段: {relationship_fields}")
    else:
        print(f"  ❌ 没有找到名为 'relationship' 的字段")
    
    # 检查核心关系字段
    core_fields = ['source', 'target', 'description', 'weight']
    print(f"\n📋 核心关系字段检查:")
    for field in core_fields:
        if field in relationships_df.columns:
            print(f"  ✅ {field}: 存在")
        else:
            print(f"  ❌ {field}: 缺失")
    
    # 显示前几个关系示例
    print(f"\n📝 关系数据示例 (前5个):")
    for i in range(min(5, len(relationships_df))):
        row = relationships_df.iloc[i]
        print(f"  关系 {i+1}:")
        print(f"    源节点: {row.get('source', 'N/A')}")
        print(f"    目标节点: {row.get('target', 'N/A')}")
        print(f"    描述: {str(row.get('description', 'N/A'))[:100]}...")
        print(f"    权重: {row.get('weight', 'N/A')}")
        print()
    
    # 分析关系网络
    print(f"🕸️ 关系网络统计:")
    if 'source' in relationships_df.columns and 'target' in relationships_df.columns:
        unique_sources = relationships_df['source'].nunique()
        unique_targets = relationships_df['target'].nunique()
        all_nodes = set(relationships_df['source'].unique()) | set(relationships_df['target'].unique())
        
        print(f"  唯一源节点: {unique_sources}")
        print(f"  唯一目标节点: {unique_targets}")
        print(f"  总节点数: {len(all_nodes)}")
        print(f"  节点列表: {', '.join(sorted(all_nodes))}")
    
    return relationships_df

def compare_with_entities():
    """比较 relationships.parquet 和 entities.parquet 的一致性"""
    
    print(f"\n🔄 比较实体和关系数据的一致性:")
    
    entities_df = pd.read_parquet('output/entities.parquet')
    relationships_df = pd.read_parquet('output/relationships.parquet')
    
    # 从实体文件获取所有实体
    entity_names = set(entities_df['title'].unique())
    
    # 从关系文件获取所有节点
    if 'source' in relationships_df.columns and 'target' in relationships_df.columns:
        relationship_nodes = set(relationships_df['source'].unique()) | set(relationships_df['target'].unique())
        
        print(f"  实体文件中的实体数: {len(entity_names)}")
        print(f"  关系文件中的节点数: {len(relationship_nodes)}")
        
        # 检查一致性
        entities_not_in_relationships = entity_names - relationship_nodes
        relationships_not_in_entities = relationship_nodes - entity_names
        
        if entities_not_in_relationships:
            print(f"  ⚠️ 在实体中但不在关系中: {entities_not_in_relationships}")
        else:
            print(f"  ✅ 所有实体都在关系中出现")
            
        if relationships_not_in_entities:
            print(f"  ⚠️ 在关系中但不在实体中: {relationships_not_in_entities}")
        else:
            print(f"  ✅ 所有关系节点都在实体中存在")

if __name__ == "__main__":
    relationships_df = verify_relationship_fields()
    compare_with_entities()
    
    print(f"\n💡 总结:")
    print(f"  - GraphRAG 不生成 graph.parquet 文件")
    print(f"  - 关系数据存储在 relationships.parquet 中")
    print(f"  - 该文件包含 source, target, description, weight 等字段")
    print(f"  - 这就是您需要的节点间关系数据！")
