<!-- markdownlint-disable MD024 -->
# ghloc API 文档

> **项目**: ghloc (GitHub Lines Of Code)
> **服务端**: Go + chi 框架
> **数据接口域名**: `https://ghloc.ifels.dev`
> **开源地址**: <https://github.com/subtle-byte/ghloc>
> **本文档版本**: 1.0.0

---

## 1. 概述

ghloc 是一个用于统计 GitHub 公开仓库代码行数的服务。其服务端对外提供基于路径的 RESTful JSON 接口，支持按分支统计，并允许通过查询参数对统计结果进行路径过滤。

## 2. 基础信息

### 2.1 Base URL

所有数据接口请求均以以下地址为根路径：

```bash
https://ghloc.ifels.dev
```

### 2.2 认证

本 API 为公开接口，**无需任何认证**（不需要 API Key 或 Token）。

### 2.3 数据来源

服务端直接下载 GitHub 仓库对应分支的 zip 归档（
`https://github.com/{user}/{repo}/archive/refs/heads/{branch}.zip`），
在服务端解析并统计后返回。

### 2.4 内容类型

- 成功响应：`application/json`
- 错误响应：`application/json`（错误信息封装于 `error` 字段）

### 2.5 统计口径

- **LOC（Lines Of Code）**：指**非空行**（即至少包含一个非空白字符的行）。
  纯空白行不计入统计。
- 接口不区分代码行、注释行与空白行，仅提供非空行总数。

---

## 3. 接口

### 3.1 获取代码统计

获取指定 GitHub 仓库在指定分支下的代码行数统计。

```bash
GET /{user}/{repo}/{branch}
```

#### 路径参数

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `user` | string | 是 | GitHub 用户名或组织名 |
| `repo` | string | 是 | 仓库名 |
| `branch` | string | 是 | 分支名（或任意引用名） |

#### 查询参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `pretty` | boolean | 否 | `true` | 是否美化输出。设为 `false` 时返回紧凑 JSON，减少传输体积 |
| `match` | string | 否 | 无 | 匹配模式，**仅保留**路径匹配的文件 |
| `filter` | string | 否 | 无 | 过滤模式，**排除**路径匹配的文件 |

> [!NOTE]
> 查询参数可通过 URL 编码传递。例如 `match=^docs/` 需编码为 `match=%5Edocs%2F`。

#### 请求示例

```http
GET https://ghloc.ifels.dev/Pancakes-Labs/astrbot_plugin_count_loc/main?pretty=false
```

#### 响应结构

成功时返回 `200 OK`，响应体为**树状 JSON 结构**，描述仓库目录的代码行数分布：

```json
{
  "loc": 3399,
  "locByLangs": {
    ".yml": 1221,
    ".py": 632,
    ".md": 624
  },
  "children": {
    ".github": {
      "loc": 1242,
      "locByLangs": {
        ".yml": 1221,
        ".md": 21
      },
      "children": {
        "workflows": {
          "loc": 617,
          "locByLangs": {
            ".yml": 617
          },
          "children": {
            "shit-mountain.yml": 283
          }
        }
      }
    },
    "main.py": {
      "loc": 152
    }
  }
}
```

#### 字段说明

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `loc` | integer | 当前节点（目录或文件）的总非空代码行数 |
| `locByLangs` | object | 按语言（文件扩展名）聚合的行数。键为文件扩展名；无扩展名的文件以其文件名为键（如 `LICENSE`） |
| `children` | object | 子节点映射。键为目录名或文件名；目录节点包含 `loc`、`locByLangs` 与 `children`，文件节点仅包含 `loc` |

> [!NOTE]
> 响应中的目录与文件按 `loc` 降序排列，`loc` 相同时按键名升序排列。

---

### 3.2 默认分支重定向

在不指定分支时，获取仓库的默认分支统计。

```bash
GET /{user}/{repo}
```

#### 请求示例

```http
GET https://ghloc.ifels.dev/Pancakes-Labs/astrbot_plugin_count_loc
```

#### 响应

服务端通过 GitHub API 查询仓库的 `default_branch` 字段，返回 `307 Temporary Redirect`，
将请求重定向至默认分支（通常是 `main` 或 `master`）：

```http
HTTP/1.1 307 Temporary Redirect
Location: /Pancakes-Labs/astrbot_plugin_count_loc/main
```

客户端应跟随重定向，或直接拼接默认分支名发起请求。

---

## 4. 缓存

服务端对已统计的仓库结果进行缓存（基于 Postgres 数据库）。重复查询同一仓库
同一分支时，会直接返回缓存的统计结果，响应速度更快。

---

## 5. match/filter 语法

`match` 与 `filter` 参数共享同一套匹配语法，二者的行为相反：

- `match`：**仅保留**路径匹配的文件；
- `filter`：**排除**路径匹配的文件。

### 5.1 语法规则

| 规则 | 说明 |
| :--- | :--- |
| 逗号 `,` | 分隔多个模式，满足任一模式即视为匹配 |
| `!` 前缀 | 取反。含 `!` 的模式若命中，则**取消**文件的匹配/过滤结果 |
| `^` 前缀 | 锚定路径**开头**（正则语义） |
| `$` 后缀 | 锚定路径**结尾**（正则语义） |

### 5.2 匹配对象

匹配针对文件在仓库内的**完整路径**（含目录层级）。

### 5.3 示例

| 表达式 | 效果 |
| :--- | :--- |
| `match=.js$` | 仅保留路径以 `.js` 结尾的文件 |
| `match=^src/` | 仅保留路径以 `src/` 开头的文件（即 `src` 目录下） |
| `match=!test` | 排除路径中包含 `test` 的文件 |
| `match=!test,!.sum` | 排除路径中包含 `test` 或 `.sum` 的文件 |
| `match=.json$,!^package-lock.json$` | 仅保留 `.json` 文件，但排除 `package-lock.json` |
| `filter=.md$` | 排除所有 `.md` 文件 |

---

## 6. 错误响应

接口错误时返回对应的 HTTP 状态码，响应体为 JSON 格式：

```json
{
  "error": "错误描述"
}
```

### 6.1 状态码

| 状态码 | 含义 | 错误消息示例 |
| :--- | :--- | :--- |
| `400 Bad Request` | 请求参数无效 | 见服务端实现（非法过滤表达式等） |
| `404 Not Found` | 仓库或分支不存在 | `{"error": "Not found"}` |
| `500 Internal Server Error` | 服务端内部错误 | 见服务端实现 |

---

## 7. 限制

### 7.1 仓库大小限制

| 项目 | 限制值 |
| :--- | :--- |
| 最大仓库压缩包大小 | **100 MB**（`MAX_REPO_SIZE_MB=100`） |
| 支持平台 | 仅 **GitHub** 公开仓库 |

超过 100 MB 的仓库将无法统计，返回错误。

### 7.2 其他说明

- 本服务为第三方公开部署，官方未对可用性做任何保证（"no any guaranty"）。
- 统计基于仓库 zip 归档，归档下载速度会影响响应时长。

---

## 附录 A. 参考实现

- 服务端入口: `cmd/server/main.go`
- 路由注册: `internal/server/github_handler/{handler,redirect}.go`
- 过滤逻辑: `internal/service/loc_count/filter.go`
- 树构建: `internal/service/loc_count/stat.go`
- 行数统计: `internal/service/loc_count/file_counter.go`
- 仓库下载与限制: `internal/infrastructure/github_files_provider/github.go`
- 错误响应封装: `internal/server/rest/write_response.go`
