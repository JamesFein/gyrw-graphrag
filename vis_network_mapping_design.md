# GraphRAG到vis-network数据映射设计文档

## 1. 概述

本文档定义了如何将GraphRAG生成的parquet文件数据转换为vis-network可视化库所需的数据格式。

## 2. 数据源分析

基于parquet文件结构分析，我们有以下关键数据源：

### 2.1 entities.parquet (13行, 10列)
- **用途**: 生成vis-network的nodes数据
- **关键字段**:
  - `id`: 实体唯一标识符
  - `title`: 实体名称（用作节点标签）
  - `description`: 实体描述（用作悬停提示）
  - `type`: 实体类型（用于节点分组和样式）

### 2.2 relationships_with_types.parquet (38行, 10列)
- **用途**: 生成vis-network的edges数据
- **关键字段**:
  - `source`: 源实体名称
  - `target`: 目标实体名称
  - `relationship_type`: 关系类型（用于边样式）
  - `description`: 关系描述（用作悬停提示）
  - `weight`: 关系权重（用于边宽度）

### 2.3 communities.parquet (3行, 12列)
- **用途**: 节点分组和社区着色
- **关键字段**:
  - `id`: 社区ID
  - `title`: 社区名称
  - `level`: 社区层级

## 3. vis-network数据格式设计

### 3.1 Nodes数据结构

```javascript
{
  id: String,           // 节点唯一ID
  label: String,        // 节点显示标签
  title: String,        // 悬停提示信息
  group: String,        // 节点分组（用于样式）
  color: Object,        // 节点颜色配置
  shape: String,        // 节点形状
  size: Number,         // 节点大小
  font: Object,         // 字体配置
  physics: Boolean      // 是否参与物理模拟
}
```

### 3.2 Edges数据结构

```javascript
{
  id: String,           // 边唯一ID
  from: String,         // 源节点ID
  to: String,           // 目标节点ID
  label: String,        // 边标签（关系类型）
  title: String,        // 悬停提示信息
  color: Object,        // 边颜色配置
  width: Number,        // 边宽度
  arrows: Object,       // 箭头配置
  dashes: Boolean,      // 是否虚线
  smooth: Object,       // 平滑曲线配置
  physics: Boolean      // 是否参与物理模拟
}
```

## 4. 数据映射规则

### 4.1 实体到节点映射

```python
def entity_to_node(entity_row):
    return {
        "id": entity_row["title"],  # 使用title作为ID
        "label": entity_row["title"],
        "title": f"<b>{entity_row['title']}</b><br/>{entity_row['description'][:200]}...",
        "group": entity_row.get("type", "default"),
        "color": get_node_color_by_type(entity_row.get("type")),
        "shape": "dot",
        "size": 25,
        "font": {"size": 14, "color": "#000000"},
        "physics": True
    }
```

### 4.2 关系到边映射

```python
def relationship_to_edge(rel_row, edge_id):
    return {
        "id": edge_id,
        "from": rel_row["source"],
        "to": rel_row["target"],
        "label": rel_row["relationship_type"],
        "title": f"<b>{rel_row['relationship_type']}</b><br/>{rel_row['description'][:200]}...",
        "color": get_edge_color_by_type(rel_row["relationship_type"]),
        "width": calculate_edge_width(rel_row["weight"]),
        "arrows": {"to": {"enabled": True, "type": get_arrow_type(rel_row["relationship_type"])}},
        "dashes": get_dash_pattern(rel_row["relationship_type"]),
        "smooth": {"enabled": True, "type": "dynamic"},
        "physics": True
    }
```

## 5. 样式配置方案

### 5.1 节点样式配置

```javascript
const nodeStyles = {
  "default": {
    color: {
      background: "#97C2FC",
      border: "#2B7CE9",
      highlight: {background: "#D2E5FF", border: "#2B7CE9"}
    }
  },
  "person": {
    color: {background: "#FFA500", border: "#FF8C00"},
    shape: "circle"
  },
  "organization": {
    color: {background: "#7BE141", border: "#4AD63A"},
    shape: "box"
  },
  "concept": {
    color: {background: "#FB7E81", border: "#FA0A10"},
    shape: "diamond"
  }
};
```

### 5.2 边样式配置

```javascript
const edgeStyles = {
  "IS_A": {
    color: {color: "#2B7CE9", highlight: "#2B7CE9"},
    arrows: {to: {type: "arrow"}},
    dashes: false,
    width: 2
  },
  "PART_OF": {
    color: {color: "#4AD63A", highlight: "#4AD63A"},
    arrows: {to: {type: "arrow"}},
    dashes: false,
    width: 3
  },
  "MENTIONS": {
    color: {color: "#848484", highlight: "#848484"},
    arrows: {to: {type: "arrow"}},
    dashes: [5, 5],
    width: 1
  },
  "TEACHES": {
    color: {color: "#FFA500", highlight: "#FFA500"},
    arrows: {to: {type: "arrow"}},
    dashes: false,
    width: 2
  },
  "COLLABORATES_WITH": {
    color: {color: "#9A4DFF", highlight: "#9A4DFF"},
    arrows: {to: {type: "circle"}},
    dashes: false,
    width: 2
  },
  "CAUSES": {
    color: {color: "#FA0A10", highlight: "#FA0A10"},
    arrows: {to: {type: "arrow"}},
    dashes: false,
    width: 3
  },
  "USES": {
    color: {color: "#00CED1", highlight: "#00CED1"},
    arrows: {to: {type: "bar"}},
    dashes: false,
    width: 2
  },
  "CONTAINS": {
    color: {color: "#32CD32", highlight: "#32CD32"},
    arrows: {to: {type: "box"}},
    dashes: false,
    width: 2
  }
};
```

## 6. 布局和物理引擎配置

### 6.1 推荐布局配置

```javascript
const layoutOptions = {
  randomSeed: 2,
  improvedLayout: true,
  clusterThreshold: 150,
  hierarchical: {
    enabled: false,
    levelSeparation: 150,
    nodeSpacing: 100,
    treeSpacing: 200,
    blockShifting: true,
    edgeMinimization: true,
    parentCentralization: true,
    direction: 'UD',
    sortMethod: 'hubsize'
  }
};
```

### 6.2 物理引擎配置

```javascript
const physicsOptions = {
  enabled: true,
  barnesHut: {
    gravitationalConstant: -2000,
    centralGravity: 0.3,
    springLength: 95,
    springConstant: 0.04,
    damping: 0.09,
    avoidOverlap: 0.1
  },
  maxVelocity: 50,
  minVelocity: 0.1,
  solver: 'barnesHut',
  stabilization: {
    enabled: true,
    iterations: 1000,
    updateInterval: 100,
    onlyDynamicEdges: false,
    fit: true
  },
  timestep: 0.5,
  adaptiveTimestep: true
};
```

## 7. 交互功能设计

### 7.1 基础交互

- **节点拖拽**: 允许用户拖拽节点重新布局
- **缩放平移**: 支持鼠标滚轮缩放和拖拽平移
- **选择高亮**: 点击节点或边时高亮显示
- **悬停提示**: 鼠标悬停显示详细信息

### 7.2 高级交互

- **搜索过滤**: 根据节点名称或类型过滤显示
- **关系类型过滤**: 按关系类型显示/隐藏边
- **社区聚类**: 按社区分组显示节点
- **导出功能**: 导出为PNG/SVG格式

## 8. 性能优化策略

### 8.1 数据优化

- **节点去重**: 确保节点ID唯一性
- **边去重**: 合并重复的关系
- **数据分页**: 大数据集分批加载
- **懒加载**: 按需加载节点详情

### 8.2 渲染优化

- **聚类显示**: 节点数量过多时自动聚类
- **LOD渲染**: 根据缩放级别调整细节
- **缓存机制**: 缓存计算结果
- **异步处理**: 大数据集异步处理

## 9. 实现优先级

1. **P0 - 核心功能**: 基础节点边渲染、基本交互
2. **P1 - 样式系统**: 关系类型样式、节点分组
3. **P2 - 交互增强**: 搜索过滤、悬停提示
4. **P3 - 性能优化**: 聚类、分页、导出功能
