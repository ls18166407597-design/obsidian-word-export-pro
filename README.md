# Word 一键导出 (Word Export Pro)

[![GitHub release](https://img.shields.io/github/v/release/liusong/obsidian-word-export-pro?style=flat-square)](https://github.com/liusong/obsidian-word-export-pro/releases/latest)

专为 Obsidian 用户设计的极简、高清、学术级 Word (.docx) 导出插件。

## 🌟 核心亮点

- **零配置，指哪打哪**：一键将 Markdown 转换为排版精美的 Word 文档，无需学习复杂的 Pandoc 参数。
- **学术级图表支持**：内置专家级 Lua 过滤器，自动识别“图 1”、“表 1”、“注：”等学术规范排版。
- **引文与参考文献**：原生支持 `bibliography` (BibTeX) 和 `CSL` 样式，完美生成论文级参考文献。
- **样式模板匹配**：支持自定义 Word 引用文档 (Reference DOCX)，让 Obsidian 导出的文档直接套用你的 Word 模板样式。
- **极致纯净**：移除了原版插件中 70% 的冗余功能，专注于提供最完美的 Word 导出体验。

## 🚀 快速开始

1. **安装插件**：在 Obsidian 插件市场搜索 `Word 一键导出` 并安装（或手动将发布包放入 `plugins` 文件夹）。
2. **安装 Pandoc**：确保你的电脑上安装了 [Pandoc](https://pandoc.org/installing.html)。
3. **开始导出**：
   - 在笔记页面点击右键，选择 **“导出为 Word”**。
   - 在弹出的窗口中选择你的 Word 模板（可选）。
   - 点击导出，搞定！

## 📚 高级功能

### 学术自动排版
插件会自动识别以下格式并应用 Word 样式：
- 图片下方的文字（如：`图 1 结构图`） -> 自动应用 `ImageCaption` 样式。
- 表格上方的文字（如：`表 1 数据统计`） -> 自动应用 `TableCaption` 样式。
- 表格下方的注释（如：`注：数据来源于...`） -> 自动应用 `TableNote` 样式。

### 参考文献支持
在笔记的 YAML 区添加引文配置即可自动触发：
```yaml
---
bibliography: references.bib
csl: apa-7th-edition.csl
link-citations: true
---
```

## 🛠 开发与贡献

本插件基于 [obsidian-enhancing-export](https://github.com/siyuan-note/obsidian-enhancing-export) 进行深度重构与优化。

- **作者**: liusong
- **许可证**: MIT

---

*如果您觉得好用，欢迎在 GitHub 上点一个 ⭐ Star！*
