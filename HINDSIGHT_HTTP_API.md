# Hindsight HTTP API

> Hindsight 线上托管版 HTTP API  
> 版本 `0.9.1` · **75** 个接口 · **12** 个分组

HTTP API for Hindsight

---

## 目录

- [快速开始](#快速开始)
- [按模块浏览](#按模块浏览)
- [接口索引](#接口索引)
- [接口详解](#接口详解)

---

## 快速开始

### 认证与常用请求头

调用需携带：

```http
Authorization: Bearer <token>
Content-Type: application/json   # 有 JSON 请求体时
```

`Authorization` **必填**。有 JSON 请求体时还需 `Content-Type: application/json`。

### 接入地址

```http
https://cloud.memory.bj.baidubce.com/api
```

接口表中的路径直接拼接在该地址后。例如：

```http
https://cloud.memory.bj.baidubce.com/api/v1/default/banks/{bank_id}/memories/recall
```

通用路径前缀为 `/v1/default/banks/{bank_id}/...`。

### 错误

| 状态 | 含义 |
| --- | --- |
| `422` | 参数或请求体校验失败 |
| `400` | 业务参数不合法 |
| `401` / `403` | 认证 / 授权 |
| `404` | 不存在 |
| `409` | 冲突 |

### 异步 operation

`retain(async)`、`refresh` mental model、创建 knowledge page 等会返回 `operation_id` → 到 **Operations** 查询。

### 关于 operationId

每个接口有唯一 `operationId`，便于在工单、日志与客户端代码里引用。

---

## 按模块浏览

| 模块 | 说明 | 接口数 | 简介 |
| --- | --- | ---: | --- |
| [Banks](#banks) | Bank 管理 | 13 | 创建、配置、清理 bank；consolidation、LLM 探测、统计等控制面。 |
| [Bank Templates](#bank-templates) | Bank 模板 | 3 | bank 模板 schema / 导入导出，便于环境间复用配置。 |
| [Memory](#memory) | 记忆（Retain / Recall / Reflect） | 13 | 主路径 retain → recall → reflect，以及 list/get/update/clear。 |
| [Knowledge Base](#knowledge-base) | 知识库树（Knowledge Pages） | 8 | folder/page 树组织 mental model；异步生成 page；hybrid 搜索与 markdown 导出。 |
| [Mental Models](#mental-models) | 心智模型 | 9 | 可刷新的合成知识（多为 markdown）。可独立使用，也可挂到 KB page。 |
| [Documents](#documents) | 文档 | 7 | 文档粒度的查看、更新、删除与追踪。 |
| [Document Transfer](#document-transfer) | 文档迁移 | 3 | 文档导入导出与迁移。 |
| [Files](#files) | 文件 | 1 | 文件对象存取。 |
| [Entities](#entities) | 实体 | 3 | 实体列表与维护。 |
| [Directives](#directives) | 指令（Directives） | 5 | 运行时 directive 管理。 |
| [Operations](#operations) | 异步操作 | 5 | 异步任务状态（retain / refresh / 建 page 等返回的 operation_id）。 |
| [Webhooks](#webhooks) | Webhooks | 5 | 事件订阅与回调配置。 |

## 接口索引

| 模块 | 方法 | 路径 | 标题 | operationId |
| --- | --- | --- | --- | --- |
| Banks | `GET` | `/v1/default/banks` | [列出 Banks](#list-banks) | `list_banks` |
| Banks | `PUT` | `/v1/default/banks/{bank_id}` | [创建或更新 Bank](#create-or-update-bank) | `create_or_update_bank` |
| Banks | `PATCH` | `/v1/default/banks/{bank_id}` | [更新 Bank](#update-bank) | `update_bank` |
| Banks | `DELETE` | `/v1/default/banks/{bank_id}` | [删除 Bank](#delete-bank) | `delete_bank` |
| Banks | `GET` | `/v1/default/banks/{bank_id}/config` | [获取 Bank 配置](#get-bank-config) | `get_bank_config` |
| Banks | `PATCH` | `/v1/default/banks/{bank_id}/config` | [更新 Bank 配置](#update-bank-config) | `update_bank_config` |
| Banks | `DELETE` | `/v1/default/banks/{bank_id}/config` | [重置 Bank 配置](#reset-bank-config) | `reset_bank_config` |
| Banks | `POST` | `/v1/default/banks/{bank_id}/consolidate` | [触发 Consolidation](#trigger-consolidation) | `trigger_consolidation` |
| Banks | `POST` | `/v1/default/banks/{bank_id}/consolidation/recover` | [恢复 Consolidation](#recover-consolidation) | `recover_consolidation` |
| Banks | `POST` | `/v1/default/banks/{bank_id}/health/llm` | [测试 Bank LLM](#test-bank-llm) | `test_bank_llm` |
| Banks | `DELETE` | `/v1/default/banks/{bank_id}/observations` | [清除 Observations](#clear-observations) | `clear_observations` |
| Banks | `GET` | `/v1/default/banks/{bank_id}/stats` | [Agent 统计](#get-agent-stats) | `get_agent_stats` |
| Banks | `GET` | `/v1/default/banks/{bank_id}/stats/memories-timeseries` | [记忆时序统计](#get-memories-timeseries) | `get_memories_timeseries` |
| Bank Templates | `GET` | `/v1/bank-template-schema` | [Get bank template JSON Schema](#get-bank-template-schema) | `get_bank_template_schema` |
| Bank Templates | `GET` | `/v1/default/banks/{bank_id}/export` | [Export bank template](#export-bank-template) | `export_bank_template` |
| Bank Templates | `POST` | `/v1/default/banks/{bank_id}/import` | [Import bank template](#import-bank-template) | `import_bank_template` |
| Memory | `GET` | `/v1/default/banks/{bank_id}/graph` | [获取记忆图](#get-graph) | `get_graph` |
| Memory | `POST` | `/v1/default/banks/{bank_id}/memories` | [写入记忆（Retain）](#retain-memories) | `retain_memories` |
| Memory | `DELETE` | `/v1/default/banks/{bank_id}/memories` | [清空 bank 记忆](#clear-bank-memories) | `clear_bank_memories` |
| Memory | `POST` | `/v1/default/banks/{bank_id}/memories/dry-run-extract` | [试运行抽取记忆](#dry-run-extract-memories) | `dry_run_extract_memories` |
| Memory | `GET` | `/v1/default/banks/{bank_id}/memories/list` | [列出记忆](#list-memories) | `list_memories` |
| Memory | `POST` | `/v1/default/banks/{bank_id}/memories/recall` | [检索记忆（Recall）](#recall-memories) | `recall_memories` |
| Memory | `GET` | `/v1/default/banks/{bank_id}/memories/{memory_id}` | [获取单条记忆](#get-memory) | `get_memory` |
| Memory | `PATCH` | `/v1/default/banks/{bank_id}/memories/{memory_id}` | [更新记忆](#update-memory) | `update_memory` |
| Memory | `GET` | `/v1/default/banks/{bank_id}/memories/{memory_id}/history` | [观察历史](#get-observation-history) | `get_observation_history` |
| Memory | `DELETE` | `/v1/default/banks/{bank_id}/memories/{memory_id}/observations` | [清除记忆观察](#clear-memory-observations) | `clear_memory_observations` |
| Memory | `GET` | `/v1/default/banks/{bank_id}/observations/scopes` | [列出 observation scopes](#list-observation-scopes) | `list_observation_scopes` |
| Memory | `POST` | `/v1/default/banks/{bank_id}/reflect` | [推理反思（Reflect）](#reflect) | `reflect` |
| Memory | `GET` | `/v1/default/banks/{bank_id}/tags` | [列出 tags](#list-tags) | `list_tags` |
| Knowledge Base | `GET` | `/v1/default/banks/{bank_id}/knowledge-base/export` | [导出知识库](#export-knowledge-base) | `export_knowledge_base` |
| Knowledge Base | `POST` | `/v1/default/banks/{bank_id}/knowledge-base/folders` | [创建知识库目录](#create-knowledge-folder) | `create_knowledge_folder` |
| Knowledge Base | `PATCH` | `/v1/default/banks/{bank_id}/knowledge-base/nodes/{node_id}` | [更新知识库节点](#update-knowledge-node) | `update_knowledge_node` |
| Knowledge Base | `DELETE` | `/v1/default/banks/{bank_id}/knowledge-base/nodes/{node_id}` | [删除知识库节点](#delete-knowledge-node) | `delete_knowledge_node` |
| Knowledge Base | `POST` | `/v1/default/banks/{bank_id}/knowledge-base/pages` | [创建知识库页面](#create-knowledge-page) | `create_knowledge_page` |
| Knowledge Base | `GET` | `/v1/default/banks/{bank_id}/knowledge-base/pages/{page_id}` | [读取知识库页面](#get-knowledge-page) | `get_knowledge_page` |
| Knowledge Base | `GET` | `/v1/default/banks/{bank_id}/knowledge-base/search` | [搜索知识库页面](#search-knowledge-base) | `search_knowledge_base` |
| Knowledge Base | `GET` | `/v1/default/banks/{bank_id}/knowledge-base/tree` | [获取知识库树](#get-knowledge-base-tree) | `get_knowledge_base_tree` |
| Mental Models | `GET` | `/v1/default/banks/{bank_id}/mental-models` | [列出心智模型](#list-mental-models) | `list_mental_models` |
| Mental Models | `POST` | `/v1/default/banks/{bank_id}/mental-models` | [创建心智模型](#create-mental-model) | `create_mental_model` |
| Mental Models | `GET` | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}` | [获取心智模型](#get-mental-model) | `get_mental_model` |
| Mental Models | `PATCH` | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}` | [更新心智模型](#update-mental-model) | `update_mental_model` |
| Mental Models | `DELETE` | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}` | [删除心智模型](#delete-mental-model) | `delete_mental_model` |
| Mental Models | `POST` | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/clear` | [清空心智模型正文](#clear-mental-model) | `clear_mental_model` |
| Mental Models | `POST` | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/dry-run-refresh` | [Dry-run mental model refresh (preview, no persistence)](#dry-run-refresh-mental-model) | `dry_run_refresh_mental_model` |
| Mental Models | `GET` | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/history` | [心智模型历史](#get-mental-model-history) | `get_mental_model_history` |
| Mental Models | `POST` | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/refresh` | [刷新心智模型](#refresh-mental-model) | `refresh_mental_model` |
| Documents | `GET` | `/v1/default/banks/{bank_id}/documents` | [List documents](#list-documents) | `list_documents` |
| Documents | `GET` | `/v1/default/banks/{bank_id}/documents/{document_id}` | [Get document details](#get-document) | `get_document` |
| Documents | `PATCH` | `/v1/default/banks/{bank_id}/documents/{document_id}` | [Update document](#update-document) | `update_document` |
| Documents | `DELETE` | `/v1/default/banks/{bank_id}/documents/{document_id}` | [Delete a document](#delete-document) | `delete_document` |
| Documents | `GET` | `/v1/default/banks/{bank_id}/documents/{document_id}/chunks` | [List document chunks](#list-document-chunks) | `list_document_chunks` |
| Documents | `POST` | `/v1/default/banks/{bank_id}/documents/{document_id}/reprocess` | [Reprocess document](#reprocess-document) | `reprocess_document` |
| Documents | `GET` | `/v1/default/chunks/{chunk_id}` | [Get chunk details](#get-chunk) | `get_chunk` |
| Document Transfer | `POST` | `/v1/default/banks/{bank_id}/document-transfer` | [Import documents (async)](#import-documents) | `import_documents` |
| Document Transfer | `POST` | `/v1/default/banks/{bank_id}/document-transfer/export` | [Export documents (async)](#export-documents) | `export_documents` |
| Document Transfer | `GET` | `/v1/default/files/download/{key}` | [Download a stored file (async export archive)](#download-file) | `download_file` |
| Files | `POST` | `/v1/default/banks/{bank_id}/files/retain` | [Convert files to memories](#file-retain) | `file_retain` |
| Entities | `GET` | `/v1/default/banks/{bank_id}/entities` | [List entities](#list-entities) | `list_entities` |
| Entities | `GET` | `/v1/default/banks/{bank_id}/entities/graph` | [Get entity co-occurrence graph](#get-entity-graph) | `get_entity_graph` |
| Entities | `GET` | `/v1/default/banks/{bank_id}/entities/{entity_id}` | [Get entity details](#get-entity) | `get_entity` |
| Directives | `GET` | `/v1/default/banks/{bank_id}/directives` | [List directives](#list-directives) | `list_directives` |
| Directives | `POST` | `/v1/default/banks/{bank_id}/directives` | [Create directive](#create-directive) | `create_directive` |
| Directives | `GET` | `/v1/default/banks/{bank_id}/directives/{directive_id}` | [Get directive](#get-directive) | `get_directive` |
| Directives | `PATCH` | `/v1/default/banks/{bank_id}/directives/{directive_id}` | [Update directive](#update-directive) | `update_directive` |
| Directives | `DELETE` | `/v1/default/banks/{bank_id}/directives/{directive_id}` | [Delete directive](#delete-directive) | `delete_directive` |
| Operations | `GET` | `/v1/default/banks/{bank_id}/operations` | [列出异步操作](#list-operations) | `list_operations` |
| Operations | `GET` | `/v1/default/banks/{bank_id}/operations/{operation_id}` | [Get operation status](#get-operation-status) | `get_operation_status` |
| Operations | `DELETE` | `/v1/default/banks/{bank_id}/operations/{operation_id}` | [取消异步操作](#cancel-operation) | `cancel_operation` |
| Operations | `DELETE` | `/v1/default/banks/{bank_id}/operations/{operation_id}/delete` | [Delete a terminal async operation](#delete-operation) | `delete_operation` |
| Operations | `POST` | `/v1/default/banks/{bank_id}/operations/{operation_id}/retry` | [重试异步操作](#retry-operation) | `retry_operation` |
| Webhooks | `POST` | `/v1/default/banks/{bank_id}/webhooks` | [Register webhook](#create-webhook) | `create_webhook` |
| Webhooks | `GET` | `/v1/default/banks/{bank_id}/webhooks` | [List webhooks](#list-webhooks) | `list_webhooks` |
| Webhooks | `DELETE` | `/v1/default/banks/{bank_id}/webhooks/{webhook_id}` | [Delete webhook](#delete-webhook) | `delete_webhook` |
| Webhooks | `PATCH` | `/v1/default/banks/{bank_id}/webhooks/{webhook_id}` | [Update webhook](#update-webhook) | `update_webhook` |
| Webhooks | `GET` | `/v1/default/banks/{bank_id}/webhooks/{webhook_id}/deliveries` | [List webhook deliveries](#list-webhook-deliveries) | `list_webhook_deliveries` |

---

## 接口详解

## Banks
<a id="banks"></a>

**Bank 管理** · 13 endpoints

创建、配置、清理 bank；consolidation、LLM 探测、统计等控制面。

### 本章目录

| Method | Path | 标题 |
| --- | --- | --- |
| `GET` | `/v1/default/banks` | [列出 Banks](#list-banks) |
| `PUT` | `/v1/default/banks/{bank_id}` | [创建或更新 Bank](#create-or-update-bank) |
| `PATCH` | `/v1/default/banks/{bank_id}` | [更新 Bank](#update-bank) |
| `DELETE` | `/v1/default/banks/{bank_id}` | [删除 Bank](#delete-bank) |
| `GET` | `/v1/default/banks/{bank_id}/config` | [获取 Bank 配置](#get-bank-config) |
| `PATCH` | `/v1/default/banks/{bank_id}/config` | [更新 Bank 配置](#update-bank-config) |
| `DELETE` | `/v1/default/banks/{bank_id}/config` | [重置 Bank 配置](#reset-bank-config) |
| `POST` | `/v1/default/banks/{bank_id}/consolidate` | [触发 Consolidation](#trigger-consolidation) |
| `POST` | `/v1/default/banks/{bank_id}/consolidation/recover` | [恢复 Consolidation](#recover-consolidation) |
| `POST` | `/v1/default/banks/{bank_id}/health/llm` | [测试 Bank LLM](#test-bank-llm) |
| `DELETE` | `/v1/default/banks/{bank_id}/observations` | [清除 Observations](#clear-observations) |
| `GET` | `/v1/default/banks/{bank_id}/stats` | [Agent 统计](#get-agent-stats) |
| `GET` | `/v1/default/banks/{bank_id}/stats/memories-timeseries` | [记忆时序统计](#get-memories-timeseries) |

### 列出 Banks
<a id="list-banks"></a>

**GET** `/v1/default/banks`

*List all memory banks*

Get a list of all agents with their profiles

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `banks` | `array<BankListItem>` | 是 |  |

<details open><summary><strong>banks[]</strong> · <code>BankListItem</code></summary>

数据结构 `BankListItem`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `bank_id` | `string` | 是 |  |
| `name` | `string?` | 否 |  |
| `disposition` | `DispositionTraits` | 是 |  |
| `mission` | `string?` | 否 |  |
| `created_at` | `string?` | 否 |  |
| `updated_at` | `string?` | 否 |  |
| `fact_count` | `integer` | 否 | 默认 `0` |
| `last_document_at` | `string?` | 否 | When a document was last *ingested* into this bank. Appending to an existing document does not move this — use `last_write_at` for write activity. |
| `last_write_at` | `string?` | 否 | When anything was last written to this bank: a document retained (including appends to an existing document) or a fact stored. Null if the bank is empty. |

<details open><summary><strong>disposition</strong> · <code>DispositionTraits</code></summary>

数据结构 `DispositionTraits`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `skepticism` | `integer` | 是 | How skeptical vs trusting (1=trusting, 5=skeptical) · ≥ `1.0` · ≤ `5.0` |
| `literalism` | `integer` | 是 | How literally to interpret information (1=flexible, 5=literal) · ≥ `1.0` · ≤ `5.0` |
| `empathy` | `integer` | 是 | How much to consider emotional context (1=detached, 5=empathetic) · ≥ `1.0` · ≤ `5.0` |

</details>

</details>

#### 响应示例

```json
{
  "banks": [
    {
      "bank_id": "user123",
      "created_at": "2024-01-15T10:30:00Z",
      "disposition": {
        "empathy": 3,
        "literalism": 3,
        "skepticism": 3
      },
      "fact_count": 156,
      "last_document_at": "2024-01-16T14:20:00Z",
      "last_write_at": "2024-01-17T09:05:00Z",
      "mission": "I am a software engineer helping my team ship quality code",
      "name": "Alice",
      "updated_at": "2024-01-16T14:20:00Z"
    }
  ]
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=list_banks`

---

### 创建或更新 Bank
<a id="create-or-update-bank"></a>

**PUT** `/v1/default/banks/{bank_id}`

*Create or update memory bank*

Create a new agent or update existing agent with disposition and mission. Auto-fills missing fields with defaults.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | `string?` | 否 | Deprecated: display label only, not advertised |
| `disposition` | `DispositionTraits?` | 否 | Deprecated: use update_bank_config instead |
| `disposition_skepticism` | `integer?` | 否 | Deprecated: use update_bank_config instead · ≥ `1.0` · ≤ `5.0` |
| `disposition_literalism` | `integer?` | 否 | Deprecated: use update_bank_config instead · ≥ `1.0` · ≤ `5.0` |
| `disposition_empathy` | `integer?` | 否 | Deprecated: use update_bank_config instead · ≥ `1.0` · ≤ `5.0` |
| `mission` | `string?` | 否 | Deprecated: use update_bank_config with reflect_mission instead |
| `background` | `string?` | 否 | Deprecated: use update_bank_config with reflect_mission instead |
| `reflect_mission` | `string?` | 否 | Mission/context for Reflect operations. Guides how Reflect interprets and uses memories. |
| `retain_mission` | `string?` | 否 | Steers what gets extracted during retain(). Injected alongside built-in extraction rules. |
| `retain_extraction_mode` | `string?` | 否 | Fact extraction mode: 'concise' (default), 'verbose', 'custom', 'verbatim', or 'chunks'. |
| `retain_custom_instructions` | `string?` | 否 | Custom extraction prompt. Only active when retain_extraction_mode is 'custom'. |
| `retain_chunk_size` | `integer?` | 否 | Target maximum characters for each content chunk during retain. |
| `retain_structured_chunk_size` | `integer?` | 否 | Maximum characters for a single JSONL line or conversation turn to keep whole during retain. Defaults to retain_chunk_size when unset. |
| `enable_observations` | `boolean?` | 否 | Toggle automatic observation consolidation after retain(). |
| `observations_mission` | `string?` | 否 | Controls what gets synthesised into observations. Replaces built-in consolidation rules entirely. |
| `enable_temporal_retrieval` | `boolean?` | 否 | Toggle the temporal retrieval arm during recall, together with the date-aware query analysis that feeds it. Useful for banks whose content carries no meaningful dates. |
| `enable_graph_retrieval` | `boolean?` | 否 | Toggle the entity/link graph traversal arm during recall. Disabling trades relational recall for latency on banks whose content has little entity structure. |
| `enable_reranking` | `boolean?` | 否 | Toggle cross-encoder reranking during recall. Disabling returns the RRF-fused ordering directly, which is faster but less precise. |

<details open><summary><strong>disposition</strong> · <code>DispositionTraits</code></summary>

数据结构 `DispositionTraits`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `skepticism` | `integer` | 是 | How skeptical vs trusting (1=trusting, 5=skeptical) · ≥ `1.0` · ≤ `5.0` |
| `literalism` | `integer` | 是 | How literally to interpret information (1=flexible, 5=literal) · ≥ `1.0` · ≤ `5.0` |
| `empathy` | `integer` | 是 | How much to consider emotional context (1=detached, 5=empathetic) · ≥ `1.0` · ≤ `5.0` |

</details>

#### 请求示例

```json
{
  "observations_mission": "Observations are stable facts about people and projects. Always include preferences and skills.",
  "retain_mission": "Always include technical decisions and architectural trade-offs. Ignore meeting logistics."
}
```

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `bank_id` | `string` | 是 |  |
| `name` | `string` | 是 |  |
| `disposition` | `DispositionTraits` | 是 |  |
| `mission` | `string` | 是 | The agent's mission - who they are and what they're trying to accomplish |
| `background` | `string?` | 否 | Deprecated: use mission instead |

<details open><summary><strong>disposition</strong> · <code>DispositionTraits</code></summary>

数据结构 `DispositionTraits`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `skepticism` | `integer` | 是 | How skeptical vs trusting (1=trusting, 5=skeptical) · ≥ `1.0` · ≤ `5.0` |
| `literalism` | `integer` | 是 | How literally to interpret information (1=flexible, 5=literal) · ≥ `1.0` · ≤ `5.0` |
| `empathy` | `integer` | 是 | How much to consider emotional context (1=detached, 5=empathetic) · ≥ `1.0` · ≤ `5.0` |

</details>

#### 响应示例

```json
{
  "bank_id": "user123",
  "disposition": {
    "empathy": 3,
    "literalism": 3,
    "skepticism": 3
  },
  "mission": "I am a software engineer helping my team stay organized and ship quality code",
  "name": "Alice"
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=create_or_update_bank`

---

### 更新 Bank
<a id="update-bank"></a>

**PATCH** `/v1/default/banks/{bank_id}`

*Partial update memory bank*

Partially update an agent's profile. Only provided fields will be updated.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | `string?` | 否 | Deprecated: display label only, not advertised |
| `disposition` | `DispositionTraits?` | 否 | Deprecated: use update_bank_config instead |
| `disposition_skepticism` | `integer?` | 否 | Deprecated: use update_bank_config instead · ≥ `1.0` · ≤ `5.0` |
| `disposition_literalism` | `integer?` | 否 | Deprecated: use update_bank_config instead · ≥ `1.0` · ≤ `5.0` |
| `disposition_empathy` | `integer?` | 否 | Deprecated: use update_bank_config instead · ≥ `1.0` · ≤ `5.0` |
| `mission` | `string?` | 否 | Deprecated: use update_bank_config with reflect_mission instead |
| `background` | `string?` | 否 | Deprecated: use update_bank_config with reflect_mission instead |
| `reflect_mission` | `string?` | 否 | Mission/context for Reflect operations. Guides how Reflect interprets and uses memories. |
| `retain_mission` | `string?` | 否 | Steers what gets extracted during retain(). Injected alongside built-in extraction rules. |
| `retain_extraction_mode` | `string?` | 否 | Fact extraction mode: 'concise' (default), 'verbose', 'custom', 'verbatim', or 'chunks'. |
| `retain_custom_instructions` | `string?` | 否 | Custom extraction prompt. Only active when retain_extraction_mode is 'custom'. |
| `retain_chunk_size` | `integer?` | 否 | Target maximum characters for each content chunk during retain. |
| `retain_structured_chunk_size` | `integer?` | 否 | Maximum characters for a single JSONL line or conversation turn to keep whole during retain. Defaults to retain_chunk_size when unset. |
| `enable_observations` | `boolean?` | 否 | Toggle automatic observation consolidation after retain(). |
| `observations_mission` | `string?` | 否 | Controls what gets synthesised into observations. Replaces built-in consolidation rules entirely. |
| `enable_temporal_retrieval` | `boolean?` | 否 | Toggle the temporal retrieval arm during recall, together with the date-aware query analysis that feeds it. Useful for banks whose content carries no meaningful dates. |
| `enable_graph_retrieval` | `boolean?` | 否 | Toggle the entity/link graph traversal arm during recall. Disabling trades relational recall for latency on banks whose content has little entity structure. |
| `enable_reranking` | `boolean?` | 否 | Toggle cross-encoder reranking during recall. Disabling returns the RRF-fused ordering directly, which is faster but less precise. |

<details open><summary><strong>disposition</strong> · <code>DispositionTraits</code></summary>

数据结构 `DispositionTraits`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `skepticism` | `integer` | 是 | How skeptical vs trusting (1=trusting, 5=skeptical) · ≥ `1.0` · ≤ `5.0` |
| `literalism` | `integer` | 是 | How literally to interpret information (1=flexible, 5=literal) · ≥ `1.0` · ≤ `5.0` |
| `empathy` | `integer` | 是 | How much to consider emotional context (1=detached, 5=empathetic) · ≥ `1.0` · ≤ `5.0` |

</details>

#### 请求示例

```json
{
  "observations_mission": "Observations are stable facts about people and projects. Always include preferences and skills.",
  "retain_mission": "Always include technical decisions and architectural trade-offs. Ignore meeting logistics."
}
```

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `bank_id` | `string` | 是 |  |
| `name` | `string` | 是 |  |
| `disposition` | `DispositionTraits` | 是 |  |
| `mission` | `string` | 是 | The agent's mission - who they are and what they're trying to accomplish |
| `background` | `string?` | 否 | Deprecated: use mission instead |

<details open><summary><strong>disposition</strong> · <code>DispositionTraits</code></summary>

数据结构 `DispositionTraits`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `skepticism` | `integer` | 是 | How skeptical vs trusting (1=trusting, 5=skeptical) · ≥ `1.0` · ≤ `5.0` |
| `literalism` | `integer` | 是 | How literally to interpret information (1=flexible, 5=literal) · ≥ `1.0` · ≤ `5.0` |
| `empathy` | `integer` | 是 | How much to consider emotional context (1=detached, 5=empathetic) · ≥ `1.0` · ≤ `5.0` |

</details>

#### 响应示例

```json
{
  "bank_id": "user123",
  "disposition": {
    "empathy": 3,
    "literalism": 3,
    "skepticism": 3
  },
  "mission": "I am a software engineer helping my team stay organized and ship quality code",
  "name": "Alice"
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=update_bank`

---

### 删除 Bank
<a id="delete-bank"></a>

**DELETE** `/v1/default/banks/{bank_id}`

*Delete memory bank*

Delete an entire memory bank including all memories, entities, documents, and the bank profile itself. This is a destructive operation that cannot be undone.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `success` | `boolean` | 是 |  |
| `message` | `string?` | 否 |  |
| `deleted_count` | `integer?` | 否 |  |

#### 响应示例

```json
{
  "deleted_count": 10,
  "message": "Deleted successfully",
  "success": true
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=delete_bank`

---

### 获取 Bank 配置
<a id="get-bank-config"></a>

**GET** `/v1/default/banks/{bank_id}/config`

*Get bank configuration*

Get fully resolved configuration for a bank including all hierarchical overrides (global → tenant → bank). The 'config' field contains all resolved config values. The 'overrides' field shows only bank-specific overrides.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `bank_id` | `string` | 是 | Bank identifier |
| `config` | `object` | 是 | Fully resolved configuration with all hierarchical overrides applied (Python field names) |
| `overrides` | `object` | 是 | Bank-specific configuration overrides only (Python field names) |

#### 响应示例

```json
{
  "bank_id": "my-bank",
  "config": {
    "retain_chunk_size": 3000,
    "retain_extraction_mode": "verbose"
  },
  "overrides": {
    "retain_extraction_mode": "verbose"
  }
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=get_bank_config`

---

### 更新 Bank 配置
<a id="update-bank-config"></a>

**PATCH** `/v1/default/banks/{bank_id}/config`

*Update bank configuration*

Update configuration overrides for a bank. Only hierarchical behavioral settings can be overridden (retention parameters, recall settings, etc.). Keys can be provided in Python field format (retain_extraction_mode) or environment variable format (HINDSIGHT_API_RETAIN_EXTRACTION_MODE).

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `updates` | `object` | 是 | Configuration overrides. Keys can be in Python field format (retain_extraction_mode) or environment variable format (HINDSIGHT_API_RETAIN_EXTRACTION_MODE). Only hierarchical fields can be overridden per-bank. |

#### 请求示例

```json
{
  "updates": {
    "retain_custom_instructions": "Extract technical details carefully",
    "retain_extraction_mode": "custom"
  }
}
```

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `bank_id` | `string` | 是 | Bank identifier |
| `config` | `object` | 是 | Fully resolved configuration with all hierarchical overrides applied (Python field names) |
| `overrides` | `object` | 是 | Bank-specific configuration overrides only (Python field names) |

#### 响应示例

```json
{
  "bank_id": "my-bank",
  "config": {
    "retain_chunk_size": 3000,
    "retain_extraction_mode": "verbose"
  },
  "overrides": {
    "retain_extraction_mode": "verbose"
  }
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=update_bank_config`

---

### 重置 Bank 配置
<a id="reset-bank-config"></a>

**DELETE** `/v1/default/banks/{bank_id}/config`

*Reset bank configuration*

Reset bank configuration to defaults by removing all bank-specific overrides. The bank will then use global and tenant-level configuration only.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `bank_id` | `string` | 是 | Bank identifier |
| `config` | `object` | 是 | Fully resolved configuration with all hierarchical overrides applied (Python field names) |
| `overrides` | `object` | 是 | Bank-specific configuration overrides only (Python field names) |

#### 响应示例

```json
{
  "bank_id": "my-bank",
  "config": {
    "retain_chunk_size": 3000,
    "retain_extraction_mode": "verbose"
  },
  "overrides": {
    "retain_extraction_mode": "verbose"
  }
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=reset_bank_config`

---

### 触发 Consolidation
<a id="trigger-consolidation"></a>

**POST** `/v1/default/banks/{bank_id}/consolidate`

*Trigger consolidation*

Run memory consolidation to create/update observations from recent memories.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**否**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `observation_scopes` | `array<array<string>>?` | 否 | Optional list of tag scopes to consolidate. Each scope is a list of tags. Only unconsolidated memories whose tags contain all tags in at least one scope will be processed. If omitted, all unconsolidated memories are processed. |

#### 请求示例

```json
{
  "observation_scopes": [
    [
      "string"
    ]
  ]
}
```

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `operation_id` | `string` | 是 | ID of the async consolidation operation |
| `deduplicated` | `boolean` | 否 | True if an existing pending task was reused · 默认 `false` |

#### 响应示例

```json
{
  "operation_id": "string",
  "deduplicated": false
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=trigger_consolidation`

---

### 恢复 Consolidation
<a id="recover-consolidation"></a>

**POST** `/v1/default/banks/{bank_id}/consolidation/recover`

*Recover failed consolidation*

Reset all memories that were permanently marked as failed during consolidation (after exhausting all LLM retries and adaptive batch splitting) so they are picked up again on the next consolidation run. Does not delete any observations.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `retried_count` | `integer` | 是 |  |

#### 响应示例

```json
{
  "retried_count": 42
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=recover_consolidation`

---

### 测试 Bank LLM
<a id="test-bank-llm"></a>

**POST** `/v1/default/banks/{bank_id}/health/llm`

*Test the bank's LLM connectivity*

Probe the LLMs this bank would use for retain / consolidation / reflect with one minimal call each (configs shared across operations are probed once), so you can discover 'not configured / unreachable' instead of a silent stall. Deliberate action (makes a real provider call); not for polling. Returns status only — never the provider, model, endpoint, API key, or raw error. Disable with HINDSIGHT_API_ENABLE_BANK_LLM_HEALTH=false.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `bank_id` | `string` | 是 | Bank identifier |
| `operations` | `array<LlmOperationHealth>` | 是 | Connectivity status per operation (retain, consolidation, reflect) |

<details open><summary><strong>operations[]</strong> · <code>LlmOperationHealth</code></summary>

数据结构 `LlmOperationHealth`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `operation` | `"retain" \| "consolidation" \| "reflect"` | 是 | Operation whose LLM was probed |
| `ok` | `boolean` | 是 | True only when the probe connected successfully |
| `status` | `"connected" \| "not_configured" \| "auth_failed" \| "unreachable" \| "timeout"` | 是 | 'connected'; 'not_configured' (provider is 'none'); 'auth_failed' (rejected — usually a wrong/expired API key); 'unreachable' (call failed); 'timeout' |
| `latency_ms` | `number?` | 否 | Round-trip latency of the probe call |

</details>

#### 响应示例

```json
{
  "bank_id": "user123",
  "operations": [
    {
      "latency_ms": 412.0,
      "ok": true,
      "operation": "retain",
      "status": "connected"
    },
    {
      "latency_ms": 412.0,
      "ok": true,
      "operation": "consolidation",
      "status": "connected"
    },
    {
      "ok": false,
      "operation": "reflect",
      "status": "not_configured"
    }
  ]
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=test_bank_llm`

---

### 清除 Observations
<a id="clear-observations"></a>

**DELETE** `/v1/default/banks/{bank_id}/observations`

*Clear all observations*

Delete all observations for a memory bank. This is useful for resetting the consolidated knowledge.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `success` | `boolean` | 是 |  |
| `message` | `string?` | 否 |  |
| `deleted_count` | `integer?` | 否 |  |

#### 响应示例

```json
{
  "deleted_count": 10,
  "message": "Deleted successfully",
  "success": true
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=clear_observations`

---

### Agent 统计
<a id="get-agent-stats"></a>

**GET** `/v1/default/banks/{bank_id}/stats`

*Get statistics for memory bank*

Get statistics about nodes and links for a specific agent

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `refresh` | query | `boolean` | 否 | Force a fresh recompute, bypassing the cached value (and refreshing the cache). · 默认 `false` |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `bank_id` | `string` | 是 |  |
| `total_nodes` | `integer` | 是 |  |
| `total_links` | `integer` | 是 |  |
| `total_documents` | `integer` | 是 |  |
| `nodes_by_fact_type` | `map<string, integer>` | 是 |  |
| `links_by_link_type` | `map<string, integer>` | 是 |  |
| `links_by_fact_type` | `map<string, integer>` | 是 |  |
| `links_breakdown` | `map<string, map<string, integer>>` | 是 |  |
| `pending_operations` | `integer` | 是 |  |
| `failed_operations` | `integer` | 是 |  |
| `operations_by_status` | `map<string, integer>` | 否 | Async operations grouped by status (pending, processing, completed, failed, cancelled). |
| `last_consolidated_at` | `string?` | 否 | When consolidation last ran (ISO format) |
| `last_memory_write_at` | `string?` | 否 | When a memory was last written in this bank — stored, edited, or consolidated (ISO format). Null if the bank has no memories. A mental model whose `last_refreshed_at` is at or after this is up to date whatever its tags; an older one may need a refresh, which only the single mental-model read can confirm. |
| `pending_consolidation` | `integer` | 否 | Number of source memories (world/experience) still queued for consolidation into observations. Excludes memories whose consolidation permanently failed — those are counted only in failed_consolidation — so this drains to 0 when the consolidator catches up. · 默认 `0` |
| `failed_consolidation` | `integer` | 否 | Number of source memories (world/experience) whose consolidation permanently failed and can be retried via the consolidation recovery endpoint. · 默认 `0` |
| `total_observations` | `integer` | 否 | Total number of observations · 默认 `0` |

#### 响应示例

```json
{
  "bank_id": "user123",
  "failed_consolidation": 0,
  "failed_operations": 0,
  "last_consolidated_at": "2024-01-15T10:30:00Z",
  "last_memory_write_at": "2024-01-15T11:05:00Z",
  "links_breakdown": {
    "fact": {
      "entity": 40,
      "semantic": 60,
      "temporal": 100
    }
  },
  "links_by_fact_type": {
    "fact": 200,
    "observation": 40,
    "preference": 60
  },
  "links_by_link_type": {
    "entity": 50,
    "semantic": 100,
    "temporal": 150
  },
  "nodes_by_fact_type": {
    "fact": 100,
    "observation": 20,
    "preference": 30
  },
  "pending_consolidation": 0,
  "pending_operations": 2,
  "total_documents": 10,
  "total_links": 300,
  "total_nodes": 150,
  "total_observations": 45
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=get_agent_stats`

---

### 记忆时序统计
<a id="get-memories-timeseries"></a>

**GET** `/v1/default/banks/{bank_id}/stats/memories-timeseries`

*Memory ingestion time-series*

Memories ingested over a period, bucketed by time and broken down by fact type.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `period` | query | `string` | 否 | 默认 `"7d"` |
| `time_field` | query | `string` | 否 | Timestamp column to bucket on. `created_at` (default) = ingest time; `mentioned_at` / `occurred_start` = event time, useful for migrated corpora where ingest time is a single point and doesn't reflect the underlying knowledge timeline. Unknown values fall back to `created_at`. · 默认 `"created_at"` |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `bank_id` | `string` | 是 |  |
| `period` | `string` | 是 | One of: 1h, 12h, 1d, 7d, 30d, 90d. |
| `trunc` | `string` | 是 | Bucket granularity: minute, hour, day. |
| `time_field` | `string` | 否 | Timestamp column used to assign each row to a bucket. `created_at` shows ingest time; `mentioned_at` / `occurred_start` show event time (falls back to `created_at` per row when null). · 默认 `"created_at"` |
| `buckets` | `array<MemoryTimeseriesBucket>` | 否 | Per-bucket counts, always returned fully padded for the requested period. |

<details open><summary><strong>buckets[]</strong> · <code>MemoryTimeseriesBucket</code></summary>

数据结构 `MemoryTimeseriesBucket`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `time` | `string` | 是 | Bucket start timestamp in ISO-8601 (UTC). |
| `world` | `integer` | 否 | World-fact memories ingested in this bucket. · 默认 `0` |
| `experience` | `integer` | 否 | Experience memories ingested in this bucket. · 默认 `0` |
| `observation` | `integer` | 否 | Observations recorded in this bucket. · 默认 `0` |

</details>

#### 响应示例

```json
{
  "bank_id": "string",
  "period": "string",
  "trunc": "string",
  "time_field": "created_at",
  "buckets": [
    {
      "time": "string",
      "world": 0,
      "experience": 0,
      "observation": 0
    }
  ]
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=get_memories_timeseries`

---

## Bank Templates
<a id="bank-templates"></a>

**Bank 模板** · 3 endpoints

bank 模板 schema / 导入导出，便于环境间复用配置。

### 本章目录

| Method | Path | 标题 |
| --- | --- | --- |
| `GET` | `/v1/bank-template-schema` | [Get bank template JSON Schema](#get-bank-template-schema) |
| `GET` | `/v1/default/banks/{bank_id}/export` | [Export bank template](#export-bank-template) |
| `POST` | `/v1/default/banks/{bank_id}/import` | [Import bank template](#import-bank-template) |

### Get bank template JSON Schema
<a id="get-bank-template-schema"></a>

**GET** `/v1/bank-template-schema`

Returns the JSON Schema for the bank template manifest format. Use this to validate template manifests before importing.

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

_无展开字段（标量、自由 object 或未声明 properties）_

`operationId=get_bank_template_schema`

---

### Export bank template
<a id="export-bank-template"></a>

**GET** `/v1/default/banks/{bank_id}/export`

Export a bank's current configuration, mental models, and directives as a template manifest. The exported manifest can be imported into another bank to replicate the setup.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `version` | `string` | 是 | Manifest schema version (currently '1') |
| `bank` | `BankTemplateConfig?` | 否 | Bank configuration to apply. Omit to leave config unchanged. |
| `mental_models` | `array<BankTemplateMentalModel>?` | 否 | Mental models to create or update (matched by id). Omit to leave unchanged. |
| `directives` | `array<BankTemplateDirective>?` | 否 | Directives to create or update (matched by name). Omit to leave unchanged. |

<details open><summary><strong>bank</strong> · <code>BankTemplateConfig</code></summary>

数据结构 `BankTemplateConfig`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `reflect_mission` | `string?` | 否 | Mission/context for Reflect operations |
| `retain_mission` | `string?` | 否 | Steers what gets extracted during retain |
| `retain_extraction_mode` | `string?` | 否 | Fact extraction mode: 'concise' (default), 'verbose', 'custom', 'verbatim', or 'chunks' |
| `retain_custom_instructions` | `string?` | 否 | Custom extraction prompt (when mode='custom') |
| `retain_chunk_size` | `integer?` | 否 | Target max characters for each content chunk |
| `retain_structured_chunk_size` | `integer?` | 否 | Max characters for a single JSONL line or conversation turn to keep whole; defaults to retain_chunk_size when unset |
| `enable_observations` | `boolean?` | 否 | Toggle observation consolidation |
| `observations_mission` | `string?` | 否 | Controls what gets synthesised |
| `enable_temporal_retrieval` | `boolean?` | 否 | Toggle the temporal arm (and its date-aware query analysis) during recall |
| `enable_graph_retrieval` | `boolean?` | 否 | Toggle the entity/link graph arm during recall |
| `enable_reranking` | `boolean?` | 否 | Toggle cross-encoder reranking during recall |
| `disposition_skepticism` | `integer?` | 否 | Skepticism trait (1-5) · ≥ `1.0` · ≤ `5.0` |
| `disposition_literalism` | `integer?` | 否 | Literalism trait (1-5) · ≥ `1.0` · ≤ `5.0` |
| `disposition_empathy` | `integer?` | 否 | Empathy trait (1-5) · ≥ `1.0` · ≤ `5.0` |
| `entity_labels` | `array<LabelGroup-Output>?` | 否 | Controlled vocabulary for entity labels |
| `entities_allow_free_form` | `boolean?` | 否 | Allow entities outside the label vocabulary |
| `retain_default_strategy` | `string?` | 否 | Name of the default retain strategy (key into retain_strategies map) |
| `retain_strategies` | `object?` | 否 | Map of retain strategy name to per-strategy config dict |
| `retain_chunk_batch_size` | `integer?` | 否 | Max chunks per streaming batch (0 disables batching) |
| `mcp_enabled_tools` | `array<string>?` | 否 | MCP tool allowlist for this bank (None = all tools) |
| `consolidation_llm_batch_size` | `integer?` | 否 | LLM batch size for observation consolidation |
| `consolidation_source_facts_max_tokens` | `integer?` | 否 | Max tokens of source facts per consolidation batch |
| `consolidation_source_facts_max_tokens_per_observation` | `integer?` | 否 | Max tokens of source facts per observation |
| `max_observations_per_scope` | `integer?` | 否 | Max observations to retain per consolidation scope |
| `observation_scope_limits` | `array<object>?` | 否 | Per-scope overrides of max_observations_per_scope: [{"scope": ["run_*", "shared"], "limit": 1}]. Each scope is a list of fnmatch tag-globs; a consolidation scope matches under exact cover (every tag matched by a glob and every glob matched by a tag). The first matching rule wins; unmatched scopes fall back to max_observations_per_scope. |
| `reflect_source_facts_max_tokens` | `integer?` | 否 | Max tokens of source facts per reflect call |
| `llm_gemini_safety_settings` | `array<any>?` | 否 | Per-bank Gemini/VertexAI safety filter settings |
| `recall_budget_function` | `string?` | 否 | Recall budget mapping function: 'fixed' or 'adaptive' |
| `recall_budget_fixed_low` | `integer?` | 否 | Fixed thinking_budget for budget=low (function='fixed') |
| `recall_budget_fixed_mid` | `integer?` | 否 | Fixed thinking_budget for budget=mid (function='fixed') |
| `recall_budget_fixed_high` | `integer?` | 否 | Fixed thinking_budget for budget=high (function='fixed') |
| `recall_budget_adaptive_low` | `number?` | 否 | Ratio of max_tokens for budget=low (function='adaptive') |
| `recall_budget_adaptive_mid` | `number?` | 否 | Ratio of max_tokens for budget=mid (function='adaptive') |
| `recall_budget_adaptive_high` | `number?` | 否 | Ratio of max_tokens for budget=high (function='adaptive') |
| `recall_budget_min` | `integer?` | 否 | Floor for the adaptive function (after clamping) |
| `recall_budget_max` | `integer?` | 否 | Ceiling for the adaptive function (after clamping) |
| `audit_log_enabled` | `boolean?` | 否 | Enable audit logging for this bank (overrides the server default) |
| `store_document_text` | `boolean?` | 否 | Persist raw source text (documents.original_text / chunks.chunk_text). Set false to keep only derived facts. |
| `enable_auto_consolidation` | `boolean?` | 否 | Automatically consolidate observations after retain |
| `consolidation_max_memories_per_round` | `integer?` | 否 | Max memory units fed into a single consolidation round |
| `consolidation_llm_parallelism` | `integer?` | 否 | Number of consolidation LLM batches processed concurrently |
| `recall_include_chunks` | `boolean?` | 否 | Include raw chunks in recall results |
| `recall_max_tokens` | `integer?` | 否 | Max tokens of results returned by recall |
| `recall_chunks_max_tokens` | `integer?` | 否 | Max tokens of raw chunks returned by recall (when recall_include_chunks is set) |
| `memory_defense` | `object?` | 否 | Memory Defense policy for this bank (validated against the DefensePolicy schema on write) |

<details open><summary><strong>entity_labels[]</strong> · <code>LabelGroup-Output</code></summary>

数据结构 `LabelGroup-Output`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `key` | `string` | 是 |  |
| `description` | `string` | 否 | 默认 `""` |
| `type` | `"value" \| "multi-values" \| "text" \| "map"` | 否 | 默认 `"value"` |
| `optional` | `boolean` | 否 | 默认 `true` |
| `tag` | `boolean` | 否 | 默认 `false` |
| `values` | `array<LabelValue>` | 否 | 默认 `[]` |
| `fields` | `map<string, MapField-Output>` | 否 | 默认 `{}` |

<details open><summary><strong>values[]</strong> · <code>LabelValue</code></summary>

数据结构 `LabelValue`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `value` | `string` | 是 |  |
| `description` | `string` | 否 | 默认 `""` |

</details>

</details>

</details>

<details open><summary><strong>mental_models[]</strong> · <code>BankTemplateMentalModel</code></summary>

数据结构 `BankTemplateMentalModel`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 | Unique ID for the mental model (alphanumeric lowercase with hyphens) |
| `name` | `string` | 是 | Human-readable name for the mental model |
| `source_query` | `string` | 是 | The query to run to generate content |
| `tags` | `array<string>` | 否 | Tags for scoped visibility · 默认 `[]` |
| `max_tokens` | `integer` | 否 | Maximum tokens for generated content · 默认 `2048` · ≥ `256.0` · ≤ `8192.0` |
| `trigger` | `MentalModelTrigger-Output` | 否 | Trigger settings · 默认 `{}` |

<details open><summary><strong>trigger</strong> · <code>MentalModelTrigger-Output</code></summary>

数据结构 `MentalModelTrigger-Output`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `mode` | `"full" \| "delta"` | 否 | Refresh mode. 'full' (default) regenerates the mental model content from scratch on each refresh. 'delta' performs surgical edits against the existing content: unchanged sections are preserved byte-for-byte, stale content is removed, new content is added. If the mental model has no existing content, or if the source_query has changed since the last refresh, delta mode falls back to a full regeneration automatically. · 默认 `"full"` |
| `refresh_after_consolidation` | `boolean` | 否 | If true, refresh this mental model after observations consolidation (real-time mode) · 默认 `false` |
| `refresh_cron` | `string?` | 否 | Cron expression (UTC, standard 5-field syntax, e.g. '0 3 * * *' for daily at 03:00 UTC) for refreshing this mental model on a fixed schedule. Mutually exclusive with refresh_after_consolidation — a model refreshes either after consolidation or on a cron schedule, not both. A scheduled refresh only runs when the model is stale (new memories in its scope since the last refresh); if nothing changed, the tick is skipped to avoid a wasted LLM call. null = no schedule. |
| `fact_types` | `array<"world" \| "experience" \| "observation">?` | 否 | Filter which fact types are retrieved during reflect. None means all types (world, experience, observation). |
| `exclude_mental_models` | `boolean` | 否 | If true, exclude all mental models from the reflect loop (skip search_mental_models tool). · 默认 `false` |
| `exclude_mental_model_ids` | `array<string>?` | 否 | Exclude specific mental models by ID from the reflect loop. |
| `tags_match` | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"?` | 否 | Override how the model's tags filter memories during refresh. If not set, defaults to 'all_strict' when the model has tags (security isolation) or 'any' when the model has no tags. Set to 'any' to include untagged memories alongside tagged ones during refresh. |
| `tag_groups` | `array<TagGroupLeaf \| TagGroupAnd-Output \| TagGroupOr-Output \| TagGroupNot-Output>?` | 否 | Compound boolean tag expressions to use during refresh instead of the model's own tags. When set, these tag groups are passed to reflect and the model's flat tags are NOT used for filtering. Supports nested and/or/not expressions for complex tag-based scoping. |
| `include_chunks` | `boolean?` | 否 | Override whether the internal recall used during refresh returns raw chunk text. None means use the bank/global config default (recall_include_chunks). |
| `recall_max_tokens` | `integer?` | 否 | Override the token budget for facts returned by the internal recall during refresh. None means use the bank/global config default (recall_max_tokens). |
| `recall_chunks_max_tokens` | `integer?` | 否 | Override the token budget for raw chunks returned by the internal recall during refresh. None means use the bank/global config default (recall_chunks_max_tokens). |
| `response_schema` | `object?` | 否 | Optional JSON Schema for structured output. When set, each refresh runs the same structured-output extraction as reflect's response_schema and stores the parsed result under reflect_response.structured_output alongside the markdown content. |
| `keep_trace` | `boolean` | 否 | If true, every refresh of this mental model records how it reached its result under reflect_response.trace: the mode it ran in and why, the resolved scope and time window, how many facts retrieval returned versus how many the agent used, the tool and LLM calls, and any delta operations. Only the latest refresh's trace is kept. This is the only way to diagnose a cron- or consolidation-driven refresh after the fact, since no human sees those run. Tool outputs are reduced to result counts to keep the stored trace bounded; use LLM request tracing for raw prompts and responses. · 默认 `false` |

</details>

</details>

<details open><summary><strong>directives[]</strong> · <code>BankTemplateDirective</code></summary>

数据结构 `BankTemplateDirective`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | `string` | 是 | Human-readable name for the directive (used as match key on re-import) |
| `content` | `string` | 是 | The directive text to inject into prompts |
| `priority` | `integer` | 否 | Higher priority directives are injected first · 默认 `0` |
| `is_active` | `boolean` | 否 | Whether this directive is active · 默认 `true` |
| `tags` | `array<string>` | 否 | Tags for filtering · 默认 `[]` |

</details>

#### 响应示例

```json
{
  "bank": {
    "disposition_empathy": 5,
    "enable_observations": true,
    "reflect_mission": "You are helping a support agent remember customer interactions.",
    "retain_mission": "Extract customer issues, resolutions, and sentiment."
  },
  "directives": [
    {
      "content": "Always respond with empathy and understanding.",
      "name": "Always be empathetic",
      "priority": 10
    }
  ],
  "mental_models": [
    {
      "id": "sentiment-overview",
      "name": "Customer Sentiment Overview",
      "source_query": "What is the overall sentiment trend?",
      "trigger": {
        "refresh_after_consolidation": true
      }
    }
  ],
  "version": "1"
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=export_bank_template`

---

### Import bank template
<a id="import-bank-template"></a>

**POST** `/v1/default/banks/{bank_id}/import`

Import a bank template manifest to create or update a bank's configuration, mental models, and directives. If the bank does not exist it is created. Config fields are applied as per-bank overrides. Mental models are matched by id, directives by name — existing ones are updated, new ones are created. Use dry_run=true to validate the manifest without applying changes.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `dry_run` | query | `boolean` | 否 | Validate only, do not apply changes · 默认 `false` |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `bank_id` | `string` | 是 | Bank that was imported into |
| `config_applied` | `boolean` | 是 | Whether bank config was updated |
| `mental_models_created` | `array<string>` | 否 | IDs of newly created mental models · 默认 `[]` |
| `mental_models_updated` | `array<string>` | 否 | IDs of updated mental models · 默认 `[]` |
| `directives_created` | `array<string>` | 否 | Names of newly created directives · 默认 `[]` |
| `directives_updated` | `array<string>` | 否 | Names of updated directives · 默认 `[]` |
| `operation_ids` | `array<string>` | 否 | Operation IDs for mental model content generation (async) · 默认 `[]` |
| `dry_run` | `boolean` | 否 | True if this was a validation-only run · 默认 `false` |

#### 响应示例

```json
{
  "bank_id": "string",
  "config_applied": false,
  "mental_models_created": [],
  "mental_models_updated": [],
  "directives_created": [],
  "directives_updated": [],
  "operation_ids": [],
  "dry_run": false
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=import_bank_template`

---

## Memory
<a id="memory"></a>

**记忆（Retain / Recall / Reflect）** · 13 endpoints

主路径 retain → recall → reflect，以及 list/get/update/clear。

### 本章目录

| Method | Path | 标题 |
| --- | --- | --- |
| `GET` | `/v1/default/banks/{bank_id}/graph` | [获取记忆图](#get-graph) |
| `POST` | `/v1/default/banks/{bank_id}/memories` | [写入记忆（Retain）](#retain-memories) |
| `DELETE` | `/v1/default/banks/{bank_id}/memories` | [清空 bank 记忆](#clear-bank-memories) |
| `POST` | `/v1/default/banks/{bank_id}/memories/dry-run-extract` | [试运行抽取记忆](#dry-run-extract-memories) |
| `GET` | `/v1/default/banks/{bank_id}/memories/list` | [列出记忆](#list-memories) |
| `POST` | `/v1/default/banks/{bank_id}/memories/recall` | [检索记忆（Recall）](#recall-memories) |
| `GET` | `/v1/default/banks/{bank_id}/memories/{memory_id}` | [获取单条记忆](#get-memory) |
| `PATCH` | `/v1/default/banks/{bank_id}/memories/{memory_id}` | [更新记忆](#update-memory) |
| `GET` | `/v1/default/banks/{bank_id}/memories/{memory_id}/history` | [观察历史](#get-observation-history) |
| `DELETE` | `/v1/default/banks/{bank_id}/memories/{memory_id}/observations` | [清除记忆观察](#clear-memory-observations) |
| `GET` | `/v1/default/banks/{bank_id}/observations/scopes` | [列出 observation scopes](#list-observation-scopes) |
| `POST` | `/v1/default/banks/{bank_id}/reflect` | [推理反思（Reflect）](#reflect) |
| `GET` | `/v1/default/banks/{bank_id}/tags` | [列出 tags](#list-tags) |

### 获取记忆图
<a id="get-graph"></a>

**GET** `/v1/default/banks/{bank_id}/graph`

*Get memory graph data*

Retrieve graph data for visualization, optionally filtered by type (world/experience/observation).

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `type` | query | `string?` | 否 | Type |
| `limit` | query | `integer` | 否 | 默认 `1000` · ≥ `0` |
| `q` | query | `string?` | 否 | Q |
| `tags` | query | `array<string>?` | 否 | Tags |
| `tags_match` | query | `string` | 否 | 默认 `"all_strict"` |
| `document_id` | query | `string?` | 否 | Document Id |
| `chunk_id` | query | `string?` | 否 | Chunk Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `nodes` | `array<object>` | 是 |  |
| `edges` | `array<object>` | 是 |  |
| `table_rows` | `array<object>` | 是 |  |
| `total_units` | `integer` | 是 |  |
| `limit` | `integer` | 是 |  |

#### 响应示例

```json
{
  "edges": [
    {
      "from": "1",
      "to": "2",
      "type": "semantic",
      "weight": 0.8
    }
  ],
  "limit": 1000,
  "nodes": [
    {
      "id": "1",
      "label": "Alice works at Google",
      "type": "world"
    },
    {
      "id": "2",
      "label": "Bob went hiking",
      "type": "world"
    }
  ],
  "table_rows": [
    {
      "context": "Work info",
      "date": "2024-01-15 10:30",
      "entities": "Alice (PERSON), Google (ORGANIZATION)",
      "id": "abc12345...",
      "text": "Alice works at Google"
    }
  ],
  "total_units": 2
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=get_graph`

---

### 写入记忆（Retain）
<a id="retain-memories"></a>

**POST** `/v1/default/banks/{bank_id}/memories`

*Retain memories*

Retain memory items with automatic fact extraction.

This is the main endpoint for storing memories. It supports both synchronous and asynchronous processing via the `async` parameter.

**Features:**
- Efficient batch processing
- Automatic fact extraction from natural language
- Entity recognition and linking
- Document tracking with automatic upsert (when document_id is provided)
- Temporal and semantic linking
- Optional asynchronous processing

**The system automatically:**
1. Extracts semantic facts from the content
2. Generates embeddings
3. Deduplicates similar facts
4. Creates temporal, semantic, and entity links
5. Tracks document metadata

**When `async=true`:** Returns immediately after queuing. Use the operations endpoint to monitor progress.

**When `async=false` (default):** Waits for processing to complete.

**Note:** If a memory item has a `document_id` that already exists, the old document and its memory units will be deleted before creating new ones (upsert behavior).

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `items` | `array<MemoryItem>` | 是 |  |
| `async` | `boolean` | 否 | If true, process asynchronously in background. If false, wait for completion (default: false) · 默认 `false` |
| `operation_id` | `string?` | 否 | Optional client-supplied UUID used as the identity of an async retain operation. Re-submitting with the same operation_id returns the original operation and creates no new work, so retrying after a lost or timed-out acknowledgement will not enqueue a duplicate. Reusing an id that belongs to a different operation returns HTTP 409. Ignored for synchronous retain. |

<details open><summary><strong>items[]</strong> · <code>MemoryItem</code></summary>

数据结构 `MemoryItem`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `content` | `string` | 是 |  |
| `timestamp` | `string(date-time) \| string \| null` | 否 | When the content occurred. Accepts an ISO 8601 datetime string (e.g. '2024-01-15T10:30:00Z'), null/omitted (defaults to now), or the special string 'unset' to explicitly store without any timestamp (use this for timeless content such as fictional documents or static reference material). |
| `context` | `string?` | 否 |  |
| `metadata` | `map<string, string>?` | 否 |  |
| `document_id` | `string?` | 否 | Optional document ID for this memory item. Provide a distinct document_id per source document — items sharing a document_id are grouped into the same document. Auto-generated when omitted. |
| `entities` | `array<EntityInput>?` | 否 | Optional entities to combine with auto-extracted entities. |
| `tags` | `array<string>?` | 否 | Optional tags for visibility scoping. Memories with tags can be filtered during recall. |
| `observation_scopes` | `"per_tag" \| "combined" \| "all_combinations" \| "shared" \| array<array<string>> \| null` | 否 | How to scope observations during consolidation. 'per_tag' runs one consolidation pass per individual tag, creating separate observations for each tag. 'combined' (default) runs a single pass with all tags together. 'shared' runs a single pass over one global, untagged scope, so memories consolidate together regardless of their tags — useful for deduplicating across volatile per-call provenance tags (e.g. per-session ids) while keeping those tags on the source facts. A list of tag lists runs one pass per inner list, giving full control over which combinations to use. |
| `strategy` | `string?` | 否 | Named retain strategy for this item. Overrides the bank's default strategy for this item only. Strategies are defined in the bank config under 'retain_strategies'. |
| `update_mode` | `"replace" \| "append"?` | 否 | How to handle an existing document with the same document_id. 'replace' (default) deletes old data and reprocesses from scratch. 'append' concatenates new content to the existing document text and reprocesses. |

<details open><summary><strong>entities[]</strong> · <code>EntityInput</code></summary>

数据结构 `EntityInput`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `text` | `string` | 是 | The entity name/text |
| `type` | `string?` | 否 | Optional entity type (e.g., 'PERSON', 'ORG', 'CONCEPT') |

</details>

</details>

#### 请求示例

```json
{
  "async": false,
  "items": [
    {
      "content": "Alice works at Google",
      "context": "work",
      "document_id": "conversation_123"
    },
    {
      "content": "Bob went hiking yesterday",
      "document_id": "conversation_123",
      "timestamp": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `success` | `boolean` | 是 |  |
| `bank_id` | `string` | 是 |  |
| `items_count` | `integer` | 是 |  |
| `async` | `boolean` | 是 | Whether the operation was processed asynchronously |
| `operation_id` | `string?` | 否 | Operation ID for tracking async operations. Use GET /v1/default/banks/{bank_id}/operations to list operations. Only present when async=true. When items use different per-item strategies, use operation_ids instead. |
| `operation_ids` | `array<string>?` | 否 | Operation IDs when items were submitted as multiple strategy groups (async=true with mixed per-item strategies). operation_id is set to the first entry for backward compatibility. |
| `usage` | `TokenUsage?` | 否 | Token usage metrics for LLM calls during fact extraction (only present for synchronous operations) |

<details open><summary><strong>usage</strong> · <code>TokenUsage</code></summary>

数据结构 `TokenUsage`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `input_tokens` | `integer` | 否 | Number of input/prompt tokens consumed · 默认 `0` |
| `output_tokens` | `integer` | 否 | Number of visible output/completion tokens generated (excludes reasoning/thoughts) · 默认 `0` |
| `total_tokens` | `integer` | 否 | Total tokens (input + output, excludes thoughts) · 默认 `0` |
| `cached_tokens` | `integer` | 否 | Cached/cache-read prompt tokens, when reported by the provider · 默认 `0` |
| `thoughts_tokens` | `integer` | 否 | Reasoning/thinking tokens generated by the model. Billed at the output rate by some providers (e.g. Gemini 2.5+ family) but not surfaced in the visible response. · 默认 `0` |

</details>

#### 响应示例

```json
{
  "async": false,
  "bank_id": "user123",
  "items_count": 2,
  "success": true,
  "usage": {
    "input_tokens": 500,
    "output_tokens": 100,
    "total_tokens": 600
  }
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=retain_memories`

---

### 清空 bank 记忆
<a id="clear-bank-memories"></a>

**DELETE** `/v1/default/banks/{bank_id}/memories`

*Clear memory bank memories*

Delete memory units for a memory bank. Optionally filter by type (world, experience, observation) to delete only specific types. This is a destructive operation that cannot be undone. The bank profile (disposition and background) will be preserved.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `type` | query | `string?` | 否 | Optional fact type filter (world, experience, observation) |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `success` | `boolean` | 是 |  |
| `message` | `string?` | 否 |  |
| `deleted_count` | `integer?` | 否 |  |

#### 响应示例

```json
{
  "deleted_count": 10,
  "message": "Deleted successfully",
  "success": true
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=clear_bank_memories`

---

### 试运行抽取记忆
<a id="dry-run-extract-memories"></a>

**POST** `/v1/default/banks/{bank_id}/memories/dry-run-extract`

*Dry-run fact extraction (preview, no persistence)*

Preview what the retain step would extract from text WITHOUT changing the bank — no entity resolution, links, embeddings, or persistence. Returns the candidate facts and the LLM token usage. Every prompt-affecting setting (retain mission, extraction mode, chunk size, …) is overridable in the body to A/B a candidate config against the bank's current one. This is a read-only tool: nothing is stored.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `content` | `string` | 是 | Text to extract facts from (e.g. a document or a single chunk). |
| `context` | `string` | 否 | Optional context about the content. · 默认 `""` |
| `timestamp` | `string(date-time)?` | 否 | Reference timestamp for resolving relative times (ISO 8601). |
| `retain_mission` | `string?` | 否 |  |
| `retain_extraction_mode` | `string?` | 否 |  |
| `retain_custom_instructions` | `string?` | 否 |  |
| `retain_extract_causal_links` | `boolean?` | 否 |  |
| `retain_chunk_size` | `integer?` | 否 |  |
| `entity_labels` | `array<LabelGroup-Input>?` | 否 | Controlled vocabulary for entity labels (overrides the bank's config for this call) |
| `entities_allow_free_form` | `boolean?` | 否 |  |
| `llm_output_language` | `string?` | 否 |  |

<details open><summary><strong>entity_labels[]</strong> · <code>LabelGroup-Input</code></summary>

数据结构 `LabelGroup-Input`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `key` | `string` | 是 |  |
| `description` | `string` | 否 | 默认 `""` |
| `type` | `"value" \| "multi-values" \| "text" \| "map"` | 否 | 默认 `"value"` |
| `optional` | `boolean` | 否 | 默认 `true` |
| `tag` | `boolean` | 否 | 默认 `false` |
| `values` | `array<LabelValue>` | 否 | 默认 `[]` |
| `fields` | `map<string, MapField-Input>` | 否 | 默认 `{}` |

<details open><summary><strong>values[]</strong> · <code>LabelValue</code></summary>

数据结构 `LabelValue`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `value` | `string` | 是 |  |
| `description` | `string` | 否 | 默认 `""` |

</details>

</details>

#### 请求示例

```json
{
  "content": "string",
  "context": "",
  "timestamp": "2026-01-01T00:00:00Z",
  "retain_mission": "string",
  "retain_extraction_mode": "string",
  "retain_custom_instructions": "string",
  "retain_extract_causal_links": false,
  "retain_chunk_size": 0,
  "entity_labels": [
    {
      "key": "string",
      "description": "",
      "type": "value",
      "optional": true,
      "tag": false,
      "values": [],
      "fields": {}
    }
  ],
  "entities_allow_free_form": false,
  "llm_output_language": "string"
}
```

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `facts` | `array<ExtractedFact>` | 否 | Candidate facts the retain step would extract. |
| `usage` | `TokenUsage` | 否 | Aggregated token usage across the extraction LLM calls. |

<details open><summary><strong>facts[]</strong> · <code>ExtractedFact</code></summary>

数据结构 `ExtractedFact`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `text` | `string` | 是 | The extracted fact text. |
| `fact_type` | `string` | 是 | Perspective classification: 'world' or 'experience'. |
| `occurred_start` | `string?` | 否 | ISO timestamp the fact's event started, if dated. |
| `occurred_end` | `string?` | 否 | ISO timestamp the fact's event ended, if dated. |
| `entities` | `array<string>` | 否 | Raw (unresolved) entity names mentioned in the fact. |

</details>

<details open><summary><strong>usage</strong> · <code>TokenUsage</code></summary>

数据结构 `TokenUsage`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `input_tokens` | `integer` | 否 | Number of input/prompt tokens consumed · 默认 `0` |
| `output_tokens` | `integer` | 否 | Number of visible output/completion tokens generated (excludes reasoning/thoughts) · 默认 `0` |
| `total_tokens` | `integer` | 否 | Total tokens (input + output, excludes thoughts) · 默认 `0` |
| `cached_tokens` | `integer` | 否 | Cached/cache-read prompt tokens, when reported by the provider · 默认 `0` |
| `thoughts_tokens` | `integer` | 否 | Reasoning/thinking tokens generated by the model. Billed at the output rate by some providers (e.g. Gemini 2.5+ family) but not surfaced in the visible response. · 默认 `0` |

</details>

#### 响应示例

```json
{
  "facts": [
    {
      "text": "string",
      "fact_type": "string",
      "occurred_start": "string",
      "occurred_end": "string",
      "entities": [
        "string"
      ]
    }
  ],
  "usage": {
    "input_tokens": 1500,
    "output_tokens": 500,
    "total_tokens": 2000
  }
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=dry_run_extract_memories`

---

### 列出记忆
<a id="list-memories"></a>

**GET** `/v1/default/banks/{bank_id}/memories/list`

*List memory units*

List memory units with pagination and optional full-text search. Supports filtering by type, source document, and linked entity ID. Results are sorted by most recent first (mentioned_at DESC, then created_at DESC).

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `type` | query | `string?` | 否 | Type |
| `q` | query | `string?` | 否 | Q |
| `consolidation_state` | query | `string?` | 否 | Consolidation State |
| `state` | query | `string?` | 否 | State |
| `document_id` | query | `string?` | 否 | Document Id |
| `entity_id` | query | `string?` | 否 | Entity Id |
| `tags` | query | `array<string>?` | 否 | Tags |
| `tags_match` | query | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"` | 否 | 默认 `"any"` |
| `limit` | query | `integer` | 否 | 默认 `100` · ≥ `0` |
| `offset` | query | `integer` | 否 | 默认 `0` · ≥ `0` |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `items` | `array<object>` | 是 |  |
| `total` | `integer` | 是 |  |
| `limit` | `integer` | 是 |  |
| `offset` | `integer` | 是 |  |

#### 响应示例

```json
{
  "items": [
    {
      "context": "Work conversation",
      "date": "2024-01-15T10:30:00Z",
      "entities": "Alice (PERSON), Google (ORGANIZATION)",
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "metadata": {
        "channel": "engineering",
        "source": "slack"
      },
      "text": "Alice works at Google on the AI team",
      "type": "world"
    }
  ],
  "limit": 100,
  "offset": 0,
  "total": 150
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=list_memories`

---

### 检索记忆（Recall）
<a id="recall-memories"></a>

**POST** `/v1/default/banks/{bank_id}/memories/recall`

*Recall memory*

Recall memory using semantic similarity and spreading activation.

The type parameter is optional and must be one of:
- `world`: General knowledge about people, places, events, and things that happen
- `experience`: Memories about experience, conversations, actions taken, and tasks performed

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `query` | `string` | 是 |  |
| `types` | `array<string>?` | 否 | List of fact types to recall: 'world', 'experience', 'observation'. Defaults to world and experience if not specified. |
| `prefer_observations` | `boolean` | 否 | When recalling raw facts ('world'/'experience') together with 'observation', drop any raw fact that an observation in the results was consolidated from, so the observation supersedes it and you don't get duplicate content. The freed slots are backfilled with the next results, keeping the result count at the requested budget. Disabled by default; set to true to enable. No effect unless 'observation' and at least one raw type are both requested. · 默认 `false` |
| `budget` | `Budget` | 否 | 默认 `"mid"` |
| `max_tokens` | `integer` | 否 | 默认 `4096` |
| `trace` | `boolean` | 否 | 默认 `false` |
| `query_timestamp` | `string?` | 否 | ISO format date string (e.g., '2023-05-30T23:40:00'). Used as the query-time anchor for relative temporal expressions and recency scoring. |
| `include` | `IncludeOptions` | 否 | Options for including additional data (entities are included by default) · 默认 `{}` |
| `tags` | `array<string>?` | 否 | Filter memories by tags. If not specified, all memories are returned. Omitting tags (or passing []) together with tags_match='exact' filters to untagged/global observations only (the scope written by observation_scopes='shared'). |
| `tags_match` | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"` | 否 | How to match tags: 'any' (OR, includes untagged), 'all' (AND, includes untagged), 'any_strict' (OR, excludes untagged), 'all_strict' (AND, excludes untagged), 'exact' (set-equality on the full scope, excludes untagged). With 'exact' and no tags (or []), the empty global scope is selected and only untagged memories match. · 默认 `"any"` |
| `tag_groups` | `array<TagGroupLeaf \| TagGroupAnd-Input \| TagGroupOr-Input \| TagGroupNot-Input>?` | 否 | Compound tag filter using boolean groups. Groups in the list are AND-ed. Each group is a leaf {tags, match} or compound {and: [...]}, {or: [...]}, {not: ...}. |
| `min_scores` | `MinScores?` | 否 | Optional per-stage score floors (all inclusive, AND-ed). `semantic` and `keyword` are retrieval-level cutoffs pushed into the SQL arms (overriding the global similarity/BM25 minimums for this request); `reranker` and `final` are post-ranking filters on the scored results. Any field left unset imposes no floor; omitting `min_scores` entirely (the default) applies no score filtering. Use with care — the reranker's absolute scores are not calibrated across queries (a clearly-relevant match may score ~0.001 even though it is ranked first). |

<details open><summary><strong>budget</strong> · <code>Budget</code></summary>

类型：`Budget`

</details>

<details open><summary><strong>include</strong> · <code>IncludeOptions</code></summary>

数据结构 `IncludeOptions`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `entities` | `EntityIncludeOptions?` | 否 | Include entity observations. Set to null to disable entity inclusion. · 默认 `{"max_tokens": 500}` |
| `chunks` | `ChunkIncludeOptions?` | 否 | Include raw chunks. Set to {} to enable, null to disable (default: disabled). |
| `source_facts` | `SourceFactsIncludeOptions?` | 否 | Include source facts for observation-type results. Set to {} to enable, null to disable (default: disabled). |

<details open><summary><strong>entities</strong> · <code>EntityIncludeOptions</code></summary>

数据结构 `EntityIncludeOptions`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `max_tokens` | `integer` | 否 | Maximum tokens for entity observations · 默认 `500` |

</details>

<details open><summary><strong>chunks</strong> · <code>ChunkIncludeOptions</code></summary>

数据结构 `ChunkIncludeOptions`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `max_tokens` | `integer` | 否 | Maximum tokens for chunks (chunks may be truncated) · 默认 `8192` |

</details>

<details open><summary><strong>source_facts</strong> · <code>SourceFactsIncludeOptions</code></summary>

数据结构 `SourceFactsIncludeOptions`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `max_tokens` | `integer` | 否 | Maximum total tokens for source facts across all observations (-1 = unlimited) · 默认 `4096` |
| `max_tokens_per_observation` | `integer` | 否 | Maximum tokens of source facts per observation (-1 = unlimited) · 默认 `-1` |

</details>

</details>

<details open><summary><strong>min_scores</strong> · <code>MinScores</code></summary>

数据结构 `MinScores`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `semantic` | `number?` | 否 | Retrieval-level: minimum vector similarity (0-1). |
| `keyword` | `number?` | 否 | Retrieval-level: minimum keyword/full-text (BM25) score. |
| `reranker` | `number?` | 否 | Post-query: minimum normalized reranker score (0-1). |
| `final` | `number?` | 否 | Post-query: minimum final ranking score. |

</details>

#### 请求示例

```json
{
  "budget": "mid",
  "include": {
    "entities": {
      "max_tokens": 500
    }
  },
  "max_tokens": 4096,
  "query": "What did Alice say about machine learning?",
  "query_timestamp": "2023-05-30T23:40:00",
  "tags": [
    "user_a"
  ],
  "tags_match": "any",
  "trace": true,
  "types": [
    "world",
    "experience"
  ]
}
```

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `results` | `array<RecallResult>` | 是 |  |
| `trace` | `object?` | 否 |  |
| `entities` | `map<string, EntityStateResponse>?` | 否 | Entity states for entities mentioned in results |
| `chunks` | `map<string, ChunkData>?` | 否 | Chunks for facts, keyed by chunk_id |
| `source_facts` | `map<string, RecallResult>?` | 否 | Source facts for observation-type results, keyed by fact ID |
| `source_facts_truncated` | `boolean?` | 否 | Whether the source_facts map was cut short by the token budget. When true, some IDs in results[].source_fact_ids have no entry in source_facts — the budget ran out, the references are not dangling. Only set when source facts were requested. |

<details open><summary><strong>results[]</strong> · <code>RecallResult</code></summary>

数据结构 `RecallResult`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `text` | `string` | 是 |  |
| `type` | `string?` | 否 |  |
| `entities` | `array<string>?` | 否 |  |
| `context` | `string?` | 否 |  |
| `occurred_start` | `string?` | 否 |  |
| `occurred_end` | `string?` | 否 |  |
| `mentioned_at` | `string?` | 否 |  |
| `document_id` | `string?` | 否 |  |
| `metadata` | `map<string, string>?` | 否 |  |
| `chunk_id` | `string?` | 否 |  |
| `tags` | `array<string>?` | 否 |  |
| `source_fact_ids` | `array<string>?` | 否 |  |
| `scores` | `RecallScores?` | 否 |  |

<details open><summary><strong>scores</strong> · <code>RecallScores</code></summary>

数据结构 `RecallScores`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `final` | `number` | 是 | Final ranking score (combined reranker + recency/temporal/proof boosts) |
| `reranker` | `number?` | 否 | Cross-encoder relevance, normalized 0-1. None when the reranker is a passthrough (rrf/interleave modes). |
| `semantic` | `number?` | 否 | Vector cosine similarity (0-1). None if this result was not surfaced semantically. |
| `keyword` | `number?` | 否 | Keyword/full-text (BM25) score (>= 0, unbounded). None if this result was not surfaced by keyword search. |

</details>

</details>

#### 响应示例

```json
{
  "chunks": {
    "456e7890-e12b-34d5-a678-901234567890": {
      "chunk_index": 0,
      "id": "456e7890-e12b-34d5-a678-901234567890",
      "text": "Alice works at Google on the AI team. She's been there for 3 years..."
    }
  },
  "entities": {
    "Alice": {
      "canonical_name": "Alice",
      "entity_id": "123e4567-e89b-12d3-a456-426614174001",
      "observations": [
        {
          "mentioned_at": "2024-01-15T10:30:00Z",
          "text": "Alice works at Google on the AI team"
        }
      ]
    }
  },
  "results": [
    {
      "chunk_id": "456e7890-e12b-34d5-a678-901234567890",
      "context": "work info",
      "entities": [
        "Alice",
        "Google"
      ],
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "occurred_end": "2024-01-15T10:30:00Z",
      "occurred_start": "2024-01-15T10:30:00Z",
      "text": "Alice works at Google on the AI team",
      "type": "world"
    }
  ],
  "trace": {
    "num_results": 1,
    "query": "What did Alice say about machine learning?",
    "time_seconds": 0.123
  }
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=recall_memories`

---

### 获取单条记忆
<a id="get-memory"></a>

**GET** `/v1/default/banks/{bank_id}/memories/{memory_id}`

*Get memory unit*

Get a single memory unit by ID with all its metadata including entities and tags. Note: the 'history' field is deprecated and always returns an empty list - use GET /memories/{memory_id}/history instead.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `memory_id` | path | `string` | 是 | Memory Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

_无展开字段（标量、自由 object 或未声明 properties）_

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=get_memory`

---

### 更新记忆
<a id="update-memory"></a>

**PATCH** `/v1/default/banks/{bank_id}/memories/{memory_id}`

*Curate memory unit*

Edit a memory's text and/or change its curation state (invalidate / revert). Invalidated memories are excluded from recall, consolidation, and graph maintenance but kept for audit (reversible). Only world/experience facts can be curated; observations are derived.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `memory_id` | path | `string` | 是 | Memory Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `text` | `string?` | 否 | New fact text. Re-embeds the memory, drops its derived observations and links, and triggers re-consolidation. |
| `context` | `string?` | 否 | New context for the fact. '' clears it; omit to leave unchanged. |
| `occurred_start` | `string?` | 否 | New occurred-range start (ISO 8601). '' clears it; omit to leave unchanged. |
| `occurred_end` | `string?` | 否 | New occurred-range end (ISO 8601). '' clears it; omit to leave unchanged. |
| `fact_type` | `string?` | 否 | Reclassify the fact: 'world' or 'experience'. Omit to leave unchanged. |
| `entities` | `array<string>?` | 否 | Replace the fact's entities. Names are resolved/find-or-created the same way retain does; '[]' detaches all entities. Omit to leave unchanged. |
| `state` | `string?` | 否 | Curation state: 'invalidated' to soft-retire the memory (excluded from recall/consolidation, links and derived observations pruned, moved to the archive) or 'valid' to revert. Reversible. |
| `reason` | `string?` | 否 | Optional free-text reason recorded when invalidating. |

#### 请求示例

```json
{
  "reason": "superseded: server decommissioned 2026-06-01",
  "state": "invalidated"
}
```

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

_无展开字段（标量、自由 object 或未声明 properties）_

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=update_memory`

---

### 观察历史
<a id="get-observation-history"></a>

**GET** `/v1/default/banks/{bank_id}/memories/{memory_id}/history`

*Get observation history*

Get the full history of an observation, with each change's source facts resolved to their text.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `memory_id` | path | `string` | 是 | Memory Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

_无展开字段（标量、自由 object 或未声明 properties）_

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=get_observation_history`

---

### 清除记忆观察
<a id="clear-memory-observations"></a>

**DELETE** `/v1/default/banks/{bank_id}/memories/{memory_id}/observations`

*Clear observations for a memory*

Delete all observations derived from a specific memory and reset it for re-consolidation. The memory itself is not deleted. A consolidation job is triggered automatically so the memory will produce fresh observations on the next consolidation run.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `memory_id` | path | `string` | 是 | Memory Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `deleted_count` | `integer` | 是 |  |

#### 响应示例

```json
{
  "deleted_count": 3
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=clear_memory_observations`

---

### 列出 observation scopes
<a id="list-observation-scopes"></a>

**GET** `/v1/default/banks/{bank_id}/observations/scopes`

*List observation scopes*

Enumerate the distinct scopes across a bank's observations. Each observation lives under a scope: the exact set of tags it was consolidated with. Returns every distinct scope (tag order normalized) with the number of observations in it; the empty tag list is the global/untagged scope. Use a returned scope with the graph endpoint (tags=<scope> & tags_match=exact) to filter observations to exactly that scope.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `scopes` | `array<ObservationScope>` | 是 | Distinct observation scopes, most populous first |

<details open><summary><strong>scopes[]</strong> · <code>ObservationScope</code></summary>

数据结构 `ObservationScope`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `tags` | `array<string>` | 是 | The exact tag set defining this scope (normalized order). Empty list is the global/untagged scope. |
| `count` | `integer` | 是 | Number of observations that live under this scope |

</details>

#### 响应示例

```json
{
  "scopes": [
    {
      "count": 12,
      "tags": [
        "user:alice"
      ]
    },
    {
      "count": 4,
      "tags": [
        "user:alice",
        "project:apollo"
      ]
    },
    {
      "count": 2,
      "tags": []
    }
  ]
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=list_observation_scopes`

---

### 推理反思（Reflect）
<a id="reflect"></a>

**POST** `/v1/default/banks/{bank_id}/reflect`

*Reflect and generate answer*

Reflect and formulate an answer using bank identity, world facts, observations, and mental models.

This endpoint:
1. Retrieves experience (conversations and events)
2. Retrieves world facts relevant to the query
3. Retrieves observations and mental models (bank's synthesized perspectives)
4. Uses LLM to formulate a contextual answer
5. Returns plain text answer and the facts used

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `query` | `string` | 是 |  |
| `budget` | `Budget` | 否 | 默认 `"low"` |
| `max_tokens` | `integer` | 否 | Maximum tokens for the response · 默认 `4096` |
| `include` | `ReflectIncludeOptions` | 否 | Options for including additional data (disabled by default) |
| `response_schema` | `object?` | 否 | Optional JSON Schema for structured output. When provided, the response will include a 'structured_output' field with the LLM response parsed according to this schema. |
| `tags` | `array<string>?` | 否 | Scope raw facts, observations, mental models, and tagged directives during reflection. With no tags, memory retrieval is unfiltered while only untagged/global directives are loaded. Use tags=[] with tags_match='exact' to select the untagged/global scope. |
| `tags_match` | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"` | 否 | How to match tags: 'any' (OR, includes untagged), 'all' (AND, includes untagged), 'any_strict' (OR, excludes untagged), 'all_strict' (AND, excludes untagged), or 'exact' (set equality). Untagged directives remain global in every mode. · 默认 `"any"` |
| `tag_groups` | `array<TagGroupLeaf \| TagGroupAnd-Input \| TagGroupOr-Input \| TagGroupNot-Input>?` | 否 | Compound tag filter using boolean groups. Groups in the list are AND-ed. Each group is a leaf {tags, match} or compound {and: [...]}, {or: [...]}, {not: ...}. Mutually exclusive with tags. |
| `apply_all_directives` | `boolean` | 否 | Apply every active directive regardless of tags. By default directives are scoped like memories: untagged directives always apply, and tagged directives apply only when the request's tags match them. Set true to apply all active directives, ignoring tag scope. · 默认 `false` |
| `fact_types` | `array<"world" \| "experience" \| "observation">?` | 否 | Filter which fact types are retrieved during reflect. None means all types (world, experience, observation). |
| `exclude_mental_models` | `boolean` | 否 | If true, exclude all mental models from the reflect loop (skip search_mental_models tool). · 默认 `false` |
| `exclude_mental_model_ids` | `array<string>?` | 否 | Exclude specific mental models by ID from the reflect loop. |

<details open><summary><strong>budget</strong> · <code>Budget</code></summary>

类型：`Budget`

</details>

<details open><summary><strong>include</strong> · <code>ReflectIncludeOptions</code></summary>

数据结构 `ReflectIncludeOptions`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `facts` | `FactsIncludeOptions?` | 否 | Include facts that the answer is based on. Set to {} to enable, null to disable (default: disabled). |
| `tool_calls` | `ToolCallsIncludeOptions?` | 否 | Include tool calls trace. Set to {} for full trace (input+output), {output: false} for inputs only. |

<details open><summary><strong>facts</strong> · <code>FactsIncludeOptions</code></summary>

类型：`FactsIncludeOptions`

</details>

<details open><summary><strong>tool_calls</strong> · <code>ToolCallsIncludeOptions</code></summary>

数据结构 `ToolCallsIncludeOptions`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `output` | `boolean` | 否 | Include tool outputs in the trace. Set to false to only include inputs (smaller payload). · 默认 `true` |

</details>

</details>

#### 请求示例

```json
{
  "budget": "low",
  "include": {
    "facts": {}
  },
  "max_tokens": 4096,
  "query": "What do you think about artificial intelligence?",
  "response_schema": {
    "properties": {
      "summary": {
        "type": "string"
      },
      "key_points": {
        "items": {
          "type": "string"
        },
        "type": "array"
      }
    },
    "required": [
      "summary",
      "key_points"
    ],
    "type": "object"
  },
  "tags": [
    "user_a"
  ],
  "tags_match": "any"
}
```

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `text` | `string` | 是 | The reflect response as well-formatted markdown (headers, lists, bold/italic, code blocks, etc.) |
| `based_on` | `ReflectBasedOn?` | 否 | Evidence used to generate the response. Only present when include.facts is set. |
| `structured_output` | `object?` | 否 | Structured output parsed according to the request's response_schema. Only present when response_schema was provided in the request. |
| `usage` | `TokenUsage?` | 否 | Token usage metrics for LLM calls during reflection. |
| `trace` | `ReflectTrace?` | 否 | Execution trace of tool and LLM calls. Only present when include.tool_calls is set. |

<details open><summary><strong>based_on</strong> · <code>ReflectBasedOn</code></summary>

数据结构 `ReflectBasedOn`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `memories` | `array<ReflectFact>` | 否 | Memory facts used to generate the response · 默认 `[]` |
| `mental_models` | `array<ReflectMentalModel>` | 否 | Mental models used during reflection · 默认 `[]` |
| `directives` | `array<ReflectDirective>` | 否 | Directives applied during reflection · 默认 `[]` |

<details open><summary><strong>memories[]</strong> · <code>ReflectFact</code></summary>

数据结构 `ReflectFact`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string?` | 否 |  |
| `text` | `string` | 是 | Fact text. When type='observation', this contains markdown-formatted consolidated knowledge |
| `type` | `string?` | 否 |  |
| `context` | `string?` | 否 |  |
| `occurred_start` | `string?` | 否 |  |
| `occurred_end` | `string?` | 否 |  |

</details>

<details open><summary><strong>mental_models[]</strong> · <code>ReflectMentalModel</code></summary>

数据结构 `ReflectMentalModel`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 | Mental model ID |
| `text` | `string` | 是 | Mental model content |
| `context` | `string?` | 否 | Additional context |

</details>

<details open><summary><strong>directives[]</strong> · <code>ReflectDirective</code></summary>

数据结构 `ReflectDirective`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 | Directive ID |
| `name` | `string` | 是 | Directive name |
| `content` | `string` | 是 | Directive content |

</details>

</details>

<details open><summary><strong>usage</strong> · <code>TokenUsage</code></summary>

数据结构 `TokenUsage`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `input_tokens` | `integer` | 否 | Number of input/prompt tokens consumed · 默认 `0` |
| `output_tokens` | `integer` | 否 | Number of visible output/completion tokens generated (excludes reasoning/thoughts) · 默认 `0` |
| `total_tokens` | `integer` | 否 | Total tokens (input + output, excludes thoughts) · 默认 `0` |
| `cached_tokens` | `integer` | 否 | Cached/cache-read prompt tokens, when reported by the provider · 默认 `0` |
| `thoughts_tokens` | `integer` | 否 | Reasoning/thinking tokens generated by the model. Billed at the output rate by some providers (e.g. Gemini 2.5+ family) but not surfaced in the visible response. · 默认 `0` |

</details>

<details open><summary><strong>trace</strong> · <code>ReflectTrace</code></summary>

数据结构 `ReflectTrace`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `tool_calls` | `array<ReflectToolCall>` | 否 | Tool calls made during reflection · 默认 `[]` |
| `llm_calls` | `array<ReflectLLMCall>` | 否 | LLM calls made during reflection · 默认 `[]` |

<details open><summary><strong>tool_calls[]</strong> · <code>ReflectToolCall</code></summary>

数据结构 `ReflectToolCall`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `tool` | `string` | 是 | Tool name: lookup, recall, learn, expand |
| `input` | `object` | 是 | Tool input parameters |
| `output` | `object?` | 否 | Tool output (only included when include.tool_calls.output is true) |
| `duration_ms` | `integer` | 是 | Execution time in milliseconds |
| `iteration` | `integer` | 否 | Iteration number (1-based) when this tool was called · 默认 `0` |

</details>

<details open><summary><strong>llm_calls[]</strong> · <code>ReflectLLMCall</code></summary>

数据结构 `ReflectLLMCall`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `scope` | `string` | 是 | Call scope: agent_1, agent_2, final, etc. |
| `duration_ms` | `integer` | 是 | Execution time in milliseconds |

</details>

</details>

#### 响应示例

```json
{
  "based_on": {
    "memories": [
      {
        "id": "123",
        "text": "AI is used in healthcare",
        "type": "world"
      },
      {
        "id": "456",
        "text": "I discussed AI applications last week",
        "type": "experience"
      }
    ]
  },
  "structured_output": {
    "key_points": [
      "Used in healthcare",
      "Discussed recently"
    ],
    "summary": "AI is transformative"
  },
  "text": "## AI Overview\n\nBased on my understanding, AI is a **transformative technology**:\n\n- Used extensively in healthcare\n- Discussed in recent conversations\n- Continues to evolve rapidly",
  "trace": {
    "llm_calls": [
      {
        "duration_ms": 1200,
        "scope": "agent_1"
      }
    ],
    "observations": [
      {
        "id": "obs-1",
        "name": "AI Technology",
        "subtype": "structural",
        "type": "concept"
      }
    ],
    "tool_calls": [
      {
        "duration_ms": 150,
        "input": {
          "query": "AI"
        },
        "tool": "recall"
      }
    ]
  },
  "usage": {
    "input_tokens": 1500,
    "output_tokens": 500,
    "total_tokens": 2000
  }
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=reflect`

---

### 列出 tags
<a id="list-tags"></a>

**GET** `/v1/default/banks/{bank_id}/tags`

*List tags*

List all unique tags in a memory bank with usage counts. Supports wildcard search using '*' (e.g., 'user:*', '*-fred', 'tag*-2'). Case-insensitive. Use `source=mental_models` to list tags used on mental models instead of memories.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `q` | query | `string?` | 否 | Wildcard pattern to filter tags (e.g., 'user:*' for user:alice, '*-admin' for role-admin). Use '*' as wildcard. Case-insensitive. |
| `source` | query | `"memories" \| "mental_models"` | 否 | Where to read tags from: 'memories' (memory_units, default) or 'mental_models'. · 默认 `"memories"` |
| `limit` | query | `integer` | 否 | Maximum number of tags to return · 默认 `100` · ≥ `0` |
| `offset` | query | `integer` | 否 | Offset for pagination · 默认 `0` · ≥ `0` |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `items` | `array<TagItem>` | 是 |  |
| `total` | `integer` | 是 |  |
| `limit` | `integer` | 是 |  |
| `offset` | `integer` | 是 |  |

<details open><summary><strong>items[]</strong> · <code>TagItem</code></summary>

数据结构 `TagItem`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `tag` | `string` | 是 | The tag value |
| `count` | `integer` | 是 | Number of memories with this tag |

</details>

#### 响应示例

```json
{
  "items": [
    {
      "count": 42,
      "tag": "user:alice"
    },
    {
      "count": 15,
      "tag": "user:bob"
    },
    {
      "count": 8,
      "tag": "session:abc123"
    }
  ],
  "limit": 100,
  "offset": 0,
  "total": 25
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=list_tags`

---

## Knowledge Base
<a id="knowledge-base"></a>

**知识库树（Knowledge Pages）** · 8 endpoints

folder/page 树组织 mental model；异步生成 page；hybrid 搜索与 markdown 导出。

### 本章目录

| Method | Path | 标题 |
| --- | --- | --- |
| `GET` | `/v1/default/banks/{bank_id}/knowledge-base/export` | [导出知识库](#export-knowledge-base) |
| `POST` | `/v1/default/banks/{bank_id}/knowledge-base/folders` | [创建知识库目录](#create-knowledge-folder) |
| `PATCH` | `/v1/default/banks/{bank_id}/knowledge-base/nodes/{node_id}` | [更新知识库节点](#update-knowledge-node) |
| `DELETE` | `/v1/default/banks/{bank_id}/knowledge-base/nodes/{node_id}` | [删除知识库节点](#delete-knowledge-node) |
| `POST` | `/v1/default/banks/{bank_id}/knowledge-base/pages` | [创建知识库页面](#create-knowledge-page) |
| `GET` | `/v1/default/banks/{bank_id}/knowledge-base/pages/{page_id}` | [读取知识库页面](#get-knowledge-page) |
| `GET` | `/v1/default/banks/{bank_id}/knowledge-base/search` | [搜索知识库页面](#search-knowledge-base) |
| `GET` | `/v1/default/banks/{bank_id}/knowledge-base/tree` | [获取知识库树](#get-knowledge-base-tree) |

### 导出知识库
<a id="export-knowledge-base"></a>

**GET** `/v1/default/banks/{bank_id}/knowledge-base/export`

*Export the knowledge base as a markdown bundle*

Return a portable markdown bundle: a nested index.md, one <id>.md per page, and history logs.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `files` | `array<KnowledgePageBundleFile>` | 是 |  |

<details open><summary><strong>files[]</strong> · <code>KnowledgePageBundleFile</code></summary>

数据结构 `KnowledgePageBundleFile`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `path` | `string` | 是 |  |
| `content` | `string` | 是 |  |

</details>

#### 响应示例

```json
{
  "files": [
    {
      "path": "string",
      "content": "string"
    }
  ]
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=export_knowledge_base`

---

### 创建知识库目录
<a id="create-knowledge-folder"></a>

**POST** `/v1/default/banks/{bank_id}/knowledge-base/folders`

*Create a knowledge-base folder*

Create a folder, optionally nested under a parent folder.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | `string` | 是 |  |
| `parent_id` | `string?` | 否 |  |

#### 请求示例

```json
{
  "name": "string",
  "parent_id": "string"
}
```

#### 响应

- 状态码：`201` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `kind` | `"folder" \| "page"` | 是 | 节点类型：`folder` 或 `page`。 |
| `name` | `string` | 是 |  |
| `parent_id` | `string?` | 否 |  |
| `mental_model_id` | `string?` | 否 | Backing mental model id (pages only). |
| `managed` | `boolean` | 否 | Client-set flag: true = system-owned, false = hand-authored. · 默认 `false` |
| `description` | `string?` | 否 | Page source query (the page's `description`). |
| `tags` | `array<string>` | 否 | 默认 `[]` |
| `timestamp` | `string?` | 否 | Last refresh (page) or last update (folder). |
| `is_stale` | `boolean?` | 否 | Pages only, populated by the tree endpoint. False means the page is up to date — nothing in the bank has been written since its last refresh. True means it *may* need a refresh: something was written, but possibly outside the page's tags. Read the page's mental model for the exact answer. Shares the bank-stats freshness, so it can lag a just-written memory by up to a minute. |
| `children` | `array<KnowledgeNode>` | 否 | 默认 `[]` |

<details open><summary><strong>children[]</strong> · <code>KnowledgeNode</code></summary>

数据结构 `KnowledgeNode`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `kind` | `"folder" \| "page"` | 是 | 节点类型：`folder` 或 `page`。 |
| `name` | `string` | 是 |  |
| `parent_id` | `string?` | 否 |  |
| `mental_model_id` | `string?` | 否 | Backing mental model id (pages only). |
| `managed` | `boolean` | 否 | Client-set flag: true = system-owned, false = hand-authored. · 默认 `false` |
| `description` | `string?` | 否 | Page source query (the page's `description`). |
| `tags` | `array<string>` | 否 | 默认 `[]` |
| `timestamp` | `string?` | 否 | Last refresh (page) or last update (folder). |
| `is_stale` | `boolean?` | 否 | Pages only, populated by the tree endpoint. False means the page is up to date — nothing in the bank has been written since its last refresh. True means it *may* need a refresh: something was written, but possibly outside the page's tags. Read the page's mental model for the exact answer. Shares the bank-stats freshness, so it can lag a just-written memory by up to a minute. |
| `children` | `array<KnowledgeNode>` | 否 | 默认 `[]` |

<details><summary>嵌套 <code>children[]</code> → <code>KnowledgeNode</code>（已展开过，跳过）</summary></details>

</details>

#### 响应示例

```json
{
  "id": "string",
  "kind": "folder",
  "name": "string",
  "parent_id": "string",
  "mental_model_id": "string",
  "managed": false,
  "description": "string",
  "tags": [],
  "timestamp": "string",
  "is_stale": false,
  "children": []
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=create_knowledge_folder`

---

### 更新知识库节点
<a id="update-knowledge-node"></a>

**PATCH** `/v1/default/banks/{bank_id}/knowledge-base/nodes/{node_id}`

*Rename/move a knowledge-base node or update a page's options*

Rename a node (set `name`), move it under another folder (set `parent_id`, null for the root), and/or update a page's options (`source_query`, `tags`, `max_tokens`). Changing `source_query` schedules an async refresh so the page rebuilds against the new question.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `node_id` | path | `string` | 是 | Node Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | `string?` | 否 |  |
| `parent_id` | `string?` | 否 |  |
| `source_query` | `string?` | 否 |  |
| `tags` | `array<string>?` | 否 |  |
| `max_tokens` | `integer?` | 否 |  |

#### 请求示例

```json
{
  "name": "string",
  "parent_id": "string",
  "source_query": "string",
  "tags": [
    "string"
  ],
  "max_tokens": 0
}
```

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `kind` | `"folder" \| "page"` | 是 | 节点类型：`folder` 或 `page`。 |
| `name` | `string` | 是 |  |
| `parent_id` | `string?` | 否 |  |
| `mental_model_id` | `string?` | 否 | Backing mental model id (pages only). |
| `managed` | `boolean` | 否 | Client-set flag: true = system-owned, false = hand-authored. · 默认 `false` |
| `description` | `string?` | 否 | Page source query (the page's `description`). |
| `tags` | `array<string>` | 否 | 默认 `[]` |
| `timestamp` | `string?` | 否 | Last refresh (page) or last update (folder). |
| `is_stale` | `boolean?` | 否 | Pages only, populated by the tree endpoint. False means the page is up to date — nothing in the bank has been written since its last refresh. True means it *may* need a refresh: something was written, but possibly outside the page's tags. Read the page's mental model for the exact answer. Shares the bank-stats freshness, so it can lag a just-written memory by up to a minute. |
| `children` | `array<KnowledgeNode>` | 否 | 默认 `[]` |

<details open><summary><strong>children[]</strong> · <code>KnowledgeNode</code></summary>

数据结构 `KnowledgeNode`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `kind` | `"folder" \| "page"` | 是 | 节点类型：`folder` 或 `page`。 |
| `name` | `string` | 是 |  |
| `parent_id` | `string?` | 否 |  |
| `mental_model_id` | `string?` | 否 | Backing mental model id (pages only). |
| `managed` | `boolean` | 否 | Client-set flag: true = system-owned, false = hand-authored. · 默认 `false` |
| `description` | `string?` | 否 | Page source query (the page's `description`). |
| `tags` | `array<string>` | 否 | 默认 `[]` |
| `timestamp` | `string?` | 否 | Last refresh (page) or last update (folder). |
| `is_stale` | `boolean?` | 否 | Pages only, populated by the tree endpoint. False means the page is up to date — nothing in the bank has been written since its last refresh. True means it *may* need a refresh: something was written, but possibly outside the page's tags. Read the page's mental model for the exact answer. Shares the bank-stats freshness, so it can lag a just-written memory by up to a minute. |
| `children` | `array<KnowledgeNode>` | 否 | 默认 `[]` |

<details><summary>嵌套 <code>children[]</code> → <code>KnowledgeNode</code>（已展开过，跳过）</summary></details>

</details>

#### 响应示例

```json
{
  "id": "string",
  "kind": "folder",
  "name": "string",
  "parent_id": "string",
  "mental_model_id": "string",
  "managed": false,
  "description": "string",
  "tags": [],
  "timestamp": "string",
  "is_stale": false,
  "children": []
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=update_knowledge_node`

---

### 删除知识库节点
<a id="delete-knowledge-node"></a>

**DELETE** `/v1/default/banks/{bank_id}/knowledge-base/nodes/{node_id}`

*Delete a knowledge-base node*

Delete a folder or page and its whole subtree (pages' mental models are removed too).

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `node_id` | path | `string` | 是 | Node Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

_无展开字段（标量、自由 object 或未声明 properties）_

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=delete_knowledge_node`

---

### 创建知识库页面
<a id="create-knowledge-page"></a>

**POST** `/v1/default/banks/{bank_id}/knowledge-base/pages`

*Create a knowledge-base page*

Create a page (a mental model + tree node). Content is generated asynchronously; use the returned operation_id to track completion.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | `string` | 是 |  |
| `source_query` | `string` | 是 |  |
| `parent_id` | `string?` | 否 |  |
| `tags` | `array<string>?` | 否 |  |
| `max_tokens` | `integer?` | 否 |  |
| `trigger` | `MentalModelTrigger-Input?` | 否 |  |

<details open><summary><strong>trigger</strong> · <code>MentalModelTrigger-Input</code></summary>

数据结构 `MentalModelTrigger-Input`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `mode` | `"full" \| "delta"` | 否 | Refresh mode. 'full' (default) regenerates the mental model content from scratch on each refresh. 'delta' performs surgical edits against the existing content: unchanged sections are preserved byte-for-byte, stale content is removed, new content is added. If the mental model has no existing content, or if the source_query has changed since the last refresh, delta mode falls back to a full regeneration automatically. · 默认 `"full"` |
| `refresh_after_consolidation` | `boolean` | 否 | If true, refresh this mental model after observations consolidation (real-time mode) · 默认 `false` |
| `refresh_cron` | `string?` | 否 | Cron expression (UTC, standard 5-field syntax, e.g. '0 3 * * *' for daily at 03:00 UTC) for refreshing this mental model on a fixed schedule. Mutually exclusive with refresh_after_consolidation — a model refreshes either after consolidation or on a cron schedule, not both. A scheduled refresh only runs when the model is stale (new memories in its scope since the last refresh); if nothing changed, the tick is skipped to avoid a wasted LLM call. null = no schedule. |
| `fact_types` | `array<"world" \| "experience" \| "observation">?` | 否 | Filter which fact types are retrieved during reflect. None means all types (world, experience, observation). |
| `exclude_mental_models` | `boolean` | 否 | If true, exclude all mental models from the reflect loop (skip search_mental_models tool). · 默认 `false` |
| `exclude_mental_model_ids` | `array<string>?` | 否 | Exclude specific mental models by ID from the reflect loop. |
| `tags_match` | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"?` | 否 | Override how the model's tags filter memories during refresh. If not set, defaults to 'all_strict' when the model has tags (security isolation) or 'any' when the model has no tags. Set to 'any' to include untagged memories alongside tagged ones during refresh. |
| `tag_groups` | `array<TagGroupLeaf \| TagGroupAnd-Input \| TagGroupOr-Input \| TagGroupNot-Input>?` | 否 | Compound boolean tag expressions to use during refresh instead of the model's own tags. When set, these tag groups are passed to reflect and the model's flat tags are NOT used for filtering. Supports nested and/or/not expressions for complex tag-based scoping. |
| `include_chunks` | `boolean?` | 否 | Override whether the internal recall used during refresh returns raw chunk text. None means use the bank/global config default (recall_include_chunks). |
| `recall_max_tokens` | `integer?` | 否 | Override the token budget for facts returned by the internal recall during refresh. None means use the bank/global config default (recall_max_tokens). |
| `recall_chunks_max_tokens` | `integer?` | 否 | Override the token budget for raw chunks returned by the internal recall during refresh. None means use the bank/global config default (recall_chunks_max_tokens). |
| `response_schema` | `object?` | 否 | Optional JSON Schema for structured output. When set, each refresh runs the same structured-output extraction as reflect's response_schema and stores the parsed result under reflect_response.structured_output alongside the markdown content. |
| `keep_trace` | `boolean` | 否 | If true, every refresh of this mental model records how it reached its result under reflect_response.trace: the mode it ran in and why, the resolved scope and time window, how many facts retrieval returned versus how many the agent used, the tool and LLM calls, and any delta operations. Only the latest refresh's trace is kept. This is the only way to diagnose a cron- or consolidation-driven refresh after the fact, since no human sees those run. Tool outputs are reduced to result counts to keep the stored trace bounded; use LLM request tracing for raw prompts and responses. · 默认 `false` |

</details>

#### 请求示例

```json
{
  "name": "string",
  "source_query": "string",
  "parent_id": "string",
  "tags": [
    "string"
  ],
  "max_tokens": 0,
  "trigger": {
    "mode": "full",
    "refresh_after_consolidation": false,
    "refresh_cron": "string",
    "fact_types": [
      "world"
    ],
    "exclude_mental_models": false,
    "exclude_mental_model_ids": [
      "string"
    ],
    "tags_match": "any",
    "tag_groups": [],
    "include_chunks": false,
    "recall_max_tokens": 0,
    "recall_chunks_max_tokens": 0,
    "response_schema": {},
    "keep_trace": false
  }
}
```

#### 响应

- 状态码：`201` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `page_id` | `string` | 是 |  |
| `mental_model_id` | `string` | 是 |  |
| `operation_id` | `string?` | 否 |  |

#### 响应示例

```json
{
  "page_id": "string",
  "mental_model_id": "string",
  "operation_id": "string"
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=create_knowledge_page`

---

### 读取知识库页面
<a id="get-knowledge-page"></a>

**GET** `/v1/default/banks/{bank_id}/knowledge-base/pages/{page_id}`

*Get a knowledge-base page*

Return a single page as a markdown document (frontmatter + markdown body).

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `page_id` | path | `string` | 是 | Page Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `name` | `string` | 是 |  |
| `type` | `string` | 是 | Page type — from a `type:<x>` tag, else 'knowledge-page'. |
| `description` | `string?` | 否 | The source query that rebuilds the page. |
| `tags` | `array<string>` | 否 | 默认 `[]` |
| `timestamp` | `string?` | 否 | Last refresh time (falls back to creation). |
| `body` | `string?` | 否 | The page's synthesized markdown body. |
| `markdown` | `string` | 是 | The full markdown document: YAML frontmatter + markdown body. |

#### 响应示例

```json
{
  "id": "string",
  "name": "string",
  "type": "string",
  "markdown": "string",
  "description": "string",
  "tags": [],
  "timestamp": "string",
  "body": "string"
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=get_knowledge_page`

---

### 搜索知识库页面
<a id="search-knowledge-base"></a>

**GET** `/v1/default/banks/{bank_id}/knowledge-base/search`

*Hybrid search over knowledge pages (BM25 + vector)*

Doc-level hybrid search across a bank's knowledge pages: a full-text (BM25) match and a vector-similarity match, Reciprocal-Rank-Fusion fused. No reranker — tuned for latency.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `q` | query | `string` | 是 | Search query · minLen `1` |
| `limit` | query | `integer` | 否 | Maximum results to return · 默认 `10` · ≥ `1` · ≤ `50` |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `results` | `array<KnowledgePageSearchResult>` | 是 |  |
| `total` | `integer` | 是 |  |

<details open><summary><strong>results[]</strong> · <code>KnowledgePageSearchResult</code></summary>

数据结构 `KnowledgePageSearchResult`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `name` | `string` | 是 |  |
| `mental_model_id` | `string?` | 否 |  |
| `snippet` | `string` | 是 |  |
| `score` | `number` | 是 |  |
| `updated_at` | `string?` | 否 |  |

</details>

#### 响应示例

```json
{
  "results": [
    {
      "id": "string",
      "name": "string",
      "snippet": "string",
      "score": 0,
      "mental_model_id": "string",
      "updated_at": "string"
    }
  ],
  "total": 0
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=search_knowledge_base`

---

### 获取知识库树
<a id="get-knowledge-base-tree"></a>

**GET** `/v1/default/banks/{bank_id}/knowledge-base/tree`

*Get the knowledge-base tree*

Return the knowledge base as a nested tree of folders and pages.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `roots` | `array<KnowledgeNode>` | 是 |  |

<details open><summary><strong>roots[]</strong> · <code>KnowledgeNode</code></summary>

数据结构 `KnowledgeNode`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `kind` | `"folder" \| "page"` | 是 | 节点类型：`folder` 或 `page`。 |
| `name` | `string` | 是 |  |
| `parent_id` | `string?` | 否 |  |
| `mental_model_id` | `string?` | 否 | Backing mental model id (pages only). |
| `managed` | `boolean` | 否 | Client-set flag: true = system-owned, false = hand-authored. · 默认 `false` |
| `description` | `string?` | 否 | Page source query (the page's `description`). |
| `tags` | `array<string>` | 否 | 默认 `[]` |
| `timestamp` | `string?` | 否 | Last refresh (page) or last update (folder). |
| `is_stale` | `boolean?` | 否 | Pages only, populated by the tree endpoint. False means the page is up to date — nothing in the bank has been written since its last refresh. True means it *may* need a refresh: something was written, but possibly outside the page's tags. Read the page's mental model for the exact answer. Shares the bank-stats freshness, so it can lag a just-written memory by up to a minute. |
| `children` | `array<KnowledgeNode>` | 否 | 默认 `[]` |

<details><summary>嵌套 <code>children[]</code> → <code>KnowledgeNode</code>（已展开过，跳过）</summary></details>

</details>

#### 响应示例

```json
{
  "roots": [
    {
      "id": "string",
      "kind": "folder",
      "name": "string",
      "parent_id": "string",
      "mental_model_id": "string",
      "managed": false,
      "description": "string",
      "tags": [],
      "timestamp": "string",
      "is_stale": false,
      "children": []
    }
  ]
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=get_knowledge_base_tree`

---

## Mental Models
<a id="mental-models"></a>

**心智模型** · 9 endpoints

可刷新的合成知识（多为 markdown）。可独立使用，也可挂到 KB page。

### 本章目录

| Method | Path | 标题 |
| --- | --- | --- |
| `GET` | `/v1/default/banks/{bank_id}/mental-models` | [列出心智模型](#list-mental-models) |
| `POST` | `/v1/default/banks/{bank_id}/mental-models` | [创建心智模型](#create-mental-model) |
| `GET` | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}` | [获取心智模型](#get-mental-model) |
| `PATCH` | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}` | [更新心智模型](#update-mental-model) |
| `DELETE` | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}` | [删除心智模型](#delete-mental-model) |
| `POST` | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/clear` | [清空心智模型正文](#clear-mental-model) |
| `POST` | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/dry-run-refresh` | [Dry-run mental model refresh (preview, no persistence)](#dry-run-refresh-mental-model) |
| `GET` | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/history` | [心智模型历史](#get-mental-model-history) |
| `POST` | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/refresh` | [刷新心智模型](#refresh-mental-model) |

### 列出心智模型
<a id="list-mental-models"></a>

**GET** `/v1/default/banks/{bank_id}/mental-models`

*List mental models*

List user-curated living documents that stay current.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `tags` | query | `array<string>?` | 否 | Filter by tags |
| `tags_match` | query | `"any" \| "all" \| "exact"` | 否 | How to match tags · 默认 `"any"` |
| `detail` | query | `"metadata" \| "content" \| "full"` | 否 | Detail level: 'metadata' (names/tags only), 'content' (adds content/config), 'full' (includes reflect_response) · 默认 `"full"` |
| `limit` | query | `integer` | 否 | 默认 `100` · ≥ `1` · ≤ `1000` |
| `offset` | query | `integer` | 否 | 默认 `0` · ≥ `0` |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `items` | `array<MentalModelResponse>` | 是 |  |

<details open><summary><strong>items[]</strong> · <code>MentalModelResponse</code></summary>

数据结构 `MentalModelResponse`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `bank_id` | `string` | 是 |  |
| `name` | `string` | 是 |  |
| `source_query` | `string?` | 否 |  |
| `content` | `string?` | 否 | The mental model content as well-formatted markdown (auto-generated from reflect endpoint) |
| `tags` | `array<string>` | 否 | 默认 `[]` |
| `max_tokens` | `integer?` | 否 |  |
| `trigger` | `MentalModelTrigger-Output?` | 否 |  |
| `last_refreshed_at` | `string?` | 否 |  |
| `created_at` | `string?` | 否 |  |
| `reflect_response` | `object?` | 否 | Full reflect API response payload including based_on facts and observations |
| `is_stale` | `boolean?` | 否 | True when memories matching this mental model's tag/fact_type scope have been written since last_refreshed_at. Exact, and costly to compute, so it is populated only by the single mental-model read at detail=full — never when listing. For a whole list, compare each `last_refreshed_at` against the bank's `last_memory_write_at` from GET /stats: at or after it means up to date, older means it may need a refresh. |

<details open><summary><strong>trigger</strong> · <code>MentalModelTrigger-Output</code></summary>

数据结构 `MentalModelTrigger-Output`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `mode` | `"full" \| "delta"` | 否 | Refresh mode. 'full' (default) regenerates the mental model content from scratch on each refresh. 'delta' performs surgical edits against the existing content: unchanged sections are preserved byte-for-byte, stale content is removed, new content is added. If the mental model has no existing content, or if the source_query has changed since the last refresh, delta mode falls back to a full regeneration automatically. · 默认 `"full"` |
| `refresh_after_consolidation` | `boolean` | 否 | If true, refresh this mental model after observations consolidation (real-time mode) · 默认 `false` |
| `refresh_cron` | `string?` | 否 | Cron expression (UTC, standard 5-field syntax, e.g. '0 3 * * *' for daily at 03:00 UTC) for refreshing this mental model on a fixed schedule. Mutually exclusive with refresh_after_consolidation — a model refreshes either after consolidation or on a cron schedule, not both. A scheduled refresh only runs when the model is stale (new memories in its scope since the last refresh); if nothing changed, the tick is skipped to avoid a wasted LLM call. null = no schedule. |
| `fact_types` | `array<"world" \| "experience" \| "observation">?` | 否 | Filter which fact types are retrieved during reflect. None means all types (world, experience, observation). |
| `exclude_mental_models` | `boolean` | 否 | If true, exclude all mental models from the reflect loop (skip search_mental_models tool). · 默认 `false` |
| `exclude_mental_model_ids` | `array<string>?` | 否 | Exclude specific mental models by ID from the reflect loop. |
| `tags_match` | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"?` | 否 | Override how the model's tags filter memories during refresh. If not set, defaults to 'all_strict' when the model has tags (security isolation) or 'any' when the model has no tags. Set to 'any' to include untagged memories alongside tagged ones during refresh. |
| `tag_groups` | `array<TagGroupLeaf \| TagGroupAnd-Output \| TagGroupOr-Output \| TagGroupNot-Output>?` | 否 | Compound boolean tag expressions to use during refresh instead of the model's own tags. When set, these tag groups are passed to reflect and the model's flat tags are NOT used for filtering. Supports nested and/or/not expressions for complex tag-based scoping. |
| `include_chunks` | `boolean?` | 否 | Override whether the internal recall used during refresh returns raw chunk text. None means use the bank/global config default (recall_include_chunks). |
| `recall_max_tokens` | `integer?` | 否 | Override the token budget for facts returned by the internal recall during refresh. None means use the bank/global config default (recall_max_tokens). |
| `recall_chunks_max_tokens` | `integer?` | 否 | Override the token budget for raw chunks returned by the internal recall during refresh. None means use the bank/global config default (recall_chunks_max_tokens). |
| `response_schema` | `object?` | 否 | Optional JSON Schema for structured output. When set, each refresh runs the same structured-output extraction as reflect's response_schema and stores the parsed result under reflect_response.structured_output alongside the markdown content. |
| `keep_trace` | `boolean` | 否 | If true, every refresh of this mental model records how it reached its result under reflect_response.trace: the mode it ran in and why, the resolved scope and time window, how many facts retrieval returned versus how many the agent used, the tool and LLM calls, and any delta operations. Only the latest refresh's trace is kept. This is the only way to diagnose a cron- or consolidation-driven refresh after the fact, since no human sees those run. Tool outputs are reduced to result counts to keep the stored trace bounded; use LLM request tracing for raw prompts and responses. · 默认 `false` |

</details>

</details>

#### 响应示例

```json
{
  "items": [
    {
      "id": "string",
      "bank_id": "string",
      "name": "string",
      "source_query": "string",
      "content": "string",
      "tags": [],
      "max_tokens": 0,
      "trigger": {
        "mode": "full",
        "refresh_after_consolidation": false,
        "refresh_cron": "string",
        "fact_types": [],
        "exclude_mental_models": false,
        "exclude_mental_model_ids": [],
        "tags_match": "any",
        "tag_groups": [],
        "include_chunks": false,
        "recall_max_tokens": 0,
        "recall_chunks_max_tokens": 0,
        "response_schema": {},
        "keep_trace": false
      },
      "last_refreshed_at": "string",
      "created_at": "string",
      "reflect_response": {},
      "is_stale": false
    }
  ]
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=list_mental_models`

---

### 创建心智模型
<a id="create-mental-model"></a>

**POST** `/v1/default/banks/{bank_id}/mental-models`

*Create mental model*

Create a mental model by running reflect with the source query in the background. Returns an operation ID to track progress. The content is auto-generated by the reflect endpoint. Use the operations endpoint to check completion status.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string?` | 否 | Optional custom ID for the mental model (alphanumeric lowercase with hyphens) |
| `name` | `string` | 是 | Human-readable name for the mental model |
| `source_query` | `string` | 是 | The query to run to generate content |
| `tags` | `array<string>` | 否 | Tags for scoped visibility · 默认 `[]` |
| `max_tokens` | `integer` | 否 | Maximum tokens for generated content · 默认 `2048` · ≥ `256.0` · ≤ `8192.0` |
| `trigger` | `MentalModelTrigger-Input` | 否 | Trigger settings · 默认 `{}` |

<details open><summary><strong>trigger</strong> · <code>MentalModelTrigger-Input</code></summary>

数据结构 `MentalModelTrigger-Input`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `mode` | `"full" \| "delta"` | 否 | Refresh mode. 'full' (default) regenerates the mental model content from scratch on each refresh. 'delta' performs surgical edits against the existing content: unchanged sections are preserved byte-for-byte, stale content is removed, new content is added. If the mental model has no existing content, or if the source_query has changed since the last refresh, delta mode falls back to a full regeneration automatically. · 默认 `"full"` |
| `refresh_after_consolidation` | `boolean` | 否 | If true, refresh this mental model after observations consolidation (real-time mode) · 默认 `false` |
| `refresh_cron` | `string?` | 否 | Cron expression (UTC, standard 5-field syntax, e.g. '0 3 * * *' for daily at 03:00 UTC) for refreshing this mental model on a fixed schedule. Mutually exclusive with refresh_after_consolidation — a model refreshes either after consolidation or on a cron schedule, not both. A scheduled refresh only runs when the model is stale (new memories in its scope since the last refresh); if nothing changed, the tick is skipped to avoid a wasted LLM call. null = no schedule. |
| `fact_types` | `array<"world" \| "experience" \| "observation">?` | 否 | Filter which fact types are retrieved during reflect. None means all types (world, experience, observation). |
| `exclude_mental_models` | `boolean` | 否 | If true, exclude all mental models from the reflect loop (skip search_mental_models tool). · 默认 `false` |
| `exclude_mental_model_ids` | `array<string>?` | 否 | Exclude specific mental models by ID from the reflect loop. |
| `tags_match` | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"?` | 否 | Override how the model's tags filter memories during refresh. If not set, defaults to 'all_strict' when the model has tags (security isolation) or 'any' when the model has no tags. Set to 'any' to include untagged memories alongside tagged ones during refresh. |
| `tag_groups` | `array<TagGroupLeaf \| TagGroupAnd-Input \| TagGroupOr-Input \| TagGroupNot-Input>?` | 否 | Compound boolean tag expressions to use during refresh instead of the model's own tags. When set, these tag groups are passed to reflect and the model's flat tags are NOT used for filtering. Supports nested and/or/not expressions for complex tag-based scoping. |
| `include_chunks` | `boolean?` | 否 | Override whether the internal recall used during refresh returns raw chunk text. None means use the bank/global config default (recall_include_chunks). |
| `recall_max_tokens` | `integer?` | 否 | Override the token budget for facts returned by the internal recall during refresh. None means use the bank/global config default (recall_max_tokens). |
| `recall_chunks_max_tokens` | `integer?` | 否 | Override the token budget for raw chunks returned by the internal recall during refresh. None means use the bank/global config default (recall_chunks_max_tokens). |
| `response_schema` | `object?` | 否 | Optional JSON Schema for structured output. When set, each refresh runs the same structured-output extraction as reflect's response_schema and stores the parsed result under reflect_response.structured_output alongside the markdown content. |
| `keep_trace` | `boolean` | 否 | If true, every refresh of this mental model records how it reached its result under reflect_response.trace: the mode it ran in and why, the resolved scope and time window, how many facts retrieval returned versus how many the agent used, the tool and LLM calls, and any delta operations. Only the latest refresh's trace is kept. This is the only way to diagnose a cron- or consolidation-driven refresh after the fact, since no human sees those run. Tool outputs are reduced to result counts to keep the stored trace bounded; use LLM request tracing for raw prompts and responses. · 默认 `false` |

</details>

#### 请求示例

```json
{
  "id": "team-communication",
  "max_tokens": 2048,
  "name": "Team Communication Preferences",
  "source_query": "How does the team prefer to communicate?",
  "tags": [
    "team"
  ],
  "trigger": {
    "refresh_after_consolidation": false
  }
}
```

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `mental_model_id` | `string?` | 否 | ID of the created mental model |
| `operation_id` | `string` | 是 | Operation ID to track refresh progress |

#### 响应示例

```json
{
  "operation_id": "string",
  "mental_model_id": "string"
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=create_mental_model`

---

### 获取心智模型
<a id="get-mental-model"></a>

**GET** `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}`

*Get mental model*

Get a specific mental model by ID.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `mental_model_id` | path | `string` | 是 | Mental Model Id |
| `detail` | query | `"metadata" \| "content" \| "full"` | 否 | Detail level: 'metadata' (names/tags only), 'content' (adds content/config), 'full' (includes reflect_response) · 默认 `"full"` |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `bank_id` | `string` | 是 |  |
| `name` | `string` | 是 |  |
| `source_query` | `string?` | 否 |  |
| `content` | `string?` | 否 | The mental model content as well-formatted markdown (auto-generated from reflect endpoint) |
| `tags` | `array<string>` | 否 | 默认 `[]` |
| `max_tokens` | `integer?` | 否 |  |
| `trigger` | `MentalModelTrigger-Output?` | 否 |  |
| `last_refreshed_at` | `string?` | 否 |  |
| `created_at` | `string?` | 否 |  |
| `reflect_response` | `object?` | 否 | Full reflect API response payload including based_on facts and observations |
| `is_stale` | `boolean?` | 否 | True when memories matching this mental model's tag/fact_type scope have been written since last_refreshed_at. Exact, and costly to compute, so it is populated only by the single mental-model read at detail=full — never when listing. For a whole list, compare each `last_refreshed_at` against the bank's `last_memory_write_at` from GET /stats: at or after it means up to date, older means it may need a refresh. |

<details open><summary><strong>trigger</strong> · <code>MentalModelTrigger-Output</code></summary>

数据结构 `MentalModelTrigger-Output`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `mode` | `"full" \| "delta"` | 否 | Refresh mode. 'full' (default) regenerates the mental model content from scratch on each refresh. 'delta' performs surgical edits against the existing content: unchanged sections are preserved byte-for-byte, stale content is removed, new content is added. If the mental model has no existing content, or if the source_query has changed since the last refresh, delta mode falls back to a full regeneration automatically. · 默认 `"full"` |
| `refresh_after_consolidation` | `boolean` | 否 | If true, refresh this mental model after observations consolidation (real-time mode) · 默认 `false` |
| `refresh_cron` | `string?` | 否 | Cron expression (UTC, standard 5-field syntax, e.g. '0 3 * * *' for daily at 03:00 UTC) for refreshing this mental model on a fixed schedule. Mutually exclusive with refresh_after_consolidation — a model refreshes either after consolidation or on a cron schedule, not both. A scheduled refresh only runs when the model is stale (new memories in its scope since the last refresh); if nothing changed, the tick is skipped to avoid a wasted LLM call. null = no schedule. |
| `fact_types` | `array<"world" \| "experience" \| "observation">?` | 否 | Filter which fact types are retrieved during reflect. None means all types (world, experience, observation). |
| `exclude_mental_models` | `boolean` | 否 | If true, exclude all mental models from the reflect loop (skip search_mental_models tool). · 默认 `false` |
| `exclude_mental_model_ids` | `array<string>?` | 否 | Exclude specific mental models by ID from the reflect loop. |
| `tags_match` | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"?` | 否 | Override how the model's tags filter memories during refresh. If not set, defaults to 'all_strict' when the model has tags (security isolation) or 'any' when the model has no tags. Set to 'any' to include untagged memories alongside tagged ones during refresh. |
| `tag_groups` | `array<TagGroupLeaf \| TagGroupAnd-Output \| TagGroupOr-Output \| TagGroupNot-Output>?` | 否 | Compound boolean tag expressions to use during refresh instead of the model's own tags. When set, these tag groups are passed to reflect and the model's flat tags are NOT used for filtering. Supports nested and/or/not expressions for complex tag-based scoping. |
| `include_chunks` | `boolean?` | 否 | Override whether the internal recall used during refresh returns raw chunk text. None means use the bank/global config default (recall_include_chunks). |
| `recall_max_tokens` | `integer?` | 否 | Override the token budget for facts returned by the internal recall during refresh. None means use the bank/global config default (recall_max_tokens). |
| `recall_chunks_max_tokens` | `integer?` | 否 | Override the token budget for raw chunks returned by the internal recall during refresh. None means use the bank/global config default (recall_chunks_max_tokens). |
| `response_schema` | `object?` | 否 | Optional JSON Schema for structured output. When set, each refresh runs the same structured-output extraction as reflect's response_schema and stores the parsed result under reflect_response.structured_output alongside the markdown content. |
| `keep_trace` | `boolean` | 否 | If true, every refresh of this mental model records how it reached its result under reflect_response.trace: the mode it ran in and why, the resolved scope and time window, how many facts retrieval returned versus how many the agent used, the tool and LLM calls, and any delta operations. Only the latest refresh's trace is kept. This is the only way to diagnose a cron- or consolidation-driven refresh after the fact, since no human sees those run. Tool outputs are reduced to result counts to keep the stored trace bounded; use LLM request tracing for raw prompts and responses. · 默认 `false` |

</details>

#### 响应示例

```json
{
  "id": "string",
  "bank_id": "string",
  "name": "string",
  "source_query": "string",
  "content": "string",
  "tags": [],
  "max_tokens": 0,
  "trigger": {
    "mode": "full",
    "refresh_after_consolidation": false,
    "refresh_cron": "string",
    "fact_types": [
      "world"
    ],
    "exclude_mental_models": false,
    "exclude_mental_model_ids": [
      "string"
    ],
    "tags_match": "any",
    "tag_groups": [],
    "include_chunks": false,
    "recall_max_tokens": 0,
    "recall_chunks_max_tokens": 0,
    "response_schema": {},
    "keep_trace": false
  },
  "last_refreshed_at": "string",
  "created_at": "string",
  "reflect_response": {},
  "is_stale": false
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=get_mental_model`

---

### 更新心智模型
<a id="update-mental-model"></a>

**PATCH** `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}`

*Update mental model*

Update a mental model's name and/or source query.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `mental_model_id` | path | `string` | 是 | Mental Model Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | `string?` | 否 | New name for the mental model |
| `source_query` | `string?` | 否 | New source query for the mental model |
| `max_tokens` | `integer?` | 否 | Maximum tokens for generated content · ≥ `256.0` · ≤ `8192.0` |
| `tags` | `array<string>?` | 否 | Tags for scoped visibility |
| `trigger` | `MentalModelTrigger-Input?` | 否 | Trigger settings |

<details open><summary><strong>trigger</strong> · <code>MentalModelTrigger-Input</code></summary>

数据结构 `MentalModelTrigger-Input`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `mode` | `"full" \| "delta"` | 否 | Refresh mode. 'full' (default) regenerates the mental model content from scratch on each refresh. 'delta' performs surgical edits against the existing content: unchanged sections are preserved byte-for-byte, stale content is removed, new content is added. If the mental model has no existing content, or if the source_query has changed since the last refresh, delta mode falls back to a full regeneration automatically. · 默认 `"full"` |
| `refresh_after_consolidation` | `boolean` | 否 | If true, refresh this mental model after observations consolidation (real-time mode) · 默认 `false` |
| `refresh_cron` | `string?` | 否 | Cron expression (UTC, standard 5-field syntax, e.g. '0 3 * * *' for daily at 03:00 UTC) for refreshing this mental model on a fixed schedule. Mutually exclusive with refresh_after_consolidation — a model refreshes either after consolidation or on a cron schedule, not both. A scheduled refresh only runs when the model is stale (new memories in its scope since the last refresh); if nothing changed, the tick is skipped to avoid a wasted LLM call. null = no schedule. |
| `fact_types` | `array<"world" \| "experience" \| "observation">?` | 否 | Filter which fact types are retrieved during reflect. None means all types (world, experience, observation). |
| `exclude_mental_models` | `boolean` | 否 | If true, exclude all mental models from the reflect loop (skip search_mental_models tool). · 默认 `false` |
| `exclude_mental_model_ids` | `array<string>?` | 否 | Exclude specific mental models by ID from the reflect loop. |
| `tags_match` | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"?` | 否 | Override how the model's tags filter memories during refresh. If not set, defaults to 'all_strict' when the model has tags (security isolation) or 'any' when the model has no tags. Set to 'any' to include untagged memories alongside tagged ones during refresh. |
| `tag_groups` | `array<TagGroupLeaf \| TagGroupAnd-Input \| TagGroupOr-Input \| TagGroupNot-Input>?` | 否 | Compound boolean tag expressions to use during refresh instead of the model's own tags. When set, these tag groups are passed to reflect and the model's flat tags are NOT used for filtering. Supports nested and/or/not expressions for complex tag-based scoping. |
| `include_chunks` | `boolean?` | 否 | Override whether the internal recall used during refresh returns raw chunk text. None means use the bank/global config default (recall_include_chunks). |
| `recall_max_tokens` | `integer?` | 否 | Override the token budget for facts returned by the internal recall during refresh. None means use the bank/global config default (recall_max_tokens). |
| `recall_chunks_max_tokens` | `integer?` | 否 | Override the token budget for raw chunks returned by the internal recall during refresh. None means use the bank/global config default (recall_chunks_max_tokens). |
| `response_schema` | `object?` | 否 | Optional JSON Schema for structured output. When set, each refresh runs the same structured-output extraction as reflect's response_schema and stores the parsed result under reflect_response.structured_output alongside the markdown content. |
| `keep_trace` | `boolean` | 否 | If true, every refresh of this mental model records how it reached its result under reflect_response.trace: the mode it ran in and why, the resolved scope and time window, how many facts retrieval returned versus how many the agent used, the tool and LLM calls, and any delta operations. Only the latest refresh's trace is kept. This is the only way to diagnose a cron- or consolidation-driven refresh after the fact, since no human sees those run. Tool outputs are reduced to result counts to keep the stored trace bounded; use LLM request tracing for raw prompts and responses. · 默认 `false` |

</details>

#### 请求示例

```json
{
  "max_tokens": 4096,
  "name": "Updated Team Communication Preferences",
  "source_query": "How does the team prefer to communicate?",
  "tags": [
    "team",
    "communication"
  ],
  "trigger": {
    "refresh_after_consolidation": true
  }
}
```

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `bank_id` | `string` | 是 |  |
| `name` | `string` | 是 |  |
| `source_query` | `string?` | 否 |  |
| `content` | `string?` | 否 | The mental model content as well-formatted markdown (auto-generated from reflect endpoint) |
| `tags` | `array<string>` | 否 | 默认 `[]` |
| `max_tokens` | `integer?` | 否 |  |
| `trigger` | `MentalModelTrigger-Output?` | 否 |  |
| `last_refreshed_at` | `string?` | 否 |  |
| `created_at` | `string?` | 否 |  |
| `reflect_response` | `object?` | 否 | Full reflect API response payload including based_on facts and observations |
| `is_stale` | `boolean?` | 否 | True when memories matching this mental model's tag/fact_type scope have been written since last_refreshed_at. Exact, and costly to compute, so it is populated only by the single mental-model read at detail=full — never when listing. For a whole list, compare each `last_refreshed_at` against the bank's `last_memory_write_at` from GET /stats: at or after it means up to date, older means it may need a refresh. |

<details open><summary><strong>trigger</strong> · <code>MentalModelTrigger-Output</code></summary>

数据结构 `MentalModelTrigger-Output`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `mode` | `"full" \| "delta"` | 否 | Refresh mode. 'full' (default) regenerates the mental model content from scratch on each refresh. 'delta' performs surgical edits against the existing content: unchanged sections are preserved byte-for-byte, stale content is removed, new content is added. If the mental model has no existing content, or if the source_query has changed since the last refresh, delta mode falls back to a full regeneration automatically. · 默认 `"full"` |
| `refresh_after_consolidation` | `boolean` | 否 | If true, refresh this mental model after observations consolidation (real-time mode) · 默认 `false` |
| `refresh_cron` | `string?` | 否 | Cron expression (UTC, standard 5-field syntax, e.g. '0 3 * * *' for daily at 03:00 UTC) for refreshing this mental model on a fixed schedule. Mutually exclusive with refresh_after_consolidation — a model refreshes either after consolidation or on a cron schedule, not both. A scheduled refresh only runs when the model is stale (new memories in its scope since the last refresh); if nothing changed, the tick is skipped to avoid a wasted LLM call. null = no schedule. |
| `fact_types` | `array<"world" \| "experience" \| "observation">?` | 否 | Filter which fact types are retrieved during reflect. None means all types (world, experience, observation). |
| `exclude_mental_models` | `boolean` | 否 | If true, exclude all mental models from the reflect loop (skip search_mental_models tool). · 默认 `false` |
| `exclude_mental_model_ids` | `array<string>?` | 否 | Exclude specific mental models by ID from the reflect loop. |
| `tags_match` | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"?` | 否 | Override how the model's tags filter memories during refresh. If not set, defaults to 'all_strict' when the model has tags (security isolation) or 'any' when the model has no tags. Set to 'any' to include untagged memories alongside tagged ones during refresh. |
| `tag_groups` | `array<TagGroupLeaf \| TagGroupAnd-Output \| TagGroupOr-Output \| TagGroupNot-Output>?` | 否 | Compound boolean tag expressions to use during refresh instead of the model's own tags. When set, these tag groups are passed to reflect and the model's flat tags are NOT used for filtering. Supports nested and/or/not expressions for complex tag-based scoping. |
| `include_chunks` | `boolean?` | 否 | Override whether the internal recall used during refresh returns raw chunk text. None means use the bank/global config default (recall_include_chunks). |
| `recall_max_tokens` | `integer?` | 否 | Override the token budget for facts returned by the internal recall during refresh. None means use the bank/global config default (recall_max_tokens). |
| `recall_chunks_max_tokens` | `integer?` | 否 | Override the token budget for raw chunks returned by the internal recall during refresh. None means use the bank/global config default (recall_chunks_max_tokens). |
| `response_schema` | `object?` | 否 | Optional JSON Schema for structured output. When set, each refresh runs the same structured-output extraction as reflect's response_schema and stores the parsed result under reflect_response.structured_output alongside the markdown content. |
| `keep_trace` | `boolean` | 否 | If true, every refresh of this mental model records how it reached its result under reflect_response.trace: the mode it ran in and why, the resolved scope and time window, how many facts retrieval returned versus how many the agent used, the tool and LLM calls, and any delta operations. Only the latest refresh's trace is kept. This is the only way to diagnose a cron- or consolidation-driven refresh after the fact, since no human sees those run. Tool outputs are reduced to result counts to keep the stored trace bounded; use LLM request tracing for raw prompts and responses. · 默认 `false` |

</details>

#### 响应示例

```json
{
  "id": "string",
  "bank_id": "string",
  "name": "string",
  "source_query": "string",
  "content": "string",
  "tags": [],
  "max_tokens": 0,
  "trigger": {
    "mode": "full",
    "refresh_after_consolidation": false,
    "refresh_cron": "string",
    "fact_types": [
      "world"
    ],
    "exclude_mental_models": false,
    "exclude_mental_model_ids": [
      "string"
    ],
    "tags_match": "any",
    "tag_groups": [],
    "include_chunks": false,
    "recall_max_tokens": 0,
    "recall_chunks_max_tokens": 0,
    "response_schema": {},
    "keep_trace": false
  },
  "last_refreshed_at": "string",
  "created_at": "string",
  "reflect_response": {},
  "is_stale": false
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=update_mental_model`

---

### 删除心智模型
<a id="delete-mental-model"></a>

**DELETE** `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}`

*Delete mental model*

Delete a mental model.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `mental_model_id` | path | `string` | 是 | Mental Model Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

_无展开字段（标量、自由 object 或未声明 properties）_

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=delete_mental_model`

---

### 清空心智模型正文
<a id="clear-mental-model"></a>

**POST** `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/clear`

*Clear mental model content*

Clear a mental model's content so the next refresh performs a full re-synthesis. This is useful for delta-mode models that have accumulated drift over many incremental refreshes. After clearing, call the /refresh endpoint to trigger a clean full rebuild.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `mental_model_id` | path | `string` | 是 | Mental Model Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `bank_id` | `string` | 是 |  |
| `name` | `string` | 是 |  |
| `source_query` | `string?` | 否 |  |
| `content` | `string?` | 否 | The mental model content as well-formatted markdown (auto-generated from reflect endpoint) |
| `tags` | `array<string>` | 否 | 默认 `[]` |
| `max_tokens` | `integer?` | 否 |  |
| `trigger` | `MentalModelTrigger-Output?` | 否 |  |
| `last_refreshed_at` | `string?` | 否 |  |
| `created_at` | `string?` | 否 |  |
| `reflect_response` | `object?` | 否 | Full reflect API response payload including based_on facts and observations |
| `is_stale` | `boolean?` | 否 | True when memories matching this mental model's tag/fact_type scope have been written since last_refreshed_at. Exact, and costly to compute, so it is populated only by the single mental-model read at detail=full — never when listing. For a whole list, compare each `last_refreshed_at` against the bank's `last_memory_write_at` from GET /stats: at or after it means up to date, older means it may need a refresh. |

<details open><summary><strong>trigger</strong> · <code>MentalModelTrigger-Output</code></summary>

数据结构 `MentalModelTrigger-Output`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `mode` | `"full" \| "delta"` | 否 | Refresh mode. 'full' (default) regenerates the mental model content from scratch on each refresh. 'delta' performs surgical edits against the existing content: unchanged sections are preserved byte-for-byte, stale content is removed, new content is added. If the mental model has no existing content, or if the source_query has changed since the last refresh, delta mode falls back to a full regeneration automatically. · 默认 `"full"` |
| `refresh_after_consolidation` | `boolean` | 否 | If true, refresh this mental model after observations consolidation (real-time mode) · 默认 `false` |
| `refresh_cron` | `string?` | 否 | Cron expression (UTC, standard 5-field syntax, e.g. '0 3 * * *' for daily at 03:00 UTC) for refreshing this mental model on a fixed schedule. Mutually exclusive with refresh_after_consolidation — a model refreshes either after consolidation or on a cron schedule, not both. A scheduled refresh only runs when the model is stale (new memories in its scope since the last refresh); if nothing changed, the tick is skipped to avoid a wasted LLM call. null = no schedule. |
| `fact_types` | `array<"world" \| "experience" \| "observation">?` | 否 | Filter which fact types are retrieved during reflect. None means all types (world, experience, observation). |
| `exclude_mental_models` | `boolean` | 否 | If true, exclude all mental models from the reflect loop (skip search_mental_models tool). · 默认 `false` |
| `exclude_mental_model_ids` | `array<string>?` | 否 | Exclude specific mental models by ID from the reflect loop. |
| `tags_match` | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"?` | 否 | Override how the model's tags filter memories during refresh. If not set, defaults to 'all_strict' when the model has tags (security isolation) or 'any' when the model has no tags. Set to 'any' to include untagged memories alongside tagged ones during refresh. |
| `tag_groups` | `array<TagGroupLeaf \| TagGroupAnd-Output \| TagGroupOr-Output \| TagGroupNot-Output>?` | 否 | Compound boolean tag expressions to use during refresh instead of the model's own tags. When set, these tag groups are passed to reflect and the model's flat tags are NOT used for filtering. Supports nested and/or/not expressions for complex tag-based scoping. |
| `include_chunks` | `boolean?` | 否 | Override whether the internal recall used during refresh returns raw chunk text. None means use the bank/global config default (recall_include_chunks). |
| `recall_max_tokens` | `integer?` | 否 | Override the token budget for facts returned by the internal recall during refresh. None means use the bank/global config default (recall_max_tokens). |
| `recall_chunks_max_tokens` | `integer?` | 否 | Override the token budget for raw chunks returned by the internal recall during refresh. None means use the bank/global config default (recall_chunks_max_tokens). |
| `response_schema` | `object?` | 否 | Optional JSON Schema for structured output. When set, each refresh runs the same structured-output extraction as reflect's response_schema and stores the parsed result under reflect_response.structured_output alongside the markdown content. |
| `keep_trace` | `boolean` | 否 | If true, every refresh of this mental model records how it reached its result under reflect_response.trace: the mode it ran in and why, the resolved scope and time window, how many facts retrieval returned versus how many the agent used, the tool and LLM calls, and any delta operations. Only the latest refresh's trace is kept. This is the only way to diagnose a cron- or consolidation-driven refresh after the fact, since no human sees those run. Tool outputs are reduced to result counts to keep the stored trace bounded; use LLM request tracing for raw prompts and responses. · 默认 `false` |

</details>

#### 响应示例

```json
{
  "id": "string",
  "bank_id": "string",
  "name": "string",
  "source_query": "string",
  "content": "string",
  "tags": [],
  "max_tokens": 0,
  "trigger": {
    "mode": "full",
    "refresh_after_consolidation": false,
    "refresh_cron": "string",
    "fact_types": [
      "world"
    ],
    "exclude_mental_models": false,
    "exclude_mental_model_ids": [
      "string"
    ],
    "tags_match": "any",
    "tag_groups": [],
    "include_chunks": false,
    "recall_max_tokens": 0,
    "recall_chunks_max_tokens": 0,
    "response_schema": {},
    "keep_trace": false
  },
  "last_refreshed_at": "string",
  "created_at": "string",
  "reflect_response": {},
  "is_stale": false
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=clear_mental_model`

---

### Dry-run mental model refresh (preview, no persistence)
<a id="dry-run-refresh-mental-model"></a>

**POST** `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/dry-run-refresh`

Preview what a refresh would do to this mental model WITHOUT changing it — no content, structured document, watermark, or last_refreshed_at is written. Returns the mode the refresh ran in and why (delta silently falls back to full when there is no baseline or the source query changed), the resolved tag scope and time window it read, how many facts retrieval returned versus how many the reflect agent actually used, the delta operations it emitted, and a unified diff from the stored content to the content it would write.

This is the production refresh pipeline with two writes skipped — the content and the watermark — and nothing about it is configurable, so what it reports is what the next refresh will do. Because nothing is persisted, a delta dry run reads exactly the window the next real refresh would, and repeating it reads that same window again.

It costs the same LLM tokens as a refresh and is validated the same way.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `mental_model_id` | path | `string` | 是 | Mental Model Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `mental_model_id` | `string` | 是 | The mental model previewed. |
| `name` | `string` | 是 | Display name of the mental model. |
| `requested_mode` | `"full" \| "delta"` | 是 | The mode asked for (from the model's trigger, or overridden). |
| `effective_mode` | `"full" \| "delta"` | 是 | The mode the refresh actually ran in. |
| `mode_fallback_reason` | `"no_baseline_content" \| "source_query_changed" \| "structured_doc_unreadable" \| "delta_ops_failed" \| "delta_ops_all_skipped"?` | 否 | Why delta was requested but not applied, if that happened. |
| `outcome` | `"content_written" \| "content_preserved_no_new_facts" \| "refresh_failed_empty_candidate" \| "refresh_failed_delta_not_applied"` | 是 | What a real refresh would do with the document. |
| `would_persist` | `boolean` | 是 | Whether a real refresh would write new content. |
| `scope` | `MentalModelRefreshScope` | 是 | The resolved memory scope. |
| `window` | `MentalModelRefreshWindow` | 是 | The snapshot window read from. |
| `facts` | `MentalModelFactCounts` | 是 | Facts retrieved versus actually used. |
| `based_on` | `map<string, array<object>>` | 否 | The evidence this run would ground the document on, keyed by fact type — the same shape a refresh persists under reflect_response.based_on. Returned so a preview can show its sources without having to write them anywhere. |
| `current_content` | `string` | 是 | The model's content as it stands now. |
| `candidate_content` | `string` | 是 | Raw reflect synthesis, before any delta operations. |
| `preview_content` | `string` | 是 | The content a real refresh would store: the delta-edited document, or the candidate in full mode. |
| `diff` | `string` | 是 | Unified diff from current_content to preview_content. Empty when identical. |
| `delta_operations` | `MentalModelDeltaOperations?` | 否 | Structured operations emitted, in delta mode. |
| `trace` | `MentalModelRefreshTrace` | 是 | Execution trace of the run, always included for a dry run. |
| `usage` | `TokenUsage` | 否 | Token usage across the run's LLM calls. |
| `duration_ms` | `integer` | 否 | Wall-clock duration of the run. · 默认 `0` |
| `warnings` | `array<string>` | 否 | Conditions worth a human's attention, in plain language. |

<details open><summary><strong>scope</strong> · <code>MentalModelRefreshScope</code></summary>

数据结构 `MentalModelRefreshScope`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `tags` | `array<string>?` | 否 | Flat tags used to filter memories (null when unused). |
| `tags_match` | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"` | 是 | Resolved tag match mode. |
| `tag_groups` | `array<TagGroupLeaf \| TagGroupAnd-Output \| TagGroupOr-Output \| TagGroupNot-Output>?` | 否 | Compound tag expressions used instead of flat tags, when set. |
| `fact_types` | `array<string>?` | 否 | Fact types retrieved (null means all). |
| `exclude_mental_models` | `boolean` | 是 | Whether other mental models were excluded from the reflect loop. |
| `exclude_mental_model_ids` | `array<string>` | 否 | Mental models excluded by ID (always includes the model being refreshed). |

</details>

<details open><summary><strong>window</strong> · <code>MentalModelRefreshWindow</code></summary>

数据结构 `MentalModelRefreshWindow`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `created_after` | `string(date-time)?` | 否 | Lower bound on memory creation time. Set only in delta mode, where it is the model's last_refreshed_at — so a delta refresh only sees memories newer than the last one. |
| `created_before` | `string(date-time)` | 是 | Database-time snapshot bounding the refresh. Memories committed after this are not read, so they stay newer than the persisted watermark and are caught by the next refresh. |
| `watermark` | `string(date-time)?` | 否 | The last_refreshed_at a real refresh would persist: the newest in-scope memory visible at the snapshot, not now(). Null means no in-scope memory was visible. |

</details>

<details open><summary><strong>facts</strong> · <code>MentalModelFactCounts</code></summary>

数据结构 `MentalModelFactCounts`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `retrieved` | `map<string, integer>` | 否 | Facts the reflect agent's tool calls returned, by fact type. |
| `used` | `map<string, integer>` | 否 | Facts the agent declared it actually based the answer on, by fact type. |

</details>

<details open><summary><strong>delta_operations</strong> · <code>MentalModelDeltaOperations</code></summary>

数据结构 `MentalModelDeltaOperations`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `applied` | `array<object>` | 否 | Operations applied to the document, in order. |
| `skipped` | `array<object>` | 否 | Operations dropped as invalid, each with a reason. |

</details>

<details open><summary><strong>trace</strong> · <code>MentalModelRefreshTrace</code></summary>

数据结构 `MentalModelRefreshTrace`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `recorded_at` | `string(date-time)?` | 否 | When this trace was recorded. |
| `effective_mode` | `"full" \| "delta"` | 是 | Whether the refresh ran as full or delta. |
| `mode_fallback_reason` | `"no_baseline_content" \| "source_query_changed" \| "structured_doc_unreadable" \| "delta_ops_failed" \| "delta_ops_all_skipped"?` | 否 | Why delta was requested but not applied, if that happened. |
| `outcome` | `"content_written" \| "content_preserved_no_new_facts" \| "refresh_failed_empty_candidate" \| "refresh_failed_delta_not_applied"` | 是 | What the refresh did with the document. |
| `tool_calls` | `array<MentalModelTraceToolCall>` | 否 | Reflect tool calls made during the refresh. |
| `llm_calls` | `array<LLMCallTrace>` | 否 | LLM calls made during the refresh. |
| `delta_operations` | `MentalModelDeltaOperations?` | 否 | Structured operations emitted, in delta mode. |
| `usage` | `TokenUsage?` | 否 | Token usage across the refresh's LLM calls. |
| `duration_ms` | `integer` | 否 | Wall-clock duration of the refresh. · 默认 `0` |
| `warnings` | `array<string>` | 否 | Conditions worth a human's attention, in plain language. |

<details open><summary><strong>tool_calls[]</strong> · <code>MentalModelTraceToolCall</code></summary>

数据结构 `MentalModelTraceToolCall`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `tool` | `string` | 是 | Tool name: recall, search_observations, get_mental_model, expand, … |
| `reason` | `string?` | 否 | The agent's stated reason for the call. |
| `input` | `object` | 否 | Tool input parameters. |
| `output` | `object?` | 否 | What the tool returned. Present on a dry run, which stores nothing; omitted from the trace persisted by a real refresh to keep that row bounded. |
| `updated_at` | `string(date-time)?` | 否 | The refresh window's lower bound as given to this call — the delta watermark. Named for what it actually filters: the predicate is on the memory's updated_at, so a memory merely touched since the last refresh qualifies. Null means the tool applies no time bound at all, so its results are not limited to the window (mental-model lookup and chunk expansion behave this way). |
| `result_count` | `integer?` | 否 | Number of items the tool returned, when countable. |
| `duration_ms` | `integer` | 是 | Execution time in milliseconds. |
| `iteration` | `integer` | 否 | Agent loop iteration (1-based) this call belongs to. · 默认 `0` |

</details>

<details open><summary><strong>llm_calls[]</strong> · <code>LLMCallTrace</code></summary>

数据结构 `LLMCallTrace`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `scope` | `string` | 是 | Call scope: agent_1, agent_2, final, etc. |
| `duration_ms` | `integer` | 是 | Execution time in milliseconds |

</details>

<details open><summary><strong>delta_operations</strong> · <code>MentalModelDeltaOperations</code></summary>

数据结构 `MentalModelDeltaOperations`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `applied` | `array<object>` | 否 | Operations applied to the document, in order. |
| `skipped` | `array<object>` | 否 | Operations dropped as invalid, each with a reason. |

</details>

<details open><summary><strong>usage</strong> · <code>TokenUsage</code></summary>

数据结构 `TokenUsage`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `input_tokens` | `integer` | 否 | Number of input/prompt tokens consumed · 默认 `0` |
| `output_tokens` | `integer` | 否 | Number of visible output/completion tokens generated (excludes reasoning/thoughts) · 默认 `0` |
| `total_tokens` | `integer` | 否 | Total tokens (input + output, excludes thoughts) · 默认 `0` |
| `cached_tokens` | `integer` | 否 | Cached/cache-read prompt tokens, when reported by the provider · 默认 `0` |
| `thoughts_tokens` | `integer` | 否 | Reasoning/thinking tokens generated by the model. Billed at the output rate by some providers (e.g. Gemini 2.5+ family) but not surfaced in the visible response. · 默认 `0` |

</details>

</details>

<details open><summary><strong>usage</strong> · <code>TokenUsage</code></summary>

数据结构 `TokenUsage`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `input_tokens` | `integer` | 否 | Number of input/prompt tokens consumed · 默认 `0` |
| `output_tokens` | `integer` | 否 | Number of visible output/completion tokens generated (excludes reasoning/thoughts) · 默认 `0` |
| `total_tokens` | `integer` | 否 | Total tokens (input + output, excludes thoughts) · 默认 `0` |
| `cached_tokens` | `integer` | 否 | Cached/cache-read prompt tokens, when reported by the provider · 默认 `0` |
| `thoughts_tokens` | `integer` | 否 | Reasoning/thinking tokens generated by the model. Billed at the output rate by some providers (e.g. Gemini 2.5+ family) but not surfaced in the visible response. · 默认 `0` |

</details>

#### 响应示例

```json
{
  "effective_mode": "full",
  "facts": {
    "retrieved": {
      "observation": 12
    },
    "used": {
      "observation": 4
    }
  },
  "mental_model_id": "coding-style",
  "mode_fallback_reason": "source_query_changed",
  "name": "Coding Style",
  "outcome": "content_written",
  "requested_mode": "delta",
  "warnings": [],
  "would_persist": true
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=dry_run_refresh_mental_model`

---

### 心智模型历史
<a id="get-mental-model-history"></a>

**GET** `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/history`

*Get mental model history*

Get the refresh history of a mental model, showing content changes over time.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `mental_model_id` | path | `string` | 是 | Mental Model Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

_无展开字段（标量、自由 object 或未声明 properties）_

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=get_mental_model_history`

---

### 刷新心智模型
<a id="refresh-mental-model"></a>

**POST** `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/refresh`

*Refresh mental model*

Submit an async task to re-run the source query through reflect and update the content.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `mental_model_id` | path | `string` | 是 | Mental Model Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `operation_id` | `string` | 是 |  |
| `status` | `string` | 是 |  |

#### 响应示例

```json
{
  "operation_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=refresh_mental_model`

---

## Documents
<a id="documents"></a>

**文档** · 7 endpoints

文档粒度的查看、更新、删除与追踪。

### 本章目录

| Method | Path | 标题 |
| --- | --- | --- |
| `GET` | `/v1/default/banks/{bank_id}/documents` | [List documents](#list-documents) |
| `GET` | `/v1/default/banks/{bank_id}/documents/{document_id}` | [Get document details](#get-document) |
| `PATCH` | `/v1/default/banks/{bank_id}/documents/{document_id}` | [Update document](#update-document) |
| `DELETE` | `/v1/default/banks/{bank_id}/documents/{document_id}` | [Delete a document](#delete-document) |
| `GET` | `/v1/default/banks/{bank_id}/documents/{document_id}/chunks` | [List document chunks](#list-document-chunks) |
| `POST` | `/v1/default/banks/{bank_id}/documents/{document_id}/reprocess` | [Reprocess document](#reprocess-document) |
| `GET` | `/v1/default/chunks/{chunk_id}` | [Get chunk details](#get-chunk) |

### List documents
<a id="list-documents"></a>

**GET** `/v1/default/banks/{bank_id}/documents`

List documents with pagination and optional search, most recently written first (`updated_at` descending). Documents are the source content from which memory units are extracted.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `q` | query | `string?` | 否 | Case-insensitive substring filter on document ID (e.g. 'report' matches 'report-2024') |
| `tags` | query | `array<string>?` | 否 | Filter documents by tags |
| `tags_match` | query | `string` | 否 | How to match tags: 'any', 'all', 'any_strict', 'all_strict' · 默认 `"any_strict"` |
| `limit` | query | `integer` | 否 | 默认 `100` · ≥ `0` |
| `offset` | query | `integer` | 否 | 默认 `0` · ≥ `0` |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `items` | `array<object>` | 是 |  |
| `total` | `integer` | 是 |  |
| `limit` | `integer` | 是 |  |
| `offset` | `integer` | 是 |  |

#### 响应示例

```json
{
  "items": [
    {
      "bank_id": "user123",
      "content_hash": "abc123",
      "created_at": "2024-01-15T10:30:00Z",
      "id": "session_1",
      "memory_unit_count": 15,
      "tags": [
        "user_a",
        "session_123"
      ],
      "text_length": 5420,
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "limit": 100,
  "offset": 0,
  "total": 50
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=list_documents`

---

### Get document details
<a id="get-document"></a>

**GET** `/v1/default/banks/{bank_id}/documents/{document_id}`

Get a specific document including its original text

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `document_id` | path | `string` | 是 | Document Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `bank_id` | `string` | 是 |  |
| `original_text` | `string?` | 否 |  |
| `content_hash` | `string?` | 否 |  |
| `created_at` | `string` | 是 |  |
| `updated_at` | `string` | 是 |  |
| `memory_unit_count` | `integer` | 是 |  |
| `nodes_by_fact_type` | `map<string, integer>?` | 否 | Memory count per fact type (world, experience, observation) |
| `tags` | `array<string>` | 否 | Tags associated with this document · 默认 `[]` |
| `document_metadata` | `object?` | 否 | Document metadata |
| `retain_params` | `object?` | 否 | Parameters used during retain |
| `observation_scopes` | `string \| array<array<string>> \| null` | 否 | The observation_scopes spec configured at retain time (e.g. 'all_combinations', 'per_tag', or explicit tag-set lists), captured into retain_params. None when none was set (default 'combined' scoping) or for documents retained before this was captured. |

#### 响应示例

```json
{
  "bank_id": "user123",
  "content_hash": "abc123",
  "created_at": "2024-01-15T10:30:00Z",
  "document_metadata": {
    "channel": "#general",
    "source": "slack"
  },
  "id": "session_1",
  "memory_unit_count": 15,
  "original_text": "Full document text here...",
  "retain_params": {
    "context": "Team meeting notes",
    "event_date": "2024-01-15"
  },
  "tags": [
    "user_a",
    "session_123"
  ],
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=get_document`

---

### Update document
<a id="update-document"></a>

**PATCH** `/v1/default/banks/{bank_id}/documents/{document_id}`

Update mutable fields on a document without re-processing its content.

**Tags** (`tags`): Propagated to all associated memory units. Observations derived from those units are invalidated and queued for re-consolidation under the new tags. Co-source memories from other documents that shared those observations are also reset.

At least one field must be provided.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `document_id` | path | `string` | 是 | Document Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `tags` | `array<string>?` | 否 | New tags for the document and its memory units. Triggers observation invalidation and re-consolidation. |

#### 请求示例

```json
{
  "tags": [
    "team-a",
    "team-b"
  ]
}
```

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `success` | `boolean` | 否 | 默认 `true` |

#### 响应示例

```json
{
  "success": true
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=update_document`

---

### Delete a document
<a id="delete-document"></a>

**DELETE** `/v1/default/banks/{bank_id}/documents/{document_id}`

Delete a document and all its associated memory units and links.

This will cascade delete:
- The document itself
- All memory units extracted from this document
- All links (temporal, semantic, entity) associated with those memory units

This operation cannot be undone.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `document_id` | path | `string` | 是 | Document Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `success` | `boolean` | 是 |  |
| `message` | `string` | 是 |  |
| `document_id` | `string` | 是 |  |
| `memory_units_deleted` | `integer` | 是 |  |

#### 响应示例

```json
{
  "document_id": "session_1",
  "memory_units_deleted": 5,
  "message": "Document 'session_1' and 5 associated memory units deleted successfully",
  "success": true
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=delete_document`

---

### List document chunks
<a id="list-document-chunks"></a>

**GET** `/v1/default/banks/{bank_id}/documents/{document_id}/chunks`

List all chunks for a given document, ordered by chunk index.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `document_id` | path | `string` | 是 | Document Id |
| `limit` | query | `integer` | 否 | Maximum number of chunks to return · 默认 `100` · ≥ `1` · ≤ `1000` |
| `offset` | query | `integer` | 否 | Offset for pagination · 默认 `0` · ≥ `0` |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `items` | `array<ChunkResponse>` | 是 |  |
| `total` | `integer` | 是 |  |
| `limit` | `integer` | 是 |  |
| `offset` | `integer` | 是 |  |

<details open><summary><strong>items[]</strong> · <code>ChunkResponse</code></summary>

数据结构 `ChunkResponse`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `chunk_id` | `string` | 是 |  |
| `document_id` | `string` | 是 |  |
| `bank_id` | `string` | 是 |  |
| `chunk_index` | `integer` | 是 |  |
| `chunk_text` | `string` | 是 |  |
| `created_at` | `string` | 是 |  |

</details>

#### 响应示例

```json
{
  "items": [
    {
      "bank_id": "user123",
      "chunk_id": "user123_session_1_0",
      "chunk_index": 0,
      "chunk_text": "This is the first chunk of the document...",
      "created_at": "2024-01-15T10:30:00Z",
      "document_id": "session_1"
    }
  ],
  "total": 0,
  "limit": 0,
  "offset": 0
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=list_document_chunks`

---

### Reprocess document
<a id="reprocess-document"></a>

**POST** `/v1/default/banks/{bank_id}/documents/{document_id}/reprocess`

Re-run the retain pipeline on an existing document without changing its content. This deletes the existing memory units and re-extracts facts using the current engine configuration. Useful when the LLM model, chunking strategy, or extraction settings have changed.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `document_id` | path | `string` | 是 | Document Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `success` | `boolean` | 是 |  |
| `operation_id` | `string` | 是 |  |
| `items_count` | `integer` | 是 |  |

#### 响应示例

```json
{
  "success": false,
  "operation_id": "string",
  "items_count": 0
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=reprocess_document`

---

### Get chunk details
<a id="get-chunk"></a>

**GET** `/v1/default/chunks/{chunk_id}`

Get a specific chunk by its ID

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `chunk_id` | path | `string` | 是 | Chunk Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `chunk_id` | `string` | 是 |  |
| `document_id` | `string` | 是 |  |
| `bank_id` | `string` | 是 |  |
| `chunk_index` | `integer` | 是 |  |
| `chunk_text` | `string` | 是 |  |
| `created_at` | `string` | 是 |  |

#### 响应示例

```json
{
  "bank_id": "user123",
  "chunk_id": "user123_session_1_0",
  "chunk_index": 0,
  "chunk_text": "This is the first chunk of the document...",
  "created_at": "2024-01-15T10:30:00Z",
  "document_id": "session_1"
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=get_chunk`

---

## Document Transfer
<a id="document-transfer"></a>

**文档迁移** · 3 endpoints

文档导入导出与迁移。

### 本章目录

| Method | Path | 标题 |
| --- | --- | --- |
| `POST` | `/v1/default/banks/{bank_id}/document-transfer` | [Import documents (async)](#import-documents) |
| `POST` | `/v1/default/banks/{bank_id}/document-transfer/export` | [Export documents (async)](#export-documents) |
| `GET` | `/v1/default/files/download/{key}` | [Download a stored file (async export archive)](#download-file) |

### Import documents (async)
<a id="import-documents"></a>

**POST** `/v1/default/banks/{bank_id}/document-transfer`

Submit a transfer archive (produced by the export endpoint) for import into a bank. Runs as a background operation: facts are re-embedded with the target bank's embedding model and entities are re-resolved — no LLM extraction. Returns an operation_id; poll GET /v1/default/banks/{bank_id}/operations/{operation_id} for status and the imported/skipped counts in result_metadata. Use on_conflict to control existing document ids: skip (default), replace, or new-id.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `on_conflict` | query | `string` | 否 | skip \| replace \| new-id · 默认 `"skip"` |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `multipart/form-data` |

#### 请求体

- 格式：`multipart/form-data`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `file` | `string(binary)` | 是 | Transfer ZIP archive |

#### 请求示例

```json
{
  "file": "string"
}
```

#### 响应

- 状态码：`202` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `operation_id` | `string` | 是 |  |
| `status` | `string` | 否 | 默认 `"pending"` |

#### 响应示例

```json
{
  "operation_id": "string",
  "status": "pending"
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=import_documents`

---

### Export documents (async)
<a id="export-documents"></a>

**POST** `/v1/default/banks/{bank_id}/document-transfer/export`

Submit an async export of a bank's documents (extracted facts, entity names, causal links, chunks) as a transfer ZIP archive. Embeddings and database ids are not included — importing re-embeds with the target bank's model and re-resolves entities. Runs as a background operation to avoid pinning the API on large banks. Returns an operation_id; poll GET /v1/default/banks/{bank_id}/operations/{operation_id}. On completion the operation's result_metadata carries download_url (fetch the ZIP from GET /v1/default/files/download/{key}), storage_key, byte_size, and filename. Pass document_id query params to export specific documents, or omit to export the whole bank; include_observations=true also carries consolidated observations (whole-bank export only).

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `document_id` | query | `array<string>?` | 否 | Document id(s) to export; omit for all |
| `include_observations` | query | `boolean` | 否 | Also export consolidated observations (restored on import; whole-bank only) · 默认 `false` |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`202` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `operation_id` | `string` | 是 |  |
| `status` | `string` | 否 | 默认 `"pending"` |

#### 响应示例

```json
{
  "operation_id": "string",
  "status": "pending"
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=export_documents`

---

### Download a stored file (async export archive)
<a id="download-file"></a>

**GET** `/v1/default/files/download/{key}`

Stream a file previously written to file storage — currently the transfer ZIP produced by an async document export. The key comes from the export operation's result_metadata (storage_key / download_url). Access is authorized against the bank the key belongs to.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `key` | path | `string` | 是 | Key |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Stored file
- 格式：`application/json`

_无展开字段（标量、自由 object 或未声明 properties）_

- 格式：`application/zip`

_无响应体_

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=download_file`

---

## Files
<a id="files"></a>

**文件** · 1 endpoints

文件对象存取。

### 本章目录

| Method | Path | 标题 |
| --- | --- | --- |
| `POST` | `/v1/default/banks/{bank_id}/files/retain` | [Convert files to memories](#file-retain) |

### Convert files to memories
<a id="file-retain"></a>

**POST** `/v1/default/banks/{bank_id}/files/retain`

Upload files (PDF, DOCX, etc.), convert them to markdown, and retain as memories.

This endpoint handles file upload, conversion, and memory creation in a single operation.

**Features:**
- Supports PDF, DOCX, PPTX, XLSX, images (parser-dependent OCR), audio (with transcription)
- Automatic file-to-markdown conversion using pluggable parsers
- Files stored in object storage (PostgreSQL by default, S3 for production)
- Each file becomes a separate document with optional metadata/tags
- Always processes asynchronously — returns operation IDs immediately

**The system automatically:**
1. Stores uploaded files in object storage
2. Converts files to markdown
3. Creates document records with file metadata
4. Extracts facts and creates memory units (same as regular retain)

Use the operations endpoint to monitor progress.

**Request format:** multipart/form-data with:
- `files`: One or more files to upload
- `request`: JSON string with FileRetainRequest model

**Parser selection:**
- Set `parser` in the request body to override the server default for all files.
- Set `parser` inside a `files_metadata` entry for per-file control.
- Pass a list (e.g. `['iris', 'markitdown']`) to define an ordered fallback chain — each parser is tried in sequence until one succeeds.
- Falls back to the server default (`HINDSIGHT_API_FILE_PARSER`) if not specified.
- Only parsers enabled on the server may be requested; others return HTTP 400.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `multipart/form-data` |

#### 请求体

- 格式：`multipart/form-data`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `files` | `array<string(binary)>` | 是 | Files to upload and convert |
| `request` | `string` | 是 | JSON string with FileRetainRequest model |

#### 请求示例

```json
{
  "files": [
    "string"
  ],
  "request": "string"
}
```

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `operation_ids` | `array<string>` | 是 | Operation IDs for tracking file conversion operations. Use GET /v1/default/banks/{bank_id}/operations to list operations. |

#### 响应示例

```json
{
  "operation_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002"
  ]
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=file_retain`

---

## Entities
<a id="entities"></a>

**实体** · 3 endpoints

实体列表与维护。

### 本章目录

| Method | Path | 标题 |
| --- | --- | --- |
| `GET` | `/v1/default/banks/{bank_id}/entities` | [List entities](#list-entities) |
| `GET` | `/v1/default/banks/{bank_id}/entities/graph` | [Get entity co-occurrence graph](#get-entity-graph) |
| `GET` | `/v1/default/banks/{bank_id}/entities/{entity_id}` | [Get entity details](#get-entity) |

### List entities
<a id="list-entities"></a>

**GET** `/v1/default/banks/{bank_id}/entities`

List all entities (people, organizations, etc.) known by the bank, ordered by mention count. Supports pagination.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `limit` | query | `integer` | 否 | Maximum number of entities to return · 默认 `100` · ≥ `0` |
| `offset` | query | `integer` | 否 | Offset for pagination · 默认 `0` · ≥ `0` |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `items` | `array<EntityListItem>` | 是 |  |
| `total` | `integer` | 是 |  |
| `limit` | `integer` | 是 |  |
| `offset` | `integer` | 是 |  |

<details open><summary><strong>items[]</strong> · <code>EntityListItem</code></summary>

数据结构 `EntityListItem`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `canonical_name` | `string` | 是 |  |
| `mention_count` | `integer` | 是 |  |
| `first_seen` | `string?` | 否 |  |
| `last_seen` | `string?` | 否 |  |
| `metadata` | `object?` | 否 |  |

</details>

#### 响应示例

```json
{
  "items": [
    {
      "canonical_name": "John",
      "first_seen": "2024-01-15T10:30:00Z",
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "last_seen": "2024-02-01T14:00:00Z",
      "mention_count": 15
    }
  ],
  "limit": 100,
  "offset": 0,
  "total": 150
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=list_entities`

---

### Get entity co-occurrence graph
<a id="get-entity-graph"></a>

**GET** `/v1/default/banks/{bank_id}/entities/graph`

Return a graph of entities (nodes) and their co-occurrences (edges) for visualization.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `limit` | query | `integer` | 否 | Maximum number of co-occurrence edges to return · 默认 `1000` · ≥ `0` |
| `min_count` | query | `integer` | 否 | Minimum cooccurrence_count to include an edge · 默认 `1` |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `nodes` | `array<object>` | 是 |  |
| `edges` | `array<object>` | 是 |  |
| `total_entities` | `integer` | 是 |  |
| `total_edges` | `integer` | 是 |  |
| `limit` | `integer` | 是 |  |

#### 响应示例

```json
{
  "edges": [
    {
      "data": {
        "color": "#ffd700",
        "id": "uuid-1-uuid-2",
        "lastCooccurred": "2024-02-01T14:00:00Z",
        "lineStyle": "solid",
        "linkType": "cooccurrence",
        "source": "uuid-1",
        "target": "uuid-2",
        "weight": 5
      }
    }
  ],
  "limit": 1000,
  "nodes": [
    {
      "data": {
        "color": "#42a5f5",
        "id": "uuid-1",
        "label": "Alice",
        "mentionCount": 12
      }
    },
    {
      "data": {
        "color": "#42a5f5",
        "id": "uuid-2",
        "label": "Google",
        "mentionCount": 8
      }
    }
  ],
  "total_edges": 1,
  "total_entities": 2
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=get_entity_graph`

---

### Get entity details
<a id="get-entity"></a>

**GET** `/v1/default/banks/{bank_id}/entities/{entity_id}`

Get detailed information about an entity including observations (mental model).

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `entity_id` | path | `string` | 是 | Entity Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `canonical_name` | `string` | 是 |  |
| `mention_count` | `integer` | 是 |  |
| `first_seen` | `string?` | 否 |  |
| `last_seen` | `string?` | 否 |  |
| `metadata` | `object?` | 否 |  |
| `observations` | `array<EntityObservationResponse>` | 是 |  |

<details open><summary><strong>observations[]</strong> · <code>EntityObservationResponse</code></summary>

数据结构 `EntityObservationResponse`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `text` | `string` | 是 |  |
| `mentioned_at` | `string?` | 否 |  |

</details>

#### 响应示例

```json
{
  "canonical_name": "John",
  "first_seen": "2024-01-15T10:30:00Z",
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "last_seen": "2024-02-01T14:00:00Z",
  "mention_count": 15,
  "observations": [
    {
      "mentioned_at": "2024-01-15T10:30:00Z",
      "text": "John works at Google"
    }
  ]
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=get_entity`

---

## Directives
<a id="directives"></a>

**指令（Directives）** · 5 endpoints

运行时 directive 管理。

### 本章目录

| Method | Path | 标题 |
| --- | --- | --- |
| `GET` | `/v1/default/banks/{bank_id}/directives` | [List directives](#list-directives) |
| `POST` | `/v1/default/banks/{bank_id}/directives` | [Create directive](#create-directive) |
| `GET` | `/v1/default/banks/{bank_id}/directives/{directive_id}` | [Get directive](#get-directive) |
| `PATCH` | `/v1/default/banks/{bank_id}/directives/{directive_id}` | [Update directive](#update-directive) |
| `DELETE` | `/v1/default/banks/{bank_id}/directives/{directive_id}` | [Delete directive](#delete-directive) |

### List directives
<a id="list-directives"></a>

**GET** `/v1/default/banks/{bank_id}/directives`

List directive definitions. Unlike reflect, an omitted tag filter returns all directives.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `tags` | query | `array<string>?` | 否 | Filter directives by execution scope. Omit or pass [] to list all directives. |
| `tags_match` | query | `"any" \| "all" \| "exact"` | 否 | How tagged directives match the requested scope. Untagged/global directives are included. · 默认 `"any"` |
| `active_only` | query | `boolean` | 否 | Only return active directives · 默认 `true` |
| `limit` | query | `integer` | 否 | 默认 `100` · ≥ `1` · ≤ `1000` |
| `offset` | query | `integer` | 否 | 默认 `0` · ≥ `0` |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `items` | `array<DirectiveResponse>` | 是 |  |

<details open><summary><strong>items[]</strong> · <code>DirectiveResponse</code></summary>

数据结构 `DirectiveResponse`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `bank_id` | `string` | 是 |  |
| `name` | `string` | 是 |  |
| `content` | `string` | 是 |  |
| `priority` | `integer` | 否 | 默认 `0` |
| `is_active` | `boolean` | 否 | 默认 `true` |
| `tags` | `array<string>` | 否 | 默认 `[]` |
| `created_at` | `string?` | 否 |  |
| `updated_at` | `string?` | 否 |  |

</details>

#### 响应示例

```json
{
  "items": [
    {
      "id": "string",
      "bank_id": "string",
      "name": "string",
      "content": "string",
      "priority": 0,
      "is_active": true,
      "tags": [],
      "created_at": "string",
      "updated_at": "string"
    }
  ]
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=list_directives`

---

### Create directive
<a id="create-directive"></a>

**POST** `/v1/default/banks/{bank_id}/directives`

Create a global or tag-scoped hard rule for reflect prompts.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | `string` | 是 | Human-readable name for the directive |
| `content` | `string` | 是 | The directive text to inject into prompts |
| `priority` | `integer` | 否 | Higher priority directives are injected first · 默认 `0` |
| `is_active` | `boolean` | 否 | Whether this directive is active · 默认 `true` |
| `tags` | `array<string>` | 否 | Directive execution scope. Empty means global; non-empty requires a matching reflect scope. · 默认 `[]` |

#### 请求示例

```json
{
  "name": "string",
  "content": "string",
  "priority": 0,
  "is_active": true,
  "tags": []
}
```

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `bank_id` | `string` | 是 |  |
| `name` | `string` | 是 |  |
| `content` | `string` | 是 |  |
| `priority` | `integer` | 否 | 默认 `0` |
| `is_active` | `boolean` | 否 | 默认 `true` |
| `tags` | `array<string>` | 否 | 默认 `[]` |
| `created_at` | `string?` | 否 |  |
| `updated_at` | `string?` | 否 |  |

#### 响应示例

```json
{
  "id": "string",
  "bank_id": "string",
  "name": "string",
  "content": "string",
  "priority": 0,
  "is_active": true,
  "tags": [],
  "created_at": "string",
  "updated_at": "string"
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=create_directive`

---

### Get directive
<a id="get-directive"></a>

**GET** `/v1/default/banks/{bank_id}/directives/{directive_id}`

Get a specific directive by ID.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `directive_id` | path | `string` | 是 | Directive Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `bank_id` | `string` | 是 |  |
| `name` | `string` | 是 |  |
| `content` | `string` | 是 |  |
| `priority` | `integer` | 否 | 默认 `0` |
| `is_active` | `boolean` | 否 | 默认 `true` |
| `tags` | `array<string>` | 否 | 默认 `[]` |
| `created_at` | `string?` | 否 |  |
| `updated_at` | `string?` | 否 |  |

#### 响应示例

```json
{
  "id": "string",
  "bank_id": "string",
  "name": "string",
  "content": "string",
  "priority": 0,
  "is_active": true,
  "tags": [],
  "created_at": "string",
  "updated_at": "string"
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=get_directive`

---

### Update directive
<a id="update-directive"></a>

**PATCH** `/v1/default/banks/{bank_id}/directives/{directive_id}`

Update a directive's properties.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `directive_id` | path | `string` | 是 | Directive Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | `string?` | 否 | New name |
| `content` | `string?` | 否 | New content |
| `priority` | `integer?` | 否 | New priority |
| `is_active` | `boolean?` | 否 | New active status |
| `tags` | `array<string>?` | 否 | New tags |

#### 请求示例

```json
{
  "name": "string",
  "content": "string",
  "priority": 0,
  "is_active": false,
  "tags": [
    "string"
  ]
}
```

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `bank_id` | `string` | 是 |  |
| `name` | `string` | 是 |  |
| `content` | `string` | 是 |  |
| `priority` | `integer` | 否 | 默认 `0` |
| `is_active` | `boolean` | 否 | 默认 `true` |
| `tags` | `array<string>` | 否 | 默认 `[]` |
| `created_at` | `string?` | 否 |  |
| `updated_at` | `string?` | 否 |  |

#### 响应示例

```json
{
  "id": "string",
  "bank_id": "string",
  "name": "string",
  "content": "string",
  "priority": 0,
  "is_active": true,
  "tags": [],
  "created_at": "string",
  "updated_at": "string"
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=update_directive`

---

### Delete directive
<a id="delete-directive"></a>

**DELETE** `/v1/default/banks/{bank_id}/directives/{directive_id}`

Delete a directive.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `directive_id` | path | `string` | 是 | Directive Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

_无展开字段（标量、自由 object 或未声明 properties）_

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=delete_directive`

---

## Operations
<a id="operations"></a>

**异步操作** · 5 endpoints

异步任务状态（retain / refresh / 建 page 等返回的 operation_id）。

### 本章目录

| Method | Path | 标题 |
| --- | --- | --- |
| `GET` | `/v1/default/banks/{bank_id}/operations` | [列出异步操作](#list-operations) |
| `GET` | `/v1/default/banks/{bank_id}/operations/{operation_id}` | [Get operation status](#get-operation-status) |
| `DELETE` | `/v1/default/banks/{bank_id}/operations/{operation_id}` | [取消异步操作](#cancel-operation) |
| `DELETE` | `/v1/default/banks/{bank_id}/operations/{operation_id}/delete` | [Delete a terminal async operation](#delete-operation) |
| `POST` | `/v1/default/banks/{bank_id}/operations/{operation_id}/retry` | [重试异步操作](#retry-operation) |

### 列出异步操作
<a id="list-operations"></a>

**GET** `/v1/default/banks/{bank_id}/operations`

*List async operations*

Get a list of async operations for a specific agent, with optional filtering by status and operation type. Results are sorted by most recent first.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `status` | query | `string?` | 否 | Filter by status: pending, processing, completed, failed, or cancelled |
| `type` | query | `string?` | 否 | Filter by operation type: retain, consolidation, refresh_mental_model, file_convert_retain, webhook_delivery |
| `limit` | query | `integer` | 否 | Maximum number of operations to return · 默认 `20` · ≥ `1` · ≤ `100` |
| `offset` | query | `integer` | 否 | Number of operations to skip · 默认 `0` · ≥ `0` |
| `exclude_parents` | query | `boolean` | 否 | Exclude parent batch operations from results · 默认 `false` |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `bank_id` | `string` | 是 |  |
| `total` | `integer` | 是 |  |
| `limit` | `integer` | 是 |  |
| `offset` | `integer` | 是 |  |
| `operations` | `array<OperationResponse>` | 是 |  |

<details open><summary><strong>operations[]</strong> · <code>OperationResponse</code></summary>

数据结构 `OperationResponse`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `task_type` | `string` | 是 |  |
| `items_count` | `integer` | 是 |  |
| `document_id` | `string?` | 否 |  |
| `filename` | `string?` | 否 | Original filename for file-conversion operations (file_convert_retain); null for other task types. |
| `created_at` | `string` | 是 |  |
| `updated_at` | `string?` | 否 | When this operation's row last changed (claim, progress heartbeat, or completion). |
| `status` | `string` | 是 |  |
| `error_message` | `string?` | 否 |  |
| `retry_count` | `integer?` | 否 | Number of times this operation has been retried after failure. |
| `next_retry_at` | `string?` | 否 | When the worker will next attempt this operation. For a pending operation, a value in the future indicates the task is waiting rather than available for immediate pickup — for example, an extension may have raised DeferOperation to park the task until some backpressure window opens. Always null for completed tasks. |
| `progress` | `OperationProgress?` | 否 | Last-known progress snapshot for a running operation; null if none was recorded. |

<details open><summary><strong>progress</strong> · <code>OperationProgress</code></summary>

数据结构 `OperationProgress`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `stage` | `string` | 是 | Coarse phase the operation last reported (e.g. 'processing_batch'). |
| `at` | `string` | 是 | ISO-8601 timestamp when this snapshot was written. |
| `processed` | `integer?` | 否 | Units of work finished so far (sub-batches, memories), when known. |
| `total` | `integer?` | 否 | Total units of work for the operation, when known. |
| `detail` | `map<string, integer>?` | 否 | Operation-specific counters (e.g. observations_created, round, items_in_sub_batch). |

</details>

</details>

#### 响应示例

```json
{
  "bank_id": "user123",
  "limit": 20,
  "offset": 0,
  "operations": [
    {
      "created_at": "2024-01-15T10:30:00Z",
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "items_count": 5,
      "status": "pending",
      "task_type": "retain"
    }
  ],
  "total": 150
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=list_operations`

---

### Get operation status
<a id="get-operation-status"></a>

**GET** `/v1/default/banks/{bank_id}/operations/{operation_id}`

Get the status of a specific async operation. Returns 'pending', 'processing', 'completed', 'failed', or 'cancelled'. Completed operations remain queryable with their payload for the configured retention window and are pruned afterward.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `operation_id` | path | `string` | 是 | Operation Id |
| `include_payload` | query | `boolean` | 否 | Include the raw task payload (submission params) in the response. May be large. · 默认 `false` |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `operation_id` | `string` | 是 |  |
| `status` | `"pending" \| "processing" \| "completed" \| "failed" \| "cancelled" \| "not_found"` | 是 |  |
| `operation_type` | `string?` | 否 |  |
| `created_at` | `string?` | 否 |  |
| `updated_at` | `string?` | 否 |  |
| `completed_at` | `string?` | 否 |  |
| `error_message` | `string?` | 否 |  |
| `retry_count` | `integer?` | 否 | Number of times this operation has been retried after failure. |
| `next_retry_at` | `string?` | 否 | When the worker will next attempt this operation. For a pending operation, a value in the future indicates the task is parked (e.g. by an extension raising DeferOperation) rather than awaiting immediate pickup. |
| `progress` | `OperationProgress?` | 否 | Last-known progress snapshot for a running operation; null if none was recorded. |
| `result_metadata` | `object?` | 否 | Internal metadata for debugging. Structure may change without notice. Not for production use. |
| `child_operations` | `array<ChildOperationStatus>?` | 否 | Child operations for batch operations (if applicable) |
| `task_payload` | `object?` | 否 | Raw task payload (params the operation was submitted with). Only populated when include_payload=true. |

<details open><summary><strong>progress</strong> · <code>OperationProgress</code></summary>

数据结构 `OperationProgress`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `stage` | `string` | 是 | Coarse phase the operation last reported (e.g. 'processing_batch'). |
| `at` | `string` | 是 | ISO-8601 timestamp when this snapshot was written. |
| `processed` | `integer?` | 否 | Units of work finished so far (sub-batches, memories), when known. |
| `total` | `integer?` | 否 | Total units of work for the operation, when known. |
| `detail` | `map<string, integer>?` | 否 | Operation-specific counters (e.g. observations_created, round, items_in_sub_batch). |

</details>

<details open><summary><strong>child_operations[]</strong> · <code>ChildOperationStatus</code></summary>

数据结构 `ChildOperationStatus`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `operation_id` | `string` | 是 |  |
| `status` | `string` | 是 |  |
| `sub_batch_index` | `integer?` | 否 |  |
| `items_count` | `integer?` | 否 |  |
| `error_message` | `string?` | 否 |  |

</details>

#### 响应示例

```json
{
  "completed_at": "2024-01-15T10:31:30Z",
  "created_at": "2024-01-15T10:30:00Z",
  "operation_id": "550e8400-e29b-41d4-a716-446655440000",
  "operation_type": "refresh_mental_model",
  "status": "completed",
  "updated_at": "2024-01-15T10:31:30Z"
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=get_operation_status`

---

### 取消异步操作
<a id="cancel-operation"></a>

**DELETE** `/v1/default/banks/{bank_id}/operations/{operation_id}`

*Cancel a pending async operation*

Cancel a pending async operation by removing it from the queue

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `operation_id` | path | `string` | 是 | Operation Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `success` | `boolean` | 是 |  |
| `message` | `string` | 是 |  |
| `operation_id` | `string` | 是 |  |

#### 响应示例

```json
{
  "message": "Operation 550e8400-e29b-41d4-a716-446655440000 cancelled",
  "operation_id": "550e8400-e29b-41d4-a716-446655440000",
  "success": true
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=cancel_operation`

---

### Delete a terminal async operation
<a id="delete-operation"></a>

**DELETE** `/v1/default/banks/{bank_id}/operations/{operation_id}/delete`

Permanently remove a failed, cancelled, or completed async operation record

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `operation_id` | path | `string` | 是 | Operation Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `success` | `boolean` | 是 |  |
| `message` | `string` | 是 |  |
| `operation_id` | `string` | 是 |  |

#### 响应示例

```json
{
  "message": "Operation 550e8400-e29b-41d4-a716-446655440000 deleted",
  "operation_id": "550e8400-e29b-41d4-a716-446655440000",
  "success": true
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=delete_operation`

---

### 重试异步操作
<a id="retry-operation"></a>

**POST** `/v1/default/banks/{bank_id}/operations/{operation_id}/retry`

*Retry a failed async operation*

Re-queue a failed async operation so the worker picks it up again

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `operation_id` | path | `string` | 是 | Operation Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `success` | `boolean` | 是 |  |
| `message` | `string` | 是 |  |
| `operation_id` | `string` | 是 |  |

#### 响应示例

```json
{
  "message": "Operation 550e8400-e29b-41d4-a716-446655440000 queued for retry",
  "operation_id": "550e8400-e29b-41d4-a716-446655440000",
  "success": true
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=retry_operation`

---

## Webhooks
<a id="webhooks"></a>

**Webhooks** · 5 endpoints

事件订阅与回调配置。

### 本章目录

| Method | Path | 标题 |
| --- | --- | --- |
| `POST` | `/v1/default/banks/{bank_id}/webhooks` | [Register webhook](#create-webhook) |
| `GET` | `/v1/default/banks/{bank_id}/webhooks` | [List webhooks](#list-webhooks) |
| `DELETE` | `/v1/default/banks/{bank_id}/webhooks/{webhook_id}` | [Delete webhook](#delete-webhook) |
| `PATCH` | `/v1/default/banks/{bank_id}/webhooks/{webhook_id}` | [Update webhook](#update-webhook) |
| `GET` | `/v1/default/banks/{bank_id}/webhooks/{webhook_id}/deliveries` | [List webhook deliveries](#list-webhook-deliveries) |

### Register webhook
<a id="create-webhook"></a>

**POST** `/v1/default/banks/{bank_id}/webhooks`

Register a webhook endpoint to receive event notifications for this bank.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `url` | `string` | 是 | HTTP(S) endpoint URL to deliver events to |
| `secret` | `string?` | 否 | HMAC-SHA256 signing secret (optional) |
| `event_types` | `array<string>` | 否 | List of event types to deliver. Supported: 'retain.completed', 'consolidation.completed', 'memory_defense.triggered'. · 默认 `["consolidation.completed"]` |
| `enabled` | `boolean` | 否 | Whether this webhook is active · 默认 `true` |
| `http_config` | `WebhookHttpConfig` | 否 | HTTP delivery configuration (method, timeout, headers, params) |

<details open><summary><strong>http_config</strong> · <code>WebhookHttpConfig</code></summary>

数据结构 `WebhookHttpConfig`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `method` | `string` | 否 | HTTP method: GET or POST · 默认 `"POST"` |
| `timeout_seconds` | `integer` | 否 | HTTP request timeout in seconds · 默认 `30` |
| `headers` | `map<string, string>` | 否 | Custom HTTP headers |
| `params` | `map<string, string>` | 否 | Custom HTTP query parameters |

</details>

#### 请求示例

```json
{
  "url": "string",
  "secret": "string",
  "event_types": [
    "consolidation.completed"
  ],
  "enabled": true,
  "http_config": {
    "method": "POST",
    "timeout_seconds": 30,
    "headers": {},
    "params": {}
  }
}
```

#### 响应

- 状态码：`201` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `bank_id` | `string?` | 否 |  |
| `url` | `string` | 是 |  |
| `secret` | `string?` | 否 | Signing secret (redacted in responses) |
| `event_types` | `array<string>` | 是 |  |
| `enabled` | `boolean` | 是 |  |
| `http_config` | `WebhookHttpConfig` | 否 |  |
| `created_at` | `string?` | 否 |  |
| `updated_at` | `string?` | 否 |  |

<details open><summary><strong>http_config</strong> · <code>WebhookHttpConfig</code></summary>

数据结构 `WebhookHttpConfig`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `method` | `string` | 否 | HTTP method: GET or POST · 默认 `"POST"` |
| `timeout_seconds` | `integer` | 否 | HTTP request timeout in seconds · 默认 `30` |
| `headers` | `map<string, string>` | 否 | Custom HTTP headers |
| `params` | `map<string, string>` | 否 | Custom HTTP query parameters |

</details>

#### 响应示例

```json
{
  "id": "string",
  "bank_id": "string",
  "url": "string",
  "event_types": [
    "string"
  ],
  "enabled": false,
  "secret": "string",
  "http_config": {
    "method": "POST",
    "timeout_seconds": 30,
    "headers": {},
    "params": {}
  },
  "created_at": "string",
  "updated_at": "string"
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=create_webhook`

---

### List webhooks
<a id="list-webhooks"></a>

**GET** `/v1/default/banks/{bank_id}/webhooks`

List all webhooks registered for a bank.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `items` | `array<WebhookResponse>` | 是 |  |

<details open><summary><strong>items[]</strong> · <code>WebhookResponse</code></summary>

数据结构 `WebhookResponse`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `bank_id` | `string?` | 否 |  |
| `url` | `string` | 是 |  |
| `secret` | `string?` | 否 | Signing secret (redacted in responses) |
| `event_types` | `array<string>` | 是 |  |
| `enabled` | `boolean` | 是 |  |
| `http_config` | `WebhookHttpConfig` | 否 |  |
| `created_at` | `string?` | 否 |  |
| `updated_at` | `string?` | 否 |  |

<details open><summary><strong>http_config</strong> · <code>WebhookHttpConfig</code></summary>

数据结构 `WebhookHttpConfig`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `method` | `string` | 否 | HTTP method: GET or POST · 默认 `"POST"` |
| `timeout_seconds` | `integer` | 否 | HTTP request timeout in seconds · 默认 `30` |
| `headers` | `map<string, string>` | 否 | Custom HTTP headers |
| `params` | `map<string, string>` | 否 | Custom HTTP query parameters |

</details>

</details>

#### 响应示例

```json
{
  "items": [
    {
      "id": "string",
      "bank_id": "string",
      "url": "string",
      "event_types": [
        "string"
      ],
      "enabled": false,
      "secret": "string",
      "http_config": {
        "method": "POST",
        "timeout_seconds": 30,
        "headers": {},
        "params": {}
      },
      "created_at": "string",
      "updated_at": "string"
    }
  ]
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=list_webhooks`

---

### Delete webhook
<a id="delete-webhook"></a>

**DELETE** `/v1/default/banks/{bank_id}/webhooks/{webhook_id}`

Remove a registered webhook.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `webhook_id` | path | `string` | 是 | Webhook Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `success` | `boolean` | 是 |  |
| `message` | `string?` | 否 |  |
| `deleted_count` | `integer?` | 否 |  |

#### 响应示例

```json
{
  "deleted_count": 10,
  "message": "Deleted successfully",
  "success": true
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=delete_webhook`

---

### Update webhook
<a id="update-webhook"></a>

**PATCH** `/v1/default/banks/{bank_id}/webhooks/{webhook_id}`

Update one or more fields of a registered webhook. Only provided fields are changed.

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `webhook_id` | path | `string` | 是 | Webhook Id |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |
| `Content-Type` | header | `string` | 是 | 固定 `application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `url` | `string?` | 否 | HTTP(S) endpoint URL |
| `secret` | `string?` | 否 | HMAC-SHA256 signing secret. Omit to keep existing; send null to clear. |
| `event_types` | `array<string>?` | 否 | List of event types |
| `enabled` | `boolean?` | 否 | Whether this webhook is active |
| `http_config` | `WebhookHttpConfig?` | 否 | HTTP delivery configuration |

<details open><summary><strong>http_config</strong> · <code>WebhookHttpConfig</code></summary>

数据结构 `WebhookHttpConfig`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `method` | `string` | 否 | HTTP method: GET or POST · 默认 `"POST"` |
| `timeout_seconds` | `integer` | 否 | HTTP request timeout in seconds · 默认 `30` |
| `headers` | `map<string, string>` | 否 | Custom HTTP headers |
| `params` | `map<string, string>` | 否 | Custom HTTP query parameters |

</details>

#### 请求示例

```json
{
  "url": "string",
  "secret": "string",
  "event_types": [
    "string"
  ],
  "enabled": false,
  "http_config": {
    "method": "POST",
    "timeout_seconds": 30,
    "headers": {},
    "params": {}
  }
}
```

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `bank_id` | `string?` | 否 |  |
| `url` | `string` | 是 |  |
| `secret` | `string?` | 否 | Signing secret (redacted in responses) |
| `event_types` | `array<string>` | 是 |  |
| `enabled` | `boolean` | 是 |  |
| `http_config` | `WebhookHttpConfig` | 否 |  |
| `created_at` | `string?` | 否 |  |
| `updated_at` | `string?` | 否 |  |

<details open><summary><strong>http_config</strong> · <code>WebhookHttpConfig</code></summary>

数据结构 `WebhookHttpConfig`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `method` | `string` | 否 | HTTP method: GET or POST · 默认 `"POST"` |
| `timeout_seconds` | `integer` | 否 | HTTP request timeout in seconds · 默认 `30` |
| `headers` | `map<string, string>` | 否 | Custom HTTP headers |
| `params` | `map<string, string>` | 否 | Custom HTTP query parameters |

</details>

#### 响应示例

```json
{
  "id": "string",
  "bank_id": "string",
  "url": "string",
  "event_types": [
    "string"
  ],
  "enabled": false,
  "secret": "string",
  "http_config": {
    "method": "POST",
    "timeout_seconds": 30,
    "headers": {},
    "params": {}
  },
  "created_at": "string",
  "updated_at": "string"
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=update_webhook`

---

### List webhook deliveries
<a id="list-webhook-deliveries"></a>

**GET** `/v1/default/banks/{bank_id}/webhooks/{webhook_id}/deliveries`

Inspect delivery history for a webhook (useful for debugging).

#### 参数

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `bank_id` | path | `string` | 是 | Bank Id |
| `webhook_id` | path | `string` | 是 | Webhook Id |
| `limit` | query | `integer` | 否 | Maximum number of deliveries to return · 默认 `50` · ≤ `200` |
| `cursor` | query | `string?` | 否 | Pagination cursor (created_at of last item) |

#### 请求头

| 名称 | In | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |

#### 响应

- 状态码：`200` — Successful Response
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `items` | `array<WebhookDeliveryResponse>` | 是 |  |
| `next_cursor` | `string?` | 否 |  |

<details open><summary><strong>items[]</strong> · <code>WebhookDeliveryResponse</code></summary>

数据结构 `WebhookDeliveryResponse`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 |  |
| `webhook_id` | `string?` | 否 |  |
| `url` | `string` | 是 |  |
| `event_type` | `string` | 是 |  |
| `status` | `string` | 是 |  |
| `attempts` | `integer` | 是 |  |
| `next_retry_at` | `string?` | 否 |  |
| `last_error` | `string?` | 否 |  |
| `last_response_status` | `integer?` | 否 |  |
| `last_response_body` | `string?` | 否 |  |
| `last_attempt_at` | `string?` | 否 |  |
| `created_at` | `string?` | 否 |  |
| `updated_at` | `string?` | 否 |  |

</details>

#### 响应示例

```json
{
  "items": [
    {
      "id": "string",
      "webhook_id": "string",
      "url": "string",
      "event_type": "string",
      "status": "string",
      "attempts": 0,
      "next_retry_at": "string",
      "last_error": "string",
      "last_response_status": 0,
      "last_response_body": "string",
      "last_attempt_at": "string",
      "created_at": "string",
      "updated_at": "string"
    }
  ],
  "next_cursor": "string"
}
```

#### 响应

- 状态码：`422` — Validation Error
- 格式：`application/json`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `detail` | `array<ValidationError>` | 否 |  |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `loc` | `array<string \| integer>` | 是 | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg` | `string` | 是 |  |
| `type` | `string` | 是 |  |
| `input` | `any` | 否 |  |
| `ctx` | `Context` | 否 |  |

</details>

#### 响应示例

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "string",
      "type": "string",
      "input": null,
      "ctx": {}
    }
  ]
}
```

`operationId=list_webhook_deliveries`

---

## 附录

### 生成与更新

```bash
./scripts/generate-openapi.sh                 # 从 FastAPI 刷新 openapi.json
python3 scripts/generate-api-reading-md.py    # 生成本阅读文档
```

### 数据来源

```text
FastAPI (tags / operation_id / Pydantic models)
  → hindsight-docs/static/openapi.json
  → scripts/generate-api-reading-md.py
  → HINDSIGHT_HTTP_API.md
```

*Generated from `Hindsight HTTP API` `0.9.1` · 75 operations · nested depth ≤ 20; samples include required + optional fields when available.*
