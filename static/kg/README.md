# 知识库浏览器

> 基于 D3.js 的交互式知识图谱浏览器，纯前端静态页面，零依赖，GitHub Pages 直接托管。

## 功能特性

- 🔍 **实时搜索** — 输入即搜，支持关键词高亮
- 📑 **分类浏览** — Tab 切换：全部 / 朗新科技 / 可信数据空间 / 充电桩 / 虚拟电厂 / 数据基础设施
- 📊 **知识图谱** — D3.js 力导向图，节点大小反映关联数量，可缩放、可拖拽
- 📋 **列表视图** — 卡片式布局，快速浏览
- 🔎 **钻取查询** — 点击节点/卡片，右侧滑出详情面板
- 🔗 **归档溯源** — 每个知识点可跳转原始文档

## 技术栈

- HTML5 + CSS3 + JavaScript（原生，无框架）
- [D3.js v7](https://d3js.org/)（CDN 引入）
- [GitHub Pages](https://pages.github.com/)（免费托管）

## 本地预览

### 方式一：直接打开
```bash
# 克隆仓库
git clone https://github.com/Domi-OpenClaw/code-space.git

# 进入目录
cd code-space

# 直接用浏览器打开 index.html
open index.html
# 或
xdg-open index.html  # Linux
start index.html     # Windows
```

### 方式二：本地 HTTP 服务器

```bash
# Python 3
cd code-space
python -m http.server 8080
# 访问 http://localhost:8080

# Node.js (npx)
npx serve .

# PHP
php -S localhost:8080
```

## GitHub Pages 部署

### 自动部署
仓库已配置 GitHub Pages，推送到 `main` 分支后自动生效：
- 访问地址：`https://Domi-OpenClaw.github.io/code-space/`

### 手动部署
1. 进入仓库 **Settings** → **Pages**
2. Source 选择 `main` 分支和 `/ (root)` 目录
3. 点击 Save，等待 1-2 分钟

## 目录结构

```
code-space/
├── index.html    # 主页面（图谱 + 列表 + 搜索）
├── data.js       # 知识库数据（节点 + 边）
├── README.md     # 本文档
└── docs/
    └── knowledge-index.md  # 知识索引源文件
```

## 数据格式

### 节点 (nodes)
```javascript
{
  id: "lx-1",                    // 唯一ID
  label: "朗新科技集团中文画册",  // 显示名称
  category: "朗新科技",          // 分类
  summary: "摘要内容...",         // 简短描述
  source: "knowledge-index.md",   // 来源文件
  url: "https://...",             // 归档链接
  connections: 3                  // 关联数量（决定节点大小）
}
```

### 边 (links)
```javascript
{
  source: "lx-1",   // 源节点ID
  target: "lx-2",   // 目标节点ID
  relation: "内容关联"  // 关系类型
}
```

## 分类颜色

| 分类 | 颜色 | Emoji |
|------|------|-------|
| 朗新科技 | #3B82F6 | 🏢 |
| 可信数据空间 | #10B981 | 🔐 |
| 充电桩 | #F97316 | ⚡ |
| 虚拟电厂 | #EF4444 | ⚡ |
| 数据基础设施 | #8B5CF6 | 🏛️ |

## 图谱操作

- 🖱️ **滚轮** — 缩放
- 🖱️ **拖拽背景** — 移动画布
- 🖱️ **拖拽节点** — 调整位置
- 🖱️ **点击节点** — 查看详情
- 🖱️ **点击空白** — 关闭详情

## 更新知识库

编辑 `data.js` 中的 `KNOWLEDGE_DATA` 对象：

1. 在 `nodes` 数组添加新节点
2. 在 `links` 数组添加关联关系
3. 提交并推送，GitHub Pages 自动更新

## License

MIT
