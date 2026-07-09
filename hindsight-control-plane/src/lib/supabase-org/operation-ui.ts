type ApiKeyOperation = string;

export interface OperationUiSection {
  id: string;
  labelKey: string;
  defaultLabel: string;
  operations: readonly ApiKeyOperation[];
}

export interface OperationUiGroup {
  id: string;
  labelKey: string;
  defaultLabel: string;
  bankScoped: boolean;
  operations: readonly ApiKeyOperation[];
  sections?: readonly OperationUiSection[];
}

export const OPERATION_UI_GROUPS: readonly OperationUiGroup[] = [
  {
    id: "bank_management",
    labelKey: "authProfiles.supabaseOrg.operations.groups.bankManagement",
    defaultLabel: "Bank management",
    bankScoped: true,
    operations: [
      "get_bank_config",
      "get_bank_profile",
      "get_bank_stats",
      "update_bank",
      "update_bank_config",
      "update_bank_disposition",
      "set_bank_mission",
      "merge_bank_mission",
      "reset_bank_config",
      "delete_bank",
      "list_directives",
      "get_directive",
      "create_directive",
      "update_directive",
      "delete_directive",
    ],
  },
  {
    id: "memory_knowledge",
    labelKey: "authProfiles.supabaseOrg.operations.groups.memoryKnowledge",
    defaultLabel: "Memory & knowledge",
    bankScoped: true,
    operations: [
      "retain",
      "recall",
      "reflect",
      "get_memories_timeseries",
      "get_memory_unit",
      "list_memory_units",
      "update_memory_unit",
      "get_document",
      "list_documents",
      "update_document",
      "delete_document",
      "list_document_chunks",
      "get_chunk",
      "reprocess_document",
      "list_tags",
      "list_mental_models",
      "list_mental_model_tags",
      "mental_model_get",
      "mental_model_refresh",
      "create_mental_model",
      "update_mental_model",
      "delete_mental_model",
      "clear_mental_model",
      "list_entities",
      "get_entity",
      "get_entity_state",
      "get_entity_graph",
      "get_graph_data",
      "list_observation_scopes",
      "get_observation_history",
      "clear_observations",
      "clear_observations_for_memory",
      "submit_async_graph_maintenance",
      "consolidate",
      "submit_async_consolidation",
      "retry_failed_consolidation",
    ],
    sections: [
      {
        id: "memory_access",
        labelKey: "authProfiles.supabaseOrg.operations.sections.memoryAccess",
        defaultLabel: "Memory access",
        operations: [
          "retain",
          "recall",
          "reflect",
          "get_memories_timeseries",
          "get_memory_unit",
          "list_memory_units",
          "update_memory_unit",
          "consolidate",
          "submit_async_consolidation",
          "retry_failed_consolidation",
          "list_observation_scopes",
          "get_observation_history",
          "clear_observations",
          "clear_observations_for_memory",
          "list_tags",
        ],
      },
      {
        id: "documents",
        labelKey: "authProfiles.supabaseOrg.operations.sections.documents",
        defaultLabel: "Documents",
        operations: [
          "get_document",
          "list_documents",
          "update_document",
          "delete_document",
          "list_document_chunks",
          "get_chunk",
          "reprocess_document",
        ],
      },
      {
        id: "mental_models",
        labelKey: "authProfiles.supabaseOrg.operations.sections.mentalModels",
        defaultLabel: "Mental models",
        operations: [
          "list_mental_models",
          "list_mental_model_tags",
          "mental_model_get",
          "mental_model_refresh",
          "create_mental_model",
          "update_mental_model",
          "delete_mental_model",
          "clear_mental_model",
        ],
      },
      {
        id: "knowledge_graph",
        labelKey: "authProfiles.supabaseOrg.operations.sections.knowledgeGraph",
        defaultLabel: "Knowledge graph",
        operations: [
          "list_entities",
          "get_entity",
          "get_entity_state",
          "get_entity_graph",
          "get_graph_data",
          "submit_async_graph_maintenance",
        ],
      },
    ],
  },
  {
    id: "operation_control",
    labelKey: "authProfiles.supabaseOrg.operations.groups.operationControl",
    defaultLabel: "Operation control",
    bankScoped: true,
    operations: ["list_operations", "get_operation_status", "cancel_operation", "retry_operation"],
  },
  {
    id: "automation",
    labelKey: "authProfiles.supabaseOrg.operations.groups.automation",
    defaultLabel: "Automation",
    bankScoped: true,
    operations: [
      "list_webhooks",
      "list_webhook_deliveries",
      "create_webhook",
      "update_webhook",
      "delete_webhook",
    ],
  },
  {
    id: "key_level",
    labelKey: "authProfiles.supabaseOrg.operations.groups.createBank",
    defaultLabel: "Create bank",
    bankScoped: false,
    operations: ["create_bank"],
  },
];
