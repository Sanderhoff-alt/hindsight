# Coding Agents E2E 测试

本目录包含基于 Docker 的真实 Agent CLI 端到端测试。测试使用当前源码打包出的插件 `.tgz`，在容器中安装真实 Agent CLI 和插件，然后验证 DuMemory 记忆是否能注入 Agent 上下文，以及会话是否能写回 DuMemory。

## 与单元测试的区别

普通测试默认由以下命令运行，并排除 E2E 文件：

```bash
npm test
```

E2E 测试需要 Docker、可用的 DuMemory 服务和 Agent 凭据，默认不会运行。使用以下命令显式启动：

```bash
npm run test:harness-e2e
```

默认会遍历所有已定义的 Harness。可以使用 Vitest 的 `-t` 参数按名称筛选单个 Harness，例如只运行 Qwen Code：

```bash
npm run test:harness-e2e -- -t "qwen-code"
```

测试名称包含 Harness 名称，例如 `qwen-code`、`opencode`、`codex`。没有凭据或被标记为 `unsupported` 的 Harness 仍会跳过。

该命令等价于构建插件后执行：

```bash
npm run build
DUMEMORY_HARNESS_E2E=1 npx vitest run src/harness.e2e.test.ts
```

## DuMemory 配置

E2E 不会自动启动 DuMemory 服务。它读取以下配置：

```bash
DUMEMORY_E2E_API_URL=https://cloud.memory.bj.baidubce.com/api
DUMEMORY_E2E_API_TOKEN=<DuMemory API token>
```

如果没有设置这两个变量，runner 会从 `DUMEMORY_E2E_CONFIG` 指定的 JSON 文件读取 `apiUrl` 和 `apiToken`；再没有指定时，默认读取：

```text
~/.dumemory/coding-agent.json
```

最小运行示例：

```bash
export DUMEMORY_E2E_API_URL=https://cloud.memory.bj.baidubce.com/api
export DUMEMORY_E2E_API_TOKEN=<token>
npm run test:harness-e2e
```

如果 API 地址是 `localhost` 或 `127.0.0.1`，传入容器时会自动转换为 `host.docker.internal`，用于访问宿主机上的服务。

## 环境变量

| 变量                             | 是否需要手动设置    | 作用                                                          |
| -------------------------------- | ------------------- | ------------------------------------------------------------- |
| `DUMEMORY_HARNESS_E2E`           | npm script 自动设置 | 设置为`1` 才启用 Docker E2E。                                 |
| `DUMEMORY_E2E_API_URL`           | 推荐                | 覆盖 E2E 使用的 DuMemory API 地址。                           |
| `DUMEMORY_E2E_API_TOKEN`         | 推荐                | 覆盖 E2E 使用的 DuMemory API Token。                          |
| `DUMEMORY_E2E_CONFIG`            | 可选                | 指定包含`apiUrl`/`apiToken` 的 DuMemory JSON 配置文件。       |
| `CODEX_E2E_AUTH_PATH`            | 可选                | Codex 订阅凭据路径。                                          |
| `OPENCODE_E2E_AUTH_PATH`         | 可选                | OpenCode/OpenCode 2 订阅凭据路径。                            |
| `KILO_E2E_AUTH_PATH`             | 可选                | Kilo 订阅凭据路径。                                           |
| `GROK_E2E_AUTH_PATH`             | 可选                | Grok Build 订阅凭据路径。                                     |
| `DEVIN_E2E_AUTH_PATH`            | 可选                | Devin CLI 订阅凭据路径。                                      |
| `CLINE_E2E_AUTH_PATH`            | 可选                | Cline CLI 凭据目录路径。                                      |
| `PI_E2E_AUTH_PATH`               | 可选                | Pi 订阅凭据路径。                                             |
| `PRIME_AGENT_E2E_AUTH_PATH`      | 可选                | Prime Agent 订阅凭据路径。                                    |
| `DUMEMORY_E2E_CREDENTIAL_TARGET` | 自动注入            | 容器内的 Agent 凭据目标路径。                                 |
| `DUMEMORY_E2E_INSTALL_COMMAND`   | 自动注入            | 容器内执行的插件安装命令。                                    |
| `DUMEMORY_CONFIG`                | 自动注入            | 容器内使用的临时 DuMemory 配置路径。                          |
| `DUMEMORY_DIAG_FILE`             | 自动注入            | 容器内诊断日志输出路径。                                      |
| `DUMEMORY_STUB_BASE_URL`         | 自动注入            | Stub Model 的 API 地址，只有支持 Stub Model 的 Harness 使用。 |
| `DUMEMORY_STUB_KEY`              | 自动注入            | Stub Model 的测试 API Key。                                   |

`*_E2E_AUTH_PATH` 变量只在对应 Harness 使用真实订阅凭据时生效；没有凭据的 Harness 会跳过。Stub Model 相关变量由 runner 动态生成，不需要手动填写。

## Agent 凭据

部分 Harness 需要宿主机上的真实订阅凭据。凭据会以只读方式提供给容器，不会修改宿主机文件。可以用环境变量覆盖默认路径：

```bash
CODEX_E2E_AUTH_PATH
OPENCODE_E2E_AUTH_PATH
KILO_E2E_AUTH_PATH
GROK_E2E_AUTH_PATH
DEVIN_E2E_AUTH_PATH
CLINE_E2E_AUTH_PATH
PI_E2E_AUTH_PATH
PRIME_AGENT_E2E_AUTH_PATH
```

没有对应凭据的 Harness 会被标记为 skipped，而不是测试失败。

### 当前无条件跳过的 Harness

以下 Harness 在代码中设置了 `unsupported`，即使存在凭据也会跳过：

| Harness       | 跳过原因                                                                                           |
| ------------- | -------------------------------------------------------------------------------------------------- |
| `claude-code` | CLI 在请求 Stub Model 前等待登录或 onboarding；macOS 订阅凭据存储在 Keychain，无法直接挂载到容器。 |
| `cursor-cli`  | 自定义 endpoint 未收到模型请求，复制本机 session 后仍提示`Authentication required`。               |
| `copilot-cli` | BYOK 环境变量未能让 CLI 请求 Stub Model；真实 token 存储在系统 Keyring 中。                        |
| `devin-cli`   | CLI 能认证并运行，但 runner 当前无法捕获最终回答，因而无法可靠验证记忆注入。                       |

`unsupported` 标记定义在 `src/e2e/harnesses.ts`，并由 `src/e2e/harness.ts` 的 `harnessCredentialStatus()` 转换为 skipped 状态。

### 当前支持运行的 Harness

| Harness       | 模型/认证方式                                                     | 无凭据时 |
| ------------- | ----------------------------------------------------------------- | -------- |
| `codex`       | 使用`CODEX_E2E_AUTH_PATH` 或 `~/.codex/auth.json`。               | 跳过     |
| `dcode`       | 自动使用 Stub Model。                                             | 可运行   |
| `opencode`    | 使用`OPENCODE_E2E_AUTH_PATH` 或默认 OpenCode 凭据。               | 跳过     |
| `opencode2`   | 与 OpenCode 共用凭据。                                            | 跳过     |
| `kilo`        | 使用`KILO_E2E_AUTH_PATH`，默认复用 OpenCode 凭据。                | 跳过     |
| `grok-build`  | 使用`GROK_E2E_AUTH_PATH` 或 `~/.grok/auth.json`；只验证会话留存。 | 跳过     |
| `qwen-code`   | 自动使用 Stub Model。                                             | 可运行   |
| `cline-cli`   | 使用`CLINE_E2E_AUTH_PATH` 或 `~/.cline`。                         | 跳过     |
| `pi`          | 使用`PI_E2E_AUTH_PATH` 或 `~/.pi/agent/auth.json`。               | 跳过     |
| `prime-agent` | 使用`PRIME_AGENT_E2E_AUTH_PATH` 或 `~/.prime/agent/auth.json`。   | 跳过     |
| `dsh`         | 自动使用 Stub Model。                                             | 可运行   |

插件安装器共支持 16 个 Harness，但统一 Docker E2E runner 只注册了其中 15 个：上述 11 个当前可运行，另外 4 个因 `unsupported` 无条件跳过。

唯一没有注册到统一 Docker E2E 的是 `antigravity-cli`。当前项目中没有单独运行真实 `agy` CLI 的 E2E；Antigravity 目前只有单元测试和安装器测试，覆盖配置写入、Hook、状态栏和会话解析等逻辑。因此，`antigravity-cli` 属于插件支持范围，但不属于当前真实 Agent CLI E2E 的覆盖范围。

## 测试流程

每个 Harness 都会独立执行以下流程：

1. 使用当前源码执行 `npm pack`，得到插件 tarball。
2. 构建该 Harness 的 Docker 镜像。
3. 在容器中执行 `npm install --global /plugin/*.tgz`。
4. 复制只读挂载的 Agent 凭据，并执行插件安装命令。
5. 创建临时 Git 仓库和独立的 DuMemory Bank。
6. 预先写入一个测试决策，再启动真实 Agent CLI。
7. 检查 Agent 输出是否包含召回的决策，并检查会话是否写回 DuMemory。

## Stub Model

部分 Agent 支持自定义模型 endpoint。对这些 Agent，E2E 会启动本地 Stub Model，并通过环境变量将模型请求转发到它。Stub Model 返回可预测的测试响应，避免消耗真实模型额度和受到模型随机输出影响。

Stub Model 只替代模型服务，不替代 Agent CLI、插件 Hook 或 DuMemory 服务。某些 Agent 仍会在调用模型前要求真实订阅登录；如果 CLI 无法使用自定义 endpoint，该 Harness 会保留为 unsupported 或 skipped。

## 注意事项

- E2E 使用当前源码打包的插件，不会从 npm 下载已发布版本。
- 测试需要 Docker daemon 正常运行。
- 每个 Harness 最长等待 12 分钟。
- Grok Build 的 Hook 无法把上下文注入模型，因此该 Harness 只验证会话留存。
- Claude Code、Cursor、Copilot 等 Harness 可能受账号登录、Keychain 或宿主环境限制而跳过。
