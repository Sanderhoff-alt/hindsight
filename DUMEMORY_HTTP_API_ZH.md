# DuMemory HTTP API

> 版本 `0.9.1` · **74** 个接口 · **12** 个分组

---

## 目录

- [文档说明](#文档说明)
- [快速开始](#快速开始)
- [按模块浏览](#按模块浏览)
- [接口索引](#接口索引)
- [接口详解](#接口详解)

---

## 文档说明

本文档为 DuMemory HTTP API 中文参考手册（对标 `v0.9.1`），按照以下原则进行了翻译、削减和补充：

### 实现原则

- **以英文版为蓝本**：以英文版 HTTP API 文档为蓝本进行翻译与整理。
- **排除运维与监控接口**：排除了运维、监听、健康检查等接口。
- **排除废弃接口**：排除了被标记为 `deprecated` 的接口。
- **排除废弃字段**：有些接口虽然不是 `deprecated`，但部分字段被标记为 `deprecated`，这些字段也被排除。
- **完善字段说明**：完善了英文版中许多字段说明缺失的问题。
- **统一表述口径**：表述口径统一换成 DuMemory。

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

| 状态              | 含义                 |
| ----------------- | -------------------- |
| `422`           | 参数或请求体校验失败 |
| `400`           | 业务参数不合法       |
| `401` / `403` | 认证 / 授权          |
| `404`           | 不存在               |
| `409`           | 冲突                 |

### 异步操作

`retain(async)`、`refresh` mental model、创建 knowledge page 等会返回 `operation_id` → 到 **Operations** 查询。

### 关于 operationId

每个接口有唯一 `operationId`，便于在工单、日志与客户端代码里引用。

---

## 按模块浏览

| 模块                                   | 说明                              | 接口数 | 简介                                                                                       |
| -------------------------------------- | --------------------------------- | -----: | ------------------------------------------------------------------------------------------ |
| [Banks](#banks)                         | Bank 管理                         |     12 | 创建、配置、清理 Bank，以及 consolidation 和统计等控制面。                                 |
| [Bank Templates](#bank-templates)       | Bank 模板                         |      3 | bank 模板 schema / 导入导出，便于环境间复用配置。                                          |
| [Memory](#memory)                       | 记忆（Retain / Recall / Reflect） |     13 | 主路径 retain → recall → reflect，以及 list/get/update/clear。                           |
| [Knowledge Base](#knowledge-base)       | 知识库树（Knowledge Pages）       |      8 | folder/page 树组织 mental model；异步生成 page；hybrid 搜索与 markdown 导出。              |
| [Mental Models](#mental-models)         | 心智模型                          |      9 | 可刷新的合成知识（多为 Markdown），支持预览刷新结果。可独立使用，也可挂到 knowledge page。 |
| [Documents](#documents)                 | 文档                              |      7 | 文档粒度的查看、更新、删除与追踪。                                                         |
| [Document Transfer](#document-transfer) | 文档迁移                          |      3 | 文档的异步导出、下载、导入与迁移。                                                         |
| [Files](#files)                         | 文件                              |      1 | 文件对象存取。                                                                             |
| [Entities](#entities)                   | 实体                              |      3 | 实体列表与维护。                                                                           |
| [Directives](#directives)               | 指令（Directives）                |      5 | 运行时 directive 管理。                                                                    |
| [Operations](#operations)               | 异步操作                          |      5 | 异步任务状态（retain / refresh / 建 page 等返回的 operation_id）。                         |
| [Webhooks](#webhooks)                   | Webhooks                          |      5 | 事件订阅与回调配置。                                                                       |

## 接口索引

| 模块              | 方法       | 路径                                                                            | 标题                                                   | operationId                      |
| ----------------- | ---------- | ------------------------------------------------------------------------------- | ------------------------------------------------------ | -------------------------------- |
| Banks             | `GET`    | `/v1/default/banks`                                                           | [列出 Banks](#list-banks)                               | `list_banks`                   |
| Banks             | `PUT`    | `/v1/default/banks/{bank_id}`                                                 | [创建或更新 Bank](#create-or-update-bank)               | `create_or_update_bank`        |
| Banks             | `PATCH`  | `/v1/default/banks/{bank_id}`                                                 | [更新 Bank](#update-bank)                               | `update_bank`                  |
| Banks             | `DELETE` | `/v1/default/banks/{bank_id}`                                                 | [删除 Bank](#delete-bank)                               | `delete_bank`                  |
| Banks             | `GET`    | `/v1/default/banks/{bank_id}/config`                                          | [获取 Bank 配置](#get-bank-config)                      | `get_bank_config`              |
| Banks             | `PATCH`  | `/v1/default/banks/{bank_id}/config`                                          | [更新 Bank 配置](#update-bank-config)                   | `update_bank_config`           |
| Banks             | `DELETE` | `/v1/default/banks/{bank_id}/config`                                          | [重置 Bank 配置](#reset-bank-config)                    | `reset_bank_config`            |
| Banks             | `POST`   | `/v1/default/banks/{bank_id}/consolidate`                                     | [触发 Consolidation](#trigger-consolidation)            | `trigger_consolidation`        |
| Banks             | `POST`   | `/v1/default/banks/{bank_id}/consolidation/recover`                           | [恢复 Consolidation](#recover-consolidation)            | `recover_consolidation`        |
| Banks             | `DELETE` | `/v1/default/banks/{bank_id}/observations`                                    | [清除 Observations](#clear-observations)                | `clear_observations`           |
| Banks             | `GET`    | `/v1/default/banks/{bank_id}/stats`                                           | [Agent 统计](#get-agent-stats)                          | `get_agent_stats`              |
| Banks             | `GET`    | `/v1/default/banks/{bank_id}/stats/memories-timeseries`                       | [记忆时序统计](#get-memories-timeseries)                | `get_memories_timeseries`      |
| Bank Templates    | `GET`    | `/v1/bank-template-schema`                                                    | [获取 Bank 模板 JSON Schema](#get-bank-template-schema) | `get_bank_template_schema`     |
| Bank Templates    | `GET`    | `/v1/default/banks/{bank_id}/export`                                          | [导出 Bank 模板](#export-bank-template)                 | `export_bank_template`         |
| Bank Templates    | `POST`   | `/v1/default/banks/{bank_id}/import`                                          | [导入 Bank 模板](#import-bank-template)                 | `import_bank_template`         |
| Memory            | `GET`    | `/v1/default/banks/{bank_id}/graph`                                           | [获取记忆图](#get-graph)                                | `get_graph`                    |
| Memory            | `POST`   | `/v1/default/banks/{bank_id}/memories`                                        | [写入记忆（Retain）](#retain-memories)                  | `retain_memories`              |
| Memory            | `DELETE` | `/v1/default/banks/{bank_id}/memories`                                        | [清空 bank 记忆](#clear-bank-memories)                  | `clear_bank_memories`          |
| Memory            | `POST`   | `/v1/default/banks/{bank_id}/memories/dry-run-extract`                        | [试运行抽取记忆](#dry-run-extract-memories)             | `dry_run_extract_memories`     |
| Memory            | `GET`    | `/v1/default/banks/{bank_id}/memories/list`                                   | [列出记忆](#list-memories)                              | `list_memories`                |
| Memory            | `POST`   | `/v1/default/banks/{bank_id}/memories/recall`                                 | [检索记忆（Recall）](#recall-memories)                  | `recall_memories`              |
| Memory            | `GET`    | `/v1/default/banks/{bank_id}/memories/{memory_id}`                            | [获取单条记忆](#get-memory)                             | `get_memory`                   |
| Memory            | `PATCH`  | `/v1/default/banks/{bank_id}/memories/{memory_id}`                            | [更新记忆](#update-memory)                              | `update_memory`                |
| Memory            | `GET`    | `/v1/default/banks/{bank_id}/memories/{memory_id}/history`                    | [观察历史](#get-observation-history)                    | `get_observation_history`      |
| Memory            | `DELETE` | `/v1/default/banks/{bank_id}/memories/{memory_id}/observations`               | [清除记忆观察](#clear-memory-observations)              | `clear_memory_observations`    |
| Memory            | `GET`    | `/v1/default/banks/{bank_id}/observations/scopes`                             | [列出 observation scopes](#list-observation-scopes)     | `list_observation_scopes`      |
| Memory            | `POST`   | `/v1/default/banks/{bank_id}/reflect`                                         | [推理反思（Reflect）](#reflect)                         | `reflect`                      |
| Memory            | `GET`    | `/v1/default/banks/{bank_id}/tags`                                            | [列出 tags](#list-tags)                                 | `list_tags`                    |
| Knowledge Base    | `GET`    | `/v1/default/banks/{bank_id}/knowledge-base/export`                           | [导出知识库](#export-knowledge-base)                    | `export_knowledge_base`        |
| Knowledge Base    | `POST`   | `/v1/default/banks/{bank_id}/knowledge-base/folders`                          | [创建知识库目录](#create-knowledge-folder)              | `create_knowledge_folder`      |
| Knowledge Base    | `PATCH`  | `/v1/default/banks/{bank_id}/knowledge-base/nodes/{node_id}`                  | [更新知识库节点](#update-knowledge-node)                | `update_knowledge_node`        |
| Knowledge Base    | `DELETE` | `/v1/default/banks/{bank_id}/knowledge-base/nodes/{node_id}`                  | [删除知识库节点](#delete-knowledge-node)                | `delete_knowledge_node`        |
| Knowledge Base    | `POST`   | `/v1/default/banks/{bank_id}/knowledge-base/pages`                            | [创建知识库页面](#create-knowledge-page)                | `create_knowledge_page`        |
| Knowledge Base    | `GET`    | `/v1/default/banks/{bank_id}/knowledge-base/pages/{page_id}`                  | [读取知识库页面](#get-knowledge-page)                   | `get_knowledge_page`           |
| Knowledge Base    | `GET`    | `/v1/default/banks/{bank_id}/knowledge-base/search`                           | [搜索知识库页面](#search-knowledge-base)                | `search_knowledge_base`        |
| Knowledge Base    | `GET`    | `/v1/default/banks/{bank_id}/knowledge-base/tree`                             | [获取知识库树](#get-knowledge-base-tree)                | `get_knowledge_base_tree`      |
| Mental Models     | `GET`    | `/v1/default/banks/{bank_id}/mental-models`                                   | [列出心智模型](#list-mental-models)                     | `list_mental_models`           |
| Mental Models     | `POST`   | `/v1/default/banks/{bank_id}/mental-models`                                   | [创建心智模型](#create-mental-model)                    | `create_mental_model`          |
| Mental Models     | `GET`    | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}`                 | [获取心智模型](#get-mental-model)                       | `get_mental_model`             |
| Mental Models     | `PATCH`  | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}`                 | [更新心智模型](#update-mental-model)                    | `update_mental_model`          |
| Mental Models     | `DELETE` | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}`                 | [删除心智模型](#delete-mental-model)                    | `delete_mental_model`          |
| Mental Models     | `POST`   | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/clear`           | [清空心智模型正文](#clear-mental-model)                 | `clear_mental_model`           |
| Mental Models     | `GET`    | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/history`         | [心智模型历史](#get-mental-model-history)               | `get_mental_model_history`     |
| Mental Models     | `POST`   | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/refresh`         | [刷新心智模型](#refresh-mental-model)                   | `refresh_mental_model`         |
| Mental Models     | `POST`   | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/dry-run-refresh` | [预览心智模型刷新](#dry-run-refresh-mental-model)       | `dry_run_refresh_mental_model` |
| Documents         | `GET`    | `/v1/default/banks/{bank_id}/documents`                                       | [列出 document](#list-documents)                        | `list_documents`               |
| Documents         | `GET`    | `/v1/default/banks/{bank_id}/documents/{document_id}`                         | [获取 document 详情](#get-document)                     | `get_document`                 |
| Documents         | `PATCH`  | `/v1/default/banks/{bank_id}/documents/{document_id}`                         | [更新 document](#update-document)                       | `update_document`              |
| Documents         | `DELETE` | `/v1/default/banks/{bank_id}/documents/{document_id}`                         | [删除 document](#delete-document)                       | `delete_document`              |
| Documents         | `GET`    | `/v1/default/banks/{bank_id}/documents/{document_id}/chunks`                  | [列出 document chunk](#list-document-chunks)            | `list_document_chunks`         |
| Documents         | `POST`   | `/v1/default/banks/{bank_id}/documents/{document_id}/reprocess`               | [重新处理 document](#reprocess-document)                | `reprocess_document`           |
| Documents         | `GET`    | `/v1/default/chunks/{chunk_id}`                                               | [获取 chunk 详情](#get-chunk)                           | `get_chunk`                    |
| Document Transfer | `POST`   | `/v1/default/banks/{bank_id}/document-transfer/export`                        | [异步导出 document](#export-documents)                  | `export_documents`             |
| Document Transfer | `GET`    | `/v1/default/files/download/{key}`                                            | [下载导出文件](#download-file)                          | `download_file`                |
| Document Transfer | `POST`   | `/v1/default/banks/{bank_id}/document-transfer`                               | [导入 document（异步）](#import-documents)              | `import_documents`             |
| Files             | `POST`   | `/v1/default/banks/{bank_id}/files/retain`                                    | [将文件转换为记忆](#file-retain)                        | `file_retain`                  |
| Entities          | `GET`    | `/v1/default/banks/{bank_id}/entities`                                        | [列出 entity](#list-entities)                           | `list_entities`                |
| Entities          | `GET`    | `/v1/default/banks/{bank_id}/entities/graph`                                  | [获取 entity 共现图](#get-entity-graph)                 | `get_entity_graph`             |
| Entities          | `GET`    | `/v1/default/banks/{bank_id}/entities/{entity_id}`                            | [获取 entity 详情](#get-entity)                         | `get_entity`                   |
| Directives        | `GET`    | `/v1/default/banks/{bank_id}/directives`                                      | [列出 directive](#list-directives)                      | `list_directives`              |
| Directives        | `POST`   | `/v1/default/banks/{bank_id}/directives`                                      | [创建 directive](#create-directive)                     | `create_directive`             |
| Directives        | `GET`    | `/v1/default/banks/{bank_id}/directives/{directive_id}`                       | [获取 directive](#get-directive)                        | `get_directive`                |
| Directives        | `PATCH`  | `/v1/default/banks/{bank_id}/directives/{directive_id}`                       | [更新 directive](#update-directive)                     | `update_directive`             |
| Directives        | `DELETE` | `/v1/default/banks/{bank_id}/directives/{directive_id}`                       | [删除 directive](#delete-directive)                     | `delete_directive`             |
| Operations        | `GET`    | `/v1/default/banks/{bank_id}/operations`                                      | [列出异步操作](#list-operations)                        | `list_operations`              |
| Operations        | `GET`    | `/v1/default/banks/{bank_id}/operations/{operation_id}`                       | [获取异步操作状态](#get-operation-status)               | `get_operation_status`         |
| Operations        | `DELETE` | `/v1/default/banks/{bank_id}/operations/{operation_id}`                       | [取消异步操作](#cancel-operation)                       | `cancel_operation`             |
| Operations        | `DELETE` | `/v1/default/banks/{bank_id}/operations/{operation_id}/delete`                | [删除已终止的异步操作](#delete-operation)               | `delete_operation`             |
| Operations        | `POST`   | `/v1/default/banks/{bank_id}/operations/{operation_id}/retry`                 | [重试异步操作](#retry-operation)                        | `retry_operation`              |
| Webhooks          | `POST`   | `/v1/default/banks/{bank_id}/webhooks`                                        | [注册 webhook](#create-webhook)                         | `create_webhook`               |
| Webhooks          | `GET`    | `/v1/default/banks/{bank_id}/webhooks`                                        | [列出 webhook](#list-webhooks)                          | `list_webhooks`                |
| Webhooks          | `DELETE` | `/v1/default/banks/{bank_id}/webhooks/{webhook_id}`                           | [删除 webhook](#delete-webhook)                         | `delete_webhook`               |
| Webhooks          | `PATCH`  | `/v1/default/banks/{bank_id}/webhooks/{webhook_id}`                           | [更新 webhook](#update-webhook)                         | `update_webhook`               |
| Webhooks          | `GET`    | `/v1/default/banks/{bank_id}/webhooks/{webhook_id}/deliveries`                | [列出 webhook delivery](#list-webhook-deliveries)       | `list_webhook_deliveries`      |

---

## 接口详解

## Banks

<a id="banks"></a>

**Bank 管理** · 12 个接口

创建、配置、清理 Bank，以及 consolidation 和统计等控制面。

### 本章目录

| Method     | Path                                                      | 标题                                        |
| ---------- | --------------------------------------------------------- | ------------------------------------------- |
| `GET`    | `/v1/default/banks`                                     | [列出 Banks](#list-banks)                    |
| `PUT`    | `/v1/default/banks/{bank_id}`                           | [创建或更新 Bank](#create-or-update-bank)    |
| `PATCH`  | `/v1/default/banks/{bank_id}`                           | [更新 Bank](#update-bank)                    |
| `DELETE` | `/v1/default/banks/{bank_id}`                           | [删除 Bank](#delete-bank)                    |
| `GET`    | `/v1/default/banks/{bank_id}/config`                    | [获取 Bank 配置](#get-bank-config)           |
| `PATCH`  | `/v1/default/banks/{bank_id}/config`                    | [更新 Bank 配置](#update-bank-config)        |
| `DELETE` | `/v1/default/banks/{bank_id}/config`                    | [重置 Bank 配置](#reset-bank-config)         |
| `POST`   | `/v1/default/banks/{bank_id}/consolidate`               | [触发 Consolidation](#trigger-consolidation) |
| `POST`   | `/v1/default/banks/{bank_id}/consolidation/recover`     | [恢复 Consolidation](#recover-consolidation) |
| `DELETE` | `/v1/default/banks/{bank_id}/observations`              | [清除 Observations](#clear-observations)     |
| `GET`    | `/v1/default/banks/{bank_id}/stats`                     | [Agent 统计](#get-agent-stats)               |
| `GET`    | `/v1/default/banks/{bank_id}/stats/memories-timeseries` | [记忆时序统计](#get-memories-timeseries)     |

### 列出 Banks

<a id="list-banks"></a>

**GET** `/v1/default/banks`

获取所有 agent 及其 profile 列表

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段      | 类型                    | 必填 | 说明        |
| --------- | ----------------------- | ---- | ----------- |
| `banks` | `array<BankListItem>` | 是   | Bank 列表。 |

<details open><summary><strong>banks[]</strong> · <code>BankListItem</code></summary>

数据结构 `BankListItem`：

| 字段                 | 类型                  | 必填 | 说明                                                                                                                                     |
| -------------------- | --------------------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `bank_id`          | `string`            | 是   | 所属 Bank 的唯一标识符。                                                                                                                 |
| `name`             | `string?`           | 否   | 名称。                                                                                                                                   |
| `disposition`      | `DispositionTraits` | 是   | Bank 的 disposition 特征配置。                                                                                                           |
| `mission`          | `string?`           | 否   | Bank 或 agent 的 mission。                                                                                                               |
| `created_at`       | `string?`           | 否   | 创建时间。                                                                                                                               |
| `updated_at`       | `string?`           | 否   | 最后更新时间。                                                                                                                           |
| `fact_count`       | `integer`           | 否   | 默认值：`0`                                                                                                                            |
| `last_document_at` | `string?`           | 否   | 最近一个 document 的时间。                                                                                                               |
| `last_write_at`    | `string?`           | 否   | 最近一次向此 Bank 写入内容的时间，包括 Retain 新 document、追加现有 document，以及创建或更新 mental model、knowledge page 或 directive。 |

<details open><summary><strong>disposition</strong> · <code>DispositionTraits</code></summary>

数据结构 `DispositionTraits`：

| 字段           | 类型        | 必填 | 说明                                                                 |
| -------------- | ----------- | ---- | -------------------------------------------------------------------- |
| `skepticism` | `integer` | 是   | 对信息持怀疑还是信任的程度（1=信任，5=怀疑）；取值范围：`1`–`5` |
| `literalism` | `integer` | 是   | 对信息进行字面解读的程度（1=灵活，5=字面）；取值范围：`1`–`5`   |
| `empathy`    | `integer` | 是   | 考虑情绪背景的程度（1=疏离，5=共情）；取值范围：`1`–`5`         |

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
      "mission": "I am a software engineer helping my team ship quality code",
      "name": "Alice",
      "updated_at": "2024-01-16T14:20:00Z"
    }
  ]
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

创建 agent，或更新已有 agent 的 disposition 与 mission；缺失字段会自动填充默认值。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段                             | 类型                   | 必填 | 说明                                                                                             |
| -------------------------------- | ---------------------- | ---- | ------------------------------------------------------------------------------------------------ |
| `name`                         | `string?`            | 否   | 已弃用：仅用于显示标签，不对外宣传                                                               |
| `disposition`                  | `DispositionTraits?` | 否   | 已弃用：请改用 update_bank_config                                                                |
| `disposition_skepticism`       | `integer?`           | 否   | 已弃用：请改用 update_bank_config；取值范围：`1`–`5`                                        |
| `disposition_literalism`       | `integer?`           | 否   | 已弃用：请改用 update_bank_config；取值范围：`1`–`5`                                        |
| `disposition_empathy`          | `integer?`           | 否   | 已弃用：请改用 update_bank_config；取值范围：`1`–`5`                                        |
| `mission`                      | `string?`            | 否   | 已弃用：请改用带 reflect_mission 的 update_bank_config                                           |
| `background`                   | `string?`            | 否   | 已弃用：请改用带 reflect_mission 的 update_bank_config                                           |
| `reflect_mission`              | `string?`            | 否   | Reflect 异步操作的 mission/context；指导 Reflect 如何理解和使用 memories。                       |
| `retain_mission`               | `string?`            | 否   | 控制 retain() 抽取的内容；会与内置抽取规则一起注入。                                             |
| `retain_extraction_mode`       | `string?`            | 否   | Fact 抽取模式：'concise'（默认）、'verbose'、'custom'、'verbatim' 或 'chunks'。                  |
| `retain_custom_instructions`   | `string?`            | 否   | 自定义抽取 prompt。仅当 retain_extraction_mode 为 'custom' 时生效。                              |
| `retain_chunk_size`            | `integer?`           | 否   | Retain 期间每个内容 chunk 的目标最大字符数。                                                     |
| `retain_structured_chunk_size` | `integer?`           | 否   | Retain 期间单条 JSONL 行或单轮对话保持完整时允许的最大字符数。未设置时默认为 retain_chunk_size。 |
| `enable_observations`          | `boolean?`           | 否   | 是否在 retain() 后自动进行 observation consolidation。                                           |
| `enable_temporal_retrieval`    | `boolean?`           | 否   | 是否在 Recall 中启用时序检索及日期感知查询。                                                     |
| `enable_graph_retrieval`       | `boolean?`           | 否   | 是否在 Recall 中启用图检索。                                                                     |
| `enable_reranking`             | `boolean?`           | 否   | 是否在 Recall 中启用 reranker。                                                                  |
| `observations_mission`         | `string?`            | 否   | 控制合成到 observations 中的内容；会完全替代内置 consolidation 规则。                            |

<details open><summary><strong>disposition</strong> · <code>DispositionTraits</code></summary>

数据结构 `DispositionTraits`：

| 字段           | 类型        | 必填 | 说明                                                                 |
| -------------- | ----------- | ---- | -------------------------------------------------------------------- |
| `skepticism` | `integer` | 是   | 对信息持怀疑还是信任的程度（1=信任，5=怀疑）；取值范围：`1`–`5` |
| `literalism` | `integer` | 是   | 对信息进行字面解读的程度（1=灵活，5=字面）；取值范围：`1`–`5`   |
| `empathy`    | `integer` | 是   | 考虑情绪背景的程度（1=疏离，5=共情）；取值范围：`1`–`5`         |

</details>

#### 请求示例

```json
{
  "observations_mission": "Observations are stable facts about people and projects. Always include preferences and skills.",
  "retain_mission": "Always include technical decisions and architectural trade-offs. Ignore meeting logistics."
}
```

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段            | 类型                  | 必填 | 说明                                           |
| --------------- | --------------------- | ---- | ---------------------------------------------- |
| `bank_id`     | `string`            | 是   | 所属 Bank 的唯一标识符。                       |
| `name`        | `string`            | 是   | 名称。                                         |
| `disposition` | `DispositionTraits` | 是   | Bank 的 disposition 特征配置。                 |
| `mission`     | `string`            | 是   | agent 的 mission：agent 是谁以及要完成什么目标 |
| `background`  | `string?`           | 否   | 已弃用：请改用 mission                         |

<details open><summary><strong>disposition</strong> · <code>DispositionTraits</code></summary>

数据结构 `DispositionTraits`：

| 字段           | 类型        | 必填 | 说明                                                                 |
| -------------- | ----------- | ---- | -------------------------------------------------------------------- |
| `skepticism` | `integer` | 是   | 对信息持怀疑还是信任的程度（1=信任，5=怀疑）；取值范围：`1`–`5` |
| `literalism` | `integer` | 是   | 对信息进行字面解读的程度（1=灵活，5=字面）；取值范围：`1`–`5`   |
| `empathy`    | `integer` | 是   | 考虑情绪背景的程度（1=疏离，5=共情）；取值范围：`1`–`5`         |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

部分更新 agent profile；只会更新请求中提供的字段。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段                             | 类型                   | 必填 | 说明                                                                                             |
| -------------------------------- | ---------------------- | ---- | ------------------------------------------------------------------------------------------------ |
| `name`                         | `string?`            | 否   | 已弃用：仅用于显示标签，不对外宣传                                                               |
| `disposition`                  | `DispositionTraits?` | 否   | 已弃用：请改用 update_bank_config                                                                |
| `disposition_skepticism`       | `integer?`           | 否   | 已弃用：请改用 update_bank_config；取值范围：`1`–`5`                                        |
| `disposition_literalism`       | `integer?`           | 否   | 已弃用：请改用 update_bank_config；取值范围：`1`–`5`                                        |
| `disposition_empathy`          | `integer?`           | 否   | 已弃用：请改用 update_bank_config；取值范围：`1`–`5`                                        |
| `mission`                      | `string?`            | 否   | 已弃用：请改用带 reflect_mission 的 update_bank_config                                           |
| `background`                   | `string?`            | 否   | 已弃用：请改用带 reflect_mission 的 update_bank_config                                           |
| `reflect_mission`              | `string?`            | 否   | Reflect 异步操作的 mission/context；指导 Reflect 如何理解和使用 memories。                       |
| `retain_mission`               | `string?`            | 否   | 控制 retain() 抽取的内容；会与内置抽取规则一起注入。                                             |
| `retain_extraction_mode`       | `string?`            | 否   | Fact 抽取模式：'concise'（默认）、'verbose'、'custom'、'verbatim' 或 'chunks'。                  |
| `retain_custom_instructions`   | `string?`            | 否   | 自定义抽取 prompt。仅当 retain_extraction_mode 为 'custom' 时生效。                              |
| `retain_chunk_size`            | `integer?`           | 否   | Retain 期间每个内容 chunk 的目标最大字符数。                                                     |
| `retain_structured_chunk_size` | `integer?`           | 否   | Retain 期间单条 JSONL 行或单轮对话保持完整时允许的最大字符数。未设置时默认为 retain_chunk_size。 |
| `enable_observations`          | `boolean?`           | 否   | 是否在 retain() 后自动进行 observation consolidation。                                           |
| `enable_temporal_retrieval`    | `boolean?`           | 否   | 是否在 Recall 中启用时序检索及日期感知查询。                                                     |
| `enable_graph_retrieval`       | `boolean?`           | 否   | 是否在 Recall 中启用图检索。                                                                     |
| `enable_reranking`             | `boolean?`           | 否   | 是否在 Recall 中启用 reranker。                                                                  |
| `observations_mission`         | `string?`            | 否   | 控制合成到 observations 中的内容；会完全替代内置 consolidation 规则。                            |

<details open><summary><strong>disposition</strong> · <code>DispositionTraits</code></summary>

数据结构 `DispositionTraits`：

| 字段           | 类型        | 必填 | 说明                                                                 |
| -------------- | ----------- | ---- | -------------------------------------------------------------------- |
| `skepticism` | `integer` | 是   | 对信息持怀疑还是信任的程度（1=信任，5=怀疑）；取值范围：`1`–`5` |
| `literalism` | `integer` | 是   | 对信息进行字面解读的程度（1=灵活，5=字面）；取值范围：`1`–`5`   |
| `empathy`    | `integer` | 是   | 考虑情绪背景的程度（1=疏离，5=共情）；取值范围：`1`–`5`         |

</details>

#### 请求示例

```json
{
  "observations_mission": "Observations are stable facts about people and projects. Always include preferences and skills.",
  "retain_mission": "Always include technical decisions and architectural trade-offs. Ignore meeting logistics."
}
```

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段            | 类型                  | 必填 | 说明                                           |
| --------------- | --------------------- | ---- | ---------------------------------------------- |
| `bank_id`     | `string`            | 是   | 所属 Bank 的唯一标识符。                       |
| `name`        | `string`            | 是   | 名称。                                         |
| `disposition` | `DispositionTraits` | 是   | Bank 的 disposition 特征配置。                 |
| `mission`     | `string`            | 是   | agent 的 mission：agent 是谁以及要完成什么目标 |
| `background`  | `string?`           | 否   | 已弃用：请改用 mission                         |

<details open><summary><strong>disposition</strong> · <code>DispositionTraits</code></summary>

数据结构 `DispositionTraits`：

| 字段           | 类型        | 必填 | 说明                                                                 |
| -------------- | ----------- | ---- | -------------------------------------------------------------------- |
| `skepticism` | `integer` | 是   | 对信息持怀疑还是信任的程度（1=信任，5=怀疑）；取值范围：`1`–`5` |
| `literalism` | `integer` | 是   | 对信息进行字面解读的程度（1=灵活，5=字面）；取值范围：`1`–`5`   |
| `empathy`    | `integer` | 是   | 考虑情绪背景的程度（1=疏离，5=共情）；取值范围：`1`–`5`         |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

删除整个 memory bank，包括所有 memories、entities、documents 以及 bank profile。此操作具有破坏性且无法撤销。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段              | 类型         | 必填 | 说明           |
| ----------------- | ------------ | ---- | -------------- |
| `success`       | `boolean`  | 是   | 操作是否成功。 |
| `message`       | `string?`  | 否   | 操作结果消息。 |
| `deleted_count` | `integer?` | 否   | 已删除数量。   |

#### 响应示例

```json
{
  "deleted_count": 10,
  "message": "Deleted successfully",
  "success": true
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

获取 Bank 的完整解析配置，包括所有层级覆盖（global → tenant → bank）。`config` 字段包含解析后的全部配置值；`overrides` 字段仅显示 Bank 专属覆盖项。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段          | 类型       | 必填 | 说明                                          |
| ------------- | ---------- | ---- | --------------------------------------------- |
| `bank_id`   | `string` | 是   | Bank 标识符                                   |
| `config`    | `object` | 是   | 应用所有层级覆盖后的完整配置（Python 字段名） |
| `overrides` | `object` | 是   | 仅包含 Bank 专属的配置覆盖项（Python 字段名） |

#### 响应示例

```json
{
  "bank_id": "my-bank",
  "config": {
    "llm_model": "gpt-4",
    "llm_provider": "openai",
    "retain_extraction_mode": "verbose"
  },
  "overrides": {
    "retain_chunk_size": 1200,
    "retain_extraction_mode": "verbose"
  }
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

更新 Bank 的配置覆盖项。支持按 Bank 覆盖的字段如下：

- 访问与审计：`mcp_enabled_tools`、`audit_log_enabled`
- 数据保留：`store_document_text`
- Retain：`retain_chunk_size`、`retain_structured_chunk_size`、`retain_extraction_mode`、`retain_mission`、`retain_custom_instructions`、`retain_default_strategy`、`retain_strategies`、`retain_chunk_batch_size`
- Entity：`entity_labels`、`entities_allow_free_form`
- Recall 开关：`enable_temporal_retrieval`、`enable_graph_retrieval`、`enable_reranking`
- Consolidation：`enable_observations`、`enable_auto_consolidation`、`consolidation_llm_batch_size`、`consolidation_llm_parallelism`、`consolidation_max_memories_per_round`、`consolidation_source_facts_max_tokens`、`consolidation_source_facts_max_tokens_per_observation`、`observations_mission`、`max_observations_per_scope`、`observation_scope_limits`
- Reflect：`reflect_mission`、`reflect_source_facts_max_tokens`
- Recall 细节：`recall_include_chunks`、`recall_max_tokens`、`recall_chunks_max_tokens`
- Recall budget：`recall_budget_function`、`recall_budget_fixed_low`、`recall_budget_fixed_mid`、`recall_budget_fixed_high`、`recall_budget_adaptive_low`、`recall_budget_adaptive_mid`、`recall_budget_adaptive_high`、`recall_budget_min`、`recall_budget_max`
- Disposition：`disposition_skepticism`、`disposition_literalism`、`disposition_empathy`
- Gemini 安全策略：`llm_gemini_safety_settings`
- Memory Defense：`memory_defense`

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段        | 类型       | 必填 | 说明                               |
| ----------- | ---------- | ---- | ---------------------------------- |
| `updates` | `object` | 是   | 配置覆盖项，仅支持上文列出的字段。 |

#### 请求示例

```json
{
  "updates": {
    "retain_chunk_size": 1200,
    "retain_custom_instructions": "请仔细抽取技术细节",
    "retain_extraction_mode": "verbose"
  }
}
```

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段          | 类型       | 必填 | 说明                                          |
| ------------- | ---------- | ---- | --------------------------------------------- |
| `bank_id`   | `string` | 是   | Bank 标识符                                   |
| `config`    | `object` | 是   | 应用所有层级覆盖后的完整配置（Python 字段名） |
| `overrides` | `object` | 是   | 仅包含 Bank 专属的配置覆盖项（Python 字段名） |

#### 响应示例

```json
{
  "bank_id": "my-bank",
  "config": {
    "llm_model": "gpt-4",
    "llm_provider": "openai",
    "retain_extraction_mode": "verbose"
  },
  "overrides": {
    "retain_chunk_size": 1200,
    "retain_extraction_mode": "verbose"
  }
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

移除 Bank 的全部专属覆盖项，将配置重置为默认值。之后该 Bank 仅使用全局和租户级配置。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段          | 类型       | 必填 | 说明                                          |
| ------------- | ---------- | ---- | --------------------------------------------- |
| `bank_id`   | `string` | 是   | Bank 标识符                                   |
| `config`    | `object` | 是   | 应用所有层级覆盖后的完整配置（Python 字段名） |
| `overrides` | `object` | 是   | 仅包含 Bank 专属的配置覆盖项（Python 字段名） |

#### 响应示例

```json
{
  "bank_id": "my-bank",
  "config": {
    "llm_model": "gpt-4",
    "llm_provider": "openai",
    "retain_extraction_mode": "verbose"
  },
  "overrides": {
    "retain_chunk_size": 1200,
    "retain_extraction_mode": "verbose"
  }
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

运行 memory consolidation，根据近期 memories 创建或更新 observations。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**否**

| 字段                   | 类型                      | 必填 | 说明                                                                                                                                                                                            |
| ---------------------- | ------------------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `observation_scopes` | `array<array<string>>?` | 否   | 可选的待 consolidation 标签 scope 列表。每个 scope 是一个标签列表；只有标签包含至少一个 scope 中全部标签、且尚未 consolidation 的 memory 才会处理。省略时处理所有尚未 consolidation 的 memory。 |

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

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段             | 类型        | 必填 | 说明                                                   |
| ---------------- | ----------- | ---- | ------------------------------------------------------ |
| `operation_id` | `string`  | 是   | 异步 consolidation 异步操作的 ID                       |
| `deduplicated` | `boolean` | 否   | 如果复用了已有的待处理任务则为 true；默认值：`false` |

#### 响应示例

```json
{
  "operation_id": "string",
  "deduplicated": false
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

重置 consolidation 期间被永久标记为失败的 memories（已耗尽所有 LLM 重试并完成自适应批次拆分），使其在下一次 consolidation 时重新处理。不会删除任何 observations。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段              | 类型        | 必填 | 说明         |
| ----------------- | ----------- | ---- | ------------ |
| `retried_count` | `integer` | 是   | 已重试数量。 |

#### 响应示例

```json
{
  "retried_count": 42
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 清除 Observations

<a id="clear-observations"></a>

**DELETE** `/v1/default/banks/{bank_id}/observations`

删除 memory bank 的所有 observations，用于重置已 consolidation 的知识。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段              | 类型         | 必填 | 说明           |
| ----------------- | ------------ | ---- | -------------- |
| `success`       | `boolean`  | 是   | 操作是否成功。 |
| `message`       | `string?`  | 否   | 操作结果消息。 |
| `deleted_count` | `integer?` | 否   | 已删除数量。   |

#### 响应示例

```json
{
  "deleted_count": 10,
  "message": "Deleted successfully",
  "success": true
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

获取指定 agent 的节点和链接统计信息

#### 参数

| 名称        | In    | 类型        | 必填 | 说明                                                      |
| ----------- | ----- | ----------- | ---- | --------------------------------------------------------- |
| `bank_id` | path  | `string`  | 是   | Bank 的唯一标识符。                                       |
| `refresh` | query | `boolean` | 否   | 强制重新计算，跳过缓存值（并刷新缓存）；默认值：`false` |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段                      | 类型                                  | 必填 | 说明                                                                                                               |
| ------------------------- | ------------------------------------- | ---- | ------------------------------------------------------------------------------------------------------------------ |
| `bank_id`               | `string`                            | 是   | 所属 Bank 的唯一标识符。                                                                                           |
| `total_nodes`           | `integer`                           | 是   | 节点总数。                                                                                                         |
| `total_links`           | `integer`                           | 是   | 链接总数。                                                                                                         |
| `total_documents`       | `integer`                           | 是   | document 总数。                                                                                                    |
| `nodes_by_fact_type`    | `map<string, integer>`              | 是   | 按 fact type 分组的节点数量。                                                                                      |
| `links_by_link_type`    | `map<string, integer>`              | 是   | 按 link type 分组的链接数量。                                                                                      |
| `links_by_fact_type`    | `map<string, integer>`              | 是   | 按 fact type 分组的链接数量。                                                                                      |
| `links_breakdown`       | `map<string, map<string, integer>>` | 是   | 链接分类统计明细。                                                                                                 |
| `pending_operations`    | `integer`                           | 是   | 待处理 operation 数量。                                                                                            |
| `failed_operations`     | `integer`                           | 是   | 失败 operation 数量。                                                                                              |
| `operations_by_status`  | `map<string, integer>`              | 否   | 按状态分组的异步操作数量（pending、processing、completed、failed、cancelled）。                                    |
| `last_consolidated_at`  | `string?`                           | 否   | 上次运行 consolidation 的时间（ISO 格式）。                                                                        |
| `pending_consolidation` | `integer`                           | 否   | 尚未处理为 observations 的 memories 数量；默认值：`0`                                                            |
| `failed_consolidation`  | `integer`                           | 否   | consolidation 永久失败、可通过 consolidation recovery 接口重试的源 memories（world/experience）数量；默认值：`0` |
| `last_memory_write_at`  | `string?`                           | 否   | 最近一次 memory 写入完成的时间。                                                                                   |
| `total_observations`    | `integer`                           | 否   | observations 总数；默认值：`0`                                                                                   |

#### 响应示例

```json
{
  "bank_id": "user123",
  "failed_consolidation": 0,
  "failed_operations": 0,
  "last_consolidated_at": "2024-01-15T10:30:00Z",
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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

指定时间段内写入的 memories，按时间分桶并按 fact type 拆分。

#### 参数

| 名称           | In    | 类型       | 必填 | 说明                                                                                                                                                                                                                               |
| -------------- | ----- | ---------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bank_id`    | path  | `string` | 是   | Bank 的唯一标识符。                                                                                                                                                                                                                |
| `period`     | query | `string` | 否   | 默认值：`"7d"`                                                                                                                                                                                                                   |
| `time_field` | query | `string` | 否   | 用于分桶的时间字段。`created_at`（默认）表示写入时间；`mentioned_at`／`occurred_start` 表示事件时间，适用于写入时间集中于单个时间点、无法反映实际知识时间线的迁移数据。未知值回退为 `created_at`；默认值：`"created_at"` |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段           | 类型                              | 必填 | 说明                                                                                                                                                                           |
| -------------- | --------------------------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `bank_id`    | `string`                        | 是   | 所属 Bank 的唯一标识符。                                                                                                                                                       |
| `period`     | `string`                        | 是   | 可选值：1h、12h、1d、7d、30d、90d。                                                                                                                                            |
| `trunc`      | `string`                        | 是   | 时间桶粒度：minute、hour、day。                                                                                                                                                |
| `time_field` | `string`                        | 否   | 用于将每行分配到时间桶的时间戳列。`created_at` 表示写入时间；`mentioned_at` / `occurred_start` 表示事件时间（为空时逐行回退到 `created_at`）；默认值：`"created_at"` |
| `buckets`    | `array<MemoryTimeseriesBucket>` | 否   | 每个时间桶的计数；按请求时间段补齐后始终完整返回。                                                                                                                             |

<details open><summary><strong>buckets[]</strong> · <code>MemoryTimeseriesBucket</code></summary>

数据结构 `MemoryTimeseriesBucket`：

| 字段            | 类型        | 必填 | 说明                                              |
| --------------- | ----------- | ---- | ------------------------------------------------- |
| `time`        | `string`  | 是   | 时间桶起始时间戳（ISO-8601，UTC）。               |
| `world`       | `integer` | 否   | 此时间桶写入的 world fact memories；默认值：`0` |
| `experience`  | `integer` | 否   | 此时间桶写入的 experience memories；默认值：`0` |
| `observation` | `integer` | 否   | 此时间桶记录的 observations；默认值：`0`        |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

**Bank 模板** · 3 个接口

bank 模板 schema / 导入导出，便于环境间复用配置。

### 本章目录

| Method   | Path                                   | 标题                                                   |
| -------- | -------------------------------------- | ------------------------------------------------------ |
| `GET`  | `/v1/bank-template-schema`           | [获取 Bank 模板 JSON Schema](#get-bank-template-schema) |
| `GET`  | `/v1/default/banks/{bank_id}/export` | [导出 Bank 模板](#export-bank-template)                 |
| `POST` | `/v1/default/banks/{bank_id}/import` | [导入 Bank 模板](#import-bank-template)                 |

### 获取 Bank 模板 JSON Schema

<a id="get-bank-template-schema"></a>

**GET** `/v1/bank-template-schema`

返回 bank template manifest 格式的 JSON Schema。导入前可用它校验 template manifest。

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

_无展开字段（标量、自由 object 或未声明 properties）_

`operationId=get_bank_template_schema`

---

### 导出 Bank 模板

<a id="export-bank-template"></a>

**GET** `/v1/default/banks/{bank_id}/export`

将 Bank 当前配置、mental models 和 directives 导出为 template manifest。导出的 manifest 可导入其他 Bank 以复现该配置。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段              | 类型                                | 必填 | 说明                                                         |
| ----------------- | ----------------------------------- | ---- | ------------------------------------------------------------ |
| `version`       | `string`                          | 是   | Manifest schema 版本（当前为 1）。                           |
| `bank`          | `BankTemplateConfig?`             | 否   | 要应用的 Bank 配置。省略则保持配置不变。                     |
| `mental_models` | `array<BankTemplateMentalModel>?` | 否   | 要创建或更新的 mental models（按 id 匹配）。省略则保持不变。 |
| `directives`    | `array<BankTemplateDirective>?`   | 否   | 要创建或更新的 directives（按名称匹配）。省略则保持不变。    |

<details open><summary><strong>bank</strong> · <code>BankTemplateConfig</code></summary>

数据结构 `BankTemplateConfig`：

| 字段                                                      | 类型                          | 必填 | 说明                                                                                                                                                                                                                                                                                                     |
| --------------------------------------------------------- | ----------------------------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `reflect_mission`                                       | `string?`                   | 否   | Reflect 异步操作的 mission/context                                                                                                                                                                                                                                                                       |
| `retain_mission`                                        | `string?`                   | 否   | 控制 retain 抽取的内容                                                                                                                                                                                                                                                                                   |
| `retain_extraction_mode`                                | `string?`                   | 否   | Fact 抽取模式：'concise'（默认）、'verbose'、'custom'、'verbatim' 或 'chunks'                                                                                                                                                                                                                            |
| `retain_custom_instructions`                            | `string?`                   | 否   | 自定义抽取 prompt（mode='custom' 时生效）                                                                                                                                                                                                                                                                |
| `retain_chunk_size`                                     | `integer?`                  | 否   | 每个内容 chunk 的目标最大字符数                                                                                                                                                                                                                                                                          |
| `retain_structured_chunk_size`                          | `integer?`                  | 否   | 单条 JSONL 行或单轮对话保持完整时允许的最大字符数；未设置时默认为 retain_chunk_size                                                                                                                                                                                                                      |
| `enable_observations`                                   | `boolean?`                  | 否   | 是否进行 observation consolidation                                                                                                                                                                                                                                                                       |
| `enable_auto_consolidation`                             | `boolean?`                  | 否   | 是否在 Retain 后自动执行 observation consolidation。                                                                                                                                                                                                                                                     |
| `enable_temporal_retrieval`                             | `boolean?`                  | 否   | 是否在 Recall 中启用时序检索及日期感知查询。                                                                                                                                                                                                                                                             |
| `enable_graph_retrieval`                                | `boolean?`                  | 否   | 是否在 Recall 中启用 entity/link 图检索。                                                                                                                                                                                                                                                                |
| `enable_reranking`                                      | `boolean?`                  | 否   | 是否在 Recall 中启用 cross-encoder reranker。                                                                                                                                                                                                                                                            |
| `entity_labels`                                         | `array<LabelGroup-Output>?` | 否   | Entity label 受控词表。                                                                                                                                                                                                                                                                                  |
| `consolidation_max_memories_per_round`                  | `integer?`                  | 否   | 每轮 consolidation 处理的 memory 最大数量。                                                                                                                                                                                                                                                              |
| `consolidation_llm_parallelism`                         | `integer?`                  | 否   | Consolidation LLM 调用的最大并发数。                                                                                                                                                                                                                                                                     |
| `recall_include_chunks`                                 | `boolean?`                  | 否   | Recall 是否默认包含原始 chunk 文本。                                                                                                                                                                                                                                                                     |
| `recall_max_tokens`                                     | `integer?`                  | 否   | Recall 返回 facts 的默认 token budget。                                                                                                                                                                                                                                                                  |
| `recall_chunks_max_tokens`                              | `integer?`                  | 否   | Recall 返回原始 chunks 的默认 token budget。                                                                                                                                                                                                                                                             |
| `memory_defense`                                        | `object?`                   | 否   | Memory Defense 配置。                                                                                                                                                                                                                                                                                    |
| `observations_mission`                                  | `string?`                   | 否   | 控制合成的内容                                                                                                                                                                                                                                                                                           |
| `disposition_skepticism`                                | `integer?`                  | 否   | Skepticism 特征（1-5）；取值范围：`1`–`5`                                                                                                                                                                                                                                                           |
| `disposition_literalism`                                | `integer?`                  | 否   | Literalism 特征（1-5）；取值范围：`1`–`5`                                                                                                                                                                                                                                                           |
| `disposition_empathy`                                   | `integer?`                  | 否   | Empathy 特征（1-5）；取值范围：`1`–`5`                                                                                                                                                                                                                                                              |
| `entities_allow_free_form`                              | `boolean?`                  | 否   | 是否允许词表之外的 entities                                                                                                                                                                                                                                                                              |
| `retain_default_strategy`                               | `string?`                   | 否   | 默认 retain strategy 的名称（retain_strategies map 中的键）                                                                                                                                                                                                                                              |
| `retain_strategies`                                     | `object?`                   | 否   | retain strategy 名称到各 strategy 配置字典的映射                                                                                                                                                                                                                                                         |
| `retain_chunk_batch_size`                               | `integer?`                  | 否   | 每个流式批次的最大 chunks 数（0 表示禁用批处理）                                                                                                                                                                                                                                                         |
| `mcp_enabled_tools`                                     | `array<string>?`            | 否   | 此 bank 的 MCP tool allowlist（null 表示所有 tools）                                                                                                                                                                                                                                                     |
| `consolidation_llm_batch_size`                          | `integer?`                  | 否   | observation consolidation 的 LLM 批次大小                                                                                                                                                                                                                                                                |
| `consolidation_source_facts_max_tokens`                 | `integer?`                  | 否   | 每个 consolidation 批次的源 facts 最大 token 数                                                                                                                                                                                                                                                          |
| `consolidation_source_facts_max_tokens_per_observation` | `integer?`                  | 否   | 每个 observation 的源 facts 最大 token 数                                                                                                                                                                                                                                                                |
| `max_observations_per_scope`                            | `integer?`                  | 否   | 每个 consolidation scope 保留的最大 observations 数                                                                                                                                                                                                                                                      |
| `observation_scope_limits`                              | `array<object>?`            | 否   | 按 scope 覆盖 max_observations_per_scope：[{"scope": ["run_*", "shared"], "limit": 1}]。每个 scope 是 fnmatch tag-globs 列表；consolidation scope 要求精确覆盖（每个 tag 都匹配某个 glob，且每个 glob 都匹配某个 tag）。按列表顺序使用第一条匹配规则；未匹配的 scope 回退到 max_observations_per_scope。 |
| `reflect_source_facts_max_tokens`                       | `integer?`                  | 否   | 每次 Reflect 调用的源 facts 最大 token 数                                                                                                                                                                                                                                                                |
| `llm_gemini_safety_settings`                            | `array<any>?`               | 否   | 每个 bank 的 Gemini/VertexAI 安全过滤设置                                                                                                                                                                                                                                                                |
| `recall_budget_function`                                | `string?`                   | 否   | Recall budget 映射函数：fixed 或 adaptive。                                                                                                                                                                                                                                                              |
| `recall_budget_fixed_low`                               | `integer?`                  | 否   | budget=low 时固定的 thinking_budget（function=fixed）。                                                                                                                                                                                                                                                  |
| `recall_budget_fixed_mid`                               | `integer?`                  | 否   | budget=mid 时固定的 thinking_budget（function=fixed）。                                                                                                                                                                                                                                                  |
| `recall_budget_fixed_high`                              | `integer?`                  | 否   | budget=high 时固定的 thinking_budget（function=fixed）。                                                                                                                                                                                                                                                 |
| `recall_budget_adaptive_low`                            | `number?`                   | 否   | budget=low 时 max_tokens 的比例（function=adaptive）。                                                                                                                                                                                                                                                   |
| `recall_budget_adaptive_mid`                            | `number?`                   | 否   | budget=mid 时 max_tokens 的比例（function=adaptive）。                                                                                                                                                                                                                                                   |
| `recall_budget_adaptive_high`                           | `number?`                   | 否   | budget=high 时 max_tokens 的比例（function=adaptive）。                                                                                                                                                                                                                                                  |
| `recall_budget_min`                                     | `integer?`                  | 否   | adaptive 函数的下限（裁剪后）。                                                                                                                                                                                                                                                                          |
| `recall_budget_max`                                     | `integer?`                  | 否   | adaptive 函数的上限（裁剪后）。                                                                                                                                                                                                                                                                          |
| `audit_log_enabled`                                     | `boolean?`                  | 否   | 是否为此 Bank 启用审计日志（覆盖服务器默认值）。                                                                                                                                                                                                                                                         |
| `store_document_text`                                   | `boolean?`                  | 否   | 是否持久化原始源文本（documents.original_text / chunks.chunk_text）。设置为 false 时仅保留派生 facts。                                                                                                                                                                                                   |

</details>

<details open><summary><strong>config.entity_labels[]</strong> · <code>LabelGroup-Output</code></summary>

数据结构 `LabelGroup-Output`：

| 字段            | 类型                                          | 必填 | 说明                                    |
| --------------- | --------------------------------------------- | ---- | --------------------------------------- |
| `key`         | `string`                                    | 是   | 字段键名。                              |
| `description` | `string`                                    | 否   | 字段说明；默认值：`""`                |
| `type`        | `"value" \| "multi-values" \| "text" \| "map"` | 否   | 字段类型；默认值：`"value"`           |
| `optional`    | `boolean`                                   | 否   | 是否为可选字段；默认值：`false`       |
| `tag`         | `boolean`                                   | 否   | 是否将字段值用作 tag；默认值：`false` |
| `values`      | `array<LabelValue>`                         | 否   | 允许的 label 值；默认值：`[]`         |
| `fields`      | `map<string, MapField-Output>`              | 否   | 子字段定义；默认值：`{}`              |

<details open><summary><strong>values[]</strong> · <code>LabelValue</code></summary>

| 字段            | 类型       | 必填 | 说明                       |
| --------------- | ---------- | ---- | -------------------------- |
| `value`       | `string` | 是   | Label 值。                 |
| `description` | `string` | 否   | Label 说明；默认值：`""` |

</details>

</details>

<details open><summary><strong>mental_models[]</strong> · <code>BankTemplateMentalModel</code></summary>

数据结构 `BankTemplateMentalModel`：

| 字段             | 类型                          | 必填 | 说明                                                                   |
| ---------------- | ----------------------------- | ---- | ---------------------------------------------------------------------- |
| `id`           | `string`                    | 是   | Mental model 的唯一 ID（小写字母数字和连字符）。                       |
| `name`         | `string`                    | 是   | Mental model 的可读名称。                                              |
| `source_query` | `string`                    | 是   | 用于生成内容的查询。                                                   |
| `tags`         | `array<string>`             | 否   | 用于限定可见范围的标签；默认值：`[]`                                 |
| `max_tokens`   | `integer`                   | 否   | 生成内容的最大 token 数；默认值：`2048`；取值范围：`256`–`8192` |
| `trigger`      | `MentalModelTrigger-Output` | 否   | 触发器设置；默认值：`{}`                                             |

<details open><summary><strong>trigger</strong> · <code>MentalModelTrigger-Output</code></summary>

数据结构 `MentalModelTrigger-Output`：

| 字段                            | 类型                                                                                   | 必填 | 说明                                                                                                                                                                                                                                                                                                                                                  |
| ------------------------------- | -------------------------------------------------------------------------------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mode`                        | `"full" \| "delta"`                                                                   | 否   | 刷新模式。`full`（默认）每次刷新都从头生成 mental model 内容；`delta` 在现有内容上进行局部编辑，逐字节保留未变化的章节，移除过时内容并加入新内容。如果 mental model 尚无内容，或 `source_query` 自上次刷新后发生变化，`delta` 会自动回退为完整生成；默认值：`"full"`                                                                        |
| `response_schema`             | `object?`                                                                            | 否   | 用于结构化输出的可选 JSON Schema。                                                                                                                                                                                                                                                                                                                    |
| `keep_trace`                  | `boolean`                                                                            | 否   | 是否保留最近一次 mental model 刷新的执行 trace；默认值：`false`                                                                                                                                                                                                                                                                                     |
| `refresh_after_consolidation` | `boolean`                                                                            | 否   | 为 true 时，在 observations consolidation 后刷新此 mental model（实时模式）；默认值：`false`                                                                                                                                                                                                                                                        |
| `refresh_cron`                | `string?`                                                                            | 否   | 用于按固定计划刷新此 mental model 的 cron 表达式（UTC，标准 5 字段语法，例如`0 3 * * *` 表示每天 UTC 03:00）。与 refresh_after_consolidation 互斥：model 只能在 consolidation 后刷新或按 cron 刷新，不能同时启用。计划刷新仅在 model 已过期时执行（自上次刷新后 scope 内出现新 memories）；没有变化时跳过，避免浪费 LLM 调用。null 表示不设置计划。 |
| `fact_types`                  | `array<"world" \| "experience" \| "observation">?`                                     | 否   | 筛选 Reflect 时检索的 fact type。null 表示全部类型（world、experience、observation）。                                                                                                                                                                                                                                                                |
| `exclude_mental_models`       | `boolean`                                                                            | 否   | 为 true 时，从 Reflect 循环中排除所有 mental models（跳过`search_mental_models` 工具）；默认值：`false`                                                                                                                                                                                                                                           |
| `exclude_mental_model_ids`    | `array<string>?`                                                                     | 否   | 按 ID 从 Reflect 循环中排除指定 mental models。                                                                                                                                                                                                                                                                                                       |
| `tags_match`                  | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"?`                             | 否   | 覆盖 refresh 时 model tags 筛选 memories 的方式。未设置时，有 tags 的 model 默认为 all_strict（用于安全隔离），无 tags 的 model 默认为 any。设置为 any 可在 refresh 时同时包含无标签和有标签 memories。                                                                                                                                               |
| `tag_groups`                  | `array<TagGroupLeaf \| TagGroupAnd-Output \| TagGroupOr-Output \| TagGroupNot-Output>?` | 否   | Refresh 时使用的复合布尔 tag 表达式，用于替代 model 自身的 tags。设置后，这些 tag groups 会传给 Reflect，model 的扁平 tags 不再用于筛选。支持嵌套 and/or/not 表达式，以实现复杂的 tag scope。                                                                                                                                                         |
| `include_chunks`              | `boolean?`                                                                           | 否   | 覆盖 refresh 内部 Recall 是否返回原始 chunk 文本。null 表示使用 Bank／全局 配置默认值（recall_include_chunks）。                                                                                                                                                                                                                                      |
| `recall_max_tokens`           | `integer?`                                                                           | 否   | 覆盖 refresh 内部 Recall 返回 facts 的 token budget。null 表示使用 Bank／全局 配置默认值（recall_max_tokens）。                                                                                                                                                                                                                                       |
| `recall_chunks_max_tokens`    | `integer?`                                                                           | 否   | 覆盖 refresh 内部 Recall 返回原始 chunks 的 token budget。null 表示使用 Bank／全局 配置默认值（recall_chunks_max_tokens）。                                                                                                                                                                                                                           |

</details>

</details>

<details open><summary><strong>directives[]</strong> · <code>BankTemplateDirective</code></summary>

数据结构 `BankTemplateDirective`：

| 字段          | 类型              | 必填 | 说明                                                    |
| ------------- | ----------------- | ---- | ------------------------------------------------------- |
| `name`      | `string`        | 是   | directive 的可读名称。 (used as match key on re-import) |
| `content`   | `string`        | 是   | 要注入 prompts 的 directive 文本。                      |
| `priority`  | `integer`       | 否   | 优先级更高的 directive 会优先注入；默认值：`0`        |
| `is_active` | `boolean`       | 否   | 此 directive 是否启用；默认值：`true`                 |
| `tags`      | `array<string>` | 否   | 用于筛选的标签；默认值：`[]`                          |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 导入 Bank 模板

<a id="import-bank-template"></a>

**POST** `/v1/default/banks/{bank_id}/import`

导入 Bank template manifest，以创建或更新 Bank 配置、mental models 和 directives。Bank 不存在时会创建。配置字段作为 Bank 级覆盖项应用。Mental models 按 id 匹配，directives 按名称匹配；已有项更新，新项创建。使用 dry_run=true 可在不应用变更的情况下校验 manifest。

#### 参数

| 名称        | In    | 类型        | 必填 | 说明                                  |
| ----------- | ----- | ----------- | ---- | ------------------------------------- |
| `bank_id` | path  | `string`  | 是   | Bank 的唯一标识符。                   |
| `dry_run` | query | `boolean` | 否   | 仅校验，不应用更改；默认值：`false` |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段                      | 类型              | 必填 | 说明                                                                      |
| ------------------------- | ----------------- | ---- | ------------------------------------------------------------------------- |
| `bank_id`               | `string`        | 是   | 被导入的 Bank。                                                           |
| `config_applied`        | `boolean`       | 是   | Bank 配置是否已更新。                                                     |
| `mental_models_created` | `array<string>` | 否   | IDs of newly created mental models；默认值：`[]`                        |
| `mental_models_updated` | `array<string>` | 否   | IDs of updated mental models；默认值：`[]`                              |
| `directives_created`    | `array<string>` | 否   | Names of newly created directives；默认值：`[]`                         |
| `directives_updated`    | `array<string>` | 否   | Names of updated directives；默认值：`[]`                               |
| `operation_ids`         | `array<string>` | 否   | Operation IDs for mental model content generation (async)；默认值：`[]` |
| `dry_run`               | `boolean`       | 否   | 此次运行是否仅执行校验；默认值：`false`                                 |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

**记忆（Retain / Recall / Reflect）** · 13 个接口

主路径 retain → recall → reflect，以及 list/get/update/clear。

### 本章目录

| Method     | Path                                                              | 标题                                               |
| ---------- | ----------------------------------------------------------------- | -------------------------------------------------- |
| `GET`    | `/v1/default/banks/{bank_id}/graph`                             | [获取记忆图](#get-graph)                            |
| `POST`   | `/v1/default/banks/{bank_id}/memories`                          | [写入记忆（Retain）](#retain-memories)              |
| `DELETE` | `/v1/default/banks/{bank_id}/memories`                          | [清空 bank 记忆](#clear-bank-memories)              |
| `POST`   | `/v1/default/banks/{bank_id}/memories/dry-run-extract`          | [试运行抽取记忆](#dry-run-extract-memories)         |
| `GET`    | `/v1/default/banks/{bank_id}/memories/list`                     | [列出记忆](#list-memories)                          |
| `POST`   | `/v1/default/banks/{bank_id}/memories/recall`                   | [检索记忆（Recall）](#recall-memories)              |
| `GET`    | `/v1/default/banks/{bank_id}/memories/{memory_id}`              | [获取单条记忆](#get-memory)                         |
| `PATCH`  | `/v1/default/banks/{bank_id}/memories/{memory_id}`              | [更新记忆](#update-memory)                          |
| `GET`    | `/v1/default/banks/{bank_id}/memories/{memory_id}/history`      | [观察历史](#get-observation-history)                |
| `DELETE` | `/v1/default/banks/{bank_id}/memories/{memory_id}/observations` | [清除记忆观察](#clear-memory-observations)          |
| `GET`    | `/v1/default/banks/{bank_id}/observations/scopes`               | [列出 observation scopes](#list-observation-scopes) |
| `POST`   | `/v1/default/banks/{bank_id}/reflect`                           | [推理反思（Reflect）](#reflect)                     |
| `GET`    | `/v1/default/banks/{bank_id}/tags`                              | [列出 tags](#list-tags)                             |

### 获取记忆图

<a id="get-graph"></a>

**GET** `/v1/default/banks/{bank_id}/graph`

获取用于可视化的图数据，可按 type（world/experience/observation）筛选。

#### 参数

| 名称            | In    | 类型               | 必填 | 说明                            |
| --------------- | ----- | ------------------ | ---- | ------------------------------- |
| `bank_id`     | path  | `string`         | 是   | Bank 的唯一标识符。             |
| `type`        | query | `string?`        | 否   | 类型。                          |
| `limit`       | query | `integer`        | 否   | 默认值：`1000`；最小值：`0` |
| `q`           | query | `string?`        | 否   | 查询参数 q。                    |
| `tags`        | query | `array<string>?` | 否   | 标签。                          |
| `tags_match`  | query | `string`         | 否   | 默认值：`"all_strict"`        |
| `document_id` | query | `string?`        | 否   | Document 的唯一 ID。            |
| `chunk_id`    | query | `string?`        | 否   | Chunk 的唯一 ID。               |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段            | 类型              | 必填 | 说明             |
| --------------- | ----------------- | ---- | ---------------- |
| `nodes`       | `array<object>` | 是   | 图中的节点列表。 |
| `edges`       | `array<object>` | 是   | 图中的边列表。   |
| `table_rows`  | `array<object>` | 是   | 表格行列表。     |
| `total_units` | `integer`       | 是   | 单元总数。       |
| `limit`       | `integer`       | 是   | 返回数量上限。   |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

写入 memory items，并自动抽取 facts。

这是存储 memories 的主要接口。通过 `async` 参数同时支持同步和异步处理。

**功能：**

- 高效批处理
- 自动从自然语言中抽取事实
- 识别实体并建立链接
- 自动追踪 document，并在提供 `document_id` 时执行 upsert
- 建立时序链接和语义链接
- 可选的异步处理

**系统会自动：**

1. 从内容中抽取语义事实
2. 生成 embedding
3. 对相似事实去重
4. 创建时序、语义和实体链接
5. 追踪 document 元数据

**当 `async=true` 时：** 加入队列后立即返回。可通过异步操作接口监控进度。

**当 `async=false`（默认）时：** 等待处理完成。

**注意：** 如果 memory item 的 `document_id` 已存在，系统会先删除旧 document 及其 memory unit，再创建新内容（upsert 行为）。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段             | 类型                  | 必填 | 说明                                                                                                                                                                                                                                          |
| ---------------- | --------------------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `items`        | `array<MemoryItem>` | 是   | 结果项目列表。                                                                                                                                                                                                                                |
| `async`        | `boolean`           | 否   | 为 true 时在后台异步处理；为 false 时等待处理完成（默认值为 false）；默认值：`false`                                                                                                                                                        |
| `operation_id` | `string?`           | 否   | 客户端可选提供的 UUID，用作异步 Retain 异步操作的身份标识。使用相同 operation_id 重新提交时会返回原 operation，不会创建新工作；因此在确认丢失或超时后重试不会重复入队。复用属于其他 异步操作的 ID 会返回 HTTP 409。同步 Retain 会忽略此字段。 |

<details open><summary><strong>items[]</strong> · <code>MemoryItem</code></summary>

数据结构 `MemoryItem`：

| 字段                   | 类型                                                                                     | 必填 | 说明                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ---------------------- | ---------------------------------------------------------------------------------------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `content`            | `string`                                                                               | 是   | 资源的正文内容；对 directive/page 等资源含其可编辑文本。                                                                                                                                                                                                                                                                                                                                                               |
| `timestamp`          | `string(date-time) \| string \| null`                                                    | 否   | 内容发生的时间。可传 ISO 8601 datetime 字符串（例如`2024-01-15T10:30:00Z`）、null/省略（默认为当前时间），或特殊值 `unset`，明确表示不保存时间戳（适用于虚构文档或静态参考资料等无时间内容）。                                                                                                                                                                                                                     |
| `context`            | `string?`                                                                              | 否   | 上下文信息。                                                                                                                                                                                                                                                                                                                                                                                                           |
| `metadata`           | `map<string, string>?`                                                                 | 否   | 附加元数据。                                                                                                                                                                                                                                                                                                                                                                                                           |
| `document_id`        | `string?`                                                                              | 否   | 此 memory item 的可选 document ID。                                                                                                                                                                                                                                                                                                                                                                                    |
| `entities`           | `array<EntityInput>?`                                                                  | 否   | 可与自动抽取 entities 合并的可选 entities。                                                                                                                                                                                                                                                                                                                                                                            |
| `tags`               | `array<string>?`                                                                       | 否   | 用于可见性 scope 的可选 tags。带 tags 的 memories 可在 recall 时筛选。                                                                                                                                                                                                                                                                                                                                                 |
| `observation_scopes` | `"per_tag" \| "combined" \| "all_combinations" \| "shared" \| array<array<string>> \| null` | 否   | consolidation 时 observation 的 scope 方式。`per_tag` 为每个独立 tag 运行一次 consolidation，并为每个 tag 创建独立 observations；`combined`（默认）将所有 tags 合并后运行一次；`shared` 在全局无标签 scope 上运行一次，使 memories 无论 tags 如何都合并在一起，适用于跨易变的调用来源 tags（如每会话 ID）去重，同时保留源 facts 上的 tags。传入 tag 列表的列表时，每个内层列表运行一次，可完全控制使用哪些组合。 |
| `strategy`           | `string?`                                                                              | 否   | 此 item 使用的命名 Retain strategy。仅覆盖该 item 的 Bank 默认 strategy。Strategies 在 Bank 配置的 retain_strategies 中定义。                                                                                                                                                                                                                                                                                          |
| `update_mode`        | `"replace" \| "append"?`                                                                | 否   | 如何处理 document_id 相同的已有 document。`replace`（默认）删除旧数据并从头重新处理；`append` 将新内容拼接到现有 document 文本后再处理。                                                                                                                                                                                                                                                                           |

<details open><summary><strong>entities[]</strong> · <code>EntityInput</code></summary>

数据结构 `EntityInput`：

| 字段     | 类型        | 必填 | 说明                                              |
| -------- | ----------- | ---- | ------------------------------------------------- |
| `text` | `string`  | 是   | Entity 名称或文本。                               |
| `type` | `string?` | 否   | 可选的 entity type（例如 PERSON、ORG、CONCEPT）。 |

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

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段              | 类型               | 必填 | 说明                                                                                                                                                                         |
| ----------------- | ------------------ | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `success`       | `boolean`        | 是   | 操作是否成功。                                                                                                                                                               |
| `bank_id`       | `string`         | 是   | 所属 Bank 的唯一标识符。                                                                                                                                                     |
| `items_count`   | `integer`        | 是   | 项目数量。                                                                                                                                                                   |
| `async`         | `boolean`        | 是   | 该异步操作 是否以异步方式处理。                                                                                                                                              |
| `operation_id`  | `string?`        | 否   | 用于跟踪异步操作的 ID。可通过`GET /v1/default/banks/{bank_id}/operations` 列出异步操作。仅在 async=true 时出现；item 使用不同 per-item strategies 时应改用 operation_ids。 |
| `operation_ids` | `array<string>?` | 否   | 当 items 按多个 strategy group 提交时的 operation IDs（async=true 且 per-item strategies 混合）。为保持向后兼容，operation_id 会设置为第一项。                               |
| `usage`         | `TokenUsage?`    | 否   | Fact 抽取期间 LLM 调用的 token 用量指标（仅同步 operation 返回）。                                                                                                           |

<details open><summary><strong>usage</strong> · <code>TokenUsage</code></summary>

数据结构 `TokenUsage`：

| 字段                | 类型        | 必填 | 说明                                                                                                                       |
| ------------------- | ----------- | ---- | -------------------------------------------------------------------------------------------------------------------------- |
| `input_tokens`    | `integer` | 否   | 消耗的输入／prompt token 数量；默认值：`0`                                                                               |
| `output_tokens`   | `integer` | 否   | 生成的可见输出／completion token 数量（不含推理／思考 token）；默认值：`0`                                               |
| `total_tokens`    | `integer` | 否   | token 总数（输入加输出，不含推理 token）；默认值：`0`                                                                    |
| `cached_tokens`   | `integer` | 否   | provider 报告的缓存命中／缓存读取 prompt token 数量；默认值：`0`                                                         |
| `thoughts_tokens` | `integer` | 否   | 模型生成的推理／思考 token 数量。部分 provider（如 Gemini 2.5+ 系列）按输出费率计费，但不会显示在可见响应中；默认值：`0` |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

删除 memory bank 中的 memory units。可按 type（world、experience、observation）筛选，仅删除指定类型。此操作无法撤销，但会保留 bank profile（disposition 和 background）。

#### 参数

| 名称        | In    | 类型        | 必填 | 说明                                                        |
| ----------- | ----- | ----------- | ---- | ----------------------------------------------------------- |
| `bank_id` | path  | `string`  | 是   | Bank 的唯一标识符。                                         |
| `type`    | query | `string?` | 否   | 可选的 fact type 筛选器（world、experience、observation）。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段              | 类型         | 必填 | 说明           |
| ----------------- | ------------ | ---- | -------------- |
| `success`       | `boolean`  | 是   | 操作是否成功。 |
| `message`       | `string?`  | 否   | 操作结果消息。 |
| `deleted_count` | `integer?` | 否   | 已删除数量。   |

#### 响应示例

```json
{
  "deleted_count": 10,
  "message": "Deleted successfully",
  "success": true
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

预览 retain 将从文本中抽取的内容，不会修改 bank，也不会执行 entity resolution、links、embeddings 或持久化。返回候选 facts 和 LLM token 用量。所有会影响 prompt 的设置（retain mission、extraction mode、chunk size 等）都可在请求体中覆盖，用于将候选配置与 bank 当前配置进行 A/B 对比。此接口为只读操作，不会保存任何内容。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段                            | 类型                         | 必填 | 说明                                                  |
| ------------------------------- | ---------------------------- | ---- | ----------------------------------------------------- |
| `content`                     | `string`                   | 是   | 用于抽取 facts 的文本（例如 document 或单个 chunk）。 |
| `context`                     | `string`                   | 否   | 关于内容的可选上下文；默认值：`""`                  |
| `timestamp`                   | `string(date-time)?`       | 否   | 用于解析相对时间的参考时间戳（ISO 8601）。            |
| `retain_mission`              | `string?`                  | 否   | Retain 使用的 mission。                               |
| `retain_extraction_mode`      | `string?`                  | 否   | Retain 的 fact 抽取模式。                             |
| `retain_custom_instructions`  | `string?`                  | 否   | Retain 的自定义抽取指令。                             |
| `retain_extract_causal_links` | `boolean?`                 | 否   | 是否抽取因果链接。                                    |
| `retain_chunk_size`           | `integer?`                 | 否   | Retain 内容 chunk 的大小。                            |
| `entity_labels`               | `array<LabelGroup-Input>?` | 否   | Entity label 受控词表；仅覆盖本次调用的 Bank 配置。   |
| `entities_allow_free_form`    | `boolean?`                 | 否   | 是否允许自由格式 entity。                             |
| `llm_output_language`         | `string?`                  | 否   | LLM 输出语言。                                        |

<details open><summary><strong>entity_labels[]</strong> · <code>LabelGroup-Input</code></summary>

数据结构 `LabelGroup-Input`：

| 字段            | 类型                                          | 必填 | 说明                                      |
| --------------- | --------------------------------------------- | ---- | ----------------------------------------- |
| `key`         | `string`                                    | 是   | 字段键名。                                |
| `description` | `string`                                    | 否   | 字段说明；默认值：`""`                  |
| `type`        | `"value" \| "multi-values" \| "text" \| "map"` | 否   | 字段类型；默认值：`"value"`             |
| `optional`    | `boolean`                                   | 否   | 是否为可选字段；默认值：`true`          |
| `tag`         | `boolean`                                   | 否   | 是否将字段值用作 tag；默认值：`false`   |
| `values`      | `array<LabelValue>`                         | 否   | `category` 类型允许的值；默认值：`[]` |
| `fields`      | `map<string, MapField-Input>`               | 否   | 子字段定义；默认值：`{}`                |

<details open><summary><strong>values[]</strong> · <code>LabelValue</code></summary>

| 字段            | 类型       | 必填 | 说明                       |
| --------------- | ---------- | ---- | -------------------------- |
| `value`       | `string` | 是   | Label 值。                 |
| `description` | `string` | 否   | Label 说明；默认值：`""` |

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
  "entity_labels": [],
  "entities_allow_free_form": false,
  "llm_output_language": "string"
}
```

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段      | 类型                     | 必填 | 说明                                   |
| --------- | ------------------------ | ---- | -------------------------------------- |
| `facts` | `array<ExtractedFact>` | 否   | Retain 步骤可能抽取的候选 facts。      |
| `usage` | `TokenUsage`           | 否   | 所有抽取 LLM 调用汇总后的 token 用量。 |

<details open><summary><strong>facts[]</strong> · <code>ExtractedFact</code></summary>

数据结构 `ExtractedFact`：

| 字段               | 类型              | 必填 | 说明                                           |
| ------------------ | ----------------- | ---- | ---------------------------------------------- |
| `text`           | `string`        | 是   | 抽取出的 fact 文本。                           |
| `fact_type`      | `string`        | 是   | 视角分类：world 或 experience。                |
| `occurred_start` | `string?`       | 否   | Fact 事件开始时间的 ISO 时间戳（如果有日期）。 |
| `occurred_end`   | `string?`       | 否   | Fact 事件结束时间的 ISO 时间戳（如果有日期）。 |
| `entities`       | `array<string>` | 否   | Fact 中提及的原始 entity 名称（尚未解析）。    |

</details>

<details open><summary><strong>usage</strong> · <code>TokenUsage</code></summary>

数据结构 `TokenUsage`：

| 字段                | 类型        | 必填 | 说明                                                                                                                       |
| ------------------- | ----------- | ---- | -------------------------------------------------------------------------------------------------------------------------- |
| `input_tokens`    | `integer` | 否   | 消耗的输入／prompt token 数量；默认值：`0`                                                                               |
| `output_tokens`   | `integer` | 否   | 生成的可见输出／completion token 数量（不含推理／思考 token）；默认值：`0`                                               |
| `total_tokens`    | `integer` | 否   | token 总数（输入加输出，不含推理 token）；默认值：`0`                                                                    |
| `cached_tokens`   | `integer` | 否   | provider 报告的缓存命中／缓存读取 prompt token 数量；默认值：`0`                                                         |
| `thoughts_tokens` | `integer` | 否   | 模型生成的推理／思考 token 数量。部分 provider（如 Gemini 2.5+ 系列）按输出费率计费，但不会显示在可见响应中；默认值：`0` |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

分页列出 memory unit，并可进行全文搜索。支持按类型、来源 document 和关联 entity ID 筛选。结果按最近时间优先排序（先按 mentioned_at DESC，再按 created_at DESC）。

#### 参数

| 名称                    | In    | 类型                                                      | 必填 | 说明                           |
| ----------------------- | ----- | --------------------------------------------------------- | ---- | ------------------------------ |
| `bank_id`             | path  | `string`                                                | 是   | Bank 的唯一标识符。            |
| `type`                | query | `string?`                                               | 否   | 类型。                         |
| `q`                   | query | `string?`                                               | 否   | 查询参数 q。                   |
| `consolidation_state` | query | `string?`                                               | 否   | Consolidation 状态。           |
| `state`               | query | `string?`                                               | 否   | 状态。                         |
| `document_id`         | query | `string?`                                               | 否   | Document 的唯一 ID。           |
| `entity_id`           | query | `string?`                                               | 否   | Entity 的唯一 ID。             |
| `tags`                | query | `array<string>?`                                        | 否   | 标签。                         |
| `tags_match`          | query | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"` | 否   | 默认值：`"any"`              |
| `limit`               | query | `integer`                                               | 否   | 默认值：`100`；最小值：`0` |
| `offset`              | query | `integer`                                               | 否   | 默认值：`0`；最小值：`0`   |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段       | 类型              | 必填 | 说明           |
| ---------- | ----------------- | ---- | -------------- |
| `items`  | `array<object>` | 是   | 结果项目列表。 |
| `total`  | `integer`       | 是   | 总数量。       |
| `limit`  | `integer`       | 是   | 返回数量上限。 |
| `offset` | `integer`       | 是   | 分页偏移量。   |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

使用语义相似度和 spreading activation Recall memories。

type 参数可选，且必须是以下值之一：

- `world`: General knowledge about people, places, events, and things that happen
- `experience`: Memories about experience, conversations, actions taken, and tasks performed

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段                    | 类型                                                                                | 必填 | 说明                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ----------------------- | ----------------------------------------------------------------------------------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `query`               | `string`                                                                          | 是   | 查询文本。                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `types`               | `array<string>?`                                                                  | 否   | Recall 的 fact type 列表：world、experience、observation。未指定时默认为 world 和 experience。                                                                                                                                                                                                                                                                                                                             |
| `prefer_observations` | `boolean`                                                                         | 否   | 同时召回原始 facts（`world`／`experience`）和 `observation` 时，如果结果中的 observation 由某条原始 fact consolidation 而来，则移除该 fact，由 observation 取代它，以避免重复内容。空出的结果位会由后续结果补齐，从而保持请求的结果数量。默认关闭；设为 true 可启用。仅当请求同时包含 `observation` 和至少一种原始 fact 类型时生效；默认值：`false`                                                              |
| `budget`              | `Budget`                                                                          | 否   | 默认值：`"mid"`                                                                                                                                                                                                                                                                                                                                                                                                          |
| `max_tokens`          | `integer`                                                                         | 否   | 默认值：`4096`                                                                                                                                                                                                                                                                                                                                                                                                           |
| `trace`               | `boolean`                                                                         | 否   | 默认值：`false`                                                                                                                                                                                                                                                                                                                                                                                                          |
| `query_timestamp`     | `string?`                                                                         | 否   | ISO 格式日期字符串（例如`2023-05-30T23:40:00`）。用作查询时间锚点，以解析相对时间表达式并计算新近度得分。                                                                                                                                                                                                                                                                                                                |
| `include`             | `IncludeOptions`                                                                  | 否   | 控制是否包含附加数据（默认包含 entities）；默认值：`{}`                                                                                                                                                                                                                                                                                                                                                                  |
| `tags`                | `array<string>?`                                                                  | 否   | 按 tags 筛选 memories。未指定时返回所有 memories。tags_match=exact 且省略 tags（或传入 []）时，仅筛选无标签/全局 observations（即 observation_scopes=shared 写入的 scope）。                                                                                                                                                                                                                                               |
| `tags_match`          | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"`                           | 否   | tag 的匹配方式: 'any' (OR, includes untagged), 'all' (AND, includes untagged), 'any_strict' (OR, excludes untagged), 'all_strict' (AND, excludes untagged), 'exact' (set-equality on the full scope, excludes untagged). With 'exact' and no tags (or []), the empty global scope is selected and only untagged memories match；默认值：`"any"`                                                                          |
| `tag_groups`          | `array<TagGroupLeaf \| TagGroupAnd-Input \| TagGroupOr-Input \| TagGroupNot-Input>?` | 否   | 使用布尔分组的复合 tag 筛选器。列表中的 groups 按 AND 组合；每个 group 可以是叶节点 {tags, match}，也可以是复合结构 {and: [...]}、{or: [...]} 或 {not: ...}。                                                                                                                                                                                                                                                              |
| `min_scores`          | `MinScores?`                                                                      | 否   | 各阶段可选的最低 score（均包含边界，并按 AND 组合）。`semantic` 和 `keyword` 是检索级 cutoff，会被推送到查询参数 q，用于覆盖本次请求的全局相似度／BM25 最低分；`reranker` 和 `final` 是对已评分结果执行的排序后过滤器。未设置的字段不施加最低分；完全省略 `min_scores`（默认行为）则不进行分数过滤。请谨慎使用：reranker 的绝对分数未在不同查询之间校准，即使结果排名第一，明显相关的匹配也可能只有约 0.001 分。 |

<details open><summary><strong>budget</strong> · <code>Budget</code></summary>

类型：`Budget`

</details>

<details open><summary><strong>include</strong> · <code>IncludeOptions</code></summary>

数据结构 `IncludeOptions`：

| 字段             | 类型                           | 必填 | 说明                                                                                         |
| ---------------- | ------------------------------ | ---- | -------------------------------------------------------------------------------------------- |
| `entities`     | `EntityIncludeOptions?`      | 否   | 包含 entity observations。设为 null 可禁用 entity 包含；默认值：`{"max_tokens": 500}`      |
| `chunks`       | `ChunkIncludeOptions?`       | 否   | 是否包含原始 chunks。设置为 {} 启用，设置为 null 禁用（默认禁用）。                          |
| `source_facts` | `SourceFactsIncludeOptions?` | 否   | 是否为 observation 类型结果包含 source facts。设置为 {} 启用，设置为 null 禁用（默认禁用）。 |

<details open><summary><strong>entities</strong> · <code>EntityIncludeOptions</code></summary>

数据结构 `EntityIncludeOptions`：

| 字段           | 类型        | 必填 | 说明                                                   |
| -------------- | ----------- | ---- | ------------------------------------------------------ |
| `max_tokens` | `integer` | 否   | entity observations 的最大 token 数量；默认值：`500` |

</details>

<details open><summary><strong>chunks</strong> · <code>ChunkIncludeOptions</code></summary>

数据结构 `ChunkIncludeOptions`：

| 字段           | 类型        | 必填 | 说明                                                         |
| -------------- | ----------- | ---- | ------------------------------------------------------------ |
| `max_tokens` | `integer` | 否   | chunks 的最大 token 数量（可能截断 chunk）；默认值：`8192` |

</details>

<details open><summary><strong>source_facts</strong> · <code>SourceFactsIncludeOptions</code></summary>

数据结构 `SourceFactsIncludeOptions`：

| 字段                           | 类型        | 必填 | 说明                                                                                             |
| ------------------------------ | ----------- | ---- | ------------------------------------------------------------------------------------------------ |
| `max_tokens`                 | `integer` | 否   | Maximum total tokens for source facts across all observations (-1 = unlimited)；默认值：`4096` |
| `max_tokens_per_observation` | `integer` | 否   | 每条 observation 可使用的来源 facts 最大 token 数量 (-1 = unlimited)；默认值：`-1`             |

</details>

</details>

<details open><summary><strong>min_scores</strong> · <code>MinScores</code></summary>

数据结构 `MinScores`：

| 字段         | 类型        | 必填 | 说明                                                |
| ------------ | ----------- | ---- | --------------------------------------------------- |
| `semantic` | `number?` | 否   | Retrieval 层的最低向量相似度（0-1）。               |
| `keyword`  | `number?` | 否   | Retrieval 层的最低 keyword/full-text（BM25）score。 |
| `reranker` | `number?` | 否   | 查询后处理的最低归一化 reranker score（0-1）。      |
| `final`    | `number?` | 否   | 查询后处理的最低最终排名 score。                    |

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

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段             | 类型                                  | 必填 | 说明                                                   |
| ---------------- | ------------------------------------- | ---- | ------------------------------------------------------ |
| `results`      | `array<RecallResult>`               | 是   | 结果列表。                                             |
| `trace`        | `object?`                           | 否   | 执行 trace。                                           |
| `entities`     | `map<string, EntityStateResponse>?` | 否   | 结果中提及 entities 的当前状态。                       |
| `chunks`       | `map<string, ChunkData>?`           | 否   | 按 chunk_id 索引的 fact chunks。                       |
| `source_facts` | `map<string, RecallResult>?`        | 否   | observation 类型结果的 source facts，按 fact ID 索引。 |

<details open><summary><strong>results[]</strong> · <code>RecallResult</code></summary>

数据结构 `RecallResult`：

| 字段                | 类型                     | 必填 | 说明                    |
| ------------------- | ------------------------ | ---- | ----------------------- |
| `id`              | `string`               | 是   | 资源的唯一标识符。      |
| `text`            | `string`               | 是   | 文本内容。              |
| `type`            | `string?`              | 否   | 对象或错误的类型。      |
| `entities`        | `array<string>?`       | 否   | 相关 entities 列表。    |
| `context`         | `string?`              | 否   | 上下文信息。            |
| `occurred_start`  | `string?`              | 否   | 事件开始时间。          |
| `occurred_end`    | `string?`              | 否   | 事件结束时间。          |
| `mentioned_at`    | `string?`              | 否   | 被提及时间。            |
| `document_id`     | `string?`              | 否   | Document 的唯一标识符。 |
| `metadata`        | `map<string, string>?` | 否   | 附加元数据。            |
| `chunk_id`        | `string?`              | 否   | Chunk 的唯一标识符。    |
| `tags`            | `array<string>?`       | 否   | 标签列表。              |
| `source_fact_ids` | `array<string>?`       | 否   | 来源 fact 的 ID 列表。  |
| `scores`          | `RecallScores?`        | 否   | 各检索阶段的 score。    |

<details open><summary><strong>scores</strong> · <code>RecallScores</code></summary>

数据结构 `RecallScores`：

| 字段         | 类型        | 必填 | 说明                                                                                    |
| ------------ | ----------- | ---- | --------------------------------------------------------------------------------------- |
| `final`    | `number`  | 是   | 最终排名 score（综合 reranker、时效/时间和 proof boosts）。                             |
| `reranker` | `number?` | 否   | Cross-encoder 相关性，归一化范围为 0-1。reranker 直通时为 null（rrf/interleave 模式）。 |
| `semantic` | `number?` | 否   | 向量余弦相似度（0-1）。结果不是由 semantic 检索召回时为 null。                          |
| `keyword`  | `number?` | 否   | Keyword/full-text（BM25）score（>= 0，无上限）。结果不是由 keyword 搜索召回时为 null。  |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

按 ID 获取单个 memory unit 及其全部 metadata，包括 entities 和 tags。注意：`history` 字段已弃用且始终返回空列表，请改用 GET /memories/{memory_id}/history。

#### 参数

| 名称          | In   | 类型       | 必填 | 说明                |
| ------------- | ---- | ---------- | ---- | ------------------- |
| `bank_id`   | path | `string` | 是   | Bank 的唯一标识符。 |
| `memory_id` | path | `string` | 是   | Memory 的唯一 ID。  |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

_无展开字段（标量、自由 object 或未声明 properties）_

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

编辑 memory 文本和/或更改其整理状态（invalidate / revert）。已 invalidate 的 memories 会从 recall、consolidation 和图维护中排除，但会保留用于审计（可恢复）。只有 world/experience facts 可整理；observations 是派生数据。

#### 参数

| 名称          | In   | 类型       | 必填 | 说明                |
| ------------- | ---- | ---------- | ---- | ------------------- |
| `bank_id`   | path | `string` | 是   | Bank 的唯一标识符。 |
| `memory_id` | path | `string` | 是   | Memory 的唯一 ID。  |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段               | 类型               | 必填 | 说明                                                                                                                                                         |
| ------------------ | ------------------ | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `text`           | `string?`        | 否   | 新的 fact 文本。系统会重新生成该 memory 的 embedding，删除其派生 observations 和链接，并触发重新 consolidation。                                             |
| `context`        | `string?`        | 否   | fact 的新 context。传入空字符串会清除；省略则保持不变。                                                                                                      |
| `occurred_start` | `string?`        | 否   | 新的发生时间范围起点（ISO 8601）。传入空字符串会清除；省略则保持不变。                                                                                       |
| `occurred_end`   | `string?`        | 否   | 新的发生时间范围终点（ISO 8601）。传入空字符串会清除；省略则保持不变。                                                                                       |
| `fact_type`      | `string?`        | 否   | 重新分类 fact：'world' 或 'experience'。省略则保持不变。                                                                                                     |
| `entities`       | `array<string>?` | 否   | 替换 fact 的 entities。名称按 Retain 相同的方式解析或查找/创建；传入 [] 会解绑所有 entities。省略则保持不变。                                                |
| `state`          | `string?`        | 否   | 整理状态：`invalidated` 将 memory 软停用（从 recall/consolidation 中排除，清理 links 和派生 observations，并移入 archive），`valid` 可恢复。此操作可逆。 |
| `reason`         | `string?`        | 否   | 使其失效时记录的可选自由文本原因。                                                                                                                           |

#### 请求示例

```json
{
  "reason": "superseded: server decommissioned 2026-06-01",
  "state": "invalidated"
}
```

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

_无展开字段（标量、自由 object 或未声明 properties）_

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

获取 observation 的完整历史，并将每次变更的源 facts 解析为对应文本。

#### 参数

| 名称          | In   | 类型       | 必填 | 说明                |
| ------------- | ---- | ---------- | ---- | ------------------- |
| `bank_id`   | path | `string` | 是   | Bank 的唯一标识符。 |
| `memory_id` | path | `string` | 是   | Memory 的唯一 ID。  |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

_无展开字段（标量、自由 object 或未声明 properties）_

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

删除指定 memory 派生的所有 observations，并重置该 memory 以便重新 consolidation。memory 本身不会删除；系统会自动触发 consolidation，使其生成新的 observations。

#### 参数

| 名称          | In   | 类型       | 必填 | 说明                |
| ------------- | ---- | ---------- | ---- | ------------------- |
| `bank_id`   | path | `string` | 是   | Bank 的唯一标识符。 |
| `memory_id` | path | `string` | 是   | Memory 的唯一 ID。  |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段              | 类型        | 必填 | 说明         |
| ----------------- | ----------- | ---- | ------------ |
| `deleted_count` | `integer` | 是   | 已删除数量。 |

#### 响应示例

```json
{
  "deleted_count": 3
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

枚举 Bank observations 中的不同 scope。每个 observation 属于一个 scope，即与其一起 consolidation 的完整 tags 集合。返回所有不同 scope（tags 顺序已规范化）及其中 observation 数量；空 tags 列表表示全局/无标签 scope。可将返回的 scope 与 graph 接口（tags=<scope></scope> 且 tags_match=exact）配合使用，将 observations 精确筛选到该 scope。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段       | 类型                        | 必填 | 说明                                        |
| ---------- | --------------------------- | ---- | ------------------------------------------- |
| `scopes` | `array<ObservationScope>` | 是   | 不同的 observation scopes，按数量最多优先。 |

<details open><summary><strong>scopes[]</strong> · <code>ObservationScope</code></summary>

数据结构 `ObservationScope`：

| 字段      | 类型              | 必填 | 说明                                                                         |
| --------- | ----------------- | ---- | ---------------------------------------------------------------------------- |
| `tags`  | `array<string>` | 是   | 定义此 scope 的精确 tags 集合（顺序已规范化）。空列表表示全局/无标签 scope。 |
| `count` | `integer`       | 是   | 此 scope 下的 observation 数量。                                             |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

使用 bank identity、world facts、observations 和 mental models 进行 Reflect 并组织回答。

此接口：

1. 检索 experience（对话和事件）
2. 检索与查询相关的 world facts
3. 检索 observations 和 mental models（Bank 的综合视角）
4. 使用 LLM 生成符合上下文的回答
5. 返回纯文本回答及所使用的事实

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段                         | 类型                                                                                | 必填 | 说明                                                                                                                                                                                                                                                                                   |
| ---------------------------- | ----------------------------------------------------------------------------------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `query`                    | `string`                                                                          | 是   | 查询文本。                                                                                                                                                                                                                                                                             |
| `budget`                   | `Budget`                                                                          | 否   | 默认值：`"low"`                                                                                                                                                                                                                                                                      |
| `max_tokens`               | `integer`                                                                         | 否   | 响应的最大 token 数量；默认值：`4096`                                                                                                                                                                                                                                                |
| `include`                  | `ReflectIncludeOptions`                                                           | 否   | 是否包含附加数据的选项（默认禁用）。                                                                                                                                                                                                                                                   |
| `response_schema`          | `object?`                                                                         | 否   | 可选的结构化输出 JSON Schema。提供后，响应会包含 structured_output 字段，其中是按此 schema 解析的 LLM 响应。                                                                                                                                                                           |
| `tags`                     | `array<string>?`                                                                  | 否   | Reflect 期间按 tags 筛选 memories。未指定时考虑所有 memories。                                                                                                                                                                                                                         |
| `tags_match`               | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"`                           | 否   | tag 的匹配方式: 'any' (OR, includes untagged), 'all' (AND, includes untagged), 'any_strict' (OR, excludes untagged), 'all_strict' (AND, excludes untagged)；默认值：`"any"`                                                                                                          |
| `tag_groups`               | `array<TagGroupLeaf \| TagGroupAnd-Input \| TagGroupOr-Input \| TagGroupNot-Input>?` | 否   | 使用布尔分组的复合 tag 筛选器。列表中的 groups 按 AND 组合；每个 group 可以是叶节点 {tags, match}，也可以是复合结构 {and: [...]}、{or: [...]} 或 {not: ...}。                                                                                                                          |
| `apply_all_directives`     | `boolean`                                                                         | 否   | Apply every active directive regardless of tags. By default directives are scoped like memories: untagged directives always apply, and tagged directives apply only when the request's tags match them. Set true to apply all active directives, ignoring tag scope；默认值：`false` |
| `fact_types`               | `array<"world" \| "experience" \| "observation">?`                                  | 否   | 筛选 Reflect 时检索的 fact type。null 表示全部类型（world、experience、observation）。                                                                                                                                                                                                 |
| `exclude_mental_models`    | `boolean`                                                                         | 否   | 为 true 时，从 Reflect 循环中排除所有 mental models（跳过 search_mental_models 工具）；默认值：`false`                                                                                                                                                                               |
| `exclude_mental_model_ids` | `array<string>?`                                                                  | 否   | 按 ID 从 Reflect 循环中排除指定 mental models。                                                                                                                                                                                                                                        |

<details open><summary><strong>budget</strong> · <code>Budget</code></summary>

类型：`Budget`

</details>

<details open><summary><strong>include</strong> · <code>ReflectIncludeOptions</code></summary>

数据结构 `ReflectIncludeOptions`：

| 字段           | 类型                         | 必填 | 说明                                                                                                        |
| -------------- | ---------------------------- | ---- | ----------------------------------------------------------------------------------------------------------- |
| `facts`      | `FactsIncludeOptions?`     | 否   | 是否包含回答依据的 facts。设置为 {} 启用，null 禁用（默认禁用）。                                           |
| `tool_calls` | `ToolCallsIncludeOptions?` | 否   | 是否包含 tool calls trace。设置为 {} 返回完整 trace（input+output），设置为 {output: false} 仅返回 inputs。 |

<details open><summary><strong>facts</strong> · <code>FactsIncludeOptions</code></summary>

类型：`FactsIncludeOptions`

</details>

<details open><summary><strong>tool_calls</strong> · <code>ToolCallsIncludeOptions</code></summary>

数据结构 `ToolCallsIncludeOptions`：

| 字段       | 类型        | 必填 | 说明                                                                               |
| ---------- | ----------- | ---- | ---------------------------------------------------------------------------------- |
| `output` | `boolean` | 否   | 在 trace 中包含工具输出。设为 false 时仅包含输入，可减小 payload；默认值：`true` |

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

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段                  | 类型                | 必填 | 说明                                                                           |
| --------------------- | ------------------- | ---- | ------------------------------------------------------------------------------ |
| `text`              | `string`          | 是   | Reflect 响应，采用格式规范的 Markdown（标题、列表、粗体/斜体、代码块等）。     |
| `based_on`          | `ReflectBasedOn?` | 否   | 生成响应所依据的证据。仅在设置 include.facts 时出现。                          |
| `structured_output` | `object?`         | 否   | 按请求 response_schema 解析的结构化输出。仅在请求提供 response_schema 时出现。 |
| `usage`             | `TokenUsage?`     | 否   | Reflect 期间 LLM 调用的 token 用量指标。                                       |
| `trace`             | `ReflectTrace?`   | 否   | Tool 和 LLM 调用的执行 trace。仅在设置 include.tool_calls 时出现。             |

<details open><summary><strong>based_on</strong> · <code>ReflectBasedOn</code></summary>

数据结构 `ReflectBasedOn`：

| 字段              | 类型                          | 必填 | 说明                                                 |
| ----------------- | ----------------------------- | ---- | ---------------------------------------------------- |
| `memories`      | `array<ReflectFact>`        | 否   | 用于生成响应的 memory facts；默认值：`[]`          |
| `mental_models` | `array<ReflectMentalModel>` | 否   | Mental models used during reflection；默认值：`[]` |
| `directives`    | `array<ReflectDirective>`   | 否   | Directives applied during reflection；默认值：`[]` |

<details open><summary><strong>memories[]</strong> · <code>ReflectFact</code></summary>

数据结构 `ReflectFact`：

| 字段               | 类型        | 必填 | 说明                                                                               |
| ------------------ | ----------- | ---- | ---------------------------------------------------------------------------------- |
| `id`             | `string?` | 否   | 对象的唯一标识符。                                                                 |
| `text`           | `string`  | 是   | Fact 文本。当 type=observation 时，此字段包含 Markdown 格式的 consolidation 知识。 |
| `type`           | `string?` | 否   | 对象或错误的类型。                                                                 |
| `context`        | `string?` | 否   | 上下文信息。                                                                       |
| `occurred_start` | `string?` | 否   | 事件开始时间。                                                                     |
| `occurred_end`   | `string?` | 否   | 事件结束时间。                                                                     |

</details>

<details open><summary><strong>mental_models[]</strong> · <code>ReflectMentalModel</code></summary>

数据结构 `ReflectMentalModel`：

| 字段        | 类型        | 必填 | 说明                     |
| ----------- | ----------- | ---- | ------------------------ |
| `id`      | `string`  | 是   | Mental model 的唯一 ID。 |
| `text`    | `string`  | 是   | Mental model 内容。      |
| `context` | `string?` | 否   | 附加 context。           |

</details>

<details open><summary><strong>directives[]</strong> · <code>ReflectDirective</code></summary>

数据结构 `ReflectDirective`：

| 字段        | 类型       | 必填 | 说明                  |
| ----------- | ---------- | ---- | --------------------- |
| `id`      | `string` | 是   | Directive 的唯一 ID。 |
| `name`    | `string` | 是   | Directive 名称。      |
| `content` | `string` | 是   | Directive 内容。      |

</details>

</details>

<details open><summary><strong>usage</strong> · <code>TokenUsage</code></summary>

数据结构 `TokenUsage`：

| 字段                | 类型        | 必填 | 说明                                                                                                                       |
| ------------------- | ----------- | ---- | -------------------------------------------------------------------------------------------------------------------------- |
| `input_tokens`    | `integer` | 否   | 消耗的输入／prompt token 数量；默认值：`0`                                                                               |
| `output_tokens`   | `integer` | 否   | 生成的可见输出／completion token 数量（不含推理／思考 token）；默认值：`0`                                               |
| `total_tokens`    | `integer` | 否   | token 总数（输入加输出，不含推理 token）；默认值：`0`                                                                    |
| `cached_tokens`   | `integer` | 否   | provider 报告的缓存命中／缓存读取 prompt token 数量；默认值：`0`                                                         |
| `thoughts_tokens` | `integer` | 否   | 模型生成的推理／思考 token 数量。部分 provider（如 Gemini 2.5+ 系列）按输出费率计费，但不会显示在可见响应中；默认值：`0` |

</details>

<details open><summary><strong>trace</strong> · <code>ReflectTrace</code></summary>

数据结构 `ReflectTrace`：

| 字段           | 类型                       | 必填 | 说明                                              |
| -------------- | -------------------------- | ---- | ------------------------------------------------- |
| `tool_calls` | `array<ReflectToolCall>` | 否   | Tool calls made during reflection；默认值：`[]` |
| `llm_calls`  | `array<ReflectLLMCall>`  | 否   | LLM calls made during reflection；默认值：`[]`  |

<details open><summary><strong>tool_calls[]</strong> · <code>ReflectToolCall</code></summary>

数据结构 `ReflectToolCall`：

| 字段            | 类型        | 必填 | 说明                                                         |
| --------------- | ----------- | ---- | ------------------------------------------------------------ |
| `tool`        | `string`  | 是   | Tool 名称：lookup、recall、learn、expand。                   |
| `input`       | `object`  | 是   | Tool 输入参数。                                              |
| `output`      | `object?` | 否   | Tool 输出（仅在 include.tool_calls.output 为 true 时包含）。 |
| `duration_ms` | `integer` | 是   | 执行耗时，单位为毫秒。                                       |
| `iteration`   | `integer` | 否   | 调用此工具时的迭代轮次（从 1 开始）；默认值：`0`           |

</details>

<details open><summary><strong>llm_calls[]</strong> · <code>ReflectLLMCall</code></summary>

数据结构 `ReflectLLMCall`：

| 字段            | 类型        | 必填 | 说明                                     |
| --------------- | ----------- | ---- | ---------------------------------------- |
| `scope`       | `string`  | 是   | 调用 scope：agent_1、agent_2、final 等。 |
| `duration_ms` | `integer` | 是   | 执行耗时，单位为毫秒。                   |

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
    "summary": "AI 具有变革性"
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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

列出 memory bank 中所有不重复的 tags 及使用次数。支持使用通配符 `*` 搜索（例如 user:*、*-fred、tag*-2），不区分大小写。使用 `source=mental_models` 可列出 mental models 使用的 tags，而不是 memories 使用的 tags。

#### 参数

| 名称        | In    | 类型                             | 必填 | 说明                                                                                                                |
| ----------- | ----- | -------------------------------- | ---- | ------------------------------------------------------------------------------------------------------------------- |
| `bank_id` | path  | `string`                       | 是   | Bank 的唯一标识符。                                                                                                 |
| `q`       | query | `string?`                      | 否   | 用于筛选 tags 的通配模式（例如 user:* 匹配 user:alice，*-admin 匹配 role-admin）。使用 * 作为通配符，不区分大小写。 |
| `source`  | query | `"memories" \| "mental_models"` | 否   | Where to read tags from: 'memories' (memory_units, default) or 'mental_models'；默认值：`"memories"`              |
| `limit`   | query | `integer`                      | 否   | 返回 tag 的最大数量；默认值：`100`；最小值：`0`                                                                 |
| `offset`  | query | `integer`                      | 否   | 分页偏移量；默认值：`0`；最小值：`0`                                                                            |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段       | 类型               | 必填 | 说明           |
| ---------- | ------------------ | ---- | -------------- |
| `items`  | `array<TagItem>` | 是   | 结果项目列表。 |
| `total`  | `integer`        | 是   | 总数量。       |
| `limit`  | `integer`        | 是   | 返回数量上限。 |
| `offset` | `integer`        | 是   | 分页偏移量。   |

<details open><summary><strong>items[]</strong> · <code>TagItem</code></summary>

数据结构 `TagItem`：

| 字段      | 类型        | 必填 | 说明                          |
| --------- | ----------- | ---- | ----------------------------- |
| `tag`   | `string`  | 是   | Tag 值。                      |
| `count` | `integer` | 是   | 带有此 tag 的 memories 数量。 |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

**知识库树（Knowledge Pages）** · 8 个接口

folder/page 树组织 mental model；异步生成 page；hybrid 搜索与 markdown 导出。

### 本章目录

| Method     | Path                                                           | 标题                                      |
| ---------- | -------------------------------------------------------------- | ----------------------------------------- |
| `GET`    | `/v1/default/banks/{bank_id}/knowledge-base/export`          | [导出知识库](#export-knowledge-base)       |
| `POST`   | `/v1/default/banks/{bank_id}/knowledge-base/folders`         | [创建知识库目录](#create-knowledge-folder) |
| `PATCH`  | `/v1/default/banks/{bank_id}/knowledge-base/nodes/{node_id}` | [更新知识库节点](#update-knowledge-node)   |
| `DELETE` | `/v1/default/banks/{bank_id}/knowledge-base/nodes/{node_id}` | [删除知识库节点](#delete-knowledge-node)   |
| `POST`   | `/v1/default/banks/{bank_id}/knowledge-base/pages`           | [创建知识库页面](#create-knowledge-page)   |
| `GET`    | `/v1/default/banks/{bank_id}/knowledge-base/pages/{page_id}` | [读取知识库页面](#get-knowledge-page)      |
| `GET`    | `/v1/default/banks/{bank_id}/knowledge-base/search`          | [搜索知识库页面](#search-knowledge-base)   |
| `GET`    | `/v1/default/banks/{bank_id}/knowledge-base/tree`            | [获取知识库树](#get-knowledge-base-tree)   |

### 导出知识库

<a id="export-knowledge-base"></a>

**GET** `/v1/default/banks/{bank_id}/knowledge-base/export`

返回可移植的 Markdown bundle：嵌套的 index.md、每个页面一个 <id></id>.md，以及历史日志。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段      | 类型                               | 必填 | 说明       |
| --------- | ---------------------------------- | ---- | ---------- |
| `files` | `array<KnowledgePageBundleFile>` | 是   | 文件列表。 |

<details open><summary><strong>files[]</strong> · <code>KnowledgePageBundleFile</code></summary>

数据结构 `KnowledgePageBundleFile`：

| 字段        | 类型       | 必填 | 说明                                                     |
| ----------- | ---------- | ---- | -------------------------------------------------------- |
| `path`    | `string` | 是   | 资源路径。                                               |
| `content` | `string` | 是   | 资源的正文内容；对 directive/page 等资源含其可编辑文本。 |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

创建文件夹，可选择嵌套在父文件夹下。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段          | 类型        | 必填 | 说明                 |
| ------------- | ----------- | ---- | -------------------- |
| `name`      | `string`  | 是   | 名称。               |
| `parent_id` | `string?` | 否   | 父节点的唯一标识符。 |

#### 请求示例

```json
{
  "name": "string",
  "parent_id": "string"
}
```

#### 响应

- 状态码：`201` — 成功响应
- 格式：`application/json`

| 字段                | 类型                     | 必填 | 说明                                                                                            |
| ------------------- | ------------------------ | ---- | ----------------------------------------------------------------------------------------------- |
| `id`              | `string`               | 是   | 资源的唯一标识符。                                                                              |
| `kind`            | `"folder" \| "page"`    | 是   | 节点类型：`folder` 或 `page`。                                                              |
| `name`            | `string`               | 是   | 名称。                                                                                          |
| `parent_id`       | `string?`              | 否   | 父节点的唯一标识符。                                                                            |
| `mental_model_id` | `string?`              | 否   | 作为页面内容来源的 mental model ID（仅 page）。                                                 |
| `managed`         | `boolean`              | 否   | Client-set flag: true = system-owned, false = hand-authored；默认值：`false`                  |
| `description`     | `string?`              | 否   | 页面的 source query（即页面`description`）。                                                  |
| `tags`            | `array<string>`        | 否   | 默认值：`[]`                                                                                  |
| `timestamp`       | `string?`              | 否   | page 的最近刷新时间，或 folder 的最近更新时间。                                                 |
| `is_stale`        | `boolean?`             | 否   | 仅适用于 page：scope 内存在比上次刷新更新的 memories（内容不同步）时为 true。由 tree 接口填充。 |
| `children`        | `array<KnowledgeNode>` | 否   | 默认值：`[]`                                                                                  |

<details open><summary><strong>children[]</strong> · <code>KnowledgeNode</code></summary>

数据结构 `KnowledgeNode`：

| 字段                | 类型                     | 必填 | 说明                                                                                            |
| ------------------- | ------------------------ | ---- | ----------------------------------------------------------------------------------------------- |
| `id`              | `string`               | 是   | 资源的唯一标识符。                                                                              |
| `kind`            | `"folder" \| "page"`    | 是   | 节点类型：`folder` 或 `page`。                                                              |
| `name`            | `string`               | 是   | 名称。                                                                                          |
| `parent_id`       | `string?`              | 否   | 父节点的唯一标识符。                                                                            |
| `mental_model_id` | `string?`              | 否   | 作为页面内容来源的 mental model ID（仅 page）。                                                 |
| `managed`         | `boolean`              | 否   | Client-set flag: true = system-owned, false = hand-authored；默认值：`false`                  |
| `description`     | `string?`              | 否   | 页面的 source query（即页面`description`）。                                                  |
| `tags`            | `array<string>`        | 否   | 默认值：`[]`                                                                                  |
| `timestamp`       | `string?`              | 否   | page 的最近刷新时间，或 folder 的最近更新时间。                                                 |
| `is_stale`        | `boolean?`             | 否   | 仅适用于 page：scope 内存在比上次刷新更新的 memories（内容不同步）时为 true。由 tree 接口填充。 |
| `children`        | `array<KnowledgeNode>` | 否   | 默认值：`[]`                                                                                  |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

重命名节点（设置 `name`）、将其移动到其他文件夹下（设置 `parent_id`，根节点使用 null），和/或更新页面选项（`source_query`、`tags`、`max_tokens`）。修改 `source_query` 会安排异步 refresh，使页面基于新问题重新构建。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |
| `node_id` | path | `string` | 是   | 节点的唯一 ID。     |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段             | 类型               | 必填 | 说明                           |
| ---------------- | ------------------ | ---- | ------------------------------ |
| `name`         | `string?`        | 否   | 名称。                         |
| `parent_id`    | `string?`        | 否   | 父节点的唯一标识符。           |
| `source_query` | `string?`        | 否   | 生成或刷新内容所使用的源查询。 |
| `tags`         | `array<string>?` | 否   | 标签列表。                     |
| `max_tokens`   | `integer?`       | 否   | 最大 token 数。                |

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

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段                | 类型                     | 必填 | 说明                                                                                            |
| ------------------- | ------------------------ | ---- | ----------------------------------------------------------------------------------------------- |
| `id`              | `string`               | 是   | 资源的唯一标识符。                                                                              |
| `kind`            | `"folder" \| "page"`    | 是   | 节点类型：`folder` 或 `page`。                                                              |
| `name`            | `string`               | 是   | 名称。                                                                                          |
| `parent_id`       | `string?`              | 否   | 父节点的唯一标识符。                                                                            |
| `mental_model_id` | `string?`              | 否   | 作为页面内容来源的 mental model ID（仅 page）。                                                 |
| `managed`         | `boolean`              | 否   | Client-set flag: true = system-owned, false = hand-authored；默认值：`false`                  |
| `description`     | `string?`              | 否   | 页面的 source query（即页面`description`）。                                                  |
| `tags`            | `array<string>`        | 否   | 默认值：`[]`                                                                                  |
| `timestamp`       | `string?`              | 否   | page 的最近刷新时间，或 folder 的最近更新时间。                                                 |
| `is_stale`        | `boolean?`             | 否   | 仅适用于 page：scope 内存在比上次刷新更新的 memories（内容不同步）时为 true。由 tree 接口填充。 |
| `children`        | `array<KnowledgeNode>` | 否   | 默认值：`[]`                                                                                  |

<details open><summary><strong>children[]</strong> · <code>KnowledgeNode</code></summary>

数据结构 `KnowledgeNode`：

| 字段                | 类型                     | 必填 | 说明                                                                                            |
| ------------------- | ------------------------ | ---- | ----------------------------------------------------------------------------------------------- |
| `id`              | `string`               | 是   | 资源的唯一标识符。                                                                              |
| `kind`            | `"folder" \| "page"`    | 是   | 节点类型：`folder` 或 `page`。                                                              |
| `name`            | `string`               | 是   | 名称。                                                                                          |
| `parent_id`       | `string?`              | 否   | 父节点的唯一标识符。                                                                            |
| `mental_model_id` | `string?`              | 否   | 作为页面内容来源的 mental model ID（仅 page）。                                                 |
| `managed`         | `boolean`              | 否   | Client-set flag: true = system-owned, false = hand-authored；默认值：`false`                  |
| `description`     | `string?`              | 否   | 页面的 source query（即页面`description`）。                                                  |
| `tags`            | `array<string>`        | 否   | 默认值：`[]`                                                                                  |
| `timestamp`       | `string?`              | 否   | page 的最近刷新时间，或 folder 的最近更新时间。                                                 |
| `is_stale`        | `boolean?`             | 否   | 仅适用于 page：scope 内存在比上次刷新更新的 memories（内容不同步）时为 true。由 tree 接口填充。 |
| `children`        | `array<KnowledgeNode>` | 否   | 默认值：`[]`                                                                                  |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

删除文件夹或页面及其整个子树（页面对应的 mental models 也会删除）。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |
| `node_id` | path | `string` | 是   | 节点的唯一 ID。     |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

_无展开字段（标量、自由 object 或未声明 properties）_

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

创建页面（一个 mental model 加一个树节点）。内容异步生成；使用返回的 operation_id 跟踪完成状态。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段             | 类型                          | 必填 | 说明                                            |
| ---------------- | ----------------------------- | ---- | ----------------------------------------------- |
| `name`         | `string`                    | 是   | 名称。                                          |
| `source_query` | `string`                    | 是   | 生成或刷新 mental model/page 内容时使用的查询。 |
| `parent_id`    | `string?`                   | 否   | 父节点的唯一标识符。                            |
| `tags`         | `array<string>?`            | 否   | 标签列表。                                      |
| `max_tokens`   | `integer?`                  | 否   | 最大 token 数。                                 |
| `trigger`      | `MentalModelTrigger-Input?` | 否   | 触发方式或触发配置。                            |

<details open><summary><strong>trigger</strong> · <code>MentalModelTrigger-Input</code></summary>

数据结构 `MentalModelTrigger-Input`：

| 字段                            | 类型                                                                                | 必填 | 说明                                                                                                                                                                                                                                                                                                                                                  |
| ------------------------------- | ----------------------------------------------------------------------------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mode`                        | `"full" \| "delta"`                                                                | 否   | 刷新模式。full（默认）每次刷新都从头生成 mental model 内容；delta 在现有内容上进行局部编辑，逐字节保留未变化的章节，移除过时内容并加入新内容。如果 mental model 尚无内容，或 source_query 自上次刷新后发生变化，delta 会自动回退为完整生成；默认值：`"full"`                                                                                        |
| `response_schema`             | `object?`                                                                         | 否   | 用于结构化输出的可选 JSON Schema。设置后，每次刷新都会执行与 Reflect`response_schema` 相同的结构化抽取，并将解析结果存入 `reflect_response.structured_output`，同时保留 Markdown 内容。                                                                                                                                                           |
| `keep_trace`                  | `boolean`                                                                         | 否   | 为 true 时，记录 mental model 每次刷新的执行 trace，便于诊断定时或 consolidation 触发的刷新。仅保留最近一次 trace；工具输出会缩减为结果数量，以限制存储规模；默认值：`false`                                                                                                                                                                        |
| `refresh_after_consolidation` | `boolean`                                                                         | 否   | 为 true 时，在 observations consolidation 后刷新此 mental model（实时模式）；默认值：`false`                                                                                                                                                                                                                                                        |
| `refresh_cron`                | `string?`                                                                         | 否   | 用于按固定计划刷新此 mental model 的 cron 表达式（UTC，标准 5 字段语法，例如`0 3 * * *` 表示每天 UTC 03:00）。与 refresh_after_consolidation 互斥：model 只能在 consolidation 后刷新或按 cron 刷新，不能同时启用。计划刷新仅在 model 已过期时执行（自上次刷新后 scope 内出现新 memories）；没有变化时跳过，避免浪费 LLM 调用。null 表示不设置计划。 |
| `fact_types`                  | `array<"world" \| "experience" \| "observation">?`                                  | 否   | 筛选 Reflect 时检索的 fact type。null 表示全部类型（world、experience、observation）。                                                                                                                                                                                                                                                                |
| `exclude_mental_models`       | `boolean`                                                                         | 否   | 为 true 时，从 Reflect 循环中排除所有 mental models（跳过 search_mental_models 工具）；默认值：`false`                                                                                                                                                                                                                                              |
| `exclude_mental_model_ids`    | `array<string>?`                                                                  | 否   | 按 ID 从 Reflect 循环中排除指定 mental models。                                                                                                                                                                                                                                                                                                       |
| `tags_match`                  | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"?`                          | 否   | 覆盖 refresh 时 model tags 筛选 memories 的方式。未设置时，有 tags 的 model 默认为 all_strict（用于安全隔离），无 tags 的 model 默认为 any。设置为 any 可在 refresh 时同时包含无标签和有标签 memories。                                                                                                                                               |
| `tag_groups`                  | `array<TagGroupLeaf \| TagGroupAnd-Input \| TagGroupOr-Input \| TagGroupNot-Input>?` | 否   | Refresh 时使用的复合布尔 tag 表达式，用于替代 model 自身的 tags。设置后，这些 tag groups 会传给 Reflect，model 的扁平 tags 不再用于筛选。支持嵌套 and/or/not 表达式，以实现复杂的 tag scope。                                                                                                                                                         |
| `include_chunks`              | `boolean?`                                                                        | 否   | 覆盖 refresh 内部 Recall 是否返回原始 chunk 文本。null 表示使用 Bank／全局 配置默认值（recall_include_chunks）。                                                                                                                                                                                                                                      |
| `recall_max_tokens`           | `integer?`                                                                        | 否   | 覆盖 refresh 内部 Recall 返回 facts 的 token budget。null 表示使用 Bank／全局 配置默认值（recall_max_tokens）。                                                                                                                                                                                                                                       |
| `recall_chunks_max_tokens`    | `integer?`                                                                        | 否   | 覆盖 refresh 内部 Recall 返回原始 chunks 的 token budget。null 表示使用 Bank／全局 配置默认值（recall_chunks_max_tokens）。                                                                                                                                                                                                                           |

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
    "recall_chunks_max_tokens": 0
  }
}
```

#### 响应

- 状态码：`201` — 成功响应
- 格式：`application/json`

| 字段                | 类型        | 必填 | 说明                        |
| ------------------- | ----------- | ---- | --------------------------- |
| `page_id`         | `string`  | 是   | 页面的唯一标识符。          |
| `mental_model_id` | `string`  | 是   | Mental model 的唯一标识符。 |
| `operation_id`    | `string?` | 否   | 异步操作 的唯一标识符。     |

#### 响应示例

```json
{
  "page_id": "string",
  "mental_model_id": "string",
  "operation_id": "string"
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

以 Markdown 文档（frontmatter + Markdown 正文）返回单个页面。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |
| `page_id` | path | `string` | 是   | Page 的唯一 ID。    |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段            | 类型              | 必填 | 说明                                                        |
| --------------- | ----------------- | ---- | ----------------------------------------------------------- |
| `id`          | `string`        | 是   | 资源的唯一标识符。                                          |
| `name`        | `string`        | 是   | 名称。                                                      |
| `type`        | `string`        | 是   | Page type；优先取 type:<x></x> tag，否则为 knowledge-page。 |
| `description` | `string?`       | 否   | 用于重建页面的 source query。                               |
| `tags`        | `array<string>` | 否   | 默认值：`[]`                                              |
| `timestamp`   | `string?`       | 否   | 最近刷新时间；没有刷新记录时回退到创建时间。                |
| `body`        | `string?`       | 否   | 页面合成后的 Markdown 正文。                                |
| `markdown`    | `string`        | 是   | 完整 Markdown 文档：YAML frontmatter + Markdown 正文。      |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

在 Bank knowledge pages 上执行 document 级混合搜索：融合 full-text（BM25）匹配和向量相似度匹配，使用 Reciprocal-Rank-Fusion 合并结果。不使用 reranker，以降低延迟。

#### 参数

| 名称        | In    | 类型        | 必填 | 说明                                                        |
| ----------- | ----- | ----------- | ---- | ----------------------------------------------------------- |
| `bank_id` | path  | `string`  | 是   | Bank 的唯一标识符。                                         |
| `q`       | query | `string`  | 是   | 搜索查询；minLen`1`                                       |
| `limit`   | query | `integer` | 否   | 返回结果的最大数量；默认值：`10`；取值范围：`1`–`50` |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段        | 类型                                 | 必填 | 说明       |
| ----------- | ------------------------------------ | ---- | ---------- |
| `results` | `array<KnowledgePageSearchResult>` | 是   | 结果列表。 |
| `total`   | `integer`                          | 是   | 总数量。   |

<details open><summary><strong>results[]</strong> · <code>KnowledgePageSearchResult</code></summary>

数据结构 `KnowledgePageSearchResult`：

| 字段                | 类型        | 必填 | 说明                        |
| ------------------- | ----------- | ---- | --------------------------- |
| `id`              | `string`  | 是   | 资源的唯一标识符。          |
| `name`            | `string`  | 是   | 名称。                      |
| `mental_model_id` | `string?` | 否   | Mental model 的唯一标识符。 |
| `snippet`         | `string`  | 是   | 匹配内容摘要。              |
| `score`           | `number`  | 是   | 匹配或排序得分。            |
| `updated_at`      | `string?` | 否   | 最后更新时间。              |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

以嵌套的文件夹和页面树返回 knowledge base。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段      | 类型                     | 必填 | 说明             |
| --------- | ------------------------ | ---- | ---------------- |
| `roots` | `array<KnowledgeNode>` | 是   | 树的根节点列表。 |

<details open><summary><strong>roots[]</strong> · <code>KnowledgeNode</code></summary>

数据结构 `KnowledgeNode`：

| 字段                | 类型                     | 必填 | 说明                                                                                            |
| ------------------- | ------------------------ | ---- | ----------------------------------------------------------------------------------------------- |
| `id`              | `string`               | 是   | 资源的唯一标识符。                                                                              |
| `kind`            | `"folder" \| "page"`    | 是   | 节点类型：`folder` 或 `page`。                                                              |
| `name`            | `string`               | 是   | 名称。                                                                                          |
| `parent_id`       | `string?`              | 否   | 父节点的唯一标识符。                                                                            |
| `mental_model_id` | `string?`              | 否   | 作为页面内容来源的 mental model ID（仅 page）。                                                 |
| `managed`         | `boolean`              | 否   | Client-set flag: true = system-owned, false = hand-authored；默认值：`false`                  |
| `description`     | `string?`              | 否   | 页面的 source query（即页面`description`）。                                                  |
| `tags`            | `array<string>`        | 否   | 默认值：`[]`                                                                                  |
| `timestamp`       | `string?`              | 否   | page 的最近刷新时间，或 folder 的最近更新时间。                                                 |
| `is_stale`        | `boolean?`             | 否   | 仅适用于 page：scope 内存在比上次刷新更新的 memories（内容不同步）时为 true。由 tree 接口填充。 |
| `children`        | `array<KnowledgeNode>` | 否   | 默认值：`[]`                                                                                  |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

**心智模型** · 9 个接口

可刷新的合成知识（多为 Markdown），支持预览刷新结果。可独立使用，也可挂到 knowledge page。

### 本章目录

| Method     | Path                                                                            | 标题                                             |
| ---------- | ------------------------------------------------------------------------------- | ------------------------------------------------ |
| `GET`    | `/v1/default/banks/{bank_id}/mental-models`                                   | [列出心智模型](#list-mental-models)               |
| `POST`   | `/v1/default/banks/{bank_id}/mental-models`                                   | [创建心智模型](#create-mental-model)              |
| `GET`    | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}`                 | [获取心智模型](#get-mental-model)                 |
| `PATCH`  | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}`                 | [更新心智模型](#update-mental-model)              |
| `DELETE` | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}`                 | [删除心智模型](#delete-mental-model)              |
| `POST`   | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/clear`           | [清空心智模型正文](#clear-mental-model)           |
| `GET`    | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/history`         | [心智模型历史](#get-mental-model-history)         |
| `POST`   | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/refresh`         | [刷新心智模型](#refresh-mental-model)             |
| `POST`   | `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/dry-run-refresh` | [预览心智模型刷新](#dry-run-refresh-mental-model) |

### 列出心智模型

<a id="list-mental-models"></a>

**GET** `/v1/default/banks/{bank_id}/mental-models`

列出由用户维护、持续保持最新的文档。

#### 参数

| 名称           | In    | 类型                                | 必填 | 说明                                                                                                        |
| -------------- | ----- | ----------------------------------- | ---- | ----------------------------------------------------------------------------------------------------------- |
| `bank_id`    | path  | `string`                          | 是   | Bank 的唯一标识符。                                                                                         |
| `tags`       | query | `array<string>?`                  | 否   | 按 tags 筛选。                                                                                              |
| `tags_match` | query | `"any" \| "all" \| "exact"`         | 否   | tag 的匹配方式；默认值：`"any"`                                                                           |
| `detail`     | query | `"metadata" \| "content" \| "full"` | 否   | 详情级别：metadata 仅含名称和标签；content 另含内容和配置；full 还包含 reflect_response；默认值：`"full"` |
| `limit`      | query | `integer`                         | 否   | 默认值：`100`；取值范围：`1`–`1000`                                                                  |
| `offset`     | query | `integer`                         | 否   | 默认值：`0`；最小值：`0`                                                                                |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段      | 类型                           | 必填 | 说明           |
| --------- | ------------------------------ | ---- | -------------- |
| `items` | `array<MentalModelResponse>` | 是   | 结果项目列表。 |

<details open><summary><strong>items[]</strong> · <code>MentalModelResponse</code></summary>

数据结构 `MentalModelResponse`：

| 字段                  | 类型                           | 必填 | 说明                                                                                                                                                  |
| --------------------- | ------------------------------ | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                | `string`                     | 是   | 资源的唯一标识符。                                                                                                                                    |
| `bank_id`           | `string`                     | 是   | 所属 Bank 的唯一标识符。                                                                                                                              |
| `name`              | `string`                     | 是   | 名称。                                                                                                                                                |
| `source_query`      | `string?`                    | 否   | 生成或刷新内容所使用的源查询。                                                                                                                        |
| `content`           | `string?`                    | 否   | Mental model 内容，采用格式规范的 Markdown，由 Reflect 接口自动生成。                                                                                 |
| `tags`              | `array<string>`              | 否   | 默认值：`[]`                                                                                                                                        |
| `max_tokens`        | `integer?`                   | 否   | 最大 token 数。                                                                                                                                       |
| `trigger`           | `MentalModelTrigger-Output?` | 否   | 触发方式或触发配置。                                                                                                                                  |
| `last_refreshed_at` | `string?`                    | 否   | 最近刷新时间。                                                                                                                                        |
| `created_at`        | `string?`                    | 否   | 创建时间。                                                                                                                                            |
| `reflect_response`  | `object?`                    | 否   | 完整的 Reflect API 响应 payload，包括 based_on facts 和 observations。                                                                                |
| `is_stale`          | `boolean?`                   | 否   | 自 last_refreshed_at 后写入了符合此 mental model tag/fact_type scope 的新 memories，或 consolidation 仍有待处理项时为 true。仅在 detail=full 时填充。 |

<details open><summary><strong>trigger</strong> · <code>MentalModelTrigger-Output</code></summary>

数据结构 `MentalModelTrigger-Output`：

| 字段                            | 类型                                                                                   | 必填 | 说明                                                                                                                                                                                                                                                                                                                                                  |
| ------------------------------- | -------------------------------------------------------------------------------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mode`                        | `"full" \| "delta"`                                                                   | 否   | 刷新模式。full（默认）每次刷新都从头生成 mental model 内容；delta 在现有内容上进行局部编辑，逐字节保留未变化的章节，移除过时内容并加入新内容。如果 mental model 尚无内容，或 source_query 自上次刷新后发生变化，delta 会自动回退为完整生成；默认值：`"full"`                                                                                        |
| `response_schema`             | `object?`                                                                            | 否   | 用于结构化输出的可选 JSON Schema。设置后，每次刷新都会执行与 Reflect`response_schema` 相同的结构化抽取，并将解析结果存入 `reflect_response.structured_output`，同时保留 Markdown 内容。                                                                                                                                                           |
| `keep_trace`                  | `boolean`                                                                            | 否   | 为 true 时，记录 mental model 每次刷新的执行 trace，便于诊断定时或 consolidation 触发的刷新。仅保留最近一次 trace；工具输出会缩减为结果数量，以限制存储规模；默认值：`false`                                                                                                                                                                        |
| `refresh_after_consolidation` | `boolean`                                                                            | 否   | 为 true 时，在 observations consolidation 后刷新此 mental model（实时模式）；默认值：`false`                                                                                                                                                                                                                                                        |
| `refresh_cron`                | `string?`                                                                            | 否   | 用于按固定计划刷新此 mental model 的 cron 表达式（UTC，标准 5 字段语法，例如`0 3 * * *` 表示每天 UTC 03:00）。与 refresh_after_consolidation 互斥：model 只能在 consolidation 后刷新或按 cron 刷新，不能同时启用。计划刷新仅在 model 已过期时执行（自上次刷新后 scope 内出现新 memories）；没有变化时跳过，避免浪费 LLM 调用。null 表示不设置计划。 |
| `fact_types`                  | `array<"world" \| "experience" \| "observation">?`                                     | 否   | 筛选 Reflect 时检索的 fact type。null 表示全部类型（world、experience、observation）。                                                                                                                                                                                                                                                                |
| `exclude_mental_models`       | `boolean`                                                                            | 否   | 为 true 时，从 Reflect 循环中排除所有 mental models（跳过 search_mental_models 工具）；默认值：`false`                                                                                                                                                                                                                                              |
| `exclude_mental_model_ids`    | `array<string>?`                                                                     | 否   | 按 ID 从 Reflect 循环中排除指定 mental models。                                                                                                                                                                                                                                                                                                       |
| `tags_match`                  | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"?`                             | 否   | 覆盖 refresh 时 model tags 筛选 memories 的方式。未设置时，有 tags 的 model 默认为 all_strict（用于安全隔离），无 tags 的 model 默认为 any。设置为 any 可在 refresh 时同时包含无标签和有标签 memories。                                                                                                                                               |
| `tag_groups`                  | `array<TagGroupLeaf \| TagGroupAnd-Output \| TagGroupOr-Output \| TagGroupNot-Output>?` | 否   | Refresh 时使用的复合布尔 tag 表达式，用于替代 model 自身的 tags。设置后，这些 tag groups 会传给 Reflect，model 的扁平 tags 不再用于筛选。支持嵌套 and/or/not 表达式，以实现复杂的 tag scope。                                                                                                                                                         |
| `include_chunks`              | `boolean?`                                                                           | 否   | 覆盖 refresh 内部 Recall 是否返回原始 chunk 文本。null 表示使用 Bank／全局 配置默认值（recall_include_chunks）。                                                                                                                                                                                                                                      |
| `recall_max_tokens`           | `integer?`                                                                           | 否   | 覆盖 refresh 内部 Recall 返回 facts 的 token budget。null 表示使用 Bank／全局 配置默认值（recall_max_tokens）。                                                                                                                                                                                                                                       |
| `recall_chunks_max_tokens`    | `integer?`                                                                           | 否   | 覆盖 refresh 内部 Recall 返回原始 chunks 的 token budget。null 表示使用 Bank／全局 配置默认值（recall_chunks_max_tokens）。                                                                                                                                                                                                                           |

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
        "recall_chunks_max_tokens": 0
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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

在后台使用 source query 运行 Reflect 创建 mental model。返回用于跟踪进度的 operation ID。内容由 Reflect 接口自动生成；可通过 Operations 接口查询完成状态。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段             | 类型                         | 必填 | 说明                                                                   |
| ---------------- | ---------------------------- | ---- | ---------------------------------------------------------------------- |
| `id`           | `string?`                  | 否   | Mental model 的可选自定义 ID（小写字母数字和连字符）。                 |
| `name`         | `string`                   | 是   | Mental model 的可读名称。                                              |
| `source_query` | `string`                   | 是   | 用于生成内容的查询。                                                   |
| `tags`         | `array<string>`            | 否   | 标签。 for scoped visibility；默认值：`[]`                           |
| `max_tokens`   | `integer`                  | 否   | 生成内容的最大 token 数；默认值：`2048`；取值范围：`256`–`8192` |
| `trigger`      | `MentalModelTrigger-Input` | 否   | 触发器设置；默认值：`{}`                                             |

<details open><summary><strong>trigger</strong> · <code>MentalModelTrigger-Input</code></summary>

数据结构 `MentalModelTrigger-Input`：

| 字段                            | 类型                                                                                | 必填 | 说明                                                                                                                                                                                                                                                                                                                                                  |
| ------------------------------- | ----------------------------------------------------------------------------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mode`                        | `"full" \| "delta"`                                                                | 否   | 刷新模式。full（默认）每次刷新都从头生成 mental model 内容；delta 在现有内容上进行局部编辑，逐字节保留未变化的章节，移除过时内容并加入新内容。如果 mental model 尚无内容，或 source_query 自上次刷新后发生变化，delta 会自动回退为完整生成；默认值：`"full"`                                                                                        |
| `response_schema`             | `object?`                                                                         | 否   | 用于结构化输出的可选 JSON Schema。设置后，每次刷新都会执行与 Reflect`response_schema` 相同的结构化抽取，并将解析结果存入 `reflect_response.structured_output`，同时保留 Markdown 内容。                                                                                                                                                           |
| `keep_trace`                  | `boolean`                                                                         | 否   | 为 true 时，记录 mental model 每次刷新的执行 trace，便于诊断定时或 consolidation 触发的刷新。仅保留最近一次 trace；工具输出会缩减为结果数量，以限制存储规模；默认值：`false`                                                                                                                                                                        |
| `refresh_after_consolidation` | `boolean`                                                                         | 否   | 为 true 时，在 observations consolidation 后刷新此 mental model（实时模式）；默认值：`false`                                                                                                                                                                                                                                                        |
| `refresh_cron`                | `string?`                                                                         | 否   | 用于按固定计划刷新此 mental model 的 cron 表达式（UTC，标准 5 字段语法，例如`0 3 * * *` 表示每天 UTC 03:00）。与 refresh_after_consolidation 互斥：model 只能在 consolidation 后刷新或按 cron 刷新，不能同时启用。计划刷新仅在 model 已过期时执行（自上次刷新后 scope 内出现新 memories）；没有变化时跳过，避免浪费 LLM 调用。null 表示不设置计划。 |
| `fact_types`                  | `array<"world" \| "experience" \| "observation">?`                                  | 否   | 筛选 Reflect 时检索的 fact type。null 表示全部类型（world、experience、observation）。                                                                                                                                                                                                                                                                |
| `exclude_mental_models`       | `boolean`                                                                         | 否   | 为 true 时，从 Reflect 循环中排除所有 mental models（跳过 search_mental_models 工具）；默认值：`false`                                                                                                                                                                                                                                              |
| `exclude_mental_model_ids`    | `array<string>?`                                                                  | 否   | 按 ID 从 Reflect 循环中排除指定 mental models。                                                                                                                                                                                                                                                                                                       |
| `tags_match`                  | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"?`                          | 否   | 覆盖 refresh 时 model tags 筛选 memories 的方式。未设置时，有 tags 的 model 默认为 all_strict（用于安全隔离），无 tags 的 model 默认为 any。设置为 any 可在 refresh 时同时包含无标签和有标签 memories。                                                                                                                                               |
| `tag_groups`                  | `array<TagGroupLeaf \| TagGroupAnd-Input \| TagGroupOr-Input \| TagGroupNot-Input>?` | 否   | Refresh 时使用的复合布尔 tag 表达式，用于替代 model 自身的 tags。设置后，这些 tag groups 会传给 Reflect，model 的扁平 tags 不再用于筛选。支持嵌套 and/or/not 表达式，以实现复杂的 tag scope。                                                                                                                                                         |
| `include_chunks`              | `boolean?`                                                                        | 否   | 覆盖 refresh 内部 Recall 是否返回原始 chunk 文本。null 表示使用 Bank／全局 配置默认值（recall_include_chunks）。                                                                                                                                                                                                                                      |
| `recall_max_tokens`           | `integer?`                                                                        | 否   | 覆盖 refresh 内部 Recall 返回 facts 的 token budget。null 表示使用 Bank／全局 配置默认值（recall_max_tokens）。                                                                                                                                                                                                                                       |
| `recall_chunks_max_tokens`    | `integer?`                                                                        | 否   | 覆盖 refresh 内部 Recall 返回原始 chunks 的 token budget。null 表示使用 Bank／全局 配置默认值（recall_chunks_max_tokens）。                                                                                                                                                                                                                           |

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

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段                | 类型        | 必填 | 说明                                   |
| ------------------- | ----------- | ---- | -------------------------------------- |
| `mental_model_id` | `string?` | 否   | 已创建 mental model 的 ID。            |
| `operation_id`    | `string`  | 是   | 用于跟踪 refresh 进度的 operation ID。 |

#### 响应示例

```json
{
  "operation_id": "string",
  "mental_model_id": "string"
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

按 ID 获取指定 mental model。

#### 参数

| 名称                | In    | 类型                                | 必填 | 说明                                                                                                        |
| ------------------- | ----- | ----------------------------------- | ---- | ----------------------------------------------------------------------------------------------------------- |
| `bank_id`         | path  | `string`                          | 是   | Bank 的唯一标识符。                                                                                         |
| `mental_model_id` | path  | `string`                          | 是   | Mental 数据结构 Id                                                                                          |
| `detail`          | query | `"metadata" \| "content" \| "full"` | 否   | 详情级别：metadata 仅含名称和标签；content 另含内容和配置；full 还包含 reflect_response；默认值：`"full"` |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段                  | 类型                           | 必填 | 说明                                                                                                                                                  |
| --------------------- | ------------------------------ | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                | `string`                     | 是   | 资源的唯一标识符。                                                                                                                                    |
| `bank_id`           | `string`                     | 是   | 所属 Bank 的唯一标识符。                                                                                                                              |
| `name`              | `string`                     | 是   | 名称。                                                                                                                                                |
| `source_query`      | `string?`                    | 否   | 生成或刷新内容所使用的源查询。                                                                                                                        |
| `content`           | `string?`                    | 否   | Mental model 内容，采用格式规范的 Markdown，由 Reflect 接口自动生成。                                                                                 |
| `tags`              | `array<string>`              | 否   | 默认值：`[]`                                                                                                                                        |
| `max_tokens`        | `integer?`                   | 否   | 最大 token 数。                                                                                                                                       |
| `trigger`           | `MentalModelTrigger-Output?` | 否   | 触发方式或触发配置。                                                                                                                                  |
| `last_refreshed_at` | `string?`                    | 否   | 最近刷新时间。                                                                                                                                        |
| `created_at`        | `string?`                    | 否   | 创建时间。                                                                                                                                            |
| `reflect_response`  | `object?`                    | 否   | 完整的 Reflect API 响应 payload，包括 based_on facts 和 observations。                                                                                |
| `is_stale`          | `boolean?`                   | 否   | 自 last_refreshed_at 后写入了符合此 mental model tag/fact_type scope 的新 memories，或 consolidation 仍有待处理项时为 true。仅在 detail=full 时填充。 |

<details open><summary><strong>trigger</strong> · <code>MentalModelTrigger-Output</code></summary>

数据结构 `MentalModelTrigger-Output`：

| 字段                            | 类型                                                                                   | 必填 | 说明                                                                                                                                                                                                                                                                                                                                                  |
| ------------------------------- | -------------------------------------------------------------------------------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mode`                        | `"full" \| "delta"`                                                                   | 否   | 刷新模式。full（默认）每次刷新都从头生成 mental model 内容；delta 在现有内容上进行局部编辑，逐字节保留未变化的章节，移除过时内容并加入新内容。如果 mental model 尚无内容，或 source_query 自上次刷新后发生变化，delta 会自动回退为完整生成；默认值：`"full"`                                                                                        |
| `response_schema`             | `object?`                                                                            | 否   | 用于结构化输出的可选 JSON Schema。设置后，每次刷新都会执行与 Reflect`response_schema` 相同的结构化抽取，并将解析结果存入 `reflect_response.structured_output`，同时保留 Markdown 内容。                                                                                                                                                           |
| `keep_trace`                  | `boolean`                                                                            | 否   | 为 true 时，记录 mental model 每次刷新的执行 trace，便于诊断定时或 consolidation 触发的刷新。仅保留最近一次 trace；工具输出会缩减为结果数量，以限制存储规模；默认值：`false`                                                                                                                                                                        |
| `refresh_after_consolidation` | `boolean`                                                                            | 否   | 为 true 时，在 observations consolidation 后刷新此 mental model（实时模式）；默认值：`false`                                                                                                                                                                                                                                                        |
| `refresh_cron`                | `string?`                                                                            | 否   | 用于按固定计划刷新此 mental model 的 cron 表达式（UTC，标准 5 字段语法，例如`0 3 * * *` 表示每天 UTC 03:00）。与 refresh_after_consolidation 互斥：model 只能在 consolidation 后刷新或按 cron 刷新，不能同时启用。计划刷新仅在 model 已过期时执行（自上次刷新后 scope 内出现新 memories）；没有变化时跳过，避免浪费 LLM 调用。null 表示不设置计划。 |
| `fact_types`                  | `array<"world" \| "experience" \| "observation">?`                                     | 否   | 筛选 Reflect 时检索的 fact type。null 表示全部类型（world、experience、observation）。                                                                                                                                                                                                                                                                |
| `exclude_mental_models`       | `boolean`                                                                            | 否   | 为 true 时，从 Reflect 循环中排除所有 mental models（跳过 search_mental_models 工具）；默认值：`false`                                                                                                                                                                                                                                              |
| `exclude_mental_model_ids`    | `array<string>?`                                                                     | 否   | 按 ID 从 Reflect 循环中排除指定 mental models。                                                                                                                                                                                                                                                                                                       |
| `tags_match`                  | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"?`                             | 否   | 覆盖 refresh 时 model tags 筛选 memories 的方式。未设置时，有 tags 的 model 默认为 all_strict（用于安全隔离），无 tags 的 model 默认为 any。设置为 any 可在 refresh 时同时包含无标签和有标签 memories。                                                                                                                                               |
| `tag_groups`                  | `array<TagGroupLeaf \| TagGroupAnd-Output \| TagGroupOr-Output \| TagGroupNot-Output>?` | 否   | Refresh 时使用的复合布尔 tag 表达式，用于替代 model 自身的 tags。设置后，这些 tag groups 会传给 Reflect，model 的扁平 tags 不再用于筛选。支持嵌套 and/or/not 表达式，以实现复杂的 tag scope。                                                                                                                                                         |
| `include_chunks`              | `boolean?`                                                                           | 否   | 覆盖 refresh 内部 Recall 是否返回原始 chunk 文本。null 表示使用 Bank／全局 配置默认值（recall_include_chunks）。                                                                                                                                                                                                                                      |
| `recall_max_tokens`           | `integer?`                                                                           | 否   | 覆盖 refresh 内部 Recall 返回 facts 的 token budget。null 表示使用 Bank／全局 配置默认值（recall_max_tokens）。                                                                                                                                                                                                                                       |
| `recall_chunks_max_tokens`    | `integer?`                                                                           | 否   | 覆盖 refresh 内部 Recall 返回原始 chunks 的 token budget。null 表示使用 Bank／全局 配置默认值（recall_chunks_max_tokens）。                                                                                                                                                                                                                           |

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
    "recall_chunks_max_tokens": 0
  },
  "last_refreshed_at": "string",
  "created_at": "string",
  "reflect_response": {},
  "is_stale": false
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

更新 mental model 的名称和/或 source query。

#### 参数

| 名称                | In   | 类型       | 必填 | 说明                |
| ------------------- | ---- | ---------- | ---- | ------------------- |
| `bank_id`         | path | `string` | 是   | Bank 的唯一标识符。 |
| `mental_model_id` | path | `string` | 是   | Mental 数据结构 Id  |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段             | 类型                          | 必填 | 说明                                                 |
| ---------------- | ----------------------------- | ---- | ---------------------------------------------------- |
| `name`         | `string?`                   | 否   | mental model 的新名称。                              |
| `source_query` | `string?`                   | 否   | Mental model 的新 source query。                     |
| `max_tokens`   | `integer?`                  | 否   | 生成内容的最大 token 数；取值范围：`256`–`8192` |
| `tags`         | `array<string>?`            | 否   | 标签。 for scoped visibility                         |
| `trigger`      | `MentalModelTrigger-Input?` | 否   | 触发器设置。                                         |

<details open><summary><strong>trigger</strong> · <code>MentalModelTrigger-Input</code></summary>

数据结构 `MentalModelTrigger-Input`：

| 字段                            | 类型                                                                                | 必填 | 说明                                                                                                                                                                                                                                                                                                                                                  |
| ------------------------------- | ----------------------------------------------------------------------------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mode`                        | `"full" \| "delta"`                                                                | 否   | 刷新模式。full（默认）每次刷新都从头生成 mental model 内容；delta 在现有内容上进行局部编辑，逐字节保留未变化的章节，移除过时内容并加入新内容。如果 mental model 尚无内容，或 source_query 自上次刷新后发生变化，delta 会自动回退为完整生成；默认值：`"full"`                                                                                        |
| `response_schema`             | `object?`                                                                         | 否   | 用于结构化输出的可选 JSON Schema。设置后，每次刷新都会执行与 Reflect`response_schema` 相同的结构化抽取，并将解析结果存入 `reflect_response.structured_output`，同时保留 Markdown 内容。                                                                                                                                                           |
| `keep_trace`                  | `boolean`                                                                         | 否   | 为 true 时，记录 mental model 每次刷新的执行 trace，便于诊断定时或 consolidation 触发的刷新。仅保留最近一次 trace；工具输出会缩减为结果数量，以限制存储规模；默认值：`false`                                                                                                                                                                        |
| `refresh_after_consolidation` | `boolean`                                                                         | 否   | 为 true 时，在 observations consolidation 后刷新此 mental model（实时模式）；默认值：`false`                                                                                                                                                                                                                                                        |
| `refresh_cron`                | `string?`                                                                         | 否   | 用于按固定计划刷新此 mental model 的 cron 表达式（UTC，标准 5 字段语法，例如`0 3 * * *` 表示每天 UTC 03:00）。与 refresh_after_consolidation 互斥：model 只能在 consolidation 后刷新或按 cron 刷新，不能同时启用。计划刷新仅在 model 已过期时执行（自上次刷新后 scope 内出现新 memories）；没有变化时跳过，避免浪费 LLM 调用。null 表示不设置计划。 |
| `fact_types`                  | `array<"world" \| "experience" \| "observation">?`                                  | 否   | 筛选 Reflect 时检索的 fact type。null 表示全部类型（world、experience、observation）。                                                                                                                                                                                                                                                                |
| `exclude_mental_models`       | `boolean`                                                                         | 否   | 为 true 时，从 Reflect 循环中排除所有 mental models（跳过 search_mental_models 工具）；默认值：`false`                                                                                                                                                                                                                                              |
| `exclude_mental_model_ids`    | `array<string>?`                                                                  | 否   | 按 ID 从 Reflect 循环中排除指定 mental models。                                                                                                                                                                                                                                                                                                       |
| `tags_match`                  | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"?`                          | 否   | 覆盖 refresh 时 model tags 筛选 memories 的方式。未设置时，有 tags 的 model 默认为 all_strict（用于安全隔离），无 tags 的 model 默认为 any。设置为 any 可在 refresh 时同时包含无标签和有标签 memories。                                                                                                                                               |
| `tag_groups`                  | `array<TagGroupLeaf \| TagGroupAnd-Input \| TagGroupOr-Input \| TagGroupNot-Input>?` | 否   | Refresh 时使用的复合布尔 tag 表达式，用于替代 model 自身的 tags。设置后，这些 tag groups 会传给 Reflect，model 的扁平 tags 不再用于筛选。支持嵌套 and/or/not 表达式，以实现复杂的 tag scope。                                                                                                                                                         |
| `include_chunks`              | `boolean?`                                                                        | 否   | 覆盖 refresh 内部 Recall 是否返回原始 chunk 文本。null 表示使用 Bank／全局 配置默认值（recall_include_chunks）。                                                                                                                                                                                                                                      |
| `recall_max_tokens`           | `integer?`                                                                        | 否   | 覆盖 refresh 内部 Recall 返回 facts 的 token budget。null 表示使用 Bank／全局 配置默认值（recall_max_tokens）。                                                                                                                                                                                                                                       |
| `recall_chunks_max_tokens`    | `integer?`                                                                        | 否   | 覆盖 refresh 内部 Recall 返回原始 chunks 的 token budget。null 表示使用 Bank／全局 配置默认值（recall_chunks_max_tokens）。                                                                                                                                                                                                                           |

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

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段                  | 类型                           | 必填 | 说明                                                                                                                                                  |
| --------------------- | ------------------------------ | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                | `string`                     | 是   | 资源的唯一标识符。                                                                                                                                    |
| `bank_id`           | `string`                     | 是   | 所属 Bank 的唯一标识符。                                                                                                                              |
| `name`              | `string`                     | 是   | 名称。                                                                                                                                                |
| `source_query`      | `string?`                    | 否   | 生成或刷新内容所使用的源查询。                                                                                                                        |
| `content`           | `string?`                    | 否   | Mental model 内容，采用格式规范的 Markdown，由 Reflect 接口自动生成。                                                                                 |
| `tags`              | `array<string>`              | 否   | 默认值：`[]`                                                                                                                                        |
| `max_tokens`        | `integer?`                   | 否   | 最大 token 数。                                                                                                                                       |
| `trigger`           | `MentalModelTrigger-Output?` | 否   | 触发方式或触发配置。                                                                                                                                  |
| `last_refreshed_at` | `string?`                    | 否   | 最近刷新时间。                                                                                                                                        |
| `created_at`        | `string?`                    | 否   | 创建时间。                                                                                                                                            |
| `reflect_response`  | `object?`                    | 否   | 完整的 Reflect API 响应 payload，包括 based_on facts 和 observations。                                                                                |
| `is_stale`          | `boolean?`                   | 否   | 自 last_refreshed_at 后写入了符合此 mental model tag/fact_type scope 的新 memories，或 consolidation 仍有待处理项时为 true。仅在 detail=full 时填充。 |

<details open><summary><strong>trigger</strong> · <code>MentalModelTrigger-Output</code></summary>

数据结构 `MentalModelTrigger-Output`：

| 字段                            | 类型                                                                                   | 必填 | 说明                                                                                                                                                                                                                                                                                                                                                  |
| ------------------------------- | -------------------------------------------------------------------------------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mode`                        | `"full" \| "delta"`                                                                   | 否   | 刷新模式。full（默认）每次刷新都从头生成 mental model 内容；delta 在现有内容上进行局部编辑，逐字节保留未变化的章节，移除过时内容并加入新内容。如果 mental model 尚无内容，或 source_query 自上次刷新后发生变化，delta 会自动回退为完整生成；默认值：`"full"`                                                                                        |
| `response_schema`             | `object?`                                                                            | 否   | 用于结构化输出的可选 JSON Schema。设置后，每次刷新都会执行与 Reflect`response_schema` 相同的结构化抽取，并将解析结果存入 `reflect_response.structured_output`，同时保留 Markdown 内容。                                                                                                                                                           |
| `keep_trace`                  | `boolean`                                                                            | 否   | 为 true 时，记录 mental model 每次刷新的执行 trace，便于诊断定时或 consolidation 触发的刷新。仅保留最近一次 trace；工具输出会缩减为结果数量，以限制存储规模；默认值：`false`                                                                                                                                                                        |
| `refresh_after_consolidation` | `boolean`                                                                            | 否   | 为 true 时，在 observations consolidation 后刷新此 mental model（实时模式）；默认值：`false`                                                                                                                                                                                                                                                        |
| `refresh_cron`                | `string?`                                                                            | 否   | 用于按固定计划刷新此 mental model 的 cron 表达式（UTC，标准 5 字段语法，例如`0 3 * * *` 表示每天 UTC 03:00）。与 refresh_after_consolidation 互斥：model 只能在 consolidation 后刷新或按 cron 刷新，不能同时启用。计划刷新仅在 model 已过期时执行（自上次刷新后 scope 内出现新 memories）；没有变化时跳过，避免浪费 LLM 调用。null 表示不设置计划。 |
| `fact_types`                  | `array<"world" \| "experience" \| "observation">?`                                     | 否   | 筛选 Reflect 时检索的 fact type。null 表示全部类型（world、experience、observation）。                                                                                                                                                                                                                                                                |
| `exclude_mental_models`       | `boolean`                                                                            | 否   | 为 true 时，从 Reflect 循环中排除所有 mental models（跳过 search_mental_models 工具）；默认值：`false`                                                                                                                                                                                                                                              |
| `exclude_mental_model_ids`    | `array<string>?`                                                                     | 否   | 按 ID 从 Reflect 循环中排除指定 mental models。                                                                                                                                                                                                                                                                                                       |
| `tags_match`                  | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"?`                             | 否   | 覆盖 refresh 时 model tags 筛选 memories 的方式。未设置时，有 tags 的 model 默认为 all_strict（用于安全隔离），无 tags 的 model 默认为 any。设置为 any 可在 refresh 时同时包含无标签和有标签 memories。                                                                                                                                               |
| `tag_groups`                  | `array<TagGroupLeaf \| TagGroupAnd-Output \| TagGroupOr-Output \| TagGroupNot-Output>?` | 否   | Refresh 时使用的复合布尔 tag 表达式，用于替代 model 自身的 tags。设置后，这些 tag groups 会传给 Reflect，model 的扁平 tags 不再用于筛选。支持嵌套 and/or/not 表达式，以实现复杂的 tag scope。                                                                                                                                                         |
| `include_chunks`              | `boolean?`                                                                           | 否   | 覆盖 refresh 内部 Recall 是否返回原始 chunk 文本。null 表示使用 Bank／全局 配置默认值（recall_include_chunks）。                                                                                                                                                                                                                                      |
| `recall_max_tokens`           | `integer?`                                                                           | 否   | 覆盖 refresh 内部 Recall 返回 facts 的 token budget。null 表示使用 Bank／全局 配置默认值（recall_max_tokens）。                                                                                                                                                                                                                                       |
| `recall_chunks_max_tokens`    | `integer?`                                                                           | 否   | 覆盖 refresh 内部 Recall 返回原始 chunks 的 token budget。null 表示使用 Bank／全局 配置默认值（recall_chunks_max_tokens）。                                                                                                                                                                                                                           |

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
    "recall_chunks_max_tokens": 0
  },
  "last_refreshed_at": "string",
  "created_at": "string",
  "reflect_response": {},
  "is_stale": false
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

删除 mental model。

#### 参数

| 名称                | In   | 类型       | 必填 | 说明                |
| ------------------- | ---- | ---------- | ---- | ------------------- |
| `bank_id`         | path | `string` | 是   | Bank 的唯一标识符。 |
| `mental_model_id` | path | `string` | 是   | Mental 数据结构 Id  |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

_无展开字段（标量、自由 object 或未声明 properties）_

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

清空 mental model 内容，使下一次 refresh 执行完整重新合成。适用于经过多次增量 refresh 后产生偏移的 delta-mode models。清空后调用 /refresh 接口触发干净的完整重建。

#### 参数

| 名称                | In   | 类型       | 必填 | 说明                |
| ------------------- | ---- | ---------- | ---- | ------------------- |
| `bank_id`         | path | `string` | 是   | Bank 的唯一标识符。 |
| `mental_model_id` | path | `string` | 是   | Mental 数据结构 Id  |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段                  | 类型                           | 必填 | 说明                                                                                                                                                  |
| --------------------- | ------------------------------ | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                | `string`                     | 是   | 资源的唯一标识符。                                                                                                                                    |
| `bank_id`           | `string`                     | 是   | 所属 Bank 的唯一标识符。                                                                                                                              |
| `name`              | `string`                     | 是   | 名称。                                                                                                                                                |
| `source_query`      | `string?`                    | 否   | 生成或刷新内容所使用的源查询。                                                                                                                        |
| `content`           | `string?`                    | 否   | Mental model 内容，采用格式规范的 Markdown，由 Reflect 接口自动生成。                                                                                 |
| `tags`              | `array<string>`              | 否   | 默认值：`[]`                                                                                                                                        |
| `max_tokens`        | `integer?`                   | 否   | 最大 token 数。                                                                                                                                       |
| `trigger`           | `MentalModelTrigger-Output?` | 否   | 触发方式或触发配置。                                                                                                                                  |
| `last_refreshed_at` | `string?`                    | 否   | 最近刷新时间。                                                                                                                                        |
| `created_at`        | `string?`                    | 否   | 创建时间。                                                                                                                                            |
| `reflect_response`  | `object?`                    | 否   | 完整的 Reflect API 响应 payload，包括 based_on facts 和 observations。                                                                                |
| `is_stale`          | `boolean?`                   | 否   | 自 last_refreshed_at 后写入了符合此 mental model tag/fact_type scope 的新 memories，或 consolidation 仍有待处理项时为 true。仅在 detail=full 时填充。 |

<details open><summary><strong>trigger</strong> · <code>MentalModelTrigger-Output</code></summary>

数据结构 `MentalModelTrigger-Output`：

| 字段                            | 类型                                                                                   | 必填 | 说明                                                                                                                                                                                                                                                                                                                                                  |
| ------------------------------- | -------------------------------------------------------------------------------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mode`                        | `"full" \| "delta"`                                                                   | 否   | 刷新模式。full（默认）每次刷新都从头生成 mental model 内容；delta 在现有内容上进行局部编辑，逐字节保留未变化的章节，移除过时内容并加入新内容。如果 mental model 尚无内容，或 source_query 自上次刷新后发生变化，delta 会自动回退为完整生成；默认值：`"full"`                                                                                        |
| `response_schema`             | `object?`                                                                            | 否   | 用于结构化输出的可选 JSON Schema。设置后，每次刷新都会执行与 Reflect`response_schema` 相同的结构化抽取，并将解析结果存入 `reflect_response.structured_output`，同时保留 Markdown 内容。                                                                                                                                                           |
| `keep_trace`                  | `boolean`                                                                            | 否   | 为 true 时，记录 mental model 每次刷新的执行 trace，便于诊断定时或 consolidation 触发的刷新。仅保留最近一次 trace；工具输出会缩减为结果数量，以限制存储规模；默认值：`false`                                                                                                                                                                        |
| `refresh_after_consolidation` | `boolean`                                                                            | 否   | 为 true 时，在 observations consolidation 后刷新此 mental model（实时模式）；默认值：`false`                                                                                                                                                                                                                                                        |
| `refresh_cron`                | `string?`                                                                            | 否   | 用于按固定计划刷新此 mental model 的 cron 表达式（UTC，标准 5 字段语法，例如`0 3 * * *` 表示每天 UTC 03:00）。与 refresh_after_consolidation 互斥：model 只能在 consolidation 后刷新或按 cron 刷新，不能同时启用。计划刷新仅在 model 已过期时执行（自上次刷新后 scope 内出现新 memories）；没有变化时跳过，避免浪费 LLM 调用。null 表示不设置计划。 |
| `fact_types`                  | `array<"world" \| "experience" \| "observation">?`                                     | 否   | 筛选 Reflect 时检索的 fact type。null 表示全部类型（world、experience、observation）。                                                                                                                                                                                                                                                                |
| `exclude_mental_models`       | `boolean`                                                                            | 否   | 为 true 时，从 Reflect 循环中排除所有 mental models（跳过 search_mental_models 工具）；默认值：`false`                                                                                                                                                                                                                                              |
| `exclude_mental_model_ids`    | `array<string>?`                                                                     | 否   | 按 ID 从 Reflect 循环中排除指定 mental models。                                                                                                                                                                                                                                                                                                       |
| `tags_match`                  | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"?`                             | 否   | 覆盖 refresh 时 model tags 筛选 memories 的方式。未设置时，有 tags 的 model 默认为 all_strict（用于安全隔离），无 tags 的 model 默认为 any。设置为 any 可在 refresh 时同时包含无标签和有标签 memories。                                                                                                                                               |
| `tag_groups`                  | `array<TagGroupLeaf \| TagGroupAnd-Output \| TagGroupOr-Output \| TagGroupNot-Output>?` | 否   | Refresh 时使用的复合布尔 tag 表达式，用于替代 model 自身的 tags。设置后，这些 tag groups 会传给 Reflect，model 的扁平 tags 不再用于筛选。支持嵌套 and/or/not 表达式，以实现复杂的 tag scope。                                                                                                                                                         |
| `include_chunks`              | `boolean?`                                                                           | 否   | 覆盖 refresh 内部 Recall 是否返回原始 chunk 文本。null 表示使用 Bank／全局 配置默认值（recall_include_chunks）。                                                                                                                                                                                                                                      |
| `recall_max_tokens`           | `integer?`                                                                           | 否   | 覆盖 refresh 内部 Recall 返回 facts 的 token budget。null 表示使用 Bank／全局 配置默认值（recall_max_tokens）。                                                                                                                                                                                                                                       |
| `recall_chunks_max_tokens`    | `integer?`                                                                           | 否   | 覆盖 refresh 内部 Recall 返回原始 chunks 的 token budget。null 表示使用 Bank／全局 配置默认值（recall_chunks_max_tokens）。                                                                                                                                                                                                                           |

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
    "recall_chunks_max_tokens": 0
  },
  "last_refreshed_at": "string",
  "created_at": "string",
  "reflect_response": {},
  "is_stale": false
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 心智模型历史

<a id="get-mental-model-history"></a>

**GET** `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/history`

获取 mental model 的刷新历史，展示内容随时间的变化。

#### 参数

| 名称                | In   | 类型       | 必填 | 说明                |
| ------------------- | ---- | ---------- | ---- | ------------------- |
| `bank_id`         | path | `string` | 是   | Bank 的唯一标识符。 |
| `mental_model_id` | path | `string` | 是   | Mental 数据结构 Id  |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

_无展开字段（标量、自由 object 或未声明 properties）_

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

提交异步任务，重新通过 Reflect 运行 source query 并更新内容。

#### 参数

| 名称                | In   | 类型       | 必填 | 说明                |
| ------------------- | ---- | ---------- | ---- | ------------------- |
| `bank_id`         | path | `string` | 是   | Bank 的唯一标识符。 |
| `mental_model_id` | path | `string` | 是   | Mental 数据结构 Id  |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段             | 类型       | 必填 | 说明                                                                               |
| ---------------- | ---------- | ---- | ---------------------------------------------------------------------------------- |
| `operation_id` | `string` | 是   | 异步操作 的唯一标识符，可用于查询状态。                                            |
| `status`       | `string` | 是   | 当前处理状态；异步操作通常为 pending、processing、completed、failed 或 cancelled。 |

#### 响应示例

```json
{
  "operation_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 预览心智模型刷新

<a id="dry-run-refresh-mental-model"></a>

**POST** `/v1/default/banks/{bank_id}/mental-models/{mental_model_id}/dry-run-refresh`

预览心智模型刷新结果，但不持久化任何更改。接口会执行完整的检索与生成流程，并返回拟生成的内容、结构化输出、事实使用情况和执行 trace，适合在修改配置或 prompt 后验证效果。

#### 参数

| 名称                | In   | 类型       | 必填 | 说明                           |
| ------------------- | ---- | ---------- | ---- | ------------------------------ |
| `bank_id`         | path | `string` | 是   | Bank 的唯一标识符。            |
| `mental_model_id` | path | `string` | 是   | 要预览刷新的 mental model ID。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段                     | 类型                                                                                                                             | 必填 | 说明                                                                                                                                      |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `mental_model_id`      | `string`                                                                                                                       | 是   | 预览的 mental model ID。                                                                                                                  |
| `name`                 | `string`                                                                                                                       | 是   | mental model 的显示名称。                                                                                                                 |
| `requested_mode`       | `"full" \| "delta"`                                                                                                             | 是   | 请求的刷新模式（来自 model trigger，也可以覆盖）。                                                                                        |
| `effective_mode`       | `"full" \| "delta"`                                                                                                             | 是   | 刷新实际执行的模式。                                                                                                                      |
| `mode_fallback_reason` | `"no_baseline_content" \| "source_query_changed" \| "structured_doc_unreadable" \| "delta_ops_failed" \| "delta_ops_all_skipped"?` | 否   | 请求 delta 但未能应用时的原因。                                                                                                           |
| `outcome`              | `"content_written" \| "content_preserved_no_new_facts" \| "refresh_failed_empty_candidate" \| "refresh_failed_delta_not_applied"` | 是   | 实际刷新将如何处理该 document。                                                                                                           |
| `would_persist`        | `boolean`                                                                                                                      | 是   | 实际刷新是否会写入新内容。                                                                                                                |
| `scope`                | `MentalModelRefreshScope`                                                                                                      | 是   | 解析后的 memory scope。                                                                                                                   |
| `window`               | `MentalModelRefreshWindow`                                                                                                     | 是   | 读取数据时使用的快照窗口。                                                                                                                |
| `facts`                | `MentalModelFactCounts`                                                                                                        | 是   | 检索到和实际使用的 facts 数量。                                                                                                           |
| `based_on`             | `map<string, array<object>>`                                                                                                   | 否   | 本次生成所依据的证据，按 fact type 分组；其结构与实际刷新持久化到`reflect_response.based_on` 的内容相同，因此预览无需写入即可展示来源。 |
| `current_content`      | `string`                                                                                                                       | 是   | model 当前的内容。                                                                                                                        |
| `candidate_content`    | `string`                                                                                                                       | 是   | 执行任何 delta 操作之前的原始 Reflect 合成内容。                                                                                          |
| `preview_content`      | `string`                                                                                                                       | 是   | 实际刷新将保存的内容：delta 模式下为编辑后的 document，full 模式下为候选内容。                                                            |
| `diff`                 | `string`                                                                                                                       | 是   | 从`current_content` 到 `preview_content` 的 unified diff；内容相同时为空。                                                            |
| `delta_operations`     | `MentalModelDeltaOperations?`                                                                                                  | 否   | delta 模式下生成的结构化操作。                                                                                                            |
| `trace`                | `MentalModelRefreshTrace`                                                                                                      | 是   | 此次运行的执行 trace；dry-run 始终包含。                                                                                                  |
| `usage`                | `TokenUsage`                                                                                                                   | 否   | 此次运行所有 LLM 调用的 token 用量。                                                                                                      |
| `duration_ms`          | `integer`                                                                                                                      | 否   | 此次运行的实际耗时；默认值：`0`                                                                                                         |
| `warnings`             | `array<string>`                                                                                                                | 否   | 需要人工关注的情况，以自然语言说明。                                                                                                      |

<details open><summary><strong>scope</strong> · <code>MentalModelRefreshScope</code></summary>

数据结构 `MentalModelRefreshScope`：

| 字段                         | 类型                                                                                   | 必填 | 说明                                                   |
| ---------------------------- | -------------------------------------------------------------------------------------- | ---- | ------------------------------------------------------ |
| `tags`                     | `array<string>?`                                                                     | 否   | 用于筛选 memories 的扁平 tags；未使用时为 null。       |
| `tags_match`               | `"any" \| "all" \| "any_strict" \| "all_strict" \| "exact"`                              | 是   | 解析后的 tag 匹配模式。                                |
| `tag_groups`               | `array<TagGroupLeaf \| TagGroupAnd-Output \| TagGroupOr-Output \| TagGroupNot-Output>?` | 否   | 设置后用于取代扁平 tags 的复合 tag 表达式。            |
| `fact_types`               | `array<string>?`                                                                     | 否   | 检索的 fact type；null 表示全部类型。                  |
| `exclude_mental_models`    | `boolean`                                                                            | 是   | 是否从 Reflect 循环中排除其他 mental models。          |
| `exclude_mental_model_ids` | `array<string>`                                                                      | 否   | 按 ID 排除的 mental models，始终包含当前刷新的 model。 |

</details>

<details open><summary><strong>window</strong> · <code>MentalModelRefreshWindow</code></summary>

数据结构 `MentalModelRefreshWindow`：

| 字段               | 类型                   | 必填 | 说明                                                                                                                                              |
| ------------------ | ---------------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `created_after`  | `string(date-time)?` | 否   | memory 创建时间的下界。仅在 delta 模式下设置，其值为 model 的`last_refreshed_at`，因此 delta 刷新只会读取比上次刷新更新的 memories。            |
| `created_before` | `string(date-time)`  | 是   | 限定此次刷新的数据库时间快照。此时间之后提交的 memories 不会被读取，因此仍会晚于持久化的 watermark，并由下一次刷新处理。                          |
| `watermark`      | `string(date-time)?` | 否   | 实际刷新将持久化的`last_refreshed_at`：取快照中可见且在 scope 内的最新 memory 时间，而不是 `now()`。null 表示没有可见且在 scope 内的 memory。 |

</details>

<details open><summary><strong>facts</strong> · <code>MentalModelFactCounts</code></summary>

数据结构 `MentalModelFactCounts`：

| 字段          | 类型                     | 必填 | 说明                                                        |
| ------------- | ------------------------ | ---- | ----------------------------------------------------------- |
| `retrieved` | `map<string, integer>` | 否   | Reflect Agent 的工具调用所返回的 facts，按 fact type 统计。 |
| `used`      | `map<string, integer>` | 否   | Agent 声明实际用于生成内容的 facts，按 fact type 统计。     |

</details>

<details open><summary><strong>delta_operations</strong> · <code>MentalModelDeltaOperations</code></summary>

数据结构 `MentalModelDeltaOperations`：

| 字段        | 类型              | 必填 | 说明                                 |
| ----------- | ----------------- | ---- | ------------------------------------ |
| `applied` | `array<object>` | 否   | 按顺序应用到 document 的操作。       |
| `skipped` | `array<object>` | 否   | 因无效而被丢弃的操作，每条均附原因。 |

</details>

<details open><summary><strong>trace</strong> · <code>MentalModelRefreshTrace</code></summary>

数据结构 `MentalModelRefreshTrace`：

| 字段                     | 类型                                                                                                                             | 必填 | 说明                                 |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------- | ---- | ------------------------------------ |
| `recorded_at`          | `string(date-time)?`                                                                                                           | 否   | 记录此 trace 的时间。                |
| `effective_mode`       | `"full" \| "delta"`                                                                                                             | 是   | 刷新实际采用 full 还是 delta 模式。  |
| `mode_fallback_reason` | `"no_baseline_content" \| "source_query_changed" \| "structured_doc_unreadable" \| "delta_ops_failed" \| "delta_ops_all_skipped"?` | 否   | 请求 delta 但未能应用时的原因。      |
| `outcome`              | `"content_written" \| "content_preserved_no_new_facts" \| "refresh_failed_empty_candidate" \| "refresh_failed_delta_not_applied"` | 是   | 此次刷新对 document 执行的处理。     |
| `tool_calls`           | `array<MentalModelTraceToolCall>`                                                                                              | 否   | 刷新期间执行的 Reflect 工具调用。    |
| `llm_calls`            | `array<LLMCallTrace>`                                                                                                          | 否   | 刷新期间执行的 LLM 调用。            |
| `delta_operations`     | `MentalModelDeltaOperations?`                                                                                                  | 否   | delta 模式下生成的结构化操作。       |
| `usage`                | `TokenUsage?`                                                                                                                  | 否   | 此次刷新所有 LLM 调用的 token 用量。 |
| `duration_ms`          | `integer`                                                                                                                      | 否   | 刷新实际耗时；默认值：`0`          |
| `warnings`             | `array<string>`                                                                                                                | 否   | 需要人工关注的情况，以自然语言说明。 |

<details open><summary><strong>tool_calls[]</strong> · <code>MentalModelTraceToolCall</code></summary>

数据结构 `MentalModelTraceToolCall`：

| 字段             | 类型                   | 必填 | 说明                                                                                                                                                                                                                                      |
| ---------------- | ---------------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tool`         | `string`             | 是   | 工具名称，例如 recall、search_observations、get_mental_model 或 expand。                                                                                                                                                                  |
| `reason`       | `string?`            | 否   | Agent 给出的调用原因。                                                                                                                                                                                                                    |
| `input`        | `object`             | 否   | 工具输入参数。                                                                                                                                                                                                                            |
| `output`       | `object?`            | 否   | 工具返回的结果。dry-run 不存储数据，因此会返回此字段；实际刷新持久化 trace 时会省略，以限制记录大小。                                                                                                                                     |
| `updated_at`   | `string(date-time)?` | 否   | 传给此次调用的刷新窗口下界，即 delta watermark。该筛选实际作用于 memory 的`updated_at`，因此自上次刷新后只要被更新过的 memory 都符合条件。null 表示不施加时间边界，结果不受刷新窗口限制（mental model 查询和 chunk 展开即采用此行为）。 |
| `result_count` | `integer?`           | 否   | 工具返回的条目数量（可统计时）。                                                                                                                                                                                                          |
| `duration_ms`  | `integer`            | 是   | 执行耗时，单位为毫秒。                                                                                                                                                                                                                    |
| `iteration`    | `integer`            | 否   | 此次调用所属的 Agent 循环轮次（从 1 开始）；默认值：`0`                                                                                                                                                                                 |

</details>

<details open><summary><strong>llm_calls[]</strong> · <code>LLMCallTrace</code></summary>

数据结构 `LLMCallTrace`：

| 字段            | 类型        | 必填 | 说明                                       |
| --------------- | ----------- | ---- | ------------------------------------------ |
| `scope`       | `string`  | 是   | 调用范围，例如 agent_1、agent_2 或 final。 |
| `duration_ms` | `integer` | 是   | 执行耗时，单位为毫秒                       |

</details>

<details open><summary><strong>delta_operations</strong> · <code>MentalModelDeltaOperations</code></summary>

数据结构 `MentalModelDeltaOperations`：

| 字段        | 类型              | 必填 | 说明                                 |
| ----------- | ----------------- | ---- | ------------------------------------ |
| `applied` | `array<object>` | 否   | 按顺序应用到 document 的操作。       |
| `skipped` | `array<object>` | 否   | 因无效而被丢弃的操作，每条均附原因。 |

</details>

<details open><summary><strong>usage</strong> · <code>TokenUsage</code></summary>

数据结构 `TokenUsage`：

| 字段                | 类型        | 必填 | 说明                                                                                                                       |
| ------------------- | ----------- | ---- | -------------------------------------------------------------------------------------------------------------------------- |
| `input_tokens`    | `integer` | 否   | 消耗的输入／prompt token 数量；默认值：`0`                                                                               |
| `output_tokens`   | `integer` | 否   | 生成的可见输出／completion token 数量（不含推理／思考 token）；默认值：`0`                                               |
| `total_tokens`    | `integer` | 否   | token 总数（输入加输出，不含推理 token）；默认值：`0`                                                                    |
| `cached_tokens`   | `integer` | 否   | provider 报告的缓存命中／缓存读取 prompt token 数量；默认值：`0`                                                         |
| `thoughts_tokens` | `integer` | 否   | 模型生成的推理／思考 token 数量。部分 provider（如 Gemini 2.5+ 系列）按输出费率计费，但不会显示在可见响应中；默认值：`0` |

</details>

</details>

<details open><summary><strong>usage</strong> · <code>TokenUsage</code></summary>

数据结构 `TokenUsage`：

| 字段                | 类型        | 必填 | 说明                                                                                                                       |
| ------------------- | ----------- | ---- | -------------------------------------------------------------------------------------------------------------------------- |
| `input_tokens`    | `integer` | 否   | 消耗的输入／prompt token 数量；默认值：`0`                                                                               |
| `output_tokens`   | `integer` | 否   | 生成的可见输出／completion token 数量（不含推理／思考 token）；默认值：`0`                                               |
| `total_tokens`    | `integer` | 否   | token 总数（输入加输出，不含推理 token）；默认值：`0`                                                                    |
| `cached_tokens`   | `integer` | 否   | provider 报告的缓存命中／缓存读取 prompt token 数量；默认值：`0`                                                         |
| `thoughts_tokens` | `integer` | 否   | 模型生成的推理／思考 token 数量。部分 provider（如 Gemini 2.5+ 系列）按输出费率计费，但不会显示在可见响应中；默认值：`0` |

</details>

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明           |
| ---------- | -------------------------- | ---- | -------------- |
| `detail` | `array<ValidationError>` | 否   | 校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

| 字段      | 类型                        | 必填 | 说明                     |
| --------- | --------------------------- | ---- | ------------------------ |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径。 |
| `msg`   | `string`                  | 是   | 错误消息。               |
| `type`  | `string`                  | 是   | 错误类型。               |
| `input` | `any`                     | 否   | 触发校验的原始输入值。   |
| `ctx`   | `Context`                 | 否   | 错误上下文。             |

</details>

`operationId=dry_run_refresh_mental_model`

---

## Documents

<a id="documents"></a>

**文档** · 7 个接口

文档粒度的查看、更新、删除与追踪。

### 本章目录

| Method     | Path                                                              | 标题                                        |
| ---------- | ----------------------------------------------------------------- | ------------------------------------------- |
| `GET`    | `/v1/default/banks/{bank_id}/documents`                         | [列出 document](#list-documents)             |
| `GET`    | `/v1/default/banks/{bank_id}/documents/{document_id}`           | [获取 document 详情](#get-document)          |
| `PATCH`  | `/v1/default/banks/{bank_id}/documents/{document_id}`           | [更新 document](#update-document)            |
| `DELETE` | `/v1/default/banks/{bank_id}/documents/{document_id}`           | [删除 document](#delete-document)            |
| `GET`    | `/v1/default/banks/{bank_id}/documents/{document_id}/chunks`    | [列出 document chunk](#list-document-chunks) |
| `POST`   | `/v1/default/banks/{bank_id}/documents/{document_id}/reprocess` | [重新处理 document](#reprocess-document)     |
| `GET`    | `/v1/default/chunks/{chunk_id}`                                 | [获取 chunk 详情](#get-chunk)                |

### 列出 document

<a id="list-documents"></a>

**GET** `/v1/default/banks/{bank_id}/documents`

分页列出 document，并支持可选搜索。document 是抽取 memory unit 的来源内容。

#### 参数

| 名称           | In    | 类型               | 必填 | 说明                                                                               |
| -------------- | ----- | ------------------ | ---- | ---------------------------------------------------------------------------------- |
| `bank_id`    | path  | `string`         | 是   | Bank 的唯一标识符。                                                                |
| `q`          | query | `string?`        | 否   | 对 document ID 进行不区分大小写的子字符串筛选（例如 report 匹配 report-2024）。    |
| `tags`       | query | `array<string>?` | 否   | 按 tags 筛选 documents。                                                           |
| `tags_match` | query | `string`         | 否   | tag 的匹配方式: 'any', 'all', 'any_strict', 'all_strict'；默认值：`"any_strict"` |
| `limit`      | query | `integer`        | 否   | 默认值：`100`；最小值：`0`                                                     |
| `offset`     | query | `integer`        | 否   | 默认值：`0`；最小值：`0`                                                       |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段       | 类型              | 必填 | 说明           |
| ---------- | ----------------- | ---- | -------------- |
| `items`  | `array<object>` | 是   | 结果项目列表。 |
| `total`  | `integer`       | 是   | 总数量。       |
| `limit`  | `integer`       | 是   | 返回数量上限。 |
| `offset` | `integer`       | 是   | 分页偏移量。   |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 获取 document 详情

<a id="get-document"></a>

**GET** `/v1/default/banks/{bank_id}/documents/{document_id}`

获取指定 document，包括Document 的原始文本；未启用文本存储时可能为 null。

#### 参数

| 名称            | In   | 类型       | 必填 | 说明                 |
| --------------- | ---- | ---------- | ---- | -------------------- |
| `bank_id`     | path | `string` | 是   | Bank 的唯一标识符。  |
| `document_id` | path | `string` | 是   | Document 的唯一 ID。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段                   | 类型                                     | 必填 | 说明                                                                                                                                                                                                                   |
| ---------------------- | ---------------------------------------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                 | `string`                               | 是   | 资源的唯一标识符。                                                                                                                                                                                                     |
| `bank_id`            | `string`                               | 是   | 所属 Bank 的唯一标识符。                                                                                                                                                                                               |
| `original_text`      | `string?`                              | 否   | Document 的原始文本；未启用文本存储时可能为 null。                                                                                                                                                                     |
| `content_hash`       | `string?`                              | 否   | 内容哈希值。                                                                                                                                                                                                           |
| `created_at`         | `string`                               | 是   | 资源创建时间（ISO 8601）。                                                                                                                                                                                             |
| `updated_at`         | `string`                               | 是   | 资源最后更新时间（ISO 8601）。                                                                                                                                                                                         |
| `memory_unit_count`  | `integer`                              | 是   | memory unit 数量。                                                                                                                                                                                                     |
| `nodes_by_fact_type` | `map<string, integer>?`                | 否   | 按 fact type（world、experience、observation）统计的 memory 数量。                                                                                                                                                     |
| `tags`               | `array<string>`                        | 否   | 与此 document 关联的标签；默认值：`[]`                                                                                                                                                                               |
| `document_metadata`  | `object?`                              | 否   | Document 的附加 metadata。                                                                                                                                                                                             |
| `retain_params`      | `object?`                              | 否   | Retain 时使用的参数。                                                                                                                                                                                                  |
| `observation_scopes` | `string \| array<array<string>> \| null` | 否   | Retain 时配置并记录到 retain_params 的 observation_scopes 规范（例如 all_combinations、per_tag 或显式 tag-set 列表）。未设置时为 null（默认使用 combined scope），在该字段开始记录之前 Retain 的 documents 也为 null。 |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 更新 document

<a id="update-document"></a>

**PATCH** `/v1/default/banks/{bank_id}/documents/{document_id}`

更新 document 的可变字段，不重新处理其内容。

**标签（`tags`）：** 新标签会传播到所有关联的 memory unit。由这些 memory unit 派生的 observations 将失效，并使用新标签排队重新 consolidation。其他 document 中与其共享这些 observations 的同源 memories 也会被重置。

至少必须提供一个字段。

#### 参数

| 名称            | In   | 类型       | 必填 | 说明                 |
| --------------- | ---- | ---------- | ---- | -------------------- |
| `bank_id`     | path | `string` | 是   | Bank 的唯一标识符。  |
| `document_id` | path | `string` | 是   | Document 的唯一 ID。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段     | 类型               | 必填 | 说明                                                                                             |
| -------- | ------------------ | ---- | ------------------------------------------------------------------------------------------------ |
| `tags` | `array<string>?` | 否   | Document 及其 memory units 的新 tags。修改后会使现有 observations 失效并触发重新 consolidation。 |

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

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段        | 类型        | 必填 | 说明             |
| ----------- | ----------- | ---- | ---------------- |
| `success` | `boolean` | 否   | 默认值：`true` |

#### 响应示例

```json
{
  "success": true
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 删除 document

<a id="delete-document"></a>

**DELETE** `/v1/default/banks/{bank_id}/documents/{document_id}`

删除 document 及其关联的全部 memory unit 和链接。

此操作将级联删除：

- document 本身
- 从该 document 抽取的全部 memory unit
- 与这些 memory unit 关联的全部链接（时序、语义和实体链接）

此操作无法撤销。

#### 参数

| 名称            | In   | 类型       | 必填 | 说明                 |
| --------------- | ---- | ---------- | ---- | -------------------- |
| `bank_id`     | path | `string` | 是   | Bank 的唯一标识符。  |
| `document_id` | path | `string` | 是   | Document 的唯一 ID。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段                     | 类型        | 必填 | 说明                        |
| ------------------------ | ----------- | ---- | --------------------------- |
| `success`              | `boolean` | 是   | 操作是否成功。              |
| `message`              | `string`  | 是   | 操作结果或错误的可读消息。  |
| `document_id`          | `string`  | 是   | Document 的唯一标识符。     |
| `memory_units_deleted` | `integer` | 是   | 已删除的 memory unit 数量。 |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 列出 document chunk

<a id="list-document-chunks"></a>

**GET** `/v1/default/banks/{bank_id}/documents/{document_id}/chunks`

列出指定 document 的所有 chunks，按 chunk index 排序。

#### 参数

| 名称            | In    | 类型        | 必填 | 说明                                                              |
| --------------- | ----- | ----------- | ---- | ----------------------------------------------------------------- |
| `bank_id`     | path  | `string`  | 是   | Bank 的唯一标识符。                                               |
| `document_id` | path  | `string`  | 是   | Document 的唯一 ID。                                              |
| `limit`       | query | `integer` | 否   | 返回 chunk 的最大数量；默认值：`100`；取值范围：`1`–`1000` |
| `offset`      | query | `integer` | 否   | 分页偏移量；默认值：`0`；最小值：`0`                          |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段       | 类型                     | 必填 | 说明           |
| ---------- | ------------------------ | ---- | -------------- |
| `items`  | `array<ChunkResponse>` | 是   | 结果项目列表。 |
| `total`  | `integer`              | 是   | 总数量。       |
| `limit`  | `integer`              | 是   | 返回数量上限。 |
| `offset` | `integer`              | 是   | 分页偏移量。   |

<details open><summary><strong>items[]</strong> · <code>ChunkResponse</code></summary>

数据结构 `ChunkResponse`：

| 字段            | 类型        | 必填 | 说明                         |
| --------------- | ----------- | ---- | ---------------------------- |
| `chunk_id`    | `string`  | 是   | Chunk 的唯一标识符。         |
| `document_id` | `string`  | 是   | Document 的唯一标识符。      |
| `bank_id`     | `string`  | 是   | 所属 Bank 的唯一标识符。     |
| `chunk_index` | `integer` | 是   | Chunk 在 document 中的索引。 |
| `chunk_text`  | `string`  | 是   | Chunk 文本。                 |
| `created_at`  | `string`  | 是   | 资源创建时间（ISO 8601）。   |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 重新处理 document

<a id="reprocess-document"></a>

**POST** `/v1/default/banks/{bank_id}/documents/{document_id}/reprocess`

在不改变 document 内容的情况下重新运行 retain pipeline。此操作会删除现有 memory units，并使用当前 engine 配置重新抽取 facts。适用于 LLM model、分块策略或抽取设置发生变化的情况。

#### 参数

| 名称            | In   | 类型       | 必填 | 说明                 |
| --------------- | ---- | ---------- | ---- | -------------------- |
| `bank_id`     | path | `string` | 是   | Bank 的唯一标识符。  |
| `document_id` | path | `string` | 是   | Document 的唯一 ID。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段             | 类型        | 必填 | 说明                                    |
| ---------------- | ----------- | ---- | --------------------------------------- |
| `success`      | `boolean` | 是   | 操作是否成功。                          |
| `operation_id` | `string`  | 是   | 异步操作 的唯一标识符，可用于查询状态。 |
| `items_count`  | `integer` | 是   | 项目数量。                              |

#### 响应示例

```json
{
  "success": false,
  "operation_id": "string",
  "items_count": 0
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 获取 chunk 详情

<a id="get-chunk"></a>

**GET** `/v1/default/chunks/{chunk_id}`

按 ID 获取指定 chunk。

#### 参数

| 名称         | In   | 类型       | 必填 | 说明              |
| ------------ | ---- | ---------- | ---- | ----------------- |
| `chunk_id` | path | `string` | 是   | Chunk 的唯一 ID。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段            | 类型        | 必填 | 说明                         |
| --------------- | ----------- | ---- | ---------------------------- |
| `chunk_id`    | `string`  | 是   | Chunk 的唯一标识符。         |
| `document_id` | `string`  | 是   | Document 的唯一标识符。      |
| `bank_id`     | `string`  | 是   | 所属 Bank 的唯一标识符。     |
| `chunk_index` | `integer` | 是   | Chunk 在 document 中的索引。 |
| `chunk_text`  | `string`  | 是   | Chunk 文本。                 |
| `created_at`  | `string`  | 是   | 资源创建时间（ISO 8601）。   |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

**文档迁移** · 3 个接口

文档的异步导出、下载、导入与迁移。

### 本章目录

| Method   | Path                                                     | 标题                                      |
| -------- | -------------------------------------------------------- | ----------------------------------------- |
| `POST` | `/v1/default/banks/{bank_id}/document-transfer/export` | [异步导出 document](#export-documents)     |
| `GET`  | `/v1/default/files/download/{key}`                     | [下载导出文件](#download-file)             |
| `POST` | `/v1/default/banks/{bank_id}/document-transfer`        | [导入 document（异步）](#import-documents) |

### 异步导出 document

<a id="export-documents"></a>

**POST** `/v1/default/banks/{bank_id}/document-transfer/export`

提交异步 document 导出任务，将 Bank 中的 document（抽取的事实、entity 名称、因果链接和 chunks）打包为迁移用 ZIP 归档。归档不包含 embeddings 和数据库 ID；导入时会使用目标 Bank 的模型重新生成 embedding 并解析实体。除非设置 `include_observations=true`，否则不会导出 consolidation 后的 observations。传入 `document_id` 查询参数可导出指定 document；省略时导出整个 Bank。接口立即返回 `operation_id`，可通过异步操作接口查询进度；完成后从操作结果中取得下载地址。

#### 参数

| 名称                     | In    | 类型               | 必填 | 说明                                                                      |
| ------------------------ | ----- | ------------------ | ---- | ------------------------------------------------------------------------- |
| `bank_id`              | path  | `string`         | 是   | Bank 的唯一标识符。                                                       |
| `document_id`          | query | `array<string>?` | 否   | 要导出的 document ID；省略时导出全部 documents。                          |
| `include_observations` | query | `boolean`        | 否   | 同时导出 consolidation 后的 observations（导入时恢复）；默认值：`false` |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`202` — 已接受导出任务
- 格式：`application/json`

| 字段             | 类型       | 必填 | 说明                          |
| ---------------- | ---------- | ---- | ----------------------------- |
| `operation_id` | `string` | 是   | 异步导出操作的 ID。           |
| `status`       | `string` | 否   | 初始状态，通常为`pending`。 |

#### 响应示例

```json
{
  "operation_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending"
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 下载导出文件

<a id="download-file"></a>

**GET** `/v1/default/files/download/{key}`

下载异步导出任务生成并存入文件存储的 ZIP 归档。`key` 来自导出操作的 `result_metadata`（`storage_key` 或 `download_url`）；服务端会根据该 key 所属的 Bank 校验访问权限，并以附件形式返回文件。

#### 参数

| 名称    | In   | 类型       | 必填 | 说明               |
| ------- | ---- | ---------- | ---- | ------------------ |
| `key` | path | `string` | 是   | 要下载的文件 key。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 文件内容
- 格式：`application/octet-stream`

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明           |
| ---------- | -------------------------- | ---- | -------------- |
| `detail` | `array<ValidationError>` | 否   | 校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

| 字段      | 类型                        | 必填 | 说明                     |
| --------- | --------------------------- | ---- | ------------------------ |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径。 |
| `msg`   | `string`                  | 是   | 错误消息。               |
| `type`  | `string`                  | 是   | 错误类型。               |
| `input` | `any`                     | 否   | 触发校验的原始输入值。   |
| `ctx`   | `Context`                 | 否   | 错误上下文。             |

</details>

`operationId=download_file`

---

### 导入 document（异步）

<a id="import-documents"></a>

**POST** `/v1/default/banks/{bank_id}/document-transfer`

提交 transfer archive（由 export 接口生成）导入 Bank。作为后台 operation 运行：使用目标 Bank 的 embedding model 重新生成 facts embedding，并重新解析 entities，不执行 LLM 抽取。返回 operation_id；轮询 GET /v1/default/banks/{bank_id}/operations/{operation_id} 获取状态及 result_metadata 中导入/跳过的数量。使用 on_conflict 控制已有 document ID：skip（默认）、replace 或 new-id。

#### 参数

| 名称            | In    | 类型       | 必填 | 说明                                         |
| --------------- | ----- | ---------- | ---- | -------------------------------------------- |
| `bank_id`     | path  | `string` | 是   | Bank 的唯一标识符。                          |
| `on_conflict` | query | `string` | 否   | skip\| replace \| new-id；默认值：`"skip"` |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                        |
| ----------------- | ------ | ---------- | ---- | --------------------------- |
| `Authorization` | header | `string` | 是   | Bearer token。              |
| `Content-Type`  | header | `string` | 是   | 固定`multipart/form-data` |

#### 请求体

- 格式：`multipart/form-data`
- 必填：**是**

| 字段     | 类型               | 必填 | 说明                     |
| -------- | ------------------ | ---- | ------------------------ |
| `file` | `string(binary)` | 是   | 用于传输的 ZIP archive。 |

#### 请求示例

```json
{
  "file": "string"
}
```

#### 响应

- 状态码：`202` — 成功响应
- 格式：`application/json`

| 字段             | 类型       | 必填 | 说明                                    |
| ---------------- | ---------- | ---- | --------------------------------------- |
| `operation_id` | `string` | 是   | 异步操作 的唯一标识符，可用于查询状态。 |
| `status`       | `string` | 否   | 默认值：`"pending"`                   |

#### 响应示例

```json
{
  "operation_id": "string",
  "status": "pending"
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

## Files

<a id="files"></a>

**文件** · 1 个接口

文件对象存取。

### 本章目录

| Method   | Path                                         | 标题                            |
| -------- | -------------------------------------------- | ------------------------------- |
| `POST` | `/v1/default/banks/{bank_id}/files/retain` | [将文件转换为记忆](#file-retain) |

### 将文件转换为记忆

<a id="file-retain"></a>

**POST** `/v1/default/banks/{bank_id}/files/retain`

上传文件（PDF、DOCX 等），将其转换为 Markdown，并 Retain 为 memories。

此接口在一次操作中完成文件上传、转换和 memory 创建。

**功能：**

- 支持 PDF、DOCX、PPTX、XLSX、图片和音频（含 OCR 与音频转写）
- 自动将文件转换为 Markdown
- 将文件存入服务端配置的文件存储
- 每个文件分别生成一个 document，可附带元数据和标签
- 始终异步处理，并立即返回异步操作 ID

**系统会自动：**

1. 将上传的文件存入服务端配置的文件存储
2. 将文件转换为 Markdown
3. 创建包含文件元数据的 document 记录
4. 抽取事实并创建 memory unit（与常规 Retain 相同）

可通过 Operations 接口监控进度。

**请求格式：** `multipart/form-data`，包含：

- `files`：一个或多个待上传文件。
- `request`: 符合 FileRetainRequest 数据结构的 JSON 字符串。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                        |
| ----------------- | ------ | ---------- | ---- | --------------------------- |
| `Authorization` | header | `string` | 是   | Bearer token。              |
| `Content-Type`  | header | `string` | 是   | 固定`multipart/form-data` |

#### 请求体

- 格式：`multipart/form-data`
- 必填：**是**

| 字段        | 类型                      | 必填 | 说明                                            |
| ----------- | ------------------------- | ---- | ----------------------------------------------- |
| `files`   | `array<string(binary)>` | 是   | 要上传并转换的文件。                            |
| `request` | `string`                | 是   | 符合 FileRetainRequest 数据结构的 JSON 字符串。 |

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

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段              | 类型              | 必填 | 说明                                                                                                      |
| ----------------- | ----------------- | ---- | --------------------------------------------------------------------------------------------------------- |
| `operation_ids` | `array<string>` | 是   | 用于跟踪文件转换 operations 的 ID 列表。使用 GET /v1/default/banks/{bank_id}/operations 列出 operations。 |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

**实体** · 3 个接口

实体列表与维护。

### 本章目录

| Method  | Path                                                 | 标题                                   |
| ------- | ---------------------------------------------------- | -------------------------------------- |
| `GET` | `/v1/default/banks/{bank_id}/entities`             | [列出 entity](#list-entities)           |
| `GET` | `/v1/default/banks/{bank_id}/entities/graph`       | [获取 entity 共现图](#get-entity-graph) |
| `GET` | `/v1/default/banks/{bank_id}/entities/{entity_id}` | [获取 entity 详情](#get-entity)         |

### 列出 entity

<a id="list-entities"></a>

**GET** `/v1/default/banks/{bank_id}/entities`

列出 bank 已知的所有 entities（人物、组织等），按提及次数排序；支持分页。

#### 参数

| 名称        | In    | 类型        | 必填 | 说明                                                   |
| ----------- | ----- | ----------- | ---- | ------------------------------------------------------ |
| `bank_id` | path  | `string`  | 是   | Bank 的唯一标识符。                                    |
| `limit`   | query | `integer` | 否   | 返回 entity 的最大数量；默认值：`100`；最小值：`0` |
| `offset`  | query | `integer` | 否   | 分页偏移量；默认值：`0`；最小值：`0`               |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段       | 类型                      | 必填 | 说明           |
| ---------- | ------------------------- | ---- | -------------- |
| `items`  | `array<EntityListItem>` | 是   | 结果项目列表。 |
| `total`  | `integer`               | 是   | 总数量。       |
| `limit`  | `integer`               | 是   | 返回数量上限。 |
| `offset` | `integer`               | 是   | 分页偏移量。   |

<details open><summary><strong>items[]</strong> · <code>EntityListItem</code></summary>

数据结构 `EntityListItem`：

| 字段               | 类型        | 必填 | 说明                |
| ------------------ | ----------- | ---- | ------------------- |
| `id`             | `string`  | 是   | 资源的唯一标识符。  |
| `canonical_name` | `string`  | 是   | Entity 的规范名称。 |
| `mention_count`  | `integer` | 是   | 提及次数。          |
| `first_seen`     | `string?` | 否   | 首次出现时间。      |
| `last_seen`      | `string?` | 否   | 最近出现时间。      |
| `metadata`       | `object?` | 否   | 附加元数据。        |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 获取 entity 共现图

<a id="get-entity-graph"></a>

**GET** `/v1/default/banks/{bank_id}/entities/graph`

返回 entities（节点）及其共现关系（edges）的图数据，用于可视化。

#### 参数

| 名称          | In    | 类型        | 必填 | 说明                                                      |
| ------------- | ----- | ----------- | ---- | --------------------------------------------------------- |
| `bank_id`   | path  | `string`  | 是   | Bank 的唯一标识符。                                       |
| `limit`     | query | `integer` | 否   | 返回共现边的最大数量；默认值：`1000`；最小值：`0`     |
| `min_count` | query | `integer` | 否   | 纳入共现边所需的最低`cooccurrence_count`；默认值：`1` |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段               | 类型              | 必填 | 说明             |
| ------------------ | ----------------- | ---- | ---------------- |
| `nodes`          | `array<object>` | 是   | 图中的节点列表。 |
| `edges`          | `array<object>` | 是   | 图中的边列表。   |
| `total_entities` | `integer`       | 是   | entity 总数。    |
| `total_edges`    | `integer`       | 是   | 边总数。         |
| `limit`          | `integer`       | 是   | 返回数量上限。   |

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
        "link类型。": "cooccurrence",
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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 获取 entity 详情

<a id="get-entity"></a>

**GET** `/v1/default/banks/{bank_id}/entities/{entity_id}`

获取 entity 的详细信息，包括 observations（mental model）。

#### 参数

| 名称          | In   | 类型       | 必填 | 说明                |
| ------------- | ---- | ---------- | ---- | ------------------- |
| `bank_id`   | path | `string` | 是   | Bank 的唯一标识符。 |
| `entity_id` | path | `string` | 是   | Entity 的唯一 ID。  |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段               | 类型                                 | 必填 | 说明                |
| ------------------ | ------------------------------------ | ---- | ------------------- |
| `id`             | `string`                           | 是   | 资源的唯一标识符。  |
| `canonical_name` | `string`                           | 是   | Entity 的规范名称。 |
| `mention_count`  | `integer`                          | 是   | 提及次数。          |
| `first_seen`     | `string?`                          | 否   | 首次出现时间。      |
| `last_seen`      | `string?`                          | 否   | 最近出现时间。      |
| `metadata`       | `object?`                          | 否   | 附加元数据。        |
| `observations`   | `array<EntityObservationResponse>` | 是   | observation 列表。  |

<details open><summary><strong>observations[]</strong> · <code>EntityObservationResponse</code></summary>

数据结构 `EntityObservationResponse`：

| 字段             | 类型        | 必填 | 说明         |
| ---------------- | ----------- | ---- | ------------ |
| `text`         | `string`  | 是   | 文本内容。   |
| `mentioned_at` | `string?` | 否   | 被提及时间。 |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

**指令（Directives）** · 5 个接口

运行时 directive 管理。

### 本章目录

| Method     | Path                                                      | 标题                               |
| ---------- | --------------------------------------------------------- | ---------------------------------- |
| `GET`    | `/v1/default/banks/{bank_id}/directives`                | [列出 directive](#list-directives)  |
| `POST`   | `/v1/default/banks/{bank_id}/directives`                | [创建 directive](#create-directive) |
| `GET`    | `/v1/default/banks/{bank_id}/directives/{directive_id}` | [获取 directive](#get-directive)    |
| `PATCH`  | `/v1/default/banks/{bank_id}/directives/{directive_id}` | [更新 directive](#update-directive) |
| `DELETE` | `/v1/default/banks/{bank_id}/directives/{directive_id}` | [删除 directive](#delete-directive) |

### 列出 directive

<a id="list-directives"></a>

**GET** `/v1/default/banks/{bank_id}/directives`

列出注入 prompt 的硬规则。

#### 参数

| 名称            | In    | 类型                        | 必填 | 说明                                       |
| --------------- | ----- | --------------------------- | ---- | ------------------------------------------ |
| `bank_id`     | path  | `string`                  | 是   | Bank 的唯一标识符。                        |
| `tags`        | query | `array<string>?`          | 否   | 按 tags 筛选。                             |
| `tags_match`  | query | `"any" \| "all" \| "exact"` | 否   | tag 的匹配方式；默认值：`"any"`          |
| `active_only` | query | `boolean`                 | 否   | 仅返回启用的 directives；默认值：`true`  |
| `limit`       | query | `integer`                 | 否   | 默认值：`100`；取值范围：`1`–`1000` |
| `offset`      | query | `integer`                 | 否   | 默认值：`0`；最小值：`0`               |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段      | 类型                         | 必填 | 说明           |
| --------- | ---------------------------- | ---- | -------------- |
| `items` | `array<DirectiveResponse>` | 是   | 结果项目列表。 |

<details open><summary><strong>items[]</strong> · <code>DirectiveResponse</code></summary>

数据结构 `DirectiveResponse`：

| 字段           | 类型              | 必填 | 说明                                                     |
| -------------- | ----------------- | ---- | -------------------------------------------------------- |
| `id`         | `string`        | 是   | 资源的唯一标识符。                                       |
| `bank_id`    | `string`        | 是   | 所属 Bank 的唯一标识符。                                 |
| `name`       | `string`        | 是   | 名称。                                                   |
| `content`    | `string`        | 是   | 资源的正文内容；对 directive/page 等资源含其可编辑文本。 |
| `priority`   | `integer`       | 否   | 默认值：`0`                                            |
| `is_active`  | `boolean`       | 否   | 默认值：`true`                                         |
| `tags`       | `array<string>` | 否   | 默认值：`[]`                                           |
| `created_at` | `string?`       | 否   | 创建时间。                                               |
| `updated_at` | `string?`       | 否   | 最后更新时间。                                           |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 创建 directive

<a id="create-directive"></a>

**POST** `/v1/default/banks/{bank_id}/directives`

创建一条将注入 prompt 的硬规则。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段          | 类型              | 必填 | 说明                                              |
| ------------- | ----------------- | ---- | ------------------------------------------------- |
| `name`      | `string`        | 是   | directive 的可读名称。                            |
| `content`   | `string`        | 是   | 要注入 prompts 的 directive 文本。                |
| `priority`  | `integer`       | 否   | 优先级更高的 directives 会优先注入；默认值：`0` |
| `is_active` | `boolean`       | 否   | 此 directive 是否启用；默认值：`true`           |
| `tags`      | `array<string>` | 否   | 用于筛选的标签；默认值：`[]`                    |

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

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段           | 类型              | 必填 | 说明                                                     |
| -------------- | ----------------- | ---- | -------------------------------------------------------- |
| `id`         | `string`        | 是   | 资源的唯一标识符。                                       |
| `bank_id`    | `string`        | 是   | 所属 Bank 的唯一标识符。                                 |
| `name`       | `string`        | 是   | 名称。                                                   |
| `content`    | `string`        | 是   | 资源的正文内容；对 directive/page 等资源含其可编辑文本。 |
| `priority`   | `integer`       | 否   | 默认值：`0`                                            |
| `is_active`  | `boolean`       | 否   | 默认值：`true`                                         |
| `tags`       | `array<string>` | 否   | 默认值：`[]`                                           |
| `created_at` | `string?`       | 否   | 创建时间。                                               |
| `updated_at` | `string?`       | 否   | 最后更新时间。                                           |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 获取 directive

<a id="get-directive"></a>

**GET** `/v1/default/banks/{bank_id}/directives/{directive_id}`

按 ID 获取指定 directive。

#### 参数

| 名称             | In   | 类型       | 必填 | 说明                  |
| ---------------- | ---- | ---------- | ---- | --------------------- |
| `bank_id`      | path | `string` | 是   | Bank 的唯一标识符。   |
| `directive_id` | path | `string` | 是   | Directive 的唯一 ID。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段           | 类型              | 必填 | 说明                                                     |
| -------------- | ----------------- | ---- | -------------------------------------------------------- |
| `id`         | `string`        | 是   | 资源的唯一标识符。                                       |
| `bank_id`    | `string`        | 是   | 所属 Bank 的唯一标识符。                                 |
| `name`       | `string`        | 是   | 名称。                                                   |
| `content`    | `string`        | 是   | 资源的正文内容；对 directive/page 等资源含其可编辑文本。 |
| `priority`   | `integer`       | 否   | 默认值：`0`                                            |
| `is_active`  | `boolean`       | 否   | 默认值：`true`                                         |
| `tags`       | `array<string>` | 否   | 默认值：`[]`                                           |
| `created_at` | `string?`       | 否   | 创建时间。                                               |
| `updated_at` | `string?`       | 否   | 最后更新时间。                                           |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 更新 directive

<a id="update-directive"></a>

**PATCH** `/v1/default/banks/{bank_id}/directives/{directive_id}`

更新 directive 属性。

#### 参数

| 名称             | In   | 类型       | 必填 | 说明                  |
| ---------------- | ---- | ---------- | ---- | --------------------- |
| `bank_id`      | path | `string` | 是   | Bank 的唯一标识符。   |
| `directive_id` | path | `string` | 是   | Directive 的唯一 ID。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段          | 类型               | 必填 | 说明           |
| ------------- | ------------------ | ---- | -------------- |
| `name`      | `string?`        | 否   | 新的名称。     |
| `content`   | `string?`        | 否   | 新的内容。     |
| `priority`  | `integer?`       | 否   | 新的优先级。   |
| `is_active` | `boolean?`       | 否   | 新的启用状态。 |
| `tags`      | `array<string>?` | 否   | 新的 tags。    |

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

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段           | 类型              | 必填 | 说明                                                     |
| -------------- | ----------------- | ---- | -------------------------------------------------------- |
| `id`         | `string`        | 是   | 资源的唯一标识符。                                       |
| `bank_id`    | `string`        | 是   | 所属 Bank 的唯一标识符。                                 |
| `name`       | `string`        | 是   | 名称。                                                   |
| `content`    | `string`        | 是   | 资源的正文内容；对 directive/page 等资源含其可编辑文本。 |
| `priority`   | `integer`       | 否   | 默认值：`0`                                            |
| `is_active`  | `boolean`       | 否   | 默认值：`true`                                         |
| `tags`       | `array<string>` | 否   | 默认值：`[]`                                           |
| `created_at` | `string?`       | 否   | 创建时间。                                               |
| `updated_at` | `string?`       | 否   | 最后更新时间。                                           |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 删除 directive

<a id="delete-directive"></a>

**DELETE** `/v1/default/banks/{bank_id}/directives/{directive_id}`

删除 directive。

#### 参数

| 名称             | In   | 类型       | 必填 | 说明                  |
| ---------------- | ---- | ---------- | ---- | --------------------- |
| `bank_id`      | path | `string` | 是   | Bank 的唯一标识符。   |
| `directive_id` | path | `string` | 是   | Directive 的唯一 ID。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

_无展开字段（标量、自由 object 或未声明 properties）_

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

**异步操作** · 5 个接口

异步任务状态（retain / refresh / 建 page 等返回的 operation_id）。

### 本章目录

| Method     | Path                                                             | 标题                                     |
| ---------- | ---------------------------------------------------------------- | ---------------------------------------- |
| `GET`    | `/v1/default/banks/{bank_id}/operations`                       | [列出异步操作](#list-operations)          |
| `GET`    | `/v1/default/banks/{bank_id}/operations/{operation_id}`        | [获取异步操作状态](#get-operation-status) |
| `DELETE` | `/v1/default/banks/{bank_id}/operations/{operation_id}`        | [取消异步操作](#cancel-operation)         |
| `DELETE` | `/v1/default/banks/{bank_id}/operations/{operation_id}/delete` | [删除已终止的异步操作](#delete-operation) |
| `POST`   | `/v1/default/banks/{bank_id}/operations/{operation_id}/retry`  | [重试异步操作](#retry-operation)          |

### 列出异步操作

<a id="list-operations"></a>

**GET** `/v1/default/banks/{bank_id}/operations`

列出指定 Bank 的异步操作，可按 status 和 operation type 筛选；结果按最近时间优先排序。

#### 参数

| 名称                | In    | 类型        | 必填 | 说明                                                                                                         |
| ------------------- | ----- | ----------- | ---- | ------------------------------------------------------------------------------------------------------------ |
| `bank_id`         | path  | `string`  | 是   | Bank 的唯一标识符。                                                                                          |
| `status`          | query | `string?` | 否   | 按状态筛选：pending、processing、completed、failed 或 cancelled。                                            |
| `type`            | query | `string?` | 否   | 按 operation type 筛选：retain、consolidation、refresh_mental_model、file_convert_retain、webhook_delivery。 |
| `limit`           | query | `integer` | 否   | 返回异步操作的最大数量；默认值：`20`；取值范围：`1`–`100`                                             |
| `offset`          | query | `integer` | 否   | 跳过的异步操作数量；默认值：`0`；最小值：`0`                                                             |
| `exclude_parents` | query | `boolean` | 否   | 从结果中排除父级批量异步操作；默认值：`false`                                                              |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段           | 类型                         | 必填 | 说明                     |
| -------------- | ---------------------------- | ---- | ------------------------ |
| `bank_id`    | `string`                   | 是   | 所属 Bank 的唯一标识符。 |
| `total`      | `integer`                  | 是   | 总数量。                 |
| `limit`      | `integer`                  | 是   | 返回数量上限。           |
| `offset`     | `integer`                  | 是   | 分页偏移量。             |
| `operations` | `array<OperationResponse>` | 是   | operation 列表。         |

<details open><summary><strong>operations[]</strong> · <code>OperationResponse</code></summary>

数据结构 `OperationResponse`：

| 字段              | 类型                   | 必填 | 说明                                                                                                                                                                                    |
| ----------------- | ---------------------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`            | `string`             | 是   | 资源的唯一标识符。                                                                                                                                                                      |
| `task_type`     | `string`             | 是   | 任务类型。                                                                                                                                                                              |
| `items_count`   | `integer`            | 是   | 项目数量。                                                                                                                                                                              |
| `document_id`   | `string?`            | 否   | Document 的唯一标识符。                                                                                                                                                                 |
| `filename`      | `string?`            | 否   | 文件转换 operation（file_convert_retain）的原始文件名；其他 task type 为 null。                                                                                                         |
| `created_at`    | `string`             | 是   | 资源创建时间（ISO 8601）。                                                                                                                                                              |
| `updated_at`    | `string?`            | 否   | 此 operation 记录最近一次发生变化的时间（claim、progress heartbeat 或 completion）。                                                                                                    |
| `status`        | `string`             | 是   | 当前处理状态；异步操作通常为 pending、processing、completed、failed 或 cancelled。                                                                                                      |
| `error_message` | `string?`            | 否   | 错误消息。                                                                                                                                                                              |
| `retry_count`   | `integer?`           | 否   | 该异步操作 失败后已重试的次数。                                                                                                                                                         |
| `next_retry_at` | `string?`            | 否   | worker 下次尝试该异步操作 的时间。对于 pending 状态的异步操作，未来时间表示任务正在等待而不是立即可取；例如扩展可能抛出 DeferOperation，让任务等待背压窗口开启。已完成任务始终为 null。 |
| `progress`      | `OperationProgress?` | 否   | 运行中异步操作最近一次已知的进度快照；未记录时为 null。                                                                                                                                 |

<details open><summary><strong>progress</strong> · <code>OperationProgress</code></summary>

数据结构 `OperationProgress`：

| 字段          | 类型                      | 必填 | 说明                                                                           |
| ------------- | ------------------------- | ---- | ------------------------------------------------------------------------------ |
| `stage`     | `string`                | 是   | Operation 最近报告的粗粒度阶段（例如 processing_batch）。                      |
| `at`        | `string`                | 是   | 写入此快照的 ISO 8601 时间戳。                                                 |
| `processed` | `integer?`              | 否   | 目前已完成的工作单元数（如子批次、memories）；未知时为空。                     |
| `total`     | `integer?`              | 否   | Operation 的工作单元总数；未知时为空。                                         |
| `detail`    | `map<string, integer>?` | 否   | Operation 专属计数器（例如 observations_created、round、items_in_sub_batch）。 |

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
      "status": "pending",
      "task_type": "retain"
    }
  ],
  "total": 150
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 获取异步操作状态

<a id="get-operation-status"></a>

**GET** `/v1/default/banks/{bank_id}/operations/{operation_id}`

获取指定异步操作 的状态。返回 pending、processing、completed、failed 或 cancelled。已完成的异步操作 在配置的保留窗口内仍可携带 payload 查询，之后会被清理。

#### 参数

| 名称                | In    | 类型        | 必填 | 说明                                                                      |
| ------------------- | ----- | ----------- | ---- | ------------------------------------------------------------------------- |
| `bank_id`         | path  | `string`  | 是   | Bank 的唯一标识符。                                                       |
| `operation_id`    | path  | `string`  | 是   | Operation 的唯一 ID。                                                     |
| `include_payload` | query | `boolean` | 否   | 在响应中包含原始任务 payload（提交参数），内容可能较大；默认值：`false` |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段                 | 类型                                                                              | 必填 | 说明                                                                                                                                       |
| -------------------- | --------------------------------------------------------------------------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `operation_id`     | `string`                                                                        | 是   | 异步操作 的唯一标识符，可用于查询状态。                                                                                                    |
| `status`           | `"pending" \| "processing" \| "completed" \| "failed" \| "cancelled" \| "not_found"` | 是   | 当前状态。                                                                                                                                 |
| `operation_type`   | `string?`                                                                       | 否   | operation 类型。                                                                                                                           |
| `created_at`       | `string?`                                                                       | 否   | 创建时间。                                                                                                                                 |
| `updated_at`       | `string?`                                                                       | 否   | 最后更新时间。                                                                                                                             |
| `completed_at`     | `string?`                                                                       | 否   | 完成时间。                                                                                                                                 |
| `error_message`    | `string?`                                                                       | 否   | 错误消息。                                                                                                                                 |
| `retry_count`      | `integer?`                                                                      | 否   | 该异步操作 失败后已重试的次数。                                                                                                            |
| `next_retry_at`    | `string?`                                                                       | 否   | worker 下次尝试该异步操作 的时间。对于 pending 状态的异步操作，未来时间表示任务被暂停（例如扩展抛出 DeferOperation），而不是等待立即处理。 |
| `progress`         | `OperationProgress?`                                                            | 否   | 运行中异步操作最近一次已知的进度快照；未记录时为 null。                                                                                    |
| `result_metadata`  | `object?`                                                                       | 否   | 用于调试的内部 metadata。结构可能随时变化，不应在生产逻辑中依赖。                                                                          |
| `child_operations` | `array<ChildOperationStatus>?`                                                  | 否   | 批量 异步操作的子 operations（如适用）。                                                                                                   |
| `task_payload`     | `object?`                                                                       | 否   | 提交异步操作时使用的原始 task payload（参数）。仅在`include_payload=true` 时填充。                                                       |

<details open><summary><strong>progress</strong> · <code>OperationProgress</code></summary>

数据结构 `OperationProgress`：

| 字段          | 类型                      | 必填 | 说明                                                                           |
| ------------- | ------------------------- | ---- | ------------------------------------------------------------------------------ |
| `stage`     | `string`                | 是   | Operation 最近报告的粗粒度阶段（例如 processing_batch）。                      |
| `at`        | `string`                | 是   | 写入此快照的 ISO 8601 时间戳。                                                 |
| `processed` | `integer?`              | 否   | 目前已完成的工作单元数（如子批次、memories）；未知时为空。                     |
| `total`     | `integer?`              | 否   | Operation 的工作单元总数；未知时为空。                                         |
| `detail`    | `map<string, integer>?` | 否   | Operation 专属计数器（例如 observations_created、round、items_in_sub_batch）。 |

</details>

<details open><summary><strong>child_operations[]</strong> · <code>ChildOperationStatus</code></summary>

数据结构 `ChildOperationStatus`：

| 字段                | 类型         | 必填 | 说明                                                                               |
| ------------------- | ------------ | ---- | ---------------------------------------------------------------------------------- |
| `operation_id`    | `string`   | 是   | 异步操作 的唯一标识符，可用于查询状态。                                            |
| `status`          | `string`   | 是   | 当前处理状态；异步操作通常为 pending、processing、completed、failed 或 cancelled。 |
| `sub_batch_index` | `integer?` | 否   | 子批次索引。                                                                       |
| `items_count`     | `integer?` | 否   | 项目数量。                                                                         |
| `error_message`   | `string?`  | 否   | 错误消息。                                                                         |

</details>

#### 响应示例

```json
{
  "completed_at": "2024-01-15T10:31:30Z",
  "created_at": "2024-01-15T10:30:00Z",
  "operation_id": "550e8400-e29b-41d4-a716-446655440000",
  "operation_type": "refresh_mental_models",
  "status": "completed",
  "updated_at": "2024-01-15T10:31:30Z"
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

从队列中移除待处理的异步操作，以取消该操作。

#### 参数

| 名称             | In   | 类型       | 必填 | 说明                  |
| ---------------- | ---- | ---------- | ---- | --------------------- |
| `bank_id`      | path | `string` | 是   | Bank 的唯一标识符。   |
| `operation_id` | path | `string` | 是   | Operation 的唯一 ID。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段             | 类型        | 必填 | 说明                                    |
| ---------------- | ----------- | ---- | --------------------------------------- |
| `success`      | `boolean` | 是   | 操作是否成功。                          |
| `message`      | `string`  | 是   | 操作结果或错误的可读消息。              |
| `operation_id` | `string`  | 是   | 异步操作 的唯一标识符，可用于查询状态。 |

#### 响应示例

```json
{
  "message": "Operation 550e8400-e29b-41d4-a716-446655440000 cancelled",
  "operation_id": "550e8400-e29b-41d4-a716-446655440000",
  "success": true
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 删除已终止的异步操作

<a id="delete-operation"></a>

**DELETE** `/v1/default/banks/{bank_id}/operations/{operation_id}/delete`

永久删除失败、已取消或已完成的异步操作 记录。

#### 参数

| 名称             | In   | 类型       | 必填 | 说明                  |
| ---------------- | ---- | ---------- | ---- | --------------------- |
| `bank_id`      | path | `string` | 是   | Bank 的唯一标识符。   |
| `operation_id` | path | `string` | 是   | Operation 的唯一 ID。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段             | 类型        | 必填 | 说明                                    |
| ---------------- | ----------- | ---- | --------------------------------------- |
| `success`      | `boolean` | 是   | 操作是否成功。                          |
| `message`      | `string`  | 是   | 操作结果或错误的可读消息。              |
| `operation_id` | `string`  | 是   | 异步操作 的唯一标识符，可用于查询状态。 |

#### 响应示例

```json
{
  "message": "Operation 550e8400-e29b-41d4-a716-446655440000 deleted",
  "operation_id": "550e8400-e29b-41d4-a716-446655440000",
  "success": true
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

重新入队失败的异步操作，使 worker 再次处理。

#### 参数

| 名称             | In   | 类型       | 必填 | 说明                  |
| ---------------- | ---- | ---------- | ---- | --------------------- |
| `bank_id`      | path | `string` | 是   | Bank 的唯一标识符。   |
| `operation_id` | path | `string` | 是   | Operation 的唯一 ID。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段             | 类型        | 必填 | 说明                                    |
| ---------------- | ----------- | ---- | --------------------------------------- |
| `success`      | `boolean` | 是   | 操作是否成功。                          |
| `message`      | `string`  | 是   | 操作结果或错误的可读消息。              |
| `operation_id` | `string`  | 是   | 异步操作 的唯一标识符，可用于查询状态。 |

#### 响应示例

```json
{
  "message": "Operation 550e8400-e29b-41d4-a716-446655440000 queued for retry",
  "operation_id": "550e8400-e29b-41d4-a716-446655440000",
  "success": true
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

**Webhooks** · 5 个接口

事件订阅与回调配置。

### 本章目录

| Method     | Path                                                             | 标题                                             |
| ---------- | ---------------------------------------------------------------- | ------------------------------------------------ |
| `POST`   | `/v1/default/banks/{bank_id}/webhooks`                         | [注册 webhook](#create-webhook)                   |
| `GET`    | `/v1/default/banks/{bank_id}/webhooks`                         | [列出 webhook](#list-webhooks)                    |
| `DELETE` | `/v1/default/banks/{bank_id}/webhooks/{webhook_id}`            | [删除 webhook](#delete-webhook)                   |
| `PATCH`  | `/v1/default/banks/{bank_id}/webhooks/{webhook_id}`            | [更新 webhook](#update-webhook)                   |
| `GET`    | `/v1/default/banks/{bank_id}/webhooks/{webhook_id}/deliveries` | [列出 webhook delivery](#list-webhook-deliveries) |

### 注册 webhook

<a id="create-webhook"></a>

**POST** `/v1/default/banks/{bank_id}/webhooks`

注册 webhook endpoint，以接收该 bank 的事件通知。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段            | 类型                  | 必填 | 说明                                                                                                                                                 |
| --------------- | --------------------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `url`         | `string`            | 是   | 接收事件投递的 HTTP(S) endpoint URL。                                                                                                                |
| `secret`      | `string?`           | 否   | HMAC-SHA256 签名密钥（可选）。                                                                                                                       |
| `event_types` | `array<string>`     | 否   | 要投递的事件类型列表。支持`retain.completed`、`consolidation.completed` 和 `memory_defense.triggered`；默认值：`["consolidation.completed"]` |
| `enabled`     | `boolean`           | 否   | 此 webhook 是否启用；默认值：`true`                                                                                                                |
| `http_config` | `WebhookHttpConfig` | 否   | HTTP 投递配置（method、timeout、headers、params）。                                                                                                  |

<details open><summary><strong>http_config</strong> · <code>WebhookHttpConfig</code></summary>

数据结构 `WebhookHttpConfig`：

| 字段                | 类型                    | 必填 | 说明                                         |
| ------------------- | ----------------------- | ---- | -------------------------------------------- |
| `method`          | `string`              | 否   | HTTP method：GET 或 POST；默认值：`"POST"` |
| `timeout_seconds` | `integer`             | 否   | HTTP 请求超时时间，单位为秒；默认值：`30`  |
| `headers`         | `map<string, string>` | 否   | 自定义 HTTP headers。                        |
| `params`          | `map<string, string>` | 否   | 自定义 HTTP query 参数。                     |

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

- 状态码：`201` — 成功响应
- 格式：`application/json`

| 字段            | 类型                  | 必填 | 说明                                          |
| --------------- | --------------------- | ---- | --------------------------------------------- |
| `id`          | `string`            | 是   | 资源的唯一标识符。                            |
| `bank_id`     | `string?`           | 否   | Bank 的唯一标识符。                           |
| `url`         | `string`            | 是   | Webhook 接收事件通知的 HTTP(S) endpoint URL。 |
| `secret`      | `string?`           | 否   | 签名密钥（响应中会脱敏）。                    |
| `event_types` | `array<string>`     | 是   | 订阅的事件类型列表。                          |
| `enabled`     | `boolean`           | 是   | 是否启用。                                    |
| `http_config` | `WebhookHttpConfig` | 否   | HTTP 配置。                                   |
| `created_at`  | `string?`           | 否   | 创建时间。                                    |
| `updated_at`  | `string?`           | 否   | 最后更新时间。                                |

<details open><summary><strong>http_config</strong> · <code>WebhookHttpConfig</code></summary>

数据结构 `WebhookHttpConfig`：

| 字段                | 类型                    | 必填 | 说明                                         |
| ------------------- | ----------------------- | ---- | -------------------------------------------- |
| `method`          | `string`              | 否   | HTTP method：GET 或 POST；默认值：`"POST"` |
| `timeout_seconds` | `integer`             | 否   | HTTP 请求超时时间，单位为秒；默认值：`30`  |
| `headers`         | `map<string, string>` | 否   | 自定义 HTTP headers。                        |
| `params`          | `map<string, string>` | 否   | 自定义 HTTP query 参数。                     |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 列出 webhook

<a id="list-webhooks"></a>

**GET** `/v1/default/banks/{bank_id}/webhooks`

列出 bank 已注册的所有 webhooks。

#### 参数

| 名称        | In   | 类型       | 必填 | 说明                |
| ----------- | ---- | ---------- | ---- | ------------------- |
| `bank_id` | path | `string` | 是   | Bank 的唯一标识符。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段      | 类型                       | 必填 | 说明           |
| --------- | -------------------------- | ---- | -------------- |
| `items` | `array<WebhookResponse>` | 是   | 结果项目列表。 |

<details open><summary><strong>items[]</strong> · <code>WebhookResponse</code></summary>

数据结构 `WebhookResponse`：

| 字段            | 类型                  | 必填 | 说明                                          |
| --------------- | --------------------- | ---- | --------------------------------------------- |
| `id`          | `string`            | 是   | 资源的唯一标识符。                            |
| `bank_id`     | `string?`           | 否   | Bank 的唯一标识符。                           |
| `url`         | `string`            | 是   | Webhook 接收事件通知的 HTTP(S) endpoint URL。 |
| `secret`      | `string?`           | 否   | 签名密钥（响应中会脱敏）。                    |
| `event_types` | `array<string>`     | 是   | 订阅的事件类型列表。                          |
| `enabled`     | `boolean`           | 是   | 是否启用。                                    |
| `http_config` | `WebhookHttpConfig` | 否   | HTTP 配置。                                   |
| `created_at`  | `string?`           | 否   | 创建时间。                                    |
| `updated_at`  | `string?`           | 否   | 最后更新时间。                                |

<details open><summary><strong>http_config</strong> · <code>WebhookHttpConfig</code></summary>

数据结构 `WebhookHttpConfig`：

| 字段                | 类型                    | 必填 | 说明                                         |
| ------------------- | ----------------------- | ---- | -------------------------------------------- |
| `method`          | `string`              | 否   | HTTP method：GET 或 POST；默认值：`"POST"` |
| `timeout_seconds` | `integer`             | 否   | HTTP 请求超时时间，单位为秒；默认值：`30`  |
| `headers`         | `map<string, string>` | 否   | 自定义 HTTP headers。                        |
| `params`          | `map<string, string>` | 否   | 自定义 HTTP query 参数。                     |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 删除 webhook

<a id="delete-webhook"></a>

**DELETE** `/v1/default/banks/{bank_id}/webhooks/{webhook_id}`

删除已注册的 webhook。

#### 参数

| 名称           | In   | 类型       | 必填 | 说明                |
| -------------- | ---- | ---------- | ---- | ------------------- |
| `bank_id`    | path | `string` | 是   | Bank 的唯一标识符。 |
| `webhook_id` | path | `string` | 是   | Webhook 的唯一 ID。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段              | 类型         | 必填 | 说明           |
| ----------------- | ------------ | ---- | -------------- |
| `success`       | `boolean`  | 是   | 操作是否成功。 |
| `message`       | `string?`  | 否   | 操作结果消息。 |
| `deleted_count` | `integer?` | 否   | 已删除数量。   |

#### 响应示例

```json
{
  "deleted_count": 10,
  "message": "Deleted successfully",
  "success": true
}
```

#### 响应

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 更新 webhook

<a id="update-webhook"></a>

**PATCH** `/v1/default/banks/{bank_id}/webhooks/{webhook_id}`

更新已注册 webhook 的一个或多个字段；只修改请求中提供的字段。

#### 参数

| 名称           | In   | 类型       | 必填 | 说明                |
| -------------- | ---- | ---------- | ---- | ------------------- |
| `bank_id`    | path | `string` | 是   | Bank 的唯一标识符。 |
| `webhook_id` | path | `string` | 是   | Webhook 的唯一 ID。 |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明                     |
| ----------------- | ------ | ---------- | ---- | ------------------------ |
| `Authorization` | header | `string` | 是   | Bearer token。           |
| `Content-Type`  | header | `string` | 是   | 固定`application/json` |

#### 请求体

- 格式：`application/json`
- 必填：**是**

| 字段            | 类型                   | 必填 | 说明                                                         |
| --------------- | ---------------------- | ---- | ------------------------------------------------------------ |
| `url`         | `string?`            | 否   | HTTP(S) endpoint 的 URL。                                    |
| `secret`      | `string?`            | 否   | HMAC-SHA256 签名密钥。省略则保留现有密钥；传入 null 则清除。 |
| `event_types` | `array<string>?`     | 否   | 事件类型列表。                                               |
| `enabled`     | `boolean?`           | 否   | 此 webhook 是否启用。                                        |
| `http_config` | `WebhookHttpConfig?` | 否   | HTTP 投递配置。                                              |

<details open><summary><strong>http_config</strong> · <code>WebhookHttpConfig</code></summary>

数据结构 `WebhookHttpConfig`：

| 字段                | 类型                    | 必填 | 说明                                         |
| ------------------- | ----------------------- | ---- | -------------------------------------------- |
| `method`          | `string`              | 否   | HTTP method：GET 或 POST；默认值：`"POST"` |
| `timeout_seconds` | `integer`             | 否   | HTTP 请求超时时间，单位为秒；默认值：`30`  |
| `headers`         | `map<string, string>` | 否   | 自定义 HTTP headers。                        |
| `params`          | `map<string, string>` | 否   | 自定义 HTTP query 参数。                     |

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

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段            | 类型                  | 必填 | 说明                                          |
| --------------- | --------------------- | ---- | --------------------------------------------- |
| `id`          | `string`            | 是   | 资源的唯一标识符。                            |
| `bank_id`     | `string?`           | 否   | Bank 的唯一标识符。                           |
| `url`         | `string`            | 是   | Webhook 接收事件通知的 HTTP(S) endpoint URL。 |
| `secret`      | `string?`           | 否   | 签名密钥（响应中会脱敏）。                    |
| `event_types` | `array<string>`     | 是   | 订阅的事件类型列表。                          |
| `enabled`     | `boolean`           | 是   | 是否启用。                                    |
| `http_config` | `WebhookHttpConfig` | 否   | HTTP 配置。                                   |
| `created_at`  | `string?`           | 否   | 创建时间。                                    |
| `updated_at`  | `string?`           | 否   | 最后更新时间。                                |

<details open><summary><strong>http_config</strong> · <code>WebhookHttpConfig</code></summary>

数据结构 `WebhookHttpConfig`：

| 字段                | 类型                    | 必填 | 说明                                         |
| ------------------- | ----------------------- | ---- | -------------------------------------------- |
| `method`          | `string`              | 否   | HTTP method：GET 或 POST；默认值：`"POST"` |
| `timeout_seconds` | `integer`             | 否   | HTTP 请求超时时间，单位为秒；默认值：`30`  |
| `headers`         | `map<string, string>` | 否   | 自定义 HTTP headers。                        |
| `params`          | `map<string, string>` | 否   | 自定义 HTTP query 参数。                     |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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

### 列出 webhook delivery

<a id="list-webhook-deliveries"></a>

**GET** `/v1/default/banks/{bank_id}/webhooks/{webhook_id}/deliveries`

查看 webhook 的 delivery 历史（便于调试）。

#### 参数

| 名称           | In    | 类型        | 必填 | 说明                                                      |
| -------------- | ----- | ----------- | ---- | --------------------------------------------------------- |
| `bank_id`    | path  | `string`  | 是   | Bank 的唯一标识符。                                       |
| `webhook_id` | path  | `string`  | 是   | Webhook 的唯一 ID。                                       |
| `limit`      | query | `integer` | 否   | 最多返回的 delivery 数量；默认值：`50`；最大值：`200` |
| `cursor`     | query | `string?` | 否   | 分页 cursor，取上一页最后一项的 created_at。              |

#### 请求头

| 名称              | In     | 类型       | 必填 | 说明           |
| ----------------- | ------ | ---------- | ---- | -------------- |
| `Authorization` | header | `string` | 是   | Bearer token。 |

#### 响应

- 状态码：`200` — 成功响应
- 格式：`application/json`

| 字段            | 类型                               | 必填 | 说明                           |
| --------------- | ---------------------------------- | ---- | ------------------------------ |
| `items`       | `array<WebhookDeliveryResponse>` | 是   | 结果项目列表。                 |
| `next_cursor` | `string?`                        | 否   | 下一页游标；没有下一页时为空。 |

<details open><summary><strong>items[]</strong> · <code>WebhookDeliveryResponse</code></summary>

数据结构 `WebhookDeliveryResponse`：

| 字段                     | 类型         | 必填 | 说明                                                                               |
| ------------------------ | ------------ | ---- | ---------------------------------------------------------------------------------- |
| `id`                   | `string`   | 是   | 资源的唯一标识符。                                                                 |
| `webhook_id`           | `string?`  | 否   | Webhook 的唯一标识符。                                                             |
| `url`                  | `string`   | 是   | Webhook 接收事件通知的 HTTP(S) endpoint URL。                                      |
| `event_type`           | `string`   | 是   | 事件类型。                                                                         |
| `status`               | `string`   | 是   | 当前处理状态；异步操作通常为 pending、processing、completed、failed 或 cancelled。 |
| `attempts`             | `integer`  | 是   | 投递尝试次数。                                                                     |
| `next_retry_at`        | `string?`  | 否   | 下次重试时间。                                                                     |
| `last_error`           | `string?`  | 否   | 最近一次错误。                                                                     |
| `last_response_status` | `integer?` | 否   | 最近一次响应状态码。                                                               |
| `last_response_body`   | `string?`  | 否   | 最近一次响应正文。                                                                 |
| `last_attempt_at`      | `string?`  | 否   | 最近一次尝试时间。                                                                 |
| `created_at`           | `string?`  | 否   | 创建时间。                                                                         |
| `updated_at`           | `string?`  | 否   | 最后更新时间。                                                                     |

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

- 状态码：`422` — 校验错误
- 格式：`application/json`

| 字段       | 类型                       | 必填 | 说明                     |
| ---------- | -------------------------- | ---- | ------------------------ |
| `detail` | `array<ValidationError>` | 否   | 详细信息或校验错误列表。 |

<details open><summary><strong>detail[]</strong> · <code>ValidationError</code></summary>

数据结构 `ValidationError`：

| 字段      | 类型                        | 必填 | 说明                                                 |
| --------- | --------------------------- | ---- | ---------------------------------------------------- |
| `loc`   | `array<string \| integer>` | 是   | 发生校验错误的位置路径；数组元素可以是字段名或索引。 |
| `msg`   | `string`                  | 是   | 错误消息或状态消息。                                 |
| `type`  | `string`                  | 是   | 对象或错误的类型。                                   |
| `input` | `any`                     | 否   | 触发校验的原始输入值。                               |
| `ctx`   | `Context`                 | 否   | 错误上下文信息。                                     |

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
