# GraphRAG 知识图谱构建与可视化 PRD

## 1. 项目概述

### 1.1 项目目标

使用 Microsoft GraphRAG 框架从文档中构建知识图谱，生成包含关系类型字段的结构化数据，并通过 Web 可视化进行分析展示。

### 1.2 核心价值

- 从非结构化文本中提取结构化知识
- 构建包含关系类型的实体关系网络
- 提供直观的 Web 图谱可视化
- 支持复杂查询和分析
- 生成标准化的关系类型分类

## 2. 技术架构

### 2.1 核心组件

- **GraphRAG**: Microsoft 开源的知识图谱构建框架
- **Web 可视化**: 基于 HTML/JavaScript 的图谱可视化界面
- **LLM**: 大语言模型（通过 OpenAI 官方 API 访问）
- **Python 环境**: 运行 GraphRAG 的基础环境
- **自定义提示系统**: 用于生成关系类型字段的提示配置

### 2.2 数据流程

```
原始文档 → GraphRAG处理（含关系类型提取） → 知识图谱 → 包含relationship_type字段的parquet文件 → Web可视化
```

### 2.3 关系类型增强方案

为了在 GraphRAG 生成的 parquet 文件中包含 relationship_type 字段，需要实施以下技术方案：

- **自定义实体关系提取提示**: 修改 GraphRAG 的实体关系提取提示，明确要求 LLM 识别并分类关系类型
- **关系类型分类体系**: 建立标准化的关系类型分类，如"因果关系"、"从属关系"、"时间关系"等
- **输出格式定制**: 配置 GraphRAG 输出格式，确保关系数据包含类型字段
- **后处理增强**: 对生成的关系数据进行后处理，补充和标准化关系类型信息

## 3. 实施步骤

### 3.1 环境准备

#### 3.1.1 安装 GraphRAG

```bash
# 创建虚拟环境（已完成）
python -m venv .venv
.venv\Scripts\activate  # Windows 激活虚拟环境

# 安装GraphRAG（已完成）
pip install graphrag
```

### 3.2 项目初始化

#### 3.2.1 创建项目目录

```bash
# 项目目录已存在：C:\Users\Administrator\Desktop\graphrag
# 当前工作目录即为项目根目录
```

#### 3.2.2 初始化 GraphRAG

```bash
python -m graphrag.index --init --root .
```

#### 3.2.3 目录结构

```
C:\Users\Administrator\Desktop\graphrag/
├── .venv/                  # 虚拟环境（已创建）
├── .env                    # 环境变量配置
├── settings.yaml          # GraphRAG配置文件
├── input/                  # 输入文档目录
│   └── 第八章.md           # 输入文档
├── output/                 # 输出结果目录
└── 第八章.md               # 原始文档文件
```

### 3.3 配置设置

#### 3.3.1 OpenAI API 说明

本项目使用 OpenAI 官方 API 来访问 GPT-4.1 模型，以获得最佳的实体抽取和关系识别效果：

- **优势**: 官方 API 稳定性高、响应速度快、支持最新模型特性
- **模型**: 使用 `gpt-4.1-2025-04-14` 获得最佳的实体抽取和关系类型识别效果
- **嵌入模型**: 使用 `text-embedding-3-large` 获得高质量的文本嵌入

#### 3.3.2 环境变量配置 (.env)

```env
# OpenAI API配置
GRAPHRAG_API_KEY=your_openai_api_key_here
GRAPHRAG_API_BASE=https://api.openai.com/v1

```

#### 3.3.3 基础配置 (settings.yaml)

```yaml
models:
  default_chat_model:
    api_key: ${GRAPHRAG_API_KEY}
    api_base: ${GRAPHRAG_API_BASE}
    type: openai_chat
    model: gpt-4.1-2025-04-14
    max_tokens: 4000
    temperature: 0
    model_supports_json: true

  default_embedding_model:
    api_key: ${GRAPHRAG_API_KEY}
    api_base: ${GRAPHRAG_API_BASE}
    type: openai_embedding
    model: text-embedding-3-large

input:
  type: file
  file_type: text
  base_dir: "input"
  file_encoding: utf-8

output:
  type: file
  base_dir: "output"

cache:
  type: file
  base_dir: "cache"

reporting:
  type: file
  base_dir: "reporting"

# 关系类型增强配置
extract_graph:
  model_id: default_chat_model
  prompt: "prompts/entity_extraction_with_types.txt"
  entity_types: ["人物", "组织", "地点", "事件", "概念", "时间"]
  max_gleanings: 1
```

### 3.4 关系类型提示配置

#### 3.4.1 创建自定义提示文件

创建 `prompts/entity_extraction_with_types.txt` 文件，包含以下关键要素：

- **实体识别指令**: 明确要求识别特定类型的实体
- **关系类型分类**: 定义标准化的关系类型分类体系
- **输出格式规范**: 指定包含 relationship_type 字段的输出格式
- **中文优化**: 针对中文文本的特殊处理指令

#### 3.4.2 关系类型分类体系

基于 Neo4j 数据库的关系类型命名规范，建立以下标准化关系类型分类体系：

**命名规范**：

- 关系类型使用全大写字母
- 使用下划线分隔单词
- 采用动词或动词短语形式
- 具有明确的语义和方向性

**位置关系类**：

- `LOCATED_IN`: 位置关系（实体-地点）
- `CONTAINS`: 包含关系（容器-内容）

**因果关系类**：

- `CAUSES`: 直接因果关系
- `LEADS_TO`: 导致关系
- `RESULTS_FROM`: 结果关系
- `INFLUENCES`: 影响关系

**协作关系类**：

- `COLLABORATES_WITH`: 协作关系
- `PARTNERS_WITH`: 合作伙伴关系
- `SUPPORTS`: 支持关系
- `ASSISTS`: 协助关系

**对立关系类**：

- `OPPOSES`: 对立关系
- `CONFLICTS_WITH`: 冲突关系
- `COMPETES_WITH`: 竞争关系
- `CONTRADICTS`: 矛盾关系

**相似关系类**：

- `SIMILAR_TO`: 相似关系
- `EQUIVALENT_TO`: 等价关系
- `RELATED_TO`: 相关关系
- `ASSOCIATED_WITH`: 关联关系

**分类关系类**：

- `IS_A`: 实体分类关系（实体-上位类）
- `PART_OF`: 局部整体关系（子概念-整体概念）
- `BELONGS_TO`: 归属关系（实体-类别/学科）
- `HAS_PROPERTY`: 属性关系（实体-属性值）

**教育关系类**：

- `HAS_TOPIC`: 主题关系（文档/课程-主题/领域）
- `PREREQUISITE`: 前置关系（前置课程-后续课程）

**方法关系类**：

- `USES`: 使用关系（方法/模型-工具/框架）
- `EXTENDS`: 扩展关系（理论/方法-上位理论/方法）

### 3.5 数据准备

#### 3.5.1 准备输入文档

- 将待分析的文档放入 `input/` 目录
- 支持格式：.txt, .md, .docx, .pdf
- 建议单个文件不超过 10MB

#### 3.5.2 文档预处理建议

- 确保文档编码为 UTF-8
- 移除不必要的格式标记
- 保持文本结构清晰

### 3.6 自定义提示文件创建

#### 3.6.1 实体关系提取提示模板

创建包含 relationship_type 字段的自定义提示文件，指导 LLM 按照 Neo4j 标准生成关系类型：

**提示要点**：

- 明确要求输出包含 relationship_type 字段
- 提供标准关系类型列表供 LLM 参考
- 指定输出格式为结构化数据
- 强调关系方向性和语义准确性

#### 3.6.2 中文关系类型映射

建立中文描述到英文标准关系类型的映射规则：

**组织位置关系**：

- "工作于" → `WORKS_FOR`
- "管理" → `MANAGES`
- "位于" → `LOCATED_IN`
- "导致" → `CAUSES`
- "合作" → `COLLABORATES_WITH`

**分类归属关系**：

- "是一种" → `IS_A`
- "属于" → `BELONGS_TO`
- "部分" → `PART_OF`
- "具有属性" → `HAS_PROPERTY`

**学术研究关系**：

- "提及" → `MENTIONS`
- "引用" → `CITES`
- "作者是" → `AUTHORED_BY`
- "发表在" → `PUBLISHED_IN`
- "来源于" → `DERIVED_FROM`

**教育教学关系**：

- "教授" → `TEACHES`
- "主题是" → `HAS_TOPIC`
- "前置课程" → `PREREQUISITE`

**方法工具关系**：

- "使用" → `USES`
- "扩展" → `EXTENDS`

### 3.6.3 自定义关系抽取 Prompt 实现

#### 创建自定义 Prompt 文件

创建 `prompts/rel_extract.prompt` 文件，内容如下：

```text
# — Goal —
从下列文本中抽取三元组，并且为每条边打上"关系类型"。
允许的关系类型只有：
BELONGS_TO, IS_A, RELATED_TO, TEACHES, PREREQUISITE_OF,
PART_OF, CAUSES, LOCATED_IN, MENTIONED_IN, WORKS_FOR,
MANAGES, CONTAINS, OCCURS_BEFORE, LEADS_TO, COLLABORATES_WITH,
OPPOSES, SIMILAR_TO, MENTIONS, CITES, AUTHORED_BY, PUBLISHED_IN,
DERIVED_FROM, HAS_TOPIC, USES, EXTENDS, HAS_PROPERTY

# — 格式 —
("relationship"{tuple_delimiter}"<head>"{tuple_delimiter}"<tail>"
{tuple_delimiter}"<relation_type>"{tuple_delimiter}"<description>"
{tuple_delimiter}<strength>){record_delimiter}

{completion_delimiter}

# — 输入 —
{text_unit_delimiter}
{input_text}
```

#### 配置 settings.yaml

在 settings.yaml 中添加以下配置：

```yaml
# 自定义Prompt配置
prompts:
  extract_graph: ./prompts/rel_extract.prompt

# 关系抽取配置
extract_graph:
  model_id: default_chat_model
  prompt: "prompts/rel_extract.prompt"
  entity_types: ["人物", "组织", "地点", "事件", "概念", "时间"]
  max_gleanings: 1

# 解析器配置
extract:
  relation_tuple_length: 6
  relation_cols: [source, target, relation_type, description, weight, strength]
  strength_position: 5
```

### 3.7 构建知识图谱

#### 3.7.1 运行索引构建

```bash
python -m graphrag.index --root .
```

#### 3.7.2 监控处理进度

- 查看 `reporting/` 目录下的日志文件
- 处理时间取决于文档大小和复杂度
- 关注关系类型提取的准确性

#### 3.7.3 输出文件说明

```
output/
├── artifacts/
│   ├── create_final_entities.parquet      # 实体数据
│   ├── create_final_relationships.parquet # 关系数据（含relationship_type字段）
│   ├── create_final_communities.parquet   # 社区数据
│   └── create_final_nodes.parquet         # 节点数据
└── graph.graphml                          # GraphML格式图谱
```

**关系数据结构增强（6 列格式）**：

- `source`: 源实体 ID
- `target`: 目标实体 ID
- `relation_type`: 标准化关系类型（新增字段）
- `description`: 关系描述
- `weight`: 关系权重
- `strength`: 关系强度（用于保持列数一致）

**关键改进**：

- 新增 `relation_type` 字段，包含标准化的 Neo4j 风格关系类型
- 支持 26 种预定义关系类型，覆盖组织、学术、教育等多个领域
- 通过自定义 Prompt 确保关系类型的一致性和准确性

### 3.8 数据验证与质量控制

#### 3.8.1 关系类型验证

**配置验证**：

- 确认 `prompts/rel_extract.prompt` 文件创建成功
- 验证 `settings.yaml` 中的配置项正确设置
- 检查 `relation_tuple_length: 6` 配置生效

**输出验证**：

- 检查生成的关系类型是否在预定义列表中
- 验证关系类型的语义准确性和方向性
- 统计各类关系类型的分布情况
- 确认 parquet 文件包含 6 列数据结构

**质量检查**：

- 验证 `relation_type` 字段非空率
- 检查关系类型与描述的一致性
- 评估关系类型分类的准确性

#### 3.8.2 数据质量评估

- 评估实体识别的准确率
- 检查关系抽取的完整性
- 验证关系方向的正确性
- 分析关系类型覆盖度和分布均衡性

## 4. 可视化方案

### 4.1 Web 可视化架构

- 使用 HTML/JavaScript 构建交互式图谱界面
- 支持关系类型的颜色编码和样式区分
- 提供关系类型筛选和搜索功能

### 4.2 关系类型可视化

- 不同关系类型使用不同颜色和线型
- 添加方向箭头显示关系方向
- 支持关系类型图例和说明

## 5. 预期成果

### 5.1 技术成果

- 生成包含 relationship_type 字段的标准化 parquet 文件
- 建立符合 Neo4j 规范的关系类型分类体系
- 实现中文文本的准确关系类型识别

### 5.2 应用价值

- 提升知识图谱的语义表达能力
- 支持更精确的图谱查询和分析
- 为后续图数据库导入提供标准化数据格式

## 6. vis-network 可视化开发任务规划

### 6.1 项目背景

基于已生成的 GraphRAG parquet 文件，开发一个基于 HTML 和 vis-network 的交互式知识图谱可视化系统，将 parquet 数据转换为优雅的可视化图谱。

### 6.2 技术栈选择

- **后端数据处理**: Python + pandas + pyarrow
- **前端可视化**: HTML + JavaScript + vis-network
- **数据格式**: JSON (nodes + edges)
- **样式设计**: CSS + vis-network 配置

### 6.3 详细任务分解

#### 任务 1: 分析 GraphRAG Parquet 文件结构

**目标**: 全面了解数据结构，为后续开发奠定基础

**具体步骤**:

1. 编写 Python 脚本读取所有 parquet 文件
2. 分析每个文件的字段名称、数据类型、样本数据
3. 重点关注以下文件:
   - `entities.parquet`: 实体信息（节点数据）
   - `relationships.parquet`: 关系信息（边数据）
   - `relationships_with_types.parquet`: 带类型的关系数据
   - `communities.parquet`: 社区信息
4. 生成数据结构报告

**输出**:

- `analyze_parquet_structure.py` - 分析脚本
- 数据结构分析报告

#### 任务 2: 设计 vis-network 知识图谱架构

**目标**: 确定数据转换方案和可视化架构

**具体步骤**:

1. 研究 vis-network 的 nodes 和 edges 数据格式要求
2. 设计 GraphRAG 到 vis-network 的映射方案:
   - entities → nodes (id, label, group, title 等)
   - relationships → edges (from, to, label, arrows 等)
3. 确定节点分组策略（按实体类型或社区）
4. 设计节点和边的基础样式规范

**输出**:

- 数据映射设计文档
- vis-network 配置方案

#### 任务 3: 实现 parquet 到 vis-network 数据转换

**目标**: 开发数据转换管道

**具体步骤**:

1. 编写 parquet 读取和处理函数
2. 实现实体到节点的转换逻辑
3. 实现关系到边的转换逻辑
4. 添加数据清洗和验证功能
5. 生成 vis-network 兼容的 JSON 文件

**输出**:

- `convert_to_visnetwork.py` - 转换脚本
- `nodes.json` 和 `edges.json` - 输出数据文件

#### 任务 4: 设计关系类型箭头样式映射

**目标**: 为不同关系类型创建视觉区分方案

**具体步骤**:

1. 分析 relationship_type 字段的所有可能值
2. 为每种关系类型设计独特样式:
   - 箭头类型: arrow, circle, bar, box 等
   - 线条样式: 实线、虚线、点线
   - 颜色方案: 使用色彩心理学原理
   - 线条粗细: 根据关系重要性
3. 创建关系样式配置文件
4. 实现动态样式应用逻辑

**关系类型样式设计原则**:

- IS_A 关系: 蓝色实线箭头（层次关系）
- PART_OF 关系: 绿色粗线箭头（包含关系）
- MENTIONS 关系: 灰色虚线箭头（引用关系）
- TEACHES 关系: 橙色实线箭头（教学关系）
- COLLABORATES_WITH 关系: 紫色实线箭头（协作关系）
- CAUSES 关系: 红色粗线箭头（因果关系）
- 其他关系: 根据语义选择合适颜色和样式

**输出**:

- `relationship_styles.json` - 样式配置文件
- 样式设计文档

#### 任务 5: 开发 HTML+vis-network 知识图谱可视化

**目标**: 创建完整的交互式可视化界面

**具体步骤**:

1. 创建 HTML 页面结构
2. 集成 vis-network 库（使用 CDN 或本地文件）
3. 实现核心功能:
   - 图谱渲染和布局
   - 节点拖拽和固定
   - 缩放和平移
   - 节点/边悬停信息
   - 搜索和过滤功能
4. 添加交互控制面板:
   - 布局算法选择
   - 关系类型过滤
   - 节点大小调整
   - 物理引擎参数调节
5. 优化性能和用户体验

**界面功能需求**:

- 响应式设计，支持不同屏幕尺寸
- 优雅的加载动画
- 工具提示显示详细信息
- 右键菜单提供快捷操作
- 导出功能（PNG/SVG）

**输出**:

- `knowledge_graph.html` - 主页面
- `graph_controller.js` - 交互逻辑
- `styles.css` - 样式文件

### 6.4 技术要求

#### 性能要求

- 支持 1000+节点的流畅渲染
- 初始加载时间 < 3 秒
- 交互响应时间 < 100ms

#### 兼容性要求

- 现代浏览器支持（Chrome 80+, Firefox 75+, Safari 13+）
- 移动端基础支持

#### 可扩展性要求

- 模块化代码结构
- 配置文件驱动的样式系统
- 支持多种数据源格式

### 6.5 项目里程碑

1. **阶段 1**: 完成数据分析和架构设计
2. **阶段 2**: 实现数据转换和样式设计
3. **阶段 3**: 开发可视化界面和交互功能
4. **阶段 4**: 测试、优化和文档完善

### 6.6 风险评估

#### 技术风险

- vis-network 性能限制：通过数据分页和聚类缓解
- 浏览器兼容性：使用 polyfill 和渐进增强
- 数据量过大：实现动态加载和过滤

#### 数据风险

- parquet 文件格式变化：建立灵活的解析机制
- 关系类型不一致：实现智能类型推断

### 6.7 成功标准

1. 成功解析所有 GraphRAG parquet 文件
2. 生成美观且信息丰富的知识图谱
3. 实现流畅的用户交互体验
4. 关系类型视觉区分度高且直观
5. 代码结构清晰，易于维护和扩展
