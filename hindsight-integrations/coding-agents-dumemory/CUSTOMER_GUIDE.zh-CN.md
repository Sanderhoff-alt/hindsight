# Coding Agents 插件接入

通过 DuMemory Coding Agents 插件（`@baiducloud/dumemory-coding-agents`）接入 Agent 记忆服务，可在各大主流终端 Coding Agent（OpenCode、Claude Code、Cursor、Google Antigravity、Codex 等）会话中使用云端长期记忆能力。插件安装后，智能体可在对话中自动感知当前项目的历史决策与架构规范，无需重复交代背景，并提供知识检索、方案记录和经验推理等记忆工具。

Coding Agents 插件通过统一安装器 `npx @baiducloud/dumemory-coding-agents install` 自动适配各 Agent 宿主的 Hook、MCP 与原生插件规范，适合希望开箱即用接入记忆服务的场景。

# 连接信息

| 信息         | 值                                                                             |
| :----------- | :----------------------------------------------------------------------------- |
| API Base URL | `https://cloud.memory.bj.baidubce.com/api`                                     |
| API Key      | 在控制台“API Key”页签中创建，写入全局配置的`apiToken` 字段                 |
| Bank ID      | 可以在控制台创建记忆库，然后静态指定；也可以按照代码仓库维度动态派生和自动创建 |
| 插件包名     | `@baiducloud/dumemory-coding-agents`                                         |

# 前提条件

确认已经安装至少一款受支持的 Coding Agent：

```bash
# 例如确认已安装 OpenCode、Claude Code 或 Cursor CLI 等
opencode --version
claude --version
cursor-cli --version
```

同时需要：

- 已在 DuMemory 控制台创建记忆库，并获取 API Base URL 与 API Key
- 本机环境安装 Node.js（推荐 Node.js `>= 18.0.0`；接入 Devin CLI 须使用 Node.js `>= 22.5.0`；接入 DeepSeek Harness 回填压缩会话须使用 Node.js `>= 22.15.0`）
- 本机网络可正常访问 DuMemory Cloud API 服务地址

# 安装方式

插件提供**全局统一安装**（一键配置整机所有 Agent）与**单 Agent 安装**（仅配置指定 Agent）。首次安装时，系统会在 `~/.dumemory/coding-agent.json` 自动生成全局配置。

> **说明**：可以使用 `--api-token <your-api-key>` 选项注入 Token，或者在执行命令后的交互中填入。

## 全局统一安装（推荐）

自动检测当前环境中已安装的所有 Coding Agent 并一键完成配置：

```bash
npx @baiducloud/dumemory-coding-agents install all
```

## 单 Agent 安装

若仅需为指定 Agent 启用记忆，可单独执行对应命令：

- **Claude Code**：`npx @baiducloud/dumemory-coding-agents install claude-code`
- **OpenCode**：`npx @baiducloud/dumemory-coding-agents install opencode`
- **OpenCode 2**：`npx @baiducloud/dumemory-coding-agents install opencode2`
- **Cursor CLI**：`npx @baiducloud/dumemory-coding-agents install cursor-cli`
- **Google Antigravity CLI**：`npx @baiducloud/dumemory-coding-agents install agy`
- **Codex CLI**：`npx @baiducloud/dumemory-coding-agents install codex`
- **DeepAgents Dcode**：`npx @baiducloud/dumemory-coding-agents install dcode`
- **DeepSeek Harness (DSH)**：`npx @baiducloud/dumemory-coding-agents install dsh`
- **GitHub Copilot CLI**：`npx @baiducloud/dumemory-coding-agents install copilot-cli`
- **Qwen Code**：`npx @baiducloud/dumemory-coding-agents install qwen-code`
- **Devin CLI**：`npx @baiducloud/dumemory-coding-agents install devin-cli`
- **Cline CLI**：`npx @baiducloud/dumemory-coding-agents install cline-cli`
- **Kilo CLI**：`npx @baiducloud/dumemory-coding-agents install kilo`
- **pi**：`npx @baiducloud/dumemory-coding-agents install pi`
- **Prime Agent**：`npx @baiducloud/dumemory-coding-agents install prime-agent`
- **Grok Build**：`npx @baiducloud/dumemory-coding-agents install grok-build`

## 导入已有历史会话（可选）

如需将本机现有的历史会话转录（Transcripts）萃取为项目记忆，可在对应项目根目录下执行：

```bash
cd /path/to/your/project
npx @baiducloud/dumemory-coding-agents install claude-code --import-conversations
```

系统将按项目目录精准解析历史会话，基于 Document ID 执行幂等去重入库。

# 推荐配置

安装后生成的全局配置文件位于 `~/.dumemory/coding-agent.json`。

## 动态 Bank ID（默认）

系统默认启用动态 Bank ID，自动感知 Git 仓库根目录，让同一代码库的所有 Agent 及 Git Worktree 共享同一套项目记忆，不同代码库之间物理隔离。推荐保持默认：

```json
{
  "apiUrl": "https://cloud.memory.bj.baidubce.com/api",
  "apiToken": "<your-api-key>",
  "dynamicBankId": true
}
```

## 固定 Bank ID

若希望当前环境固定写入控制台中指定的记忆库，可修改为：

```json
{
  "apiUrl": "https://cloud.memory.bj.baidubce.com/api",
  "apiToken": "<your-api-key>",
  "dynamicBankId": false,
  "bankId": "<your-bank-id>"
}
```

适合单项目开发或明确绑定特定记忆库的场景。

# 更新插件

更新运行时代码：

```bash
npx @baiducloud/dumemory-coding-agents update
```

或再次运行统一安装命令（原地覆盖刷新运行时，保留原有配置文件不变）：

```bash
npx @baiducloud/dumemory-coding-agents install all
```

> **说明**：
> 插件默认开启了 `autoUpdate: true`，每天在会话启动时会自动检查并在后台暂存更新，无需频繁手动执行更新命令。

# 生效与检查

安装或更新后，重新打开对应 Coding Agent 会话。

可以直接向智能体提问：

```text
你现在有哪些 DuMemory 记忆相关的工具可用？
```

回答中的可用工具应包含：

```text
dumemory_search_knowledge_pages
dumemory_read_knowledge_page
dumemory_list_knowledge_pages
dumemory_reflect
dumemory_capture_initiative
dumemory_ingest_document
dumemory_sync_status
dumemory_diagnose
```

各工具职责说明如下：

- **`dumemory_search_knowledge_pages`**：项目知识页的云端混合检索（全文+语义）。
- **`dumemory_read_knowledge_page`**：读取指定知识页完整内容（如架构规范、组件图谱等）。
- **`dumemory_list_knowledge_pages`**：列出当前代码库的所有知识页清单。
- **`dumemory_reflect`**：针对复杂设计决策与深层原因进行全库因果推理（Reflect）。
- **`dumemory_capture_initiative`**：在编码前记录或更新正在推进中的特性方案。
- **`dumemory_ingest_document`**：沉淀外部设计文档，或提交纠偏记录（`Correction: <topic>`）。
- **`dumemory_sync_status`**：检查当前代码库的记忆同步新鲜度与后台任务状态。
- **`dumemory_diagnose`**：打印当前生效的 Bank、路径、端点及配置状态（安全脱敏）。

# 可配置选项

以下选项均写在 `~/.dumemory/coding-agent.json` 中。

| 选项              | 类型    | 默认值                                       | 说明                                                             |
| :---------------- | :------ | :------------------------------------------- | :--------------------------------------------------------------- |
| `apiUrl`        | string  | `https://cloud.memory.bj.baidubce.com/api` | DuMemory API 服务地址                                            |
| `apiToken`      | string  | 无                                           | DuMemory API Key / Token，必须配置。遇 401/403 自动热重载        |
| `bankId`        | string  | 无                                           | 静态 Bank ID；单项目/单环境明确绑定特定记忆库时使用              |
| `dynamicBankId` | boolean | `true`                                     | 是否根据代码库自动生成并切换 Bank ID；多项目开发建议设为`true` |
