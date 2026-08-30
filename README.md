<!-- markdownlint-disable MD028 -->
<!-- markdownlint-disable MD033 -->
<!-- markdownlint-disable MD041 -->

![astrbot_plugin_count_loc](https://socialify.git.ci/Pancakes-Labs/astrbot_plugin_count_loc/image?custom_description=%E4%B8%80%E4%B8%AA%E4%B8%BA+AstrBot+%E6%89%93%E9%80%A0%E7%9A%84%E8%BD%BB%E9%87%8F%E7%BA%A7+Git+%E4%BB%93%E5%BA%93%E4%BB%A3%E7%A0%81%E7%BB%9F%E8%AE%A1%E6%8F%92%E4%BB%B6&description=1&forks=1&issues=1&language=1&name=1&owner=1&pulls=1&stargazers=1&theme=Auto)

<p align="center">
  <img src="assets/PluginRank.svg" alt="Plugin Rank">
  <img src="assets/StarRank.svg" alt="Star Rank">
  <img src="assets/ShitMountain.svg" alt="ShitMountain">
</p>

<img src="logo.png" width="240" height="240" align="right" alt="logo">

<p align="center">
  <img src="https://img.shields.io/badge/License-AGPL_3.0-blue.svg" alt="License: AGPL-3.0">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/AstrBot-v4.11.2+-orange.svg" alt="AstrBot v4.11.2+">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AstrBot-v4.27.4%20Compatible-brightgreen.svg" alt="Compatible with AstrBot v4.27.4">
  <img src="https://img.shields.io/github/v/release/Pancakes-Labs/astrbot_plugin_count_loc?label=Release&color=brightgreen" alt="Latest Release">
  <img src="https://img.shields.io/badge/QQ群-1033089808-12B7F3.svg" alt="QQ群">
</p>

[![Moe Counter](https://count.getloli.com/get/@DBJD-CR7?theme=moebooru)](https://github.com/Pancakes-Labs/astrbot_plugin_count_loc)

---

一个为 [AstrBot](https://github.com/AstrBotDevs/AstrBot) 设计的公开代码仓库行数统计分析插件。
只需在聊天对话中发送指令，即可对任意公开的 GitHub 或 GitLab 仓库的代码行数、文件数量、注释行数、物理总行数等指标进行快捷获取和分析。
并且支持自定义指定分支以及忽略特定目录与文件，还可以用自然语言让 LLM 自主查询喵。

## 📑 快速导航

- [✨ 功能特性](#-功能特性)
- [📊 输出示例](#-输出示例)
- [🚀 安装与使用](#-安装与使用)
- [📋 指令说明](#-指令说明)
- [🤖 函数工具自动调用](#-函数工具自动调用)
- [⚙️ 配置项详解](#️-配置项详解)
- [📂 插件目录与结构](#-插件目录与结构)
- [🏗️ 架构说明](#️-架构说明)
- [❓ 常见问题](#-常见问题)
- [🚧 已知限制](#-已知限制)
- [📄 许可证](#-许可证)

---
<!-- 开发者的话 -->
> **开发者的话：**
>
> 大家好，我是 DBJD-CR，这是我为 AstrBot 开发的第四个插件，如果存在做的不好的地方还请理解。
>
> 和我写的其他插件一样，本插件也是"Vibe Coding"的产物。
>
> 所以，**本插件的所有文件内容，全部由 AI 编写完成**，我几乎没有为该插件编写任何一行代码，仅进行了架构设计与修改部分文字描述和负责本文档的润色。所以，或许有必要添加下方的声明：

> [!WARNING]  
> 本插件和文档由 AI 生成，内容仅供参考，请仔细甄别。
>
> 插件目前仍处于开发阶段，无法 100% 保证稳定性与可用性。
>
> 虽然这个插件功能比较简单，也还是诚邀各路大佬对本插件进行测试和改进，希望大家多多指点。
>
> 如果觉得这个插件比较实用的话，**就为这个项目点个** 🌟 **Star** 🌟 **吧~** ，这是对我们的最大认可与鼓励！

> [!NOTE]
> 虽然本插件的开发过程中大量使用了 AI 进行辅助，但我保证所有内容都经过了我的严格审查，所有的 AI 生成声明都是形式上的。你可以放心参观本仓库 and 使用本插件。

> [!TIP]
> 本项目的相关开发数据 (持续更新中)：
>
> 开发时长：累计 4 天（主插件部分）
>
> 累计工时：约 15 小时（主插件部分）
>
> 使用的大模型：Gemini 3.5、3.7 Flash (With RooCode in VSCode)
>
> 对话窗口搭建：VSCode RooCode 扩展
>
> Tokens Used：24,422,000

---

## ✨ 功能特性

本插件为 AstrBot 提供以下核心能力喵：

- **自建统计引擎**：不依赖任何第三方统计 API，插件直接从 GitHub / GitLab 官方归档地址下载仓库并逐行统计，稳定可靠。
- **多平台公开仓库支持**：默认支持 GitHub，且通过参数便捷切换为 GitLab 平台。
- **自动解析默认分支**：不指定分支时，自动通过 GitHub / GitLab 官方 API 查询仓库默认分支。
- **自定义分支解析**：支持自定义分析除默认分支（如 `master`/`main`）以外的指定分支喵。
- **灵活的忽略规则**：允许以逗号分隔传入多个文件名或目录名进行过滤排除。
- **大模型智能工具调用**：适配大语言模型，通过动态注入使用指南，允许大模型在面对用户类似“帮我分析一下这个 GitHub 仓库”、“查下这个项目的代码量”等诉求时，自主决定调用本工具并返回分析结果。
- **流式卡片化排版**：使用流式卡片化列表。无论在非等宽字体还是小屏自动折行下，尽可能保持界面整洁。
- **可视化语言占比度量条**：自动根据代码量分配彩色渐变进度条方块（如 🟦🟨🟪🟩⬛⬜），直观展示前 5 大开发语言占比以及其余语言合并的 Other 比例，并控制双列图例自动折行防溢出。
- **文档健康度注释率**：反映纯代码的注释覆盖率，过滤空白行噪音。
- **群合并转发节点支持**：默认对输出内容包装成“群合并转发节点 (Node)”发出，完美保护群聊界面的整洁度，优雅且高级！
- **模块化高可维护设计**：拆分为统计引擎、语言识别、注释规则、指令解析、数据格式化等多个职责清晰的模块，代码结构高内聚低耦合，易于二次扩展。

## 📊 输出示例

```text
📊 GitHub 仓库分析报告
项目: AstrBotDevs/AstrBot
查询分支: 默认分支
忽略文件/目录: 无
查询时间: 2026-08-31 03:12:15 中国标准时间
==============================
文件组成:
🟦🟦🟦🟦🟦🟦🟦🟦🟩🟩🟩🟨⬛🟨⬜

   🟦 Python 51.5%   🟩 Vue 21.0%
   🟨 JSON 8.5%   ⬛ Markdown 6.9%
   🟨 YAML 4.3%   ⬜ 其他 7.8%
==============================
📈 语言明细:
 🔹🟦 Python:
    ├─ 文件数量: 676 个
    ├─ 代码行数: 164,169 行
    └─ 注释行数: 14,373 行
 🔹🟩 Vue:
    ├─ 文件数量: 170 个
    ├─ 代码行数: 66,974 行
    └─ 注释行数: 1,317 行
 🔹🟨 JSON:
    ├─ 文件数量: 140 个
    ├─ 代码行数: 27,077 行
    └─ 注释行数: 0 行
 🔹⬛ Markdown:
    ├─ 文件数量: 442 个
    ├─ 代码行数: 21,896 行
    └─ 注释行数: 0 行
 🔹🟨 YAML:
    ├─ 文件数量: 39 个
    ├─ 代码行数: 13,701 行
    └─ 注释行数: 134 行
 🔹🟦 TypeScript:
    ├─ 文件数量: 60 个
    ├─ 代码行数: 13,498 行
    └─ 注释行数: 1,733 行
 🔹🟨 JavaScript:
    ├─ 文件数量: 32 个
    ├─ 代码行数: 5,526 行
    └─ 注释行数: 229 行
 🔹🟪 CSS:
    ├─ 文件数量: 5 个
    ├─ 代码行数: 1,559 行
    └─ 注释行数: 198 行
 🔹🟥 HTML:
    ├─ 文件数量: 5 个
    ├─ 代码行数: 1,112 行
    └─ 注释行数: 1 行
 🔹⬜ Plain Text:
    ├─ 文件数量: 10 个
    ├─ 代码行数: 925 行
    └─ 注释行数: 0 行
 🔹🟪 Sass:
    ├─ 文件数量: 16 个
    ├─ 代码行数: 781 行
    └─ 注释行数: 33 行
 🔹⬜ License:
    ├─ 文件数量: 2 个
    ├─ 代码行数: 561 行
    └─ 注释行数: 0 行
 🔹🟩 Shell:
    ├─ 文件数量: 5 个
    ├─ 代码行数: 454 行
    └─ 注释行数: 39 行
 🔹🟫 TOML:
    ├─ 文件数量: 2 个
    ├─ 代码行数: 127 行
    └─ 注释行数: 3 行
 🔹🟦 PowerShell:
    ├─ 文件数量: 1 个
    ├─ 代码行数: 68 行
    └─ 注释行数: 2 行
 🔹🟦 TypeScript Typings:
    ├─ 文件数量: 5 个
    ├─ 代码行数: 65 行
    └─ 注释行数: 1 行
 🔹⬛ Makefile:
    ├─ 文件数量: 1 个
    ├─ 代码行数: 52 行
    └─ 注释行数: 1 行
 🔹🐳 Dockerfile:
    ├─ 文件数量: 1 个
    ├─ 代码行数: 30 行
    └─ 注释行数: 0 行
 🔹⬛ Docker ignore:
    ├─ 文件数量: 1 个
    ├─ 代码行数: 26 行
    └─ 注释行数: 0 行
 🔹🟨 SVG:
    ├─ 文件数量: 8 个
    ├─ 代码行数: 22 行
    └─ 注释行数: 0 行
 🔹🟫 Systemd:
    ├─ 文件数量: 1 个
    ├─ 代码行数: 17 行
    └─ 注释行数: 1 行
 🔹🟫 SQL:
    ├─ 文件数量: 1 个
    ├─ 代码行数: 14 行
    └─ 注释行数: 1 行
==============================
📁 总计文件数量 : 1,623 个
💻 总计代码行数 : 318,654 行
💬 总计注释行数 : 18,066 行
🫙 总计空白行数 : 53,388 行
📈 总计物理行数 : 390,108 行
🩺 代码注释比例 : 5.7% (🟠 偏低 (阅读起来要耐心喵))
```

## 🚀 安装与使用

1. **下载插件**: 通过 AstrBot 的插件市场下载。或从本 GitHub 仓库的 Release 下载 `astrbot_plugin_count_loc` 的 `.zip` 文件，在 AstrBot WebUI 中的插件页面右下角的 `➕` 选择 `从文件安装` 。
2. **安装依赖**: 本插件的核心依赖为 `httpx`。插件下载安装时会自动安装插件所需的依赖，通常无需额外安装。如果你的环境中确实缺少相关依赖，请安装：

   ```bash
   pip install httpx
   ```

3. **重启 AstrBot (可选)**: 如果插件没有正常加载或生效，可以尝试重启你的 AstrBot 程序。
4. **配置插件 (可选)**: 进入 AstrBot WebUI，找到 `代码统计` 插件，选择 `插件配置` 选项 (⚙️)，配置相关参数。

---

## 📋 指令说明

本插件目前提供了一个主指令和若干别名，支持丰富的选项来自定义统计结果。

### 💻 注册指令与别名

| 主指令 | 可用别名（Alias） |
| :--- | :--- |
| `/代码统计` | `/codeloc` `/测代码` `/统计代码` `/loc` |

### ⚙️ 参数与选项说明

| 选项 (长参数) | 简写 (短参数) | 参数值类型 | 默认值 | 作用描述 |
| :--- | :--- | :--- | :--- | :--- |
| `--branch` | `-b` | 字符串 | 默认分支 (master/main) | 指定要统计分析的 Git 远程分支名 |
| `--ignore` | `-i` | 英文逗号分隔列表 | 无 | 指定需要排除在统计之外的文件名或目录名 |
| `--gitlab` | `-g` | 无 (布尔开关) | 关 (默认 GitHub) | 加上此参数时代表目标项目为 GitLab 平台公开项目 |

### 📖 使用示例与说明

> [!TIP]
> 基础调用语法：`/代码统计 <用户名>/<仓库名> [选项]`

- **示例 1：基础统计公开 GitHub 仓库**

  ```text
  /代码统计 Pancakes-Labs/astrbot_plugin_count_loc
  ```
  
  *说明：对指定的 GitHub 仓库在默认主分支下进行全量代码行数分析。*

- **示例 2：统计指定分支并过滤特定目录**

  ```text
  /代码统计 Pancakes-Labs/astrbot_plugin_count_loc -b dev -i venv,docs,node_modules
  ```

  *说明：统计 `dev` 分支的代码，并自动忽略 `venv`、`docs` 以及 `node_modules` 文件夹下的代码行喵。*

- **示例 3：快捷指令及统计 GitLab 公开仓库**

  ```text
  /loc test_user/test_repo --gitlab
  ```

  *说明：使用别名 `loc` 对 GitLab 下的 `test_user/test_repo` 公开仓库进行分析。*

---

## 🤖 函数工具自动调用

本插件完美支持 AstrBot 的工具自动调用（Tool/Function Calling）生态。当用户在聊天中与大语言模型对话时，LLM 可以直接调用代码统计能力！

### 💡 运作机制

1. **策略注入**：在向 LLM 提交请求前，插件会向 `system_prompt` 动态追加一条工具使用指南，指导 LLM 何时及如何使用此工具。
2. **工具自决**：大语言模型检测到用户意图（例如“看看 `Pancakes-Labs/astrbot_plugin_count_loc` 这个仓库的代码量”、“我想了解这个项目的语言分布”）后，会**自主生成**并执行工具调用请求。
3. **连贯回复**：大模型获得工具返回的丰富统计信息后，会根据它当前的人格与设定为用户进行二次润色与综合回复，无需用户在工具执行后再发起一次对话，保证了交互的**高度流畅与闭环**。

效果示例：

<img width="598" height="569" alt="LLMTool" src="https://github.com/user-attachments/assets/25c4caf0-fae4-40d4-b8f8-9b043a7b5f3c" />

### 🛠️ 工具详情

- **工具名称**: `query_code_statistics`
- **工具参数**:
  - `repo_path` (string, 必须): 用户名/仓库名（例如 `Pancakes-Labs/astrbot_plugin_count_loc`）。
  - `platform` (string, 可选): 托管平台（`github` / `gitlab`，默认 `github`）。
  - `branch` (string, 可选): 远程分支名称（如 `main`、`dev`）。
  - `ignored` (string, 可选): 忽略的文件或文件夹列表，用英文逗号分隔。

---

## ⚙️ 配置项详解

本插件支持免配置开箱即用。同时，插件在 AstrBot WebUI 中提供了完整的可视化配置界面，方便您进行个性化配额调节与鉴权绑定。

### 🔑 1. API 鉴权配置 (Tokens)

控制与 Git 平台官方接口通信时的鉴权凭据，大幅提升请求频次上限。

- **GitHub Personal Access Token (`github_token`)**:
  - 类型：`String`
  - 默认值：`""`（空）
  - 说明：GitHub 个人访问令牌。
  - 提示：
    - GitHub 官方对未认证请求限制为 **60 次/小时**；配置 Token 后上限将提升至 **5,000 次/小时**。
    - 推荐在 GitHub 生成 Fine-grained Personal Access Token 并仅授予 `Contents: read`（公开仓库只读）权限；若使用 Classic PAT，勾选 `public_repo` 即可。
    - 若此处留空，插件亦会自动检测运行环境中的 `GITHUB_TOKEN` 环境变量作为回退。

- **GitLab Personal Access Token (`gitlab_token`)**:
  - 类型：`String`
  - 默认值：`""`（空）
  - 说明：GitLab 个人访问令牌。
  - 提示：
    - 用于提升 GitLab API 查询仓库元数据时的调用配额。
    - 可在 GitLab 用户设置中的 `Access Tokens` 生成，仅需赋予 `read_api` 权限。
    - 若此处留空，插件会自动检测 `GITLAB_TOKEN` 环境变量。

---

### 🛡️ 2. 统计安全限制 (Limits)

防止因用户输入超大仓库导致下载或解压过程耗尽服务器内存。

- **仓库归档最大体积 (`max_archive_mb`)**:
  - 类型：`Integer`
  - 默认值：`100`
  - 取值范围：`16` ~ `500` MB（步长 `4`）
  - 说明：限制允许下载并解压分析的仓库压缩包体积上限。
  - 提示：
    - 当远程仓库归档大小超过此阈值时，自建统计引擎会主动拦截并拒绝统计，保障宿主系统的运行稳定性。
    - 若需统计包含较多非代码静态资源的特大项目，可适当调大该阈值，并配合 `-i` / `--ignore` 参数过滤资源目录。

```json
{
  "github_token": "ghp_xxxxxxxxxxxxxxxxxxxx",  // GitHub Token
  "gitlab_token": "glpat-xxxxxxxxxxxxxxxxxxxx", // GitLab Token
  "max_archive_mb": 100                        // 归档大小安全上限 (MB)
}
```

---

## 📂 插件目录与结构

本插件在 AstrBot 目录结构中的分布以及插件自身的目录结构如下喵：

```bash
AstrBot/
└─ data/
   └─ plugins/
      └─ astrbot_plugin_count_loc/           # 插件根目录
         ├─ .gitignore                       # Git 忽略规则
         │
         ├─ _conf_schema.json                # AstrBot WebUI 插件配置规范文件
         ├─ assets/                          # README / 仓库展示资源
         │
         ├─ docs/                            # 外部 API 文档
         │
         ├─ CHANGELOG.md                     # 插件更新日志，适用于 AstrBot v4.11.2+
         ├─ command_parser.py                # 指令参数解析与规范化组件
         ├─ comment_rules.py                 # 各语言注释语法规则与逐行计数模块
         ├─ CONTRIBUTING.md                  # 本插件的贡献指南
         ├─ data_formatter.py                # 数据排版汇总与表格排版渲染器
         ├─ language_colors.py               # 语言色彩常量映射表
         ├─ language_detector.py             # 文件路径 -> 语言名称识别模块
         ├─ LICENSE                          # 许可证文件
         ├─ loc_engine.py                    # 自建统计引擎（下载归档 + 逐行统计聚合）
         ├─ logo.png                         # 插件 Logo，适用于 AstrBot v4.5.0+
         ├─ main.py                          # 插件主入口文件，做模块集成与指令入口定义
         ├─ metadata.yaml                    # 插件元数据信息，如版本、作者、支持平台等
         ├─ README.md                        # 插件说明文档
         ├─ repo_client.py                   # 代码统计请求客户端门面（委托自建引擎）
         ├─ requirements.txt                 # 插件外部依赖声明文件
         └─ run_ruff.bat                     # Ruff 一键格式化与自动修复脚本
```

---

## 🏗️ 架构说明

本插件的模块设计关系与消息处理流向如下，采用了清晰的高内聚低耦合模块化架构喵：

```mermaid
flowchart TD
    %% 样式定义
    classDef userStyle fill:#F5F5F5,stroke:#333,stroke-width:2px,color:#333;
    classDef pluginStyle fill:#E1F5FE,stroke:#0288D1,stroke-width:2px,color:#01579B;
    classDef moduleStyle fill:#E8F5E9,stroke:#388E3C,stroke-width:2px,color:#1B5E20;
    classDef engineStyle fill:#FFF8E1,stroke:#FFA000,stroke-width:2px,color:#E65100;
    classDef remoteStyle fill:#EDE7F6,stroke:#7E57C2,stroke-width:2px,color:#4A148C;

    %% 节点定义
    User(["💬 终端用户 / LLM 对话"]):::userStyle

    subgraph AstrBotHost ["AstrBot 宿主主程序"]
        MainPlugin["CountLocPlugin 插件主类<br>并发信号量 + 用户防抖<br>main.py"]:::pluginStyle
    end

    subgraph ParserFormatter ["指令与数据展示层"]
        Parser["CommandParser<br>指令解析与路径清洗<br>command_parser.py"]:::moduleStyle
        Formatter["DataFormatter<br>流式卡片排版 & 色彩度量条<br>data_formatter.py"]:::moduleStyle
        Colors["LanguageColors<br>语言颜色常量映射<br>language_colors.py"]:::moduleStyle
    end

    subgraph CoreEngine ["自建统计引擎层"]
        Client["RepoClient 门面<br>TTL 内存缓存 10min<br>repo_client.py"]:::moduleStyle
        Engine["LocEngine 自建统计引擎<br>流式下载 / 内存解压 / 安全熔断<br>loc_engine.py"]:::engineStyle
        Detector["LanguageDetector<br>扩展名与特殊文件识别<br>language_detector.py"]:::engineStyle
        Rules["CommentRules<br>状态机行级语法规则<br>comment_rules.py"]:::engineStyle
    end

    subgraph RemoteGit ["远程 Git 官方服务"]
        GitPlatform["GitHub / GitLab 官方 API<br>默认分支解析 & 归档下载<br>api.github.com / gitlab.com"]:::remoteStyle
    end

    %% 数据流向连接
    User -->|"1. 发送 /代码统计 指令或大模型 Tool Call"| MainPlugin
    MainPlugin -->|"2. 解析参数字符串与选项"| Parser
    Parser -->|"3. 返回规范化仓库路径与过滤参数"| MainPlugin

    MainPlugin -->|"4. 发起统计查询（并发限制 x2）"| Client
    Client -->|"5. 查询未命中缓存时委托"| Engine

    Engine -->|"6.1 查询默认分支（带 Token 鉴权）"| GitPlatform
    Engine -->|"6.2 流式拉取 Zip/Tar.gz 归档包"| GitPlatform
    GitPlatform -->|"6.3 字节流返回（实时体积熔断）"| Engine

    Engine -->|"7.1 提取文件路径与语言分类"| Detector
    Engine -->|"7.2 解码文本并逐行解析代码/注释/空白"| Rules
    Rules -->|"7.3 聚合指标并转换为标准列表"| Engine

    Engine -->|"8. 返回标准统计数据集"| Client
    Client -->|"9. 写入 TTL 缓存并回传结构化数据"| MainPlugin

    MainPlugin -->|"10. 传入原始统计数据"| Formatter
    Formatter -.->|"读取色彩映射"| Colors
    Formatter -->|"11. 生成可视化排版文本报告"| MainPlugin

    MainPlugin -->|"12. 群合并转发节点 / 纯文本 / LLM 工具回执"| User

    %% 容器与子图样式应用
    style AstrBotHost fill:#F1F8E9,stroke:#81C784,stroke-width:1px,stroke-dasharray: 5 5;
    style ParserFormatter fill:#ECEFF1,stroke:#B0BEC5,stroke-width:1px,stroke-dasharray: 5 5;
    style CoreEngine fill:#FFFDE7,stroke:#FFE082,stroke-width:1px,stroke-dasharray: 5 5;
    style RemoteGit fill:#F3E5F5,stroke:#CE93D8,stroke-width:1px,stroke-dasharray: 5 5;
```

---

## ❓ 常见问题

### Q1：为什么统计部分超大仓库时会提示被拦截或终止？

插件自建统计引擎内置了多重**安全防御与资源熔断机制**，以防止大仓库耗尽 AstrBot 宿主机的内存与 CPU：

- **归档大小上限**：默认限制仓库归档压缩包体积为 `100 MB`。下载过程中一旦超过阈值将立即熔断并安全中断连接。
- **文件数量与单文件体积保护**：单仓库解压文件上限为 `50,000` 个，单文本文件体积上限为 `300 MB`，超出部分自动跳过。
- **应对方案**：对于包含大量构建产物、视频或模型资产的特大项目，可在调大 `仓库归档最大体积` 的同时，配合忽略参数排除非代码目录。

### Q2：频繁查询触发 Git 平台速率限制（Rate Limit / 403）怎么办？

GitHub 官方对未提供凭据的匿名 IP 施加了 **60 次/小时** 的请求频率限制，在公网服务器或频繁调试时较易触发。

- **解决方案**：在 AstrBot WebUI 插件配置中填写 `github_token`（或在宿主机设置 `GITHUB_TOKEN` 环境变量）。
- **效果**：配置个人访问令牌后，GitHub API 接口配额将大幅提升至 **5,000 次/小时**。
- GitLab 用户同理可在插件配置中绑定 `gitlab_token`（或 `GITLAB_TOKEN` 环境变量）。

### Q3：为什么部分特殊文件未统计，或某些代码被识别为 Plain Text？

- 插件原生覆盖 40+ 种主流语言与配置格式，并对复合扩展名和特殊文件名做了专用映射。
- **二进制与媒体过滤**：图片、字体、音视频、编译后二进制文件检测到 NUL 字节特征时会自动略过，不计入代码行数。
- **未知扩展名回退**：对于尚未收录的纯文本扩展名，会回退为 `Plain Text` 并按通用注释规则处理。若需扩充支持的语言或特定注释语法，非常欢迎提交 Pull Request！

### Q4：提示网络连接异常或无法下载仓库归档？

- 本插件直接与 GitHub 官方服务 (`api.github.com`、`codeload.github.com`) 及 GitLab (`gitlab.com`) 通信。
- 请检查 AstrBot 宿主所在服务器的网络连通性，确保未被防火墙阻断，或在部署环境配置了有效的系统网络代理。

### Q5：支持私有仓库 (Private Repo) 统计吗？

- 本插件目前专注于**公开 (Public) 仓库**的代码统计分析。
- 私有仓库涉及组织权限、细粒度鉴权下载与安全隔离，当前暂未支持。

---

## 🚧 已知限制

- **公开仓库支持**：目前主要支持公开 (Public) Git 仓库的代码行数统计与归档分析，私有仓库暂未支持。
- **网络依赖性**：统计过程直接依赖宿主机与 GitHub / GitLab 官方服务的网络连通性。
- **轻量级词法解析**：统计基于高效的状态机流式行级扫描与词法识别，对单文件内混排多语言的按主语言归纳统计，不深入执行 AST 语法树编译。

## 💖 友情链接与致谢

- [AstrBot](https://github.com/AstrBotDevs/AstrBot): 在此感谢其开发团队对该项目的付出。
- [CountLOC](https://codetabs.com/count-loc/count-loc-online.html): 本插件的灵感来源。可惜 API 已经挂了。

## 📚 推荐阅读

我的其他插件：

- [主动消息 (Proactive_Chat)](https://github.com/Pancakes-Labs/astrbot_plugin_proactive_chat) - 它能让你的 Bot 在特定的会话长时间没有新消息后，用一个随机的时间间隔，主动发起一次拥有上下文感知、符合人设且包含动态情绪的对话。
- [灾害预警 (Disaster_Warning)](https://github.com/Pancakes-Labs/astrbot_plugin_disaster_warning) - 它能让你的 Bot 提供实时的地震、海啸、台风、气象预警信息推送服务。
- [视奸面板 (Live_Dashboard)](https://github.com/Pancakes-Labs/astrbot_plugin_live_dashboard) - 它能让你的 Bot 和群友随时随地视奸你。

## 🤝 贡献

欢迎提交 [Issue](https://github.com/Pancakes-Labs/astrbot_plugin_count_loc/issues) 和 [Pull Request](https://github.com/Pancakes-Labs/astrbot_plugin_count_loc/pulls) 来改进这个插件！

- 对于新功能的添加，请先通过 Issue 等方式讨论。
- 对于 PR (拉取请求)，请确保你已阅读并同意遵守本项目的 [贡献指南](https://github.com/Pancakes-Labs/astrbot_plugin_count_loc/blob/main/CONTRIBUTING.md)。

### 📞 联系我们

如果你对这个插件有任何疑问、建议或 bug 反馈，欢迎加入我的 QQ 交流群。

- **QQ 群**: 1033089808
- **群二维码**:
  
  <img width="281" alt="QQ Group QR Code" src="https://github.com/user-attachments/assets/53acb3c8-1196-4b9e-b0b3-ad3a62d5c41d" />

## 📄 许可证

GNU Affero General Public License v3.0 - 详见 [LICENSE](LICENSE) 文件。

本插件采用 AGPL v3.0 许可证，这意味着：

- 您可以自由使用、修改和分发本插件。
- 如果您在网络服务中使用本插件，必须公开源代码。
- 任何修改都必须使用相同的许可证。

## 📊 仓库状态

![Alt](https://repobeats.axiom.co/api/embed/7bb8d8bc0dc360ea8d363c821e9419a2f6d8c9ec.svg "Repobeats analytics image")

## ⭐️ 星星

<a href="https://www.star-history.com/?repos=Pancakes-Labs%2Fastrbot_plugin_count_loc&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=Pancakes-Labs/astrbot_plugin_count_loc&type=date&theme=dark&legend=top-left&sealed_token=U6SnqMCZ-8bb9FVZcRsE4UJgiF9Btm06zGBewrYTd2if-M8ZazfuYh2GPGdo1H-NIetQ6rT4jhXA3XUdr27P7PrMl4i8jiKfxa-3mVKR63urK75R87OfmA" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=Pancakes-Labs/astrbot_plugin_count_loc&type=date&legend=top-left&sealed_token=U6SnqMCZ-8bb9FVZcRsE4UJgiF9Btm06zGBewrYTd2if-M8ZazfuYh2GPGdo1H-NIetQ6rT4jhXA3XUdr27P7PrMl4i8jiKfxa-3mVKR63urK75R87OfmA" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=Pancakes-Labs/astrbot_plugin_count_loc&type=date&legend=top-left&sealed_token=U6SnqMCZ-8bb9FVZcRsE4UJgiF9Btm06zGBewrYTd2if-M8ZazfuYh2GPGdo1H-NIetQ6rT4jhXA3XUdr27P7PrMl4i8jiKfxa-3mVKR63urK75R87OfmA" />
 </picture>
</a>

---

Made with ❤️ by DBJD-CR & Gemini
