// 知识图谱可视化脚本

// 全局变量
let network = null;
let nodes = null;
let edges = null;
let allNodes = [];
let allEdges = [];
let relationshipStyles = {};
let physicsEnabled = true;

// 初始化
document.addEventListener("DOMContentLoaded", function () {
  initializeVisualization();
});

async function initializeVisualization() {
  try {
    // 加载数据
    await loadData();

    // 创建网络
    createNetwork();

    // 设置事件监听
    setupEventListeners();

    // 隐藏加载提示
    document.getElementById("loading").style.display = "none";
  } catch (error) {
    showError("加载失败: " + error.message);
  }
}

async function loadData() {
  try {
    // 加载图数据
    const graphResponse = await fetch("graph_data.json");
    const graphData = await graphResponse.json();

    allNodes = graphData.nodes;
    allEdges = graphData.edges;

    // 加载样式配置
    const stylesResponse = await fetch("relationship_styles.json");
    relationshipStyles = await stylesResponse.json();

    // 应用样式到边数据
    applyStylesToEdges();

    // 更新统计信息
    updateStats();

    // 生成过滤器和图例
    generateRelationshipFilters();
    generateRelationshipLegend();
  } catch (error) {
    throw new Error(
      "无法加载数据文件，请确保 graph_data.json 和 relationship_styles.json 文件存在"
    );
  }
}

function applyStylesToEdges() {
  allEdges.forEach((edge) => {
    const relationshipType = edge.label;
    const style =
      relationshipStyles.styles[relationshipType] ||
      relationshipStyles.styles.UNKNOWN;

    // 应用样式
    Object.assign(edge, style);
  });
}

function createNetwork() {
  // 创建数据集
  nodes = new vis.DataSet(allNodes);
  edges = new vis.DataSet(allEdges);

  // 网络配置 - 使用circle形状，确保节点名称居中
  const options = {
    nodes: {
      shape: "circle",
      size: 30,
      font: {
        size: 14,
        color: "#343434",
        face: "arial",
        background: "none",
        strokeWidth: 0,
        strokeColor: "#ffffff",
        align: "center",
        vadjust: 0, // 垂直调整，确保文字在圆心
        multi: false,
      },
      color: {
        background: "#97C2FC",
        border: "#2B7CE9",
        highlight: {
          background: "#D2E5FF",
          border: "#2B7CE9",
        },
        hover: {
          background: "#D2E5FF",
          border: "#2B7CE9",
        },
      },
      borderWidth: 2,
      borderWidthSelected: 3,
      shadow: {
        enabled: true,
        color: "rgba(0,0,0,0.2)",
        size: 5,
        x: 2,
        y: 2,
      },
      chosen: {
        node: function (values, id, selected, hovering) {
          values.size = 35;
          values.borderWidth = 3;
        },
        label: function (values, id, selected, hovering) {
          // 保持标签居中
          values.vadjust = 0;
        },
      },
      labelHighlightBold: true,
      margin: 5,
    },
    edges: {
      width: 2,
      shadow: {
        enabled: true,
        color: "rgba(0,0,0,0.1)",
        size: 3,
        x: 1,
        y: 1,
      },
      smooth: {
        enabled: true,
        type: "dynamic",
        roundness: 0.5,
      },
      arrows: {
        to: {
          enabled: true,
          scaleFactor: 1,
          type: "arrow",
        },
      },
    },
    physics: {
      enabled: true,
      // 使用 forceAtlas2Based 算法实现更好的拖动避让
      forceAtlas2Based: {
        gravitationalConstant: -50,
        centralGravity: 0.01,
        springLength: 100,
        springConstant: 0.08,
        damping: 0.4,
        avoidOverlap: 1, // 启用避免重叠
      },
      maxVelocity: 50,
      minVelocity: 0.75,
      solver: "forceAtlas2Based",
      stabilization: {
        enabled: true,
        iterations: 1000,
        updateInterval: 25,
        fit: true,
      },
      timestep: 0.35,
      adaptiveTimestep: true,
    },
    interaction: {
      hover: true,
      tooltipDelay: 300,
      hideEdgesOnDrag: false,
      hideNodesOnDrag: false,
      dragNodes: true,
      dragView: true,
      zoomView: true,
    },
    layout: {
      improvedLayout: true,
      clusterThreshold: 150,
      hierarchical: false,
    },
  };

  // 创建网络
  const container = document.getElementById("network-container");
  network = new vis.Network(container, { nodes: nodes, edges: edges }, options);
}

function setupEventListeners() {
  // 网络事件
  network.on("click", function (params) {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0];
      highlightConnectedNodes(nodeId);
    }
  });

  // 拖动开始时启用物理引擎
  network.on("dragStart", function (params) {
    if (params.nodes.length > 0) {
      // 启用物理引擎以实现动态避让
      network.setOptions({ physics: { enabled: true } });
      physicsEnabled = true;
    }
  });

  // 拖动结束后短暂保持物理引擎运行，然后关闭
  network.on("dragEnd", function (params) {
    if (params.nodes.length > 0) {
      // 延迟关闭物理引擎，让节点稳定
      setTimeout(() => {
        network.setOptions({ physics: { enabled: false } });
        physicsEnabled = false;
      }, 2000);
    }
  });

  network.on("hoverNode", function (params) {
    // 可以添加悬停效果
    document.body.style.cursor = "pointer";
  });

  network.on("blurNode", function (params) {
    document.body.style.cursor = "default";
  });

  // 稳定后停止物理引擎
  network.on("stabilizationIterationsDone", function () {
    network.setOptions({ physics: { enabled: false } });
    physicsEnabled = false;
  });

  // 搜索框事件
  document
    .getElementById("search-input")
    .addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        searchNodes();
      }
    });
}

function updateStats() {
  document.getElementById("node-count").textContent = allNodes.length;
  document.getElementById("edge-count").textContent = allEdges.length;

  const relationshipTypes = [...new Set(allEdges.map((edge) => edge.label))];
  document.getElementById("relationship-types").textContent =
    relationshipTypes.length;
}

function generateRelationshipFilters() {
  const container = document.getElementById("relationship-filters");
  const relationshipTypes = [...new Set(allEdges.map((edge) => edge.label))];

  container.innerHTML = "";

  relationshipTypes.forEach((type) => {
    const style =
      relationshipStyles.styles[type] || relationshipStyles.styles.UNKNOWN;
    const color = style.color.color;

    const item = document.createElement("div");
    item.className = "checkbox-item";
    item.innerHTML = `
                <input type="checkbox" id="filter-${type}" checked onchange="filterRelationships()">
                <div class="color-indicator" style="background-color: ${color}"></div>
                <label for="filter-${type}">${type}</label>
            `;
    container.appendChild(item);
  });
}

function generateRelationshipLegend() {
  const container = document.getElementById("relationship-legend");
  const relationshipTypes = [...new Set(allEdges.map((edge) => edge.label))];

  container.innerHTML = "";

  relationshipTypes.forEach((type) => {
    const style =
      relationshipStyles.styles[type] || relationshipStyles.styles.UNKNOWN;
    const color = style.color.color;
    const isDashed = style.dashes && style.dashes.length > 0;

    const item = document.createElement("div");
    item.className = "legend-item";
    item.innerHTML = `
                <div class="legend-line" style="background-color: ${color}; ${
      isDashed
        ? "background-image: linear-gradient(90deg, " +
          color +
          " 50%, transparent 50%); background-size: 8px 2px;"
        : ""
    }"></div>
                <span>${type}</span>
            `;
    container.appendChild(item);
  });
}

// 控制函数
function searchNodes() {
  const searchTerm = document
    .getElementById("search-input")
    .value.toLowerCase();
  if (!searchTerm) {
    clearSearch();
    return;
  }

  const matchingNodes = allNodes.filter((node) =>
    node.label.toLowerCase().includes(searchTerm)
  );

  if (matchingNodes.length > 0) {
    const nodeIds = matchingNodes.map((node) => node.id);
    network.selectNodes(nodeIds);
    network.fit({ nodes: nodeIds, animation: true });
  } else {
    showError("未找到匹配的节点");
  }
}

function clearSearch() {
  document.getElementById("search-input").value = "";
  network.unselectAll();
  network.fit();
}

function filterRelationships() {
  const checkboxes = document.querySelectorAll(
    '#relationship-filters input[type="checkbox"]'
  );
  const selectedTypes = [];

  checkboxes.forEach((checkbox) => {
    if (checkbox.checked) {
      const type = checkbox.id.replace("filter-", "");
      selectedTypes.push(type);
    }
  });

  const filteredEdges = allEdges.filter((edge) =>
    selectedTypes.includes(edge.label)
  );
  edges.clear();
  edges.add(filteredEdges);
}

function selectAllRelationships() {
  const checkboxes = document.querySelectorAll(
    '#relationship-filters input[type="checkbox"]'
  );
  checkboxes.forEach((checkbox) => (checkbox.checked = true));
  filterRelationships();
}

function deselectAllRelationships() {
  const checkboxes = document.querySelectorAll(
    '#relationship-filters input[type="checkbox"]'
  );
  checkboxes.forEach((checkbox) => (checkbox.checked = false));
  filterRelationships();
}

function fitNetwork() {
  network.fit({ animation: true });
}

function resetLayout() {
  network.setData({ nodes: nodes, edges: edges });
  network.fit();
}

function togglePhysics() {
  physicsEnabled = !physicsEnabled;
  network.setOptions({ physics: { enabled: physicsEnabled } });
}

function exportNetwork() {
  // 简单的导出功能
  alert("导出功能需要额外的库支持，这里仅作演示");
}

function highlightConnectedNodes(nodeId) {
  const connectedNodes = network.getConnectedNodes(nodeId);
  const connectedEdges = network.getConnectedEdges(nodeId);

  network.selectNodes([nodeId, ...connectedNodes]);
  network.selectEdges(connectedEdges);
}

function showError(message) {
  const errorDiv = document.createElement("div");
  errorDiv.className = "error-message";
  errorDiv.textContent = message;

  const sidebar = document.querySelector(".sidebar");
  sidebar.insertBefore(errorDiv, sidebar.firstChild);

  setTimeout(() => {
    errorDiv.remove();
  }, 5000);
}
