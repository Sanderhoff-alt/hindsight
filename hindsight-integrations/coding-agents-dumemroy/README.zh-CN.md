# hindsight-coding-agents（中文说明文档）

为 **Coding Agents（编码智能体）** 打造的长期项目记忆引擎，由 [Hindsight](https://vectorize.io/hindsight) 提供底层技术支持。  
一套统一包，适配各大主流 Agent：共享底层的推理与注入（Reflect-and-Inject）核心，并为每个 Agent 提供轻量级接入入口（**opencode**、**opencode 2**、**Kilo CLI**、**Cline CLI**、**pi**、**Prime Agent**、**DeepSeek Harness**、**Claude Code**、**Codex CLI**、**DeepAgents Dcode**、**Antigravity CLI**、**Cursor CLI**、**GitHub Copilot CLI**、**Devin CLI**、**Grok Build**）。数据接入完全全自动 —— 无需繁琐的设置命令：在你日常编码工作的过程中，仓库的 Git 历史记录与对话会话将在后台静默流式汇入专属的 Memory Bank（记忆库）。

**核心设计初衷**：大多数代码修改都可以从现有代码中推导得出，但关键的“最后一公里”往往取决于**完全不在现有代码中体现的项目专属决策** —— 比如特殊的舍入规则、重试白名单机制、平局决胜策略。这些关键决策沉淀在过去的 Git 提交历史与开发者对话中。本插件会在 Agent 开始工作的那一刻，将这些决策精准推送到模型眼前，并持续维护一组精选的**知识页面（Knowledge Pages）**（涵盖系统架构、开发规范、推进中的特性计划），供后续各会话直接继承使用。

---

## 安装（Install）

<!-- skill:begin title="Install / update" -->

```bash
npx @vectorize-io/hindsight-coding-agents install all          # 为所有检测到的 Agent 原生配置记忆插件
npx @vectorize-io/hindsight-coding-agents install claude-code  # 或仅安装指定的一个 Agent
npx @vectorize-io/hindsight-coding-agents uninstall all        # 严格清理安装时新增的内容
npx @vectorize-io/hindsight-coding-agents update               # 仅刷新运行时暂存，不改写宿主配置
```

`install` 命令需要显式指定目标 —— `all`，或者一个/多个具体的 Harness 名称。直接执行裸命令 `npx @vectorize-io/hindsight-coding-agents install` 不会改动任何配置，仅会打印可选列表，避免意外为整台机器上的所有 Agent 盲目配置。**更新也是运行同样的 `install` 命令** —— 它会在原地重新复制最新的运行时代码。

在日常使用中，你通常无需手动操作更新：系统每天会在会话启动时自动检查一次 npm 注册表，并在后台暂存更新的运行时版本（`autoUpdate`，默认开启 —— 如需锁定当前固定版本，可将其设为 `false`）。这相当于上述的 `update` 命令，它会刷新所有已配置 Agent 当前指向的文件副本，且刻意**不改动任何宿主配置文件**；只有在发布了新增 Hook 钩子的大版本、或需要接入新 Agent 时，才需要你手动重新执行 `install`。

<!-- skill:end -->

在终端交互执行时，安装器还会主动询问**记忆数据的存储位置** —— 是使用 Hindsight Cloud 官方云服务、私有化部署的服务器，还是运行在当前机器上的本地守护进程（参见 [记忆存储位置](#记忆存储位置-where-memory-lives)）。脚本化无人值守安装则可通过传递 `--server cloud|self-hosted|daemon` 参数来指定；该问题只在首次安装时询问一次，后续重复安装不会重复打扰。

---

### 各 Agent 单独安装指南（Per Agent）

安装命令统一一致，只需替换 Harness 名称。建议在全局安装该包后运行。

#### <img src="https://hindsight.vectorize.io/img/harness/claude-code.png" alt="" width="20" height="20" /> Claude Code

```bash
npx @vectorize-io/hindsight-coding-agents install claude-code
```

在 `~/.claude/settings.json` 中配置 3 个 Hook 钩子，通过 `claude mcp add` 注册用户级 MCP 服务，并安装伴生技能（Companion Skill）。

#### <img src="https://hindsight.vectorize.io/img/harness/codex.svg" alt="" width="20" height="20" /> Codex CLI

```bash
npx @vectorize-io/hindsight-coding-agents install codex
```

在 `~/.codex/hooks.json` 中配置 3 个 Hook 钩子，并在 `config.toml` 中增加 `[mcp_servers]`（需要开启 `codex_hooks = true`）。

#### <img src="https://hindsight.vectorize.io/img/harness/dcode.svg" alt="" width="20" height="20" /> DeepAgents Dcode

```bash
npx @vectorize-io/hindsight-coding-agents install dcode
```

安装器会将本包注册为 Dcode 的本地插件市场源，随后调用 Dcode 原生的 `plugin install` 命令。本插件遵循原生 Agent Plugin 规范：其根目录的 `plugin.json` 提供了共享技能、Hooks V2 的 `SessionStart`、`UserPromptSubmit` 与 `Stop` 生命周期，以及命名空间化的 `hindsight_*` MCP 服务。安装后通过 Dcode 标准的插件管理器启用即可，无需任何 Dcode 配置补丁或兼容层。

Dcode 会为其插件的 MCP 工具加上命名空间前缀，因此工具名会显示为 `plugin__hindsight-coding-…__hindsight_…` 而非原始短名 —— Agent 无论如何都能根据工具向导正确解析调用。在无头自动化运行（`dcode -n`）时，Dcode 允许只读类 Hindsight 工具运行，但会将两个写入类工具（`hindsight_ingest_document`、`hindsight_capture_initiative`）拦截在审批门禁之后（无头模式下因缺少 UI 无法审批）；因此，捕获倡议或存入文档请使用交互式 TUI 界面。同理，首次单次代码库调研（Codebase Survey）若检测到系统中安装了其他 Agent CLI，会自动借用其无头进程执行（与 Cursor、Copilot、Devin、Grok Build、Cline、Kilo 和 Prime Agent 的借用策略完全一致）。

#### <img src="https://hindsight.vectorize.io/img/harness/opencode.png" alt="" width="20" height="20" /> opencode

```bash
npx @vectorize-io/hindsight-coding-agents install opencode
```

在 `~/.config/opencode/opencode.json` 中写入插件条目 —— 原生注册工具，无需外部 MCP 服务。

#### <img src="https://hindsight.vectorize.io/img/harness/opencode.png" alt="" width="20" height="20" /> opencode 2

```bash
npx @vectorize-io/hindsight-coding-agents install opencode2
```

opencode v2（`npm @opencode-ai/cli@beta`）的 `opencode2` 二进制文件与 v1 **并行共存**，且全面重构了插件 API，因此它作为独立 Harness 单独适配。它向同一个配置文件 `~/.config/opencode/opencode.json` 写入插件条目 —— 两个 CLI 共享该文件（如果 v1 看到 v2 的 `plugins` 键则会拒绝整个配置），随后每个 CLI 从注册的同一个路径加载各自对应的入口。因此，安装其中任意一个 Harness 都会同时适配两者，卸载任意一个也会清理共享条目。

与 v1 相比有两处差异（皆由宿主特性决定）：首次单次代码库调研会借用其他已安装 Agent 的 CLI 执行（v2 插件目前无法定义调研所需的只读子 Agent）；种子灌库 Banner 写入插件日志中，而非 TUI 吐司弹窗（v2 插件无法抛出弹窗）。除此之外，Recall 召回、提示词注入、原生 `hindsight_*` 工具以及会话回写功能与 v1 完全相同。

#### <img src="https://hindsight.vectorize.io/img/harness/kilo.svg" alt="" width="20" height="20" /> Kilo CLI

```bash
npx @vectorize-io/hindsight-coding-agents install kilo
```

向 `~/.config/kilo/kilo.json[c]` 中写入插件条目。

#### <img src="https://hindsight.vectorize.io/img/harness/cursor-cli.svg" alt="" width="20" height="20" /> Cursor CLI

```bash
npx @vectorize-io/hindsight-coding-agents install cursor-cli
```

在 `~/.cursor/hooks.json`、`~/.cursor/mcp.json` 中配置钩子，并安装伴生技能。

#### <img src="https://hindsight.vectorize.io/img/harness/copilot-cli.svg" alt="" width="20" height="20" /> GitHub Copilot CLI

```bash
npx @vectorize-io/hindsight-coding-agents install copilot-cli
```

配置 `~/.copilot/hooks/`、`mcp-config.json`，并安装伴生技能。

#### <img src="https://hindsight.vectorize.io/img/harness/grok-build.svg" alt="" width="20" height="20" /> Grok Build

```bash
npx @vectorize-io/hindsight-coding-agents install grok-build
```

在 `~/.grok/config.toml` 中配置原生 Hook 和 MCP，并安装伴生技能。

#### <img src="https://hindsight.vectorize.io/img/harness/qwen-code.svg" alt="" width="20" height="20" /> Qwen Code

```bash
npx @vectorize-io/hindsight-coding-agents install qwen-code
```

在 `~/.qwen/settings.json` 中配置原生 Hook，注册 MCP 并安装伴生技能。

> Qwen 的 Hook 超时时间单位为**毫秒**（其官方文档标明："Timeout in milliseconds, default 60000"），与所有其他 Agent 不同，因此安装的超时值设置为 `30000/30000/60000`。  
> Recall 仅在真实的用户提问时触发 —— 由于 `UserPromptSubmit` 在工具返回结果继续执行时也会触发，因此交互式会话每轮提问只执行一次召回，而无头会话（`qwen -p`）、`serve`、SDK 及 ACP 会话只执行 Seed 和 Retain，不触发 Recall。

#### <img src="https://hindsight.vectorize.io/img/harness/antigravity-cli.png" alt="" width="20" height="20" /> Google Antigravity CLI

```bash
npx @vectorize-io/hindsight-coding-agents install agy
```

配置生命周期 Hook、MCP 服务，以及底部的 `Hindsight · <bank>` 终端状态行（Statusline）。

#### <img src="https://hindsight.vectorize.io/img/harness/devin-cli.svg" alt="" width="20" height="20" /> Devin CLI

```bash
npx @vectorize-io/hindsight-coding-agents install devin-cli
```

在 `~/.config/devin/config.json` 中配置 Hook 及 MCP。**要求 Node 22.5 或更高版本** —— 详见下文说明。

#### <img src="https://hindsight.vectorize.io/img/harness/cline-cli.svg" alt="" width="20" height="20" /> Cline CLI

```bash
npx @vectorize-io/hindsight-coding-agents install cline-cli
```

通过 `cline plugin install` 安装原生插件，注册 MCP 并安装伴生技能。

#### <img src="https://hindsight.vectorize.io/img/harness/pi.svg" alt="" width="20" height="20" /> pi

```bash
npx @vectorize-io/hindsight-coding-agents install pi
```

在 `~/.pi/agent/settings.json` 中配置 extension 扩展条目，并在 `~/.pi/agent/skills` 安装伴生技能 —— 原生注入工具，无需 MCP。

此命令是唯一官方支持的安装路径（对下文的 Prime Agent 同理）。我们故意没有将本插件作为标准 pi 包进行分发（`pi install npm:@vectorize-io/hindsight-coding-agents`）：因为 pi 与 Prime Agent 会读取 `package.json` 中的同一个 `pi` 键，而该键只能指定一个主入口 —— 无论未命中的宿主是哪一个，都会错误加载另一个宿主的 Bundle 并将自己汇报为错误的 Agent，导致它误读别的 Harness 配置分区并错误盖戳。因此本包完全没有包含 `pi` 键，而是由上面的安装命令将每个宿主精准指向其专属的 Bundle。

#### <img src="https://hindsight.vectorize.io/img/harness/prime-agent.svg" alt="" width="20" height="20" /> Prime Agent

```bash
npx @vectorize-io/hindsight-coding-agents install prime-agent
```

Prime Agent 是 pi 的衍生分支，因此接入方式完全一致：在 `~/.prime/agent/settings.json` 中配置扩展条目，在 `~/.prime/agent/skills` 安装技能 —— 原生注入工具，无需 MCP。同时安装两者不仅完全支持，而且是预期内的场景：  
每个宿主从各自的配置文件加载独立入口，且像所有其他成对的 Agent 一样，它们在**每个仓库共享同一个 Bank**（默认格式 `coding-agent::{gitProject}`），因此你在 pi 中沉淀的记忆在打开 Prime Agent 时无缝可用。彼此隔离的入口保留了精确的归属标识 —— 各自拥有独立的 `harnesses.<name>` 配置分区，且保留的每篇文档都打上自己真实的 Agent 标签。

#### <img src="https://hindsight.vectorize.io/img/harness/dsh.svg" alt="" width="20" height="20" /> DeepSeek Harness (DSH)

```bash
npx @vectorize-io/hindsight-coding-agents install dsh
```

在 `$DSH_HOME/cordis.patch.yml`（默认路径为 `~/.dsh`）中写入一行 Cordis 插件行，所有 dsh profile 均会自动组合该插件 —— 原生注入工具，无需 MCP。注意两点 dsh 专属细节：单个 dsh 进程可以同时服务**多个不同的仓库**（其 Web UI 允许将会话打开在你选择的任意目录中），因此其 Memory Bank 是按会话工作区动态解析的，而非随进程固定；此外，dsh 缺少面向插件的通知通道，因此种子灌库提示会写入插件日志中而非 UI 界面。大模型端可见的一切（召回记忆、知识前言、`hindsight_*` 工具）完全不受影响。如果你倾向于标准包管理方式，`dsh plugin --profile web add @vectorize-io/hindsight-coding-agents` 同样可用：该包自带 profile 补丁层，无需额外手工修改。

---

卸载命令同理：`npx @vectorize-io/hindsight-coding-agents uninstall claude-code`（或 `uninstall all`）。

**Devin CLI 依赖 Node 22.5 或更新版本**：Devin 的 Hook 仅向外部传递 session ID —— 会话内容本身存放在 `~/.local/share/devin/cli/sessions.db` 中，因此读取数据依赖 Node 22.5 内置的 `node:sqlite` 模块。安装 `devin-cli` 时会首先检查当前 Node 版本，若不满足则会明确告知原因并拒绝安装，避免配置了无法正常保存记忆的无效钩子。其余所有 Agent 均可在任何受支持的 Node 版本上运行。

`install` 会将运行所需文件复制到 `~/.hindsight/coding-agents` 并将各 Agent 的配置指向该路径，因此运行时不依赖于最初执行安装命令时的所在目录。**更新只需再次运行相同的安装命令** —— 它会在原地重新复制运行时代码，保持已有配置有效，并让所有新会话无缝运行在最新版本上。

`install` 会以幂等方式安全合并配置到各 Agent 的原生配置文件中，完整保留用户原有的所有字段；在修改前会自动将目标文件备份为 `<file>.hindsight-backup`。`uninstall` 仅精准清理本插件添加的条目。针对 Claude Code，安装还会部署一份**伴生技能（Companion Skill）**（`~/.claude/skills/hindsight-coding-agent`），指导 Agent 理解记忆系统的工作方式 —— 例如“将这部分存入 hindsight”该如何执行、可用的工具体系、单仓库配置定制、排错诊断等，开发者可以直接在对话中向 Agent 询问。

如果你更喜欢纯手工配置：

- **opencode** 与 **opencode 2**：直接在 `opencode.json` 中指向插件包目录：
  ```json
  { "plugin": ["/path/to/hindsight-coding-agents"] }
  ```
  单个条目同时服务两代 CLI：v1 通过 `package.json` 的 `main` 解析，v2 通过 `index.js` 解析，各自加载匹配的插件实现。
- **Claude Code** 与 **Codex**：使用自带的安装命令配置完整的三个 Hook + MCP 服务。本包暴露的 `bin` 命令（`hindsight-claude-hook`、`hindsight-codex-hook`、`hindsight-cursor-hook`）是供极简手工配置使用的单个提示词注入入口（`UserPromptSubmit`）。
- **接入新 Agent**：基于 Hook 的方式 ➔ 编写一个 `HookSpec` 入口（参考 `src/cursor-hook.ts`）并在 `src/harness/registry.ts` 注册一个 `hookAdapter`；常驻插件方式 ➔ 完整实现 `HarnessAdapter`（`src/core/types.ts`，参考 `src/harness/opencode.ts`），或者当它不是 opencode 衍生架构时，直接将宿主的原生插件 API 绑定到 `RuntimeCore`（参考 `src/cline.ts`、`src/dsh.ts`）。

---

## 从旧版单 Agent 插件迁移（Migrating from the per-agent plugins）

早期针对单一 Agent 的独立插件（`hindsight-claude-code`、`hindsight-cursor-cli`、`hindsight-codex` 等）已全部被本包统一取代。迁移过程只有两项数据发生流转，其余均保持不变：

1. **服务端配置自动继承**：如果检测到 `~/.hindsight/claude-code.json` 或 `~/.hindsight/codex.json` 存在，`install` 会自动迁移并接纳其端点配置 —— `hindsightApiUrl` ➔ `apiUrl`，`hindsightApiToken` ➔ `apiToken`，空 URL 表示本地守护进程。安装器会优先读取当前正在安装的 Agent 原有配置，因此安装 Codex 时会接管 Codex 原有的服务端，即使旁边留有旧的 `claude-code.json` 也不会冲突。我们充分尊重你对记忆存储位置的选择，不会在未经允许的情况下默认切换至 Cloud 导致提示词外发。如需覆盖，请显式传递 `--server`。（注：旧插件中只有这两个维护了用户配置，Cursor CLI、Copilot CLI、opencode 和 Cline 本身并无端点需迁移）。
2. **本地磁盘历史会话重新导入为新文档**：
   ```bash
   cd /path/to/your/repo
   npx @vectorize-io/hindsight-coding-agents install claude-code --import-conversations   # 或: install codex --import-conversations
   ```
   这会重新提取各 Agent 已经保存在磁盘上的历史会话转录，消耗的 Token 与导入的历史规模大致成正比。该操作可安全重复执行（数据接入层依据文档 ID 进行严格去重）。

之所以以本地转录文件为来源，而非直接迁移旧 Memory Bank，是因为旧版 Bank 无法按仓库进行拆分。旧版默认采用**单一全局静态 Bank**（`dynamicBankId` 默认为 false，所有项目的对话全部混杂在名为 `claude_code` 的单一 Bank 中），且旧文档只记录了 `retained_at`、`message_count` 和 `session_id`，没有任何标识所属 Git 项目的元数据。要理清哪些对话属于哪个仓库，最终依然需要通过 `session_id` 关联回本地转录中的工作区目录（`cwd`）；因此直接读取本地转录反而是更直接、更精准的路径。

**会话匹配规则**：只有当会话本身明确记录了其运行的目录路径时，才会被导入 —— 绝不会根据文件或文件夹名进行盲目猜测。Claude Code 会在记录中写入该目录，Codex 记在 `session_meta` 头部，DeepSeek Harness、pi 和 Prime Agent 记在会话日志头部，因此这五者都能被 100% 精确归属到所属仓库，包括在子目录中启动的会话。依靠猜测虽然省事（例如 Claude 曾以项目路径命名历史文件夹），但极其危险：因为路径中的 `/` 和 `.` 都会被转义为 `-`，导致 `repo-sub` 既可能是子目录 `repo/sub`，也可能是完全不相关的平级仓库 `repo-sub` —— 一旦猜错就会将其他项目的对话错误串流到当前仓库的 Bank 中。没有任何路径记录的会话将被安全跳过并统计计数。DeepSeek Harness 的日志采用 Zstandard 压缩格式存放于 `$DSH_HOME/sessions`，需要 Node 22.15+ 进行解压，旧版本 Node 会明确提示跳过原因。Dcode 的转录不记录目录（工作区路径深埋在其内部私有的 LangGraph 检查点数据库中），因此通过显式公开的 `dcode threads list --json` 命令契约提取仓库归属，CLI 不可用时则跳过。其余 Harness（opencode、opencode 2、Kilo、Cursor、Cline、Copilot、Devin）使用非公开版本的内部 SQLite 数据库，同样会输出原因并安全跳过。

**其余废弃行为参数一律不作转换**：旧插件中的各类行为调优参数（12 个 `recall*`、7 个 `retain*`、`bankMission`/`retainMission`、`dynamicBankGranularity`）描述的是已经被彻底重构替代的旧流水线，强行映射毫无意义。Bank 命名机制也已升级：新插件默认为每个**代码仓库**分配一个专属 Bank（`coding-agent::{gitProject}`），供所有 Agent 共同共享。如需保留旧版的按 Agent 隔离命名，可在配置中声明：

```jsonc
{ "bankIdTemplate": "{harness}::{gitProject}" } // 还原为旧版的按 Agent 分离命名
```

---

## 记忆存储位置（Where memory lives）

共有三种模式，在安装时配置（终端安装会主动交互询问；自动化脚本传递 `--server` 即可）：

| 运行模式 (`mode`) | 具体运行形态                             | 所需先决条件                                         |
| :---------------- | :--------------------------------------- | :--------------------------------------------------- |
| **`cloud`**       | Hindsight Cloud 官方托管云服务（默认）   | API Token                                            |
| **`self-hosted`** | 你自行私有部署的 Hindsight 后端服务      | 服务的 HTTP URL 地址                                 |
| **`daemon`**      | 运行在当前机器上的本地 `hindsight-embed` | 系统 PATH 中安装有 `uv` + 用于提取记忆的 LLM API Key |

```bash
npx @vectorize-io/hindsight-coding-agents install claude-code --server daemon
npx @vectorize-io/hindsight-coding-agents install claude-code --server self-hosted --api-url http://localhost:8888
npx @vectorize-io/hindsight-coding-agents install claude-code --server cloud --api-token <token>
```

重复执行 `install` 不会重复提问：若配置文件中已经指定了服务端配置，则会予以保留。

### 本地守护进程模式（Local daemon mode）

无需注册账号，也无需自行搭建服务器 —— 记忆引擎完全运行在本地机器上。插件会按需在 `127.0.0.1:9077` 启动本地 `hindsight-embed`，并将所有 Agent 统一导向该端口。

- **端口已有服务时自动复用，绝不重复启动**：单个本地守护进程服务全机的所有 Agent 和所有仓库；如果你原本就已经在跑 `hindsight-embed`，它会被直接复用。
- **冷启动在后台静默进行**：首次启动需要下载守护进程二进制并加载模型，耗时超出任何宿主 Hook 的超时阈值，因此它以 Detached 后台方式拉起。在守护进程就绪前开始的会话在前一两轮发问中处于无记忆状态 —— 未就绪的守护进程被视为暂时不可达，享受与云端/私有服务短时不可达完全相同的优雅降级容灾与诊断逻辑。URL 下游的所有组件对运行在何种模式完全无感知。
- **常驻运行，退出不杀进程**：进程会持续运行直到被手动终止。系统刻意**不采用随会话退出而杀进程的设计**：因为单个守护进程是多 Agent 全局共享的，退出当前会话绝不能导致正在后台工作的另一个 Agent 记忆突然中断。
- **macOS 额外需要现代 Rust 工具链**：`litellm`（API 的间接依赖）仅为 Linux 和 Windows 发布了预编译 Wheel 包，Mac 环境下需要由 maturin 借助本地工具链现场编译源码，其 crate 依赖较新的 `rustc`。请从 [rustup.rs](https://rustup.rs) 安装并保持更新。Linux 与 Windows 可直接使用二进制轮子，无此限制。
- **事实提炼在本地运行，因而需要 LLM 支持**：优先读取 `HINDSIGHT_API_LLM_PROVIDER`；若未配置，则依次探测 `OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`GEMINI_API_KEY`、`GROQ_API_KEY`；若均未配置，最后降级使用无需 Key 的 Claude Code CLI。安装程序会明确告知探测到的模型通道。

<!-- skill:begin title="Local daemon settings (daemon mode)" -->

本地守护进程的配置继承了旧版 Claude Code 插件的命名，方便无缝平移：

| 配置字段            | 对应环境变量                    | 默认值         | 说明与语义                               |
| :------------------ | :------------------------------ | :------------- | :--------------------------------------- |
| `serverMode`        | `HINDSIGHT_SERVER_MODE`         | `cloud`        | `cloud` \| `self-hosted` \| `daemon`     |
| `apiPort`           | `HINDSIGHT_API_PORT`            | `9077`         | 本地守护进程监听的 HTTP 端口             |
| `daemonIdleTimeout` | `HINDSIGHT_DAEMON_IDLE_TIMEOUT` | —              | 已弃用并忽略：守护进程不再因空闲自动退出 |
| `daemonProfile`     | `HINDSIGHT_DAEMON_PROFILE`      | `coding-agent` | 本地所使用的数据库 Profile 名称          |
| `embedVersion`      | `HINDSIGHT_EMBED_VERSION`       | `latest`       | 运行的 `hindsight-embed` 发布版本        |
| `embedPackagePath`  | `HINDSIGHT_EMBED_PACKAGE_PATH`  | —              | 本地研发调优时指定的本地源码检出路径     |

你导出的任何 `HINDSIGHT_API_*` 环境变量都会透明转发给本地守护进程，因此服务端高级参数在此无需另行包装。

<!-- skill:end -->

---

<!-- skill:begin -->

## 配置管理（Configuration）

所有配置收敛在**单一 JSON 文件**中：`~/.hindsight/coding-agent.json`。生效优先级由低到高如下（后者覆盖前者）：

1. 内置默认值（Built-in Defaults）
2. 环境变量 —— `HINDSIGHT_API_URL`、`HINDSIGHT_API_TOKEN`，以及各个标量设置（大写蛇形命名 `HINDSIGHT_<FIELD_IN_CAPS>`），便于容器与 CI 流水线注入配置；
3. 配置文件顶层字段（Top Level）
4. 配置文件中的 `harnesses.<name>` 分区 —— 针对特定 Agent 的个性化覆盖；
5. 配置文件中的 `banks.<resolvedBankId>` 分区 —— 针对具体 Memory Bank（项目）的个性化覆盖，在 Bank 路由计算完成后应用（参见 [针对特定仓库的启用/停用](#针对特定仓库的启用停用--banksbankid)）。

环境变量扮演的是**保底回退（Fallback）**角色：只要配置文件中显式配置了某项，文件永远优先；因此在已有配置文件的机器上声明环境变量不会产生意外篡改。两个列表类型的参数（`retainTags` 和 `optInPaths`）支持逗号分隔传递（如 `HINDSIGHT_RETAIN_TAGS="project:{gitProject},env:work"`），系统会自动执行去除空白。  
字典映射类的配置（`mapPathToBank`、`harnesses`、`banks`、`retainMetadata`）由于无法扁平展开为单一变量，仅支持在 JSON 文件中定义。`maxParallelRetains` 支持通过 `HINDSIGHT_MAX_PARALLEL_RETAINS` 供容器和 CI 调节并发。

环境变量 `HINDSIGHT_CONFIG` 可用于自定义配置文件的存放路径 —— 在容器或测试沙箱中，如果 `$HOME` 并非合适的锚点，可将其重定向到自定义路径（依然是单个文件，仅改变其磁盘位置）。其他不属于业务设置的环境变量包括 `HINDSIGHT_LOG_FILE`、`HINDSIGHT_DIAG_FILE` 与 `HINDSIGHT_LOG_LEVEL`（参见 [诊断与日志](#诊断与日志-diagnostics--logging)）。

### 配置修改何时生效（When a change takes effect）

配置在进程启动时由内存加载（不设置文件监听），因此修改后的生效时机取决于读取它的组件类型：

| 宿主组件类别                                                                                                              | 何时读取配置文件                                               | 修改何时正式生效               |
| :------------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------- | :----------------------------- |
| **Hook 类型的 Harness**<br>（Claude Code, Codex CLI, Cursor CLI, GitHub Copilot CLI, Grok Build, Antigravity CLI, Devin） | 每次触发 Hook 执行时<br>（每个 Hook 都是短生命周期独立子进程） | **下一次发问敲回车时**立即生效 |
| **常驻插件（Persistent Plugins）**<br>（opencode, opencode 2, Kilo CLI, Cline CLI, pi, Prime Agent, DeepSeek Harness）    | 每个工作区加载一次<br>（宿主加载插件时读入内存）               | **重启宿主 Agent** 之后生效    |
| **工具层背后的 MCP Server**<br>（为 `hindsight_*` 工具提供服务的子进程）                                                  | 进程启动时加载一次                                             | **下一次打开新会话窗口**时生效 |

**`apiToken` 是唯一的动态自愈例外**：所有宿主在遭遇服务端鉴权拒绝时，都会无条件重新从磁盘读取一次 Token；因此启用认证或中途轮转 Token 密钥会在下一次请求时立刻生效，完全无需重启任何进程 —— 避免了长驻 Agent 因轮转密钥而导致后续所有记忆调用瘫痪。其他所有参数（`apiUrl`、`disabled`、Bank 路由、`gitIngest`、Survey 调研与知识页面设置）均严格遵循上表规则。

调用 `hindsight_diagnose` 工具可以同时打印两端的快照 —— 既能看到当前磁盘配置文件的最新内容，也能看到内存中活跃客户端当前实际生效的值。

---

### 白名单显式准入模式（Opt-in only）

默认情况下，机器上的每一个项目都会自动开启记忆 —— 这正是“零配置（Zero-setup）”的精髓所在。如果你更倾向于隐私严密管控，希望在明确授权前对所有项目保持完全静默，可开启全局白名单模式：

```jsonc
{
  "optInOnly": true,
  "optInPaths": ["~/work/client-x", "~/oss"],
}
```

未在白名单路径下的任何项目均处于**完全钝化（Inert）状态**：不创建 Bank、不保存记忆、不跑 Git Seed 种子灌库，Agent 的表现与完全未安装本插件毫无二致。授权并不改变命名规则 —— `optInPaths` 指定的是*哪些目录被允许*，而不是*指定某个 Bank*，因此获得授权的项目依然沿用规范的 `coding-agent::{gitProject}` 隔离命名。路径基于前缀匹配，因此授权 `~/work` 会自动批准其下属的所有代码仓库，且各仓库依然保持彼此独立的 Memory Bank。

在 `mapPathToBank` 中声明了显式映射的仓库也会自动被视作已准入项目，因为将路径映射至命名 Bank 的行为本身就是明确的准入声明。但顶层单纯配置一个静态 `bankId` 并不能算作准入：它只声明了 Bank 名，没有界定哪个项目允许被记录，隐私开关必须严格执行 Fail-Closed 安全关闭原则。

插件刻意**不提供存放在代码仓库内部的准入配置文件**，正如我们完全不在仓库里放任何配置一样：绝对不能允许通过 clone 一个外部仓库就能静默激活本地记忆。

多 Agent 共享同一份配置文件，各入口会识别当前所属的 Harness（opencode 加载时认出自己是 opencode，Codex 钩子认出自己是 Codex），因此可以共存针对不同 Agent 的定制项：

```jsonc
{
  "apiUrl": "https://api.hindsight.vectorize.io",
  "harnesses": {
    "opencode": { "reflectTimeoutMs": 60000 },
    "claude-code": { "disabled": true }, // 例如：仅对 Claude Code 禁用记忆
  },
}
```

---

### 配置参数完整参考表（Reference）

| 配置字段 (Field)        | 默认值                               | 详细含义与设计机制                                                                                                                                                                                                      |
| :---------------------- | :----------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `apiUrl`                | `https://api.hindsight.vectorize.io` | Hindsight 服务端 HTTP 基础地址（使用本地服务设为 `http://localhost:8888` 或 `http://127.0.0.1:9077`）。                                                                                                                 |
| `apiToken`              | —                                    | Bearer 鉴权 Token（官方云服务必填）。遭遇 401/403 自动热重载，支持会话中途轮转密钥无需重启。                                                                                                                            |
| `bankId`                | —                                    | **显式指定全局单一静态 Bank**；若未设置，则执行针对代码仓库的动态 Bank 路由。                                                                                                                                           |
| `dynamicBankId`         | 无 `bankId` 时为 true                | 强制开启（`true`）或关闭（`false`）基于仓库名称的动态 Bank 路由。                                                                                                                                                       |
| `bankIdTemplate`        | `"coding-agent::{gitProject}"`       | 动态 Bank ID 命名模板；默认值确保同机所有 Agent 在同一代码库共享同一套记忆。                                                                                                                                            |
| `mapPathToBank`         | —                                    | 绝对路径映射到指定 Bank；**最长前缀匹配优先**；Git Worktree 自动继承主仓库的映射；优先级最高。                                                                                                                          |
| `optInOnly`             | `false`                              | 全局白名单开关：仅在已准入的项目中启用记忆，其余项目保持完全钝化（见 [Opt-in only](#白名单显式准入模式-opt-in-only)）。                                                                                                 |
| `optInPaths`            | —                                    | 准入目录白名单列表，前缀匹配并自动展开 `~`；其下每个代码库获得准入资格但依然保持各自独立的 Bank。                                                                                                                       |
| `resolveWorktrees`      | `true`                               | 是否让 Git Worktree 自动继承主工作区的 Bank 身份标识、路径准入授权与映射配置。                                                                                                                                          |
| `retainTags`            | —                                    | 插件保存文档时追加的额外标签，如 `["project:{gitProject}"]`（参见 [记录记忆来源](#记录记忆来源-recording-where-a-memory-came-from)）。                                                                                  |
| `retainMetadata`        | —                                    | 插件保存文档时追加的额外元数据字典，如 `{"repo": "{gitProject}"}`。                                                                                                                                                     |
| `manageBankConfig`      | `true`                               | 是否允许插件自适应配置 Bank 底层结构（策略、`knowledge` 标签组、Missions）。写入**严格为增量追加**：绝不覆盖你在控制台已配置的内容。设为 `false` 可完全禁止插件触碰 Bank 配置。                                         |
| `observationScopes`     | `"shared"`                           | 观察（Observations）聚合作用域：`"shared"`（默认）= 每个 Bank 共享单一全局作用域，确保多 Agent 形成统一共识；可选 `"combined"`、`"per_tag"`、`"all_combinations"`；`"per_source"` 则额外为 Git 与 Chat 设立隔离观察面。 |
| `disabled`              | `false`                              | 全局硬性急停开关（完全禁用插件和所有 Hook，用于对照测试无记忆基线表现）。                                                                                                                                               |
| `reflectTimeoutMs`      | `120000` (ms)                        | **自动会话启动 Reflect 超时上限**（Hook 类 Agent 会额外被硬限制在 25 秒内以适配宿主窗口）；超时后会话优雅降级在无 Reflect 状态下运行。                                                                                  |
| `reflectToolTimeoutMs`  | `330000` (ms)                        | 大模型主动调用 `hindsight_reflect` 时的超时上限。默认高于服务端的保护超时（300 秒），将放弃决策权交由服务端。                                                                                                           |
| `reflectBudget`         | `"high"`                             | 模型调用 `hindsight_reflect` 时的推理预算：`"low"`、`"mid"` 或 `"high"`。大规模知识库若遭遇超时可适度调低。自动 SessionStart 始终使用 `"low"`。                                                                         |
| `autoReflect`           | `true`                               | 会话**首轮提问**时是否自动推理注入 `<hindsight_memory>`。若设为 `false`，则关闭隐式注入，转为纯工具主动按需调用。                                                                                                       |
| `pageRefreshEveryTurns` | `10`                                 | 长会话中每隔多少轮用户提问向大模型重新刷新注入一次知识页名录与工具指南（防遗忘与注意力漂移）。                                                                                                                          |
| `pageTriggerType`       | `"auto-refresh"`                     | 知识页面更新触发时机与成本控制：`"auto-refresh"`（每次有新记忆产生因果重构后自动刷新，最敏锐但消耗 Token 较多）、`"cron"`（严格按定时触发）、`"manual"`（从不自动刷新）。                                               |
| `pageTriggerCron`       | —                                    | 当 `pageTriggerType: "cron"` 时的标准 UTC 5 位 Cron 表达式（如 `"0 3 * * *"`）。若该周期内代码库无任何新记忆产生，则自动跳过刷新。                                                                                      |
| `autoSeed`              | `true`                               | 冷库首次启动时，是否自动抓取 Git 历史提交记录建立初始记忆底座。                                                                                                                                                         |
| `seedLimit`             | `300`                                | 自动 Git 种子灌库抓取的最近 Commit 数量上限。                                                                                                                                                                           |
| `codebaseSurvey`        | `true`                               | 冷库首次启动时，是否通过无头子 Agent 探针漫游代码库并生成 4 篇基线架构文档。                                                                                                                                            |
| `surveyModel`           | `haiku`                              | 调研所使用的模型（目前主要用于 Claude 配方 `claude -p --model`；其他 Agent 沿用其默认配置）。                                                                                                                           |
| `surveyBudgetUsd`       | `2`                                  | 单次代码库调研的最大花费上限（美元）。                                                                                                                                                                                  |
| `surveyRefreshCommits`  | `20`                                 | 距离上次调研累计产生多少个新 Commit 后，自动增量重新触发代码库调研以跟踪架构演进（设为 `0` 表示仅冷库执行一次，后续永不重跑）。                                                                                         |
| `retainSessions`        | `true`                               | 是否在会话结束时将对话转录提炼写回记忆库。设为 `false` 则关闭会话回写（历史导入也会联动停止），但召回、Git 挖掘和工具调用依然正常工作。                                                                                 |
| `maxParallelRetains`    | `10`                                 | 针对 retain 相关请求的并发上限（保护服务端免受突发脉冲 429 限流）。                                                                                                                                                     |
| `logLevel`              | `"info"`                             | 本地插件日志输出级别（`"debug"` \| `"info"` \| `"warn"` \| `"error"`）。                                                                                                                                                |
| `autoUpdate`            | `true`                               | 每天在会话启动时后台静默检查 npm 并在发现新版本时热更 `~/.hindsight/coding-agents`。设为 `false` 可锁定版本。                                                                                                           |
| `gitIngest`             | `"message"`                          | Git 挖掘深度策略：`"message"` = 仅提交信息（汇总为单个文档，HEAD 移动时安全覆盖）；`"full"` = 提交信息 + 针对各个 Commit 的完整 Diff 渐进式挖掘；`"none"` = 彻底关闭 Git 历史提取。                                     |
| `harnesses.<name>`      | —                                    | 针对指定 Harness（Agent）的覆盖配置块。                                                                                                                                                                                 |
| `harness`               | `opencode`                           | **仅供底层 deepen 引擎测试使用**：指定 `--conversations` 读取的格式协议。                                                                                                                                               |

`pageTriggerType`/`pageTriggerCron` 仅决定知识页在**何时（When）**刷新；至于**如何（How）**刷新则由服务端控制：Hindsight 对知识页采用增量更新算法（每次迭代是在旧页面上修正，而非全量重推），上述参数是与服务端的默认参数进行合并。

**配置变更对后续创建的新页面生效**：修改配置并不会自动迁移或回溯已有旧页面的触发策略；已有页面保留其创建时绑定的 Trigger。若要修改已有页面，可通过 API（`PATCH /knowledge-base/nodes/{id}`）、SDK 或 Web 控制台进行修改，或直接删除该页面并在下次启动时由系统重新 Seed。

---

### 自主掌控 Bank 架构定制 —— `manageBankConfig`

插件连接到 Bank 时，默认会赋予其适配编码场景所需的结构：写入文档的保留策略（`git`、`gitlog`、`conversation`、`document`、`survey`）、将记忆归类到知识页面的 `knowledge` 实体标签组，以及针对空白库预置的编码专用 Missions。

**写入操作严格遵循“仅在缺失时追加”原则**：你在控制台自定义的策略、对插件内置策略的微调修改、调整过的标签组或重写的 Mission，在后续每一个会话中都会被完全保留，永远以 Bank 中已有设置为准。这一设计的妥协是：未来插件发版若*更新*了某项默认策略的提示词，不会自动强推给已经拥有该策略的旧库。若希望重置回插件最新的默认值，只需在控制台清理该策略配置，下次启动时便会自动重新写入。

将 `manageBankConfig: false` 可彻底禁止插件触碰任何 Bank 配置 —— 适用于与非编程任务共享的 Bank，或由你完全自主运维的场景。此时，该 Bank 必须自行定义上述 5 种处理策略。注意缺失处理是**静默容灾**的：服务端遇到未定义策略时不会报错拒绝，而是打出警告并使用系统通用配置提取 —— 此时 Commit Diff、会话转录与 Survey 标记都会接受通用提取处理，无法发挥专用策略的最佳效果。知识页面无论如何都会正常生成。

---

### 针对特定仓库的启用/停用 —— `banks.<bankId>`

基于**解析后的 Bank ID**（显示在会话启动 Banner 中）进行针对性覆盖，作用于 Bank 解析**之后** —— 无论仓库在磁盘上被移动到何处，配置依然持久有效：

```jsonc
{
  "banks": {
    "coding-agent::secret-client": { "disabled": true }, // 黑名单：对该涉密项目彻底关闭记忆
    "coding-agent::old-name": { "bank": "team::shared" }, // 改名或多仓库合并汇聚
    "coding-agent::big-mono": { "gitIngest": "full", "retainSessions": false },
  },
}
```

任何行为参数均可在 Bank 分区内单独定制，其中的 `bank` 字段用于**单跳重命名目标 Bank**（支持多个仓库汇聚到同一个共享 Bank 中）。

#### 实战范式：两个代码仓库，共享同一套记忆

有两种经典组织方式：

1. **按解析后的 Bank ID 汇聚** —— 适用于明确知道仓库名称的场景；不论仓库克隆在机器的何处，配置永远有效：
   ```jsonc
   {
     "banks": {
       "coding-agent::backend": { "bank": "team::product" },
       "coding-agent::frontend": { "bank": "team::product" },
     },
   }
   ```
2. **按父目录路径前缀匹配** —— 仓库收敛在统一的父目录下；一条 `mapPathToBank` 规则即可覆盖其下现在和未来所有的仓库：
   ```jsonc
   {
     "mapPathToBank": { "/Users/me/work/client-x": "client-x-memory" },
   }
   ```

经验法则：对少量精选仓库使用 **ID** 进行合并；对目录树边界（例如“凡是放在 `work/client-x` 下的所有项目全部共享记忆”）使用 **路径（Path）** 映射。

---

### Bank 路由寻址解析机制（Bank resolution）

编码记忆严格**按代码仓库物理隔离**。工作区目录对应的 Bank 解析优先级如下：

1. **`mapPathToBank` 显式映射** —— 最长绝对路径前缀匹配生效（映射仓库根目录会自动覆盖所有子目录；更深的子路径映射优先级更高；能覆盖显式的静态 `bankId`）。
2. **静态指定** —— 配置了 `bankId`（或声明了 `dynamicBankId: false`）。
3. **动态计算** —— 解析 `bankIdTemplate` 中的占位符：
   - `{gitProject}` —— **支持 Worktree 识别的仓库主名称**：通过 `git rev-parse --git-common-dir` 将所有关联的 Git Worktree 统一解析为**主分支工作树**的目录名，确保同一代码库的所有 Worktree 共享同一个 Bank。在 **Git 仓库之外**运行时，自动回退到会话启动时所在目录的文件夹名称。
   - `{project}` —— 当前工作区目录的纯文件夹名。
   - `{harness}` —— 当前执行入口的 Agent 名称（`opencode`, `claude-code`, `codex`, `antigravity-cli`, `cursor-cli`, `copilot-cli` 等）。
   - `{channel}` / `{user}` —— 来自环境变量 `$HINDSIGHT_CHANNEL_ID` / `$HINDSIGHT_USER_ID`。

默认的 `"coding-agent::{gitProject}"` 具有**跨 Agent 中立性**，因此 opencode、Claude Code、Cursor 和 Codex 在同一个仓库中无缝共享同一套记忆 —— 若希望按 Agent 分隔，可将其改为 `"{harness}-{gitProject}"`。

---

### 记录记忆来源（Recording where a memory came from）

在一库一 Bank 的模式下，Bank 本身就天然代表了来源。但在**跨项目共享的大 Bank** 场景下，所有记忆混合在一起，需要通过元数据明确归属。`retainTags` 与 `retainMetadata` 会在每次写入对话、Git 历史、Survey 产物与手动保存文档时，为数据打上精准的溯源烙印：

```jsonc
{
  "bankId": "shared", // 跨项目统一大 Bank
  "retainTags": ["project:{gitProject}", "env:work"],
  "retainMetadata": { "repo": "{gitProject}" },
}
```

后续召回即可通过 `project:<repo>` 过滤，每份文档也能直观展示其产自哪个项目。两者支持与 `bankIdTemplate` 相同的占位符，且额外支持 `{bankId}`、`{sessionId}` 与 `{timestamp}`。

系统保留了 `source:` 与 `harness:` 标签命名空间：配置中尝试声明这些命名空间会被忽略并报警，确保文档的 Agent 属性永远真实反映写入它的实体。

---

### 单代码库统一共识（One set of beliefs per repo）

本插件写入的每份文档都自带来源标签 —— `source:chat`、`harness:<id>`、`knowledge:<kind>` 等。这些标签标识了**谁写入了这篇记忆**，用于过滤检索和在 UI 上展示 Agent 专属图标。

然而，它们并不是合理的[观察（Observations）](https://hindsight.vectorize.io/developer/observations)隔离边界。服务端默认的 `combined` 模式会为每个不同的标签组合构建独立的一套观察集 —— 这会导致同一代码库如果在两个 Agent 之间交替编码，就会分化出两套永不合并、彼此盲区且计算成本翻倍的平行信念集。无论当时是哪个 Agent 在敲键盘，项目的代码规范与架构决策都应当是唯一的客观事实。

因此，本插件默认声明 `observationScopes: "shared"`：每个 Bank 内部维护**全局唯一、无标签绑定的共识观察集**，完美契合一个项目一套记忆的核心理念。

#### 将代码与对话在观察面上分离 —— `per_source`

`shared` 将项目内所有文档聚合在同一个信念集。如果你希望将“Git 提交里说明的技术点”与“聊天对话里商定的结论”在观察层面上分开问询，可开启 `"per_source"`：

```jsonc
{ "observationScopes": "per_source" }
```

此时每篇文档除汇入全局观察集外，还会按其 `source:` 标签归入专属观察面（会话归入 `["source:chat"]`，Git 提交归入 `["source:git"]`）。你可以使用 `tags: ["source:git"], tags_match: "exact"` 查询纯 Git 提炼的共识，或通过空标签查询合并共识。

---

<!-- skill:end -->

## 数据接入层底层机制（Ingestion internals，无外部 CLI）

数据摄取没有面向用户的独立命令 —— 会话启动时在后台静默拉起深化引擎（`dist/deepen.js`），自动按需补齐缺失的工作：Bank 底层策略配置、历史会话导入（基于文档 ID 去重）、单次 Gitlog 种子灌库、增量分批 Commit Diff 深度挖掘（由新至旧，单次限制批次规模），并在提取完成后驱动知识页面合成。需要严格确定性测试的场景（基准评测、E2E 测试套件）可直接运行深化引擎，并轮询 `dist/status.js` 直到 `"synced": true` —— 这与 Agent 工具 `hindsight_sync_status` 的就绪判定契约完全一致。

若要在本地体验自建 Hindsight 记忆服务端，可通过 Docker 一键拉起：

```bash
docker run -d -p 8888:8888 -p 9999:9999 -e HINDSIGHT_API_LLM_PROVIDER=gemini \
  -e HINDSIGHT_API_LLM_API_KEY=$GEMINI_API_KEY -e HINDSIGHT_API_LLM_MODEL=gemini-2.5-flash \
  ghcr.io/vectorize-io/hindsight:latest
```

---

## 伴生技能构建说明（Companion skill，自动生成）

支持技能（Skills）的宿主会得到 `skill/SKILL.md`，指导 Agent 理解插件能力与配置。**该文件由构建脚本全自动生成，切勿直接手工修改**。本 README 是单一真实信息源：`<!-- skill:begin -->` 与 `<!-- skill:end -->` 之间的内容会被提取编译进技能中。面向 Agent 的专用说明（工具调用时机、记忆归因规范、纠错协议）独立维护在 `skill-src/preamble.md` 中。

```bash
npm run skill:build   # 编辑本 README 或 preamble 之后重新构建技能
```

`src/docs-freshness.test.ts` 是一道防漂移自动化门禁：当技能陈旧未重新构建、或代码中新增了配置字段却未在 README 中体现时，测试会直接失败阻断提交。官方文档站点的对应页面同样由此文件通过脚本同步生成（`node hindsight-docs/scripts/sync-coding-agents-doc.mjs`）。

---

<!-- skill:begin -->

## 诊断与日志（Diagnostics & logging）

系统产出两套面向不同受众的日志文件：

1. **分级插件运行日志（供人工调试）**：`$TMPDIR/hindsight-coding-agent/plugin.log`（可通过 `HINDSIGHT_LOG_FILE` 覆盖） —— 记录带时间戳与模块标签的日志输出。默认级别为 `info`；可在配置中设置 `"logLevel": "debug"` 或在环境变量声明 `HINDSIGHT_LOG_LEVEL=debug` 查看极详尽的执行流。
2. **结构化诊断事件流（供程序/自动化 Harness 消费）**：每次 Reflect 推理与知识页面读取的结果均以 JSONL 形式单行追加到 `/tmp/hindsight-plugin.log`（可通过 `HINDSIGHT_DIAG_FILE` 覆盖）：
   ```json
   {
     "ts": "2026-07-27T07:05:52Z",
     "harness": "claude-code",
     "event": "reflect_ok",
     "ms": 14210,
     "chars": 792,
     "query": "..."
   }
   ```
   `reflect_failed` / `pages_failed` 记录失败详情。测试开启/关闭记忆的效果对比时可直接监控该文件 —— 若 reflect 失败则视同无记忆运行。种子灌库启动记录为 `seed_started`。

### 记忆数据是否就绪了？

调用面向 Agent 的工具 `hindsight_sync_status`（脚本调用 `dist/status.js`）：返回 `"synced": true` 表示冷启动种子记忆已经完全就绪并可供检索。它同时会返回 Gitlog 新鲜度、Commit Diff 深化推进到的具体位置、代码库调研状态（`surveyBaseline` 代表开始调研时的 Commit HEAD，`surveyDocs` 显示已入库的发现文档数量 0~4 篇 —— 缺少文档会自动重试），以及后台仍在跑的任务数。

### 如何重置清空某个仓库的记忆？

直接在服务端删除该仓库对应的 Memory Bank 即可。Bank 是本插件保留的**唯一有状态数据**；在服务端删除后，下一次在该仓库启动会话就会被当成真正的全新项目 —— 从零重新执行 Git 种子灌库与架构调研。客户端本地没有任何需要手动清理的脏文件。

### 运行时可见的标记文档说明

系统在内部记账时会生成以下两种专属标记文档，完全可以安全忽略：

- `survey-baseline:<sha>` —— 代码库调研运行期间内容为 "🛰️ researching…"，产出文档入库后翻转为 "✅ completed"。由专用 `survey` 策略维护，不会提取出任何实质记忆，仅作为重新调研频次（`surveyRefreshCommits`）的记账哨兵。
- `gitlog:<repo>` —— 聚合的 Git 提交信息种子文档，下次运行灌库时会原地更新覆盖，不会产生重复文档。

### 为什么感觉没有用到记忆？

记忆系统的所有故障都遵循 **Fail-Open 优雅降级** 原则：任何 Reflect 推理、知识页拉取或保存失败，都会静默回退到普通的无记忆对话轮次，绝不阻断正常编码，只在日志中留下记录。因此当怀疑“没有记忆”时，请检查诊断日志中该 Bank 是否真正触发过 `session_start` 与 `deepen_started`。在安装插件前就已经开启的会话没有经历过 SessionStart；但在安装后的首次用户提问时会自动触发自愈补齐。

<!-- skill:end -->
