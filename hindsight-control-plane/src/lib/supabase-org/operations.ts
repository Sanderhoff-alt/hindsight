import { OPERATION_UI_GROUPS } from "@/lib/supabase-org/operation-ui";

export type ApiKeyOperation = string;
export type OperationAction = "read" | "write";
export type OperationSource = "bank_read" | "bank_write" | "special_bank" | "unscoped";
export type OperationScope = "bank" | "unscoped";

export interface OperationDefinition {
  name: ApiKeyOperation;
  source: OperationSource;
  action: OperationAction;
  scope: OperationScope;
}

export interface OperationSection {
  id: string;
  labelKey: string;
  label: string;
  operations: readonly ApiKeyOperation[];
}

export interface OperationGroup {
  id: string;
  labelKey: string;
  label: string;
  bankScoped: boolean;
  operations: readonly ApiKeyOperation[];
  sections?: readonly OperationSection[];
}

const BANK_READ_OPERATION_NAMES = [
  "get_bank_config",
  "get_bank_profile",
  "get_bank_stats",
  "list_directives",
  "get_directive",
  "get_memories_timeseries",
  "get_memory_unit",
  "list_memory_units",
  "list_observation_scopes",
  "get_observation_history",
  "list_tags",
  "get_document",
  "list_documents",
  "list_document_chunks",
  "get_chunk",
  "list_mental_models",
  "list_mental_model_tags",
  "list_entities",
  "get_entity",
  "get_entity_state",
  "get_entity_graph",
  "get_graph_data",
  "list_operations",
  "get_operation_status",
  "list_webhooks",
  "list_webhook_deliveries",
] as const satisfies readonly ApiKeyOperation[];

const BANK_WRITE_OPERATION_NAMES = [
  "update_bank",
  "update_bank_config",
  "update_bank_disposition",
  "set_bank_mission",
  "merge_bank_mission",
  "reset_bank_config",
  "delete_bank",
  "create_directive",
  "update_directive",
  "delete_directive",
  "update_memory_unit",
  "submit_async_consolidation",
  "retry_failed_consolidation",
  "clear_observations",
  "clear_observations_for_memory",
  "update_document",
  "delete_document",
  "reprocess_document",
  "create_mental_model",
  "update_mental_model",
  "delete_mental_model",
  "clear_mental_model",
  "submit_async_graph_maintenance",
  "cancel_operation",
  "retry_operation",
  "create_webhook",
  "update_webhook",
  "delete_webhook",
] as const satisfies readonly ApiKeyOperation[];

const SPECIAL_BANK_OPERATION_DEFINITIONS = [
  { name: "recall", source: "special_bank", action: "read", scope: "bank" },
  { name: "reflect", source: "special_bank", action: "read", scope: "bank" },
  { name: "retain", source: "special_bank", action: "write", scope: "bank" },
  { name: "consolidate", source: "special_bank", action: "write", scope: "bank" },
  { name: "mental_model_get", source: "special_bank", action: "read", scope: "bank" },
  { name: "mental_model_refresh", source: "special_bank", action: "write", scope: "bank" },
] as const satisfies readonly OperationDefinition[];

const UNSCOPED_OPERATION_DEFINITIONS = [
  { name: "create_bank", source: "unscoped", action: "write", scope: "unscoped" },
] as const satisfies readonly OperationDefinition[];

function definitionsForSource(
  names: readonly ApiKeyOperation[],
  source: Extract<OperationSource, "bank_read" | "bank_write">,
  action: OperationAction
): OperationDefinition[] {
  return names.map((name) => ({ name, source, action, scope: "bank" }));
}

const operationDefinitions: OperationDefinition[] = [
  ...definitionsForSource(BANK_READ_OPERATION_NAMES, "bank_read", "read"),
  ...definitionsForSource(BANK_WRITE_OPERATION_NAMES, "bank_write", "write"),
  ...SPECIAL_BANK_OPERATION_DEFINITIONS,
  ...UNSCOPED_OPERATION_DEFINITIONS,
];

export const OPERATION_DEFINITIONS = operationDefinitions;
export const BANK_READ_OPERATIONS = operationDefinitions
  .filter((operation) => operation.source === "bank_read")
  .map((operation) => operation.name);
export const BANK_WRITE_OPERATIONS = operationDefinitions
  .filter((operation) => operation.source === "bank_write")
  .map((operation) => operation.name);
export const SPECIAL_BANK_OPERATIONS = operationDefinitions
  .filter((operation) => operation.source === "special_bank")
  .map((operation) => operation.name);
export const UNSCOPED_DATAPLANE_OPERATIONS = operationDefinitions
  .filter((operation) => operation.scope === "unscoped")
  .map((operation) => operation.name);
export const BANK_SCOPED_OPERATIONS = operationDefinitions
  .filter((operation) => operation.scope === "bank")
  .map((operation) => operation.name);
export const API_KEY_OPERATIONS = operationDefinitions.map((operation) => operation.name);

export const OPERATION_ACTIONS = Object.fromEntries(
  operationDefinitions.map((operation) => [operation.name, operation.action])
) as Record<ApiKeyOperation, OperationAction>;

export const OPERATION_GROUPS: OperationGroup[] = OPERATION_UI_GROUPS.map((group) => {
  const sections = group.sections?.map((section) => ({
    id: section.id,
    labelKey: section.labelKey,
    label: section.defaultLabel,
    operations: section.operations,
  }));
  return {
    id: group.id,
    labelKey: group.labelKey,
    label: group.defaultLabel,
    bankScoped: group.bankScoped,
    operations: group.operations,
    sections,
  };
});
