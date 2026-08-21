#!/usr/bin/env python3
"""Generate a standalone Chinese Markdown reading guide for the full Hindsight HTTP API.

From openapi.json, produce a self-contained document with:
  - tag navigation and full operation index
  - operation cards: method + path + description
  - path/query/header/body field tables (nested where useful)
  - Request samples / Response samples as JSON
  - no interactive UI assumptions, no external doc-site links
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

TAG_ORDER = [
    "Banks",
    "Bank Templates",
    "Memory",
    "Knowledge Base",
    "Mental Models",
    "Documents",
    "Document Transfer",
    "Files",
    "Entities",
    "Directives",
    "Operations",
    "Webhooks",
    "Monitoring",
    "Audit",
    "LLM Traces",
]

# Not exposed in customer-facing hosted API docs
HIDDEN_TAGS = {
    "Monitoring",
    "Audit",
    "LLM Traces",
}

HOSTED_BASE_URL = "https://cloud.memory.bj.baidubce.com/api"

TAG_ZH = {
    "Banks": "Bank 管理",
    "Bank Templates": "Bank 模板",
    "Memory": "记忆（Retain / Recall / Reflect）",
    "Knowledge Base": "知识库树（Knowledge Pages）",
    "Mental Models": "心智模型",
    "Documents": "文档",
    "Document Transfer": "文档迁移",
    "Files": "文件",
    "Entities": "实体",
    "Directives": "指令（Directives）",
    "Operations": "异步操作",
    "Webhooks": "Webhooks",
    "Monitoring": "监控与健康",
    "Audit": "审计",
    "LLM Traces": "LLM 追踪",
    "(untagged)": "未分组",
}

TAG_INTRO = {
    "Banks": "创建、配置、清理 bank；consolidation、LLM 探测、统计等控制面。",
    "Bank Templates": "bank 模板 schema / 导入导出，便于环境间复用配置。",
    "Memory": "主路径 retain → recall → reflect，以及 list/get/update/clear。",
    "Knowledge Base": "folder/page 树组织 mental model；异步生成 page；hybrid 搜索与 markdown 导出。",
    "Mental Models": "可刷新的合成知识（多为 markdown）。可独立使用，也可挂到 KB page。",
    "Documents": "文档粒度的查看、更新、删除与追踪。",
    "Document Transfer": "文档导入导出与迁移。",
    "Files": "文件对象存取。",
    "Entities": "实体列表与维护。",
    "Directives": "运行时 directive 管理。",
    "Operations": "异步任务状态（retain / refresh / 建 page 等返回的 operation_id）。",
    "Webhooks": "事件订阅与回调配置。",
    "Monitoring": "健康检查、版本、指标。",
    "Audit": "审计记录。",
    "LLM Traces": "LLM 请求追踪。",
}

OP_TITLE_ZH = {
    "retain_memories": "写入记忆（Retain）",
    "recall_memories": "检索记忆（Recall）",
    "reflect": "推理反思（Reflect）",
    "list_memories": "列出记忆",
    "get_memory": "获取单条记忆",
    "update_memory": "更新记忆",
    "clear_bank_memories": "清空 bank 记忆",
    "dry_run_extract_memories": "试运行抽取记忆",
    "get_graph": "获取记忆图",
    "get_observation_history": "观察历史",
    "clear_memory_observations": "清除记忆观察",
    "list_observation_scopes": "列出 observation scopes",
    "list_tags": "列出 tags",
    "list_mental_models": "列出心智模型",
    "create_mental_model": "创建心智模型",
    "get_mental_model": "获取心智模型",
    "update_mental_model": "更新心智模型",
    "delete_mental_model": "删除心智模型",
    "refresh_mental_model": "刷新心智模型",
    "clear_mental_model": "清空心智模型正文",
    "get_mental_model_history": "心智模型历史",
    "get_knowledge_base_tree": "获取知识库树",
    "create_knowledge_folder": "创建知识库目录",
    "create_knowledge_page": "创建知识库页面",
    "get_knowledge_page": "读取知识库页面",
    "search_knowledge_base": "搜索知识库页面",
    "export_knowledge_base": "导出知识库",
    "update_knowledge_node": "更新知识库节点",
    "delete_knowledge_node": "删除知识库节点",
    "list_operations": "列出异步操作",
    "get_operation": "获取异步操作",
    "cancel_operation": "取消异步操作",
    "retry_operation": "重试异步操作",
    "list_banks": "列出 Banks",
    "create_or_update_bank": "创建或更新 Bank",
    "update_bank": "更新 Bank",
    "delete_bank": "删除 Bank",
    "get_bank_config": "获取 Bank 配置",
    "update_bank_config": "更新 Bank 配置",
    "reset_bank_config": "重置 Bank 配置",
    "trigger_consolidation": "触发 Consolidation",
    "recover_consolidation": "恢复 Consolidation",
    "test_bank_llm": "测试 Bank LLM",
    "clear_observations": "清除 Observations",
    "get_bank_profile": "获取 Bank Profile",
    "update_bank_disposition": "更新 Disposition",
    "add_bank_background": "添加 Bank Background",
    "get_agent_stats": "Agent 统计",
    "get_memories_timeseries": "记忆时序统计",
    "health_endpoint_health_get": "健康检查",
    "get_version": "服务版本",
    "metrics_endpoint_metrics_get": "Prometheus 指标",
}

SKIP_PARAMS = {"authorization"}
MAX_DEPTH = 20

FIELD_DESCRIPTION_FALLBACKS = {
    "loc": "发生校验错误的位置路径；数组元素可以是字段名或索引。",
    "kind": "节点类型：`folder` 或 `page`。",
}


def slugify(text: str) -> str:
    s = re.sub(r"[^\w\s\-]", "", (text or "").strip().lower())
    s = re.sub(r"[\s_]+", "-", s)
    return s.strip("-") or "x"


def resolve_ref(schemas: dict, ref: str) -> tuple[str | None, dict | None]:
    if not ref or not str(ref).startswith("#/components/schemas/"):
        return None, None
    name = str(ref).split("/")[-1]
    return name, schemas.get(name)


def unwrap(schema: dict | None) -> tuple[dict, bool]:
    if not schema:
        return {}, False
    if "anyOf" in schema:
        non_null = [s for s in schema["anyOf"] if not (isinstance(s, dict) and s.get("type") == "null")]
        has_null = len(non_null) != len(schema["anyOf"])
        if len(non_null) == 1 and isinstance(non_null[0], dict):
            return non_null[0], has_null
    return schema, False


def type_str(schemas: dict, schema: dict | None, depth: int = 0) -> str:
    if not schema:
        return "any"
    if "$ref" in schema:
        name, _ = resolve_ref(schemas, schema["$ref"])
        return name or "ref"
    core, nullable = unwrap(schema)
    if "$ref" in core:
        name, _ = resolve_ref(schemas, core["$ref"])
        base = name or "ref"
        return f"{base}?" if nullable else base
    if "anyOf" in core:
        return " | ".join(type_str(schemas, s, depth + 1) for s in core["anyOf"])
    if "oneOf" in core:
        return " | ".join(type_str(schemas, s, depth + 1) for s in core["oneOf"])
    t = core.get("type")
    if t == "array":
        item = type_str(schemas, core.get("items") or {}, depth + 1)
        base = f"array<{item}>"
        return f"{base}?" if nullable else base
    if t == "object":
        if core.get("additionalProperties") is not None and not core.get("properties"):
            ap = core["additionalProperties"]
            base = "object" if ap is True else f"map<string, {type_str(schemas, ap, depth + 1)}>"
        else:
            base = core.get("title") or "object"
        return f"{base}?" if nullable else base
    if t == "string" and "enum" in core:
        vals = core["enum"]
        base = " | ".join(json.dumps(v, ensure_ascii=False) for v in vals) if len(vals) <= 8 else f"enum({len(vals)})"
        return f"{base}?" if nullable else base
    if t:
        fmt = core.get("format")
        base = f"{t}({fmt})" if fmt else t
        return f"{base}?" if nullable else base
    if "enum" in core:
        return " | ".join(json.dumps(v, ensure_ascii=False) for v in core["enum"][:8])
    if "const" in core:
        return f"const {json.dumps(core['const'], ensure_ascii=False)}"
    return "any"


def constraints(schema: dict) -> str:
    bits = []
    if "default" in schema:
        bits.append(f"默认 `{json.dumps(schema['default'], ensure_ascii=False)}`")
    if "minimum" in schema:
        bits.append(f"≥ `{schema['minimum']}`")
    if "maximum" in schema:
        bits.append(f"≤ `{schema['maximum']}`")
    if "minLength" in schema:
        bits.append(f"minLen `{schema['minLength']}`")
    if "maxLength" in schema:
        bits.append(f"maxLen `{schema['maxLength']}`")
    if "minItems" in schema:
        bits.append(f"minItems `{schema['minItems']}`")
    if "maxItems" in schema:
        bits.append(f"maxItems `{schema['maxItems']}`")
    if "pattern" in schema:
        bits.append(f"pattern `{schema['pattern']}`")
    return " · ".join(bits)


def one_line(text: str | None, limit: int | None = None) -> str:
    s = re.sub(r"\s+", " ", (text or "").strip())
    if limit is not None and len(s) > limit:
        return s[: limit - 1].rstrip() + "…"
    return s


def cell(text: str) -> str:
    return (text or "").replace("|", "\\|").replace("\n", " ")


def iter_properties(schemas: dict, schema: dict | None) -> tuple[list[tuple[str, dict]], set[str], str | None]:
    if not schema:
        return [], set(), None
    name = None
    if "$ref" in schema:
        name, schema = resolve_ref(schemas, schema["$ref"])
        if not schema:
            return [], set(), name
    core, _ = unwrap(schema)
    if "$ref" in core:
        name, core = resolve_ref(schemas, core["$ref"])
        if not core:
            return [], set(), name

    props: dict[str, dict] = {}
    required: set[str] = set(core.get("required") or [])
    if "allOf" in core:
        for part in core["allOf"]:
            p_props, p_req, _ = iter_properties(schemas, part)
            for k, v in p_props:
                props[k] = v
            required |= p_req
        props.update(core.get("properties") or {})
        required |= set(core.get("required") or [])
    else:
        props = dict(core.get("properties") or {})
        required = set(core.get("required") or [])
    return list(props.items()), required, name


def example_from_schema(
    schemas: dict,
    schema: dict | None,
    depth: int = 0,
    stack: set[str] | None = None,
) -> Any:
    stack = stack or set()
    if not schema or depth > 4:
        return None
    if "example" in schema:
        return schema["example"]
    if "examples" in schema and isinstance(schema["examples"], list) and schema["examples"]:
        return schema["examples"][0]
    if "$ref" in schema:
        name, resolved = resolve_ref(schemas, schema["$ref"])
        if not resolved or name in stack:
            return f"<{name or 'ref'}>"
        stack = set(stack)
        stack.add(name or "")
        return example_from_schema(schemas, resolved, depth, stack)
    core, _ = unwrap(schema)
    if "$ref" in core:
        return example_from_schema(schemas, core, depth, stack)
    if "example" in core:
        return core["example"]
    if "default" in core:
        return core["default"]
    if "enum" in core and core["enum"]:
        return core["enum"][0]
    t = core.get("type")
    if t == "object" or core.get("properties") or "allOf" in core:
        props, required, _ = iter_properties(schemas, core)
        props = [(n, s) for n, s in props if not (isinstance(s, dict) and s.get("deprecated"))]
        obj: dict[str, Any] = {}
        chosen: list[tuple[str, dict]] = []
        req_names = set(required)
        for n, ps in props:
            if n in req_names:
                chosen.append((n, ps))
        for n, ps in props:
            if n not in req_names:
                chosen.append((n, ps))
        for n, ps in chosen:
            obj[n] = example_from_schema(schemas, ps, depth + 1, stack)
        return obj
    if t == "array":
        item = example_from_schema(schemas, core.get("items") or {}, depth + 1, stack)
        return [item] if item is not None else []
    if t == "integer":
        return core.get("minimum", 0)
    if t == "number":
        return 0
    if t == "boolean":
        return False
    if t == "string":
        fmt = core.get("format")
        if fmt == "date-time":
            return "2026-01-01T00:00:00Z"
        if fmt == "uuid":
            return "00000000-0000-0000-0000-000000000000"
        if fmt == "date":
            return "2026-01-01"
        return "string"
    if core.get("additionalProperties") is not None:
        return {}
    return None


def render_fields(
    schemas: dict,
    schema: dict | None,
    *,
    depth: int = 0,
    seen_refs: set[str] | None = None,
    max_depth: int = MAX_DEPTH,
) -> list[str]:
    seen_refs = seen_refs or set()
    lines: list[str] = []
    props, required, resolved_name = iter_properties(schemas, schema)
    props = [(n, s) for n, s in props if not (isinstance(s, dict) and s.get("deprecated"))]
    if not props:
        core, _ = unwrap(schema or {})
        if "$ref" in (schema or {}):
            core = schema or {}
        if "$ref" in core:
            _, core = resolve_ref(schemas, core["$ref"])
            core = core or {}
        if core.get("type") == "array":
            item = core.get("items") or {}
            t = type_str(schemas, item)
            lines.append(f"数组元素类型：`{t}`")
            item_props, _, item_name = iter_properties(schemas, item)
            if item_props and depth < max_depth:
                if item_name and item_name in seen_refs:
                    lines.append(f"（`{item_name}` 已在上方展开，此处不重复）")
                    return lines
                if item_name:
                    seen_refs = set(seen_refs)
                    seen_refs.add(item_name)
                lines.append("")
                lines.append("**元素字段**" + (f" `{item_name}`" if item_name else ""))
                lines.extend(
                    render_fields(
                        schemas,
                        item,
                        depth=depth + 1,
                        seen_refs=seen_refs,
                        max_depth=max_depth,
                    )
                )
            return lines
        t = type_str(schemas, schema)
        if t and t != "any":
            lines.append(f"类型：`{t}`")
        else:
            lines.append("_无展开字段（标量、自由 object 或未声明 properties）_")
        return lines

    if resolved_name and depth > 0:
        lines += [f"数据结构 `{resolved_name}`：", ""]

    lines += [
        "| 字段 | 类型 | 必填 | 说明 |",
        "| --- | --- | --- | --- |",
    ]
    nested_blocks: list[tuple[str, dict, str | None]] = []

    for fname, fsch in props:
        core, nullable = unwrap(fsch or {})
        desc = one_line((fsch or {}).get("description") or core.get("description"))
        if not desc:
            desc = FIELD_DESCRIPTION_FALLBACKS.get(fname, "")
        cons = constraints(core) or constraints(fsch or {})
        if cons:
            desc = f"{desc} · {cons}" if desc else cons
        typ = type_str(schemas, fsch)
        req = "是" if fname in required and not nullable else "否"
        if "example" in (fsch or {}):
            desc = (desc + " · " if desc else "") + (f"例 `{json.dumps((fsch or {})['example'], ensure_ascii=False)}`")
        elif "example" in core:
            desc = (desc + " · " if desc else "") + (f"例 `{json.dumps(core['example'], ensure_ascii=False)}`")
        lines.append(f"| `{fname}` | `{cell(typ)}` | {req} | {cell(desc)} |")

        if depth < max_depth:
            target = core
            item_name = None
            if "$ref" in target:
                item_name, _ = resolve_ref(schemas, target["$ref"])
                nested_blocks.append((fname, target, item_name))
            elif target.get("type") == "array" and isinstance(target.get("items"), dict):
                items = target["items"]
                if "$ref" in items or items.get("properties") or items.get("allOf"):
                    if "$ref" in items:
                        item_name, _ = resolve_ref(schemas, items["$ref"])
                    nested_blocks.append((fname + "[]", items, item_name))
            elif target.get("properties") or target.get("allOf"):
                nested_blocks.append((fname, target, target.get("title")))

    for fname, target, model_name in nested_blocks:
        if model_name and model_name in seen_refs:
            lines += [
                "",
                f"<details><summary>嵌套 <code>{fname}</code> → <code>{model_name}</code>"
                f"（已展开过，跳过）</summary></details>",
            ]
            continue
        local_seen = set(seen_refs)
        if model_name:
            local_seen.add(model_name)
        lines += [
            "",
            f"<details open><summary><strong>{fname}</strong>"
            + (f" · <code>{model_name}</code>" if model_name else "")
            + "</summary>",
            "",
        ]
        lines.extend(
            render_fields(
                schemas,
                target,
                depth=depth + 1,
                seen_refs=local_seen,
                max_depth=max_depth,
            )
        )
        lines += ["", "</details>"]
    return lines


def collect_ops(spec: dict):
    by = defaultdict(list)
    for path, methods in sorted((spec.get("paths") or {}).items()):
        for method, op in methods.items():
            if method.startswith("x-") or not isinstance(op, dict):
                continue
            if op.get("deprecated") is True:
                continue
            tags = op.get("tags") or ["(untagged)"]
            tag = tags[0]
            if tag in HIDDEN_TAGS:
                continue
            by[tag].append((method.upper(), path, op))
    return by


def get_body(op: dict) -> tuple[str | None, dict | None, bool]:
    body = op.get("requestBody")
    if not body:
        return None, None, False
    content = body.get("content") or {}
    for ct in (
        "application/json",
        "multipart/form-data",
        "application/x-www-form-urlencoded",
        "text/plain",
        "application/octet-stream",
    ):
        if ct in content:
            return ct, content[ct].get("schema"), bool(body.get("required"))
    if content:
        ct = next(iter(content))
        return ct, content[ct].get("schema"), bool(body.get("required"))
    return None, None, bool(body.get("required"))


def op_title(op: dict) -> str:
    oid = op.get("operationId") or ""
    if oid in OP_TITLE_ZH:
        return OP_TITLE_ZH[oid]
    return (op.get("summary") or oid or "operation").strip()


def sample_block(title: str, payload: Any) -> list[str]:
    if payload is None:
        return []
    try:
        body = json.dumps(payload, ensure_ascii=False, indent=2)
    except TypeError:
        return []
    return [f"#### {title}", "", "```json", body, "```", ""]


def generate(spec: dict) -> str:
    schemas = spec.get("components", {}).get("schemas", {})
    ops_by_tag = collect_ops(spec)
    ordered_tags = [t for t in TAG_ORDER if t in ops_by_tag and t not in HIDDEN_TAGS] + sorted(
        t for t in ops_by_tag if t not in TAG_ORDER and t not in HIDDEN_TAGS
    )
    total_ops = sum(len(v) for v in ops_by_tag.values())
    info = spec.get("info") or {}
    title = info.get("title") or "Hindsight HTTP API"
    version = info.get("version") or ""
    desc = one_line(info.get("description") or "HTTP API for Hindsight", 300)

    out: list[str] = []
    out += [
        f"# {title}",
        "",
        "> Hindsight 线上托管版 HTTP API  ",
        f"> 版本 `{version}` · **{total_ops}** 个接口 · **{len(ordered_tags)}** 个分组",
        "",
        desc,
        "",
        "---",
        "",
        "## 目录",
        "",
        "- [快速开始](#快速开始)",
        "- [按模块浏览](#按模块浏览)",
        "- [接口索引](#接口索引)",
        "- [接口详解](#接口详解)",
        "",
        "---",
        "",
        "## 快速开始",
        "",
        "### 认证与常用请求头",
        "",
        "调用需携带：",
        "",
        "```http",
        "Authorization: Bearer <token>",
        "Content-Type: application/json   # 有 JSON 请求体时",
        "```",
        "",
        "`Authorization` **必填**。有 JSON 请求体时还需 `Content-Type: application/json`。",
        "",
        "### 接入地址",
        "",
        "```http",
        HOSTED_BASE_URL,
        "```",
        "",
        "接口表中的路径直接拼接在该地址后。例如：",
        "",
        "```http",
        f"{HOSTED_BASE_URL}/v1/default/banks/{{bank_id}}/memories/recall",
        "```",
        "",
        "通用路径前缀为 `/v1/default/banks/{bank_id}/...`。",
        "",
        "### 错误",
        "",
        "| 状态 | 含义 |",
        "| --- | --- |",
        "| `422` | 参数或请求体校验失败 |",
        "| `400` | 业务参数不合法 |",
        "| `401` / `403` | 认证 / 授权 |",
        "| `404` | 不存在 |",
        "| `409` | 冲突 |",
        "",
        "### 异步 operation",
        "",
        "`retain(async)`、`refresh` mental model、创建 knowledge page 等会返回 `operation_id` → 到 **Operations** 查询。",
        "",
        "### 关于 operationId",
        "",
        "每个接口有唯一 `operationId`，便于在工单、日志与客户端代码里引用。",
        "",
        "---",
        "",
        "## 按模块浏览",
        "",
        "| 模块 | 说明 | 接口数 | 简介 |",
        "| --- | --- | ---: | --- |",
    ]
    for t in ordered_tags:
        out.append(f"| [{t}](#{slugify(t)}) | {TAG_ZH.get(t, t)} | {len(ops_by_tag[t])} | {TAG_INTRO.get(t, '')} |")

    out += [
        "",
        "## 接口索引",
        "",
        "| 模块 | 方法 | 路径 | 标题 | operationId |",
        "| --- | --- | --- | --- | --- |",
    ]
    for t in ordered_tags:
        for method, path, op in ops_by_tag[t]:
            oid = op.get("operationId") or ""
            out.append(f"| {t} | `{method}` | `{path}` | [{cell(op_title(op))}](#{slugify(oid)}) | `{oid}` |")

    out += ["", "---", "", "## 接口详解", ""]

    for t in ordered_tags:
        zh = TAG_ZH.get(t, t)
        out += [
            f"## {t}",
            f'<a id="{slugify(t)}"></a>',
            "",
            f"**{zh}** · {len(ops_by_tag[t])} endpoints",
            "",
            TAG_INTRO.get(t, ""),
            "",
            "### 本章目录",
            "",
            "| Method | Path | 标题 |",
            "| --- | --- | --- |",
        ]
        for method, path, op in ops_by_tag[t]:
            oid = op.get("operationId") or slugify(path)
            out.append(f"| `{method}` | `{path}` | [{cell(op_title(op))}](#{slugify(oid)}) |")
        out.append("")

        for method, path, op in ops_by_tag[t]:
            oid = op.get("operationId") or f"{method.lower()}-{slugify(path)}"
            title_zh = op_title(op)
            summary = (op.get("summary") or "").strip()
            description = (op.get("description") or "").strip()

            out += [
                f"### {title_zh}",
                f'<a id="{slugify(oid)}"></a>',
                "",
                f"**{method}** `{path}`",
                "",
            ]
            if summary and summary not in title_zh:
                out += [f"*{summary}*", ""]
            if description:
                out += [description, ""]

            all_params = [p for p in (op.get("parameters") or []) if not p.get("deprecated")]
            path_query = [p for p in all_params if p.get("in") in {"path", "query"}]
            header_params = [p for p in all_params if p.get("in") == "header"]

            def append_param_rows(plist):
                rows = []
                for p in plist:
                    sch = p.get("schema") or {}
                    desc_p = one_line(p.get("description") or sch.get("description"))
                    cons = constraints(sch)
                    if cons:
                        desc_p = f"{desc_p} · {cons}" if desc_p else cons
                    if "example" in sch:
                        desc_p = (desc_p + " · " if desc_p else "") + (
                            f"例 `{json.dumps(sch['example'], ensure_ascii=False)}`"
                        )
                    # sensible fallbacks for common headers / empty descriptions
                    name = (p.get("name") or "").lower()
                    required = bool(p.get("required"))
                    if name == "authorization":
                        # Hosted SaaS docs: auth is required even if OpenAPI marks it optional
                        required = True
                        desc_p = "Bearer token（线上托管版必填）"
                        display_name = "Authorization"
                        typ = "string"
                    else:
                        display_name = p.get("name")
                        typ = cell(type_str(schemas, sch))
                        if not desc_p:
                            title = sch.get("title")
                            if title:
                                desc_p = str(title)
                    if name != "authorization":
                        pass
                    rows.append(
                        f"| `{display_name}` | {p.get('in')} | `{typ}` | "
                        f"{'是' if required else '否'} | {cell(desc_p)} |"
                    )
                return rows

            if path_query:
                out += [
                    "#### 参数",
                    "",
                    "| 名称 | In | 类型 | 必填 | 说明 |",
                    "| --- | --- | --- | --- | --- |",
                ]
                out.extend(append_param_rows(path_query))
                out.append("")

            # Request headers: OpenAPI header params + Content-Type for JSON bodies
            ct_for_headers, body_schema_for_headers, _ = get_body(op)
            header_rows = append_param_rows(header_params)
            already = {(p.get("name") or "").lower() for p in header_params}
            # Hosted SaaS: require Authorization on API routes even when OpenAPI omits it
            if path.startswith("/v1/") and "authorization" not in already:
                header_rows.insert(
                    0,
                    "| `Authorization` | header | `string` | 是 | Bearer token（线上托管版必填） |",
                )
                already.add("authorization")
            if ct_for_headers and body_schema_for_headers is not None:
                if "content-type" not in already:
                    header_rows.append(f"| `Content-Type` | header | `string` | 是 | 固定 `{ct_for_headers}` |")
            if header_rows:
                out += [
                    "#### 请求头",
                    "",
                    "| 名称 | In | 类型 | 必填 | 说明 |",
                    "| --- | --- | --- | --- | --- |",
                ]
                out.extend(header_rows)
                out.append("")

            ct, body_schema, body_req = get_body(op)
            if body_schema is not None:
                out += [
                    "#### 请求体",
                    "",
                    f"- 格式：`{ct}`",
                    f"- 必填：**{'是' if body_req else '否'}**",
                    "",
                ]
                out.extend(render_fields(schemas, body_schema, depth=0, max_depth=MAX_DEPTH))
                out.append("")
                out.extend(sample_block("请求示例", example_from_schema(schemas, body_schema)))

            for code, response in sorted((op.get("responses") or {}).items()):
                response = response or {}
                resp_desc = response.get("description") or ""
                out += [
                    "#### 响应",
                    "",
                    f"- 状态码：`{code}`" + (f" — {one_line(resp_desc)}" if resp_desc else ""),
                ]
                content = response.get("content") or {}
                if not content:
                    out += ["", "_无响应体_", ""]
                    continue
                for resp_ct, media in content.items():
                    resp_schema = (media or {}).get("schema")
                    out.append(f"- 格式：`{resp_ct}`")
                    if resp_schema is not None:
                        out.append("")
                        out.extend(render_fields(schemas, resp_schema, depth=0, max_depth=MAX_DEPTH))
                        out.append("")
                        out.extend(sample_block("响应示例", example_from_schema(schemas, resp_schema)))
                    else:
                        out += ["", "_无响应体_", ""]

            out += [
                f"`operationId={oid}`",
                "",
                "---",
                "",
            ]

    out += [
        "## 附录",
        "",
        "### 生成与更新",
        "",
        "```bash",
        "./scripts/generate-openapi.sh                 # 从 FastAPI 刷新 openapi.json",
        "python3 scripts/generate-api-reading-md.py    # 生成本阅读文档",
        "```",
        "",
        "### 数据来源",
        "",
        "```text",
        "FastAPI (tags / operation_id / Pydantic models)",
        "  → hindsight-docs/static/openapi.json",
        "  → scripts/generate-api-reading-md.py",
        "  → HINDSIGHT_HTTP_API.md",
        "```",
        "",
        f"*Generated from `{title}` `{version}` · {total_ops} operations · "
        f"nested depth ≤ {MAX_DEPTH}; samples include required + optional fields when available.*",
        "",
    ]
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--openapi", type=Path, default=Path("hindsight-docs/static/openapi.json"))
    parser.add_argument("--output", type=Path, default=Path("HINDSIGHT_HTTP_API.md"))
    args = parser.parse_args()
    text = generate(json.loads(args.openapi.read_text()))
    args.output.write_text(text)
    print(f"Wrote {args.output} ({text.count(chr(10)) + 1} lines, {args.output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
