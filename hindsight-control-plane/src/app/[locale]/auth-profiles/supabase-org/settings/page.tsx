"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Copy, KeyRound, Plus, RefreshCw, Save, Trash2, UserPlus } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { withBasePath } from "@/lib/base-path";

type Role = "owner" | "admin" | "member";

interface Organization {
  id: string;
  name: string;
  role: Role;
}

interface Member {
  org_id: string;
  user_id: string;
  email?: string;
  role: Role;
}

interface Invite {
  id: string;
  email: string;
  role: Role;
  expires_at: string;
  accepted_at?: string | null;
  revoked_at?: string | null;
}

interface ApiKeySummary {
  id: string;
  name: string;
  allowed_operations?: string[] | null;
  bank_scope_mode?: "all" | "selected";
  scoped_bank_ids?: string[];
  revoked_at?: string | null;
  created_at: string;
  can_view_secret?: boolean;
}

interface BankSummary {
  bank_id?: string;
  id?: string;
  name?: string;
}

interface VersionInfo {
  features?: {
    auth_provider?: string;
    profile_match?: boolean;
  };
}

const API_BASE = "/api/auth-profiles/supabase-org";
const READ_OPERATIONS = [
  "get_bank_config",
  "get_bank_profile",
  "get_bank_stats",
  "get_chunk",
  "get_directive",
  "get_document",
  "get_entity",
  "get_entity_graph",
  "get_entity_state",
  "get_graph_data",
  "get_memories_timeseries",
  "get_memory_unit",
  "get_observation_history",
  "get_operation_status",
  "list_directives",
  "list_document_chunks",
  "list_documents",
  "list_entities",
  "list_memory_units",
  "list_mental_models",
  "list_mental_model_tags",
  "list_observation_scopes",
  "list_operations",
  "list_tags",
  "list_webhook_deliveries",
  "list_webhooks",
  "recall",
  "reflect",
] as const;
const WRITE_OPERATIONS = [
  "cancel_operation",
  "clear_mental_model",
  "clear_observations",
  "clear_observations_for_memory",
  "create_directive",
  "create_mental_model",
  "create_webhook",
  "delete_bank",
  "delete_directive",
  "delete_document",
  "delete_mental_model",
  "delete_webhook",
  "merge_bank_mission",
  "reprocess_document",
  "reset_bank_config",
  "retain",
  "retry_operation",
  "retry_failed_consolidation",
  "run_consolidation",
  "set_bank_mission",
  "submit_async_consolidation",
  "submit_async_graph_maintenance",
  "update_bank",
  "update_bank_config",
  "update_bank_disposition",
  "update_directive",
  "update_document",
  "update_memory_unit",
  "update_mental_model",
  "update_webhook",
] as const;
const MEMBER_WRITE_OPERATIONS = [
  "create_mental_model",
  "retain",
  "update_document",
  "update_memory_unit",
  "update_mental_model",
] as const;
type ApiKeyOperationName = (typeof READ_OPERATIONS)[number] | (typeof WRITE_OPERATIONS)[number];
const COPY: Record<string, string> = {
  organizationSettings: "Organization settings",
  noOrganizationSelected: "No organization selected",
  selectOrganization: "Select organization",
  organizationName: "Organization name",
  newOrganization: "New organization",
  inviteLinkCreated: "Invite link created",
  inviteLinkOneTime:
    "Copy this link now. It is only shown after creation and will not be available after you leave or refresh this page.",
  apiKeys: "API keys",
  keyName: "Key name",
  allAllowedOperations: "All allowed operations",
};

export default function SettingsPage() {
  const t = (key: string) => COPY[key] || key;
  const router = useRouter();
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [selectedOrgId, setSelectedOrgId] = useState("");
  const [members, setMembers] = useState<Member[]>([]);
  const [invites, setInvites] = useState<Invite[]>([]);
  const [apiKeys, setApiKeys] = useState<ApiKeySummary[]>([]);
  const [banks, setBanks] = useState<BankSummary[]>([]);
  const [orgName, setOrgName] = useState("");
  const [newOrgName, setNewOrgName] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<Role>("member");
  const [apiKeyName, setApiKeyName] = useState("");
  const [apiKeyOperations, setApiKeyOperations] = useState<ApiKeyOperationName[]>([]);
  const [apiKeyBankScopeMode, setApiKeyBankScopeMode] = useState<"all" | "selected">("all");
  const [apiKeyBankIds, setApiKeyBankIds] = useState<string[]>([]);
  const [newInviteLink, setNewInviteLink] = useState<string | null>(null);
  const [newApiKey, setNewApiKey] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const currentOrg = useMemo(
    () => organizations.find((organization) => organization.id === selectedOrgId),
    [organizations, selectedOrgId]
  );
  const canAdmin = currentOrg?.role === "owner" || currentOrg?.role === "admin";
  const canOwner = currentOrg?.role === "owner";
  const availableApiKeyOperations = useMemo(
    () =>
      currentOrg?.role === "member"
        ? [...READ_OPERATIONS, ...MEMBER_WRITE_OPERATIONS]
        : [...READ_OPERATIONS, ...WRITE_OPERATIONS],
    [currentOrg?.role]
  );

  async function loadAll() {
    setLoading(true);
    try {
      const version = await fetchJson<VersionInfo>("/api/version");
      if (
        version.features?.auth_provider !== "supabase_org" ||
        version.features?.profile_match === false
      ) {
        router.replace("/dashboard");
        return;
      }

      const me = await fetchJson<{
        organizations: Organization[];
        current: { org_id: string; role: Role } | null;
      }>(`${API_BASE}/me`);
      setOrganizations(me.organizations);
      const nextOrgId = me.current?.org_id || me.organizations[0]?.id || "";
      setSelectedOrgId(nextOrgId);
      setOrgName(
        me.organizations.find((organization) => organization.id === nextOrgId)?.name || ""
      );
      const [team, inviteList, keyList, bankList] = await Promise.all([
        fetchJson<{ members: Member[] }>(`${API_BASE}/team`),
        fetchJson<{ invites: Invite[] }>(`${API_BASE}/team/invites`),
        fetchJson<{ api_keys: ApiKeySummary[] }>(`${API_BASE}/api-keys`),
        fetchJson<{ banks: BankSummary[] }>("/api/banks"),
      ]);
      setMembers(team.members);
      setInvites(inviteList.invites);
      setApiKeys(keyList.api_keys);
      setBanks(bankList.banks || []);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to load settings");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  useEffect(() => {
    setApiKeyOperations((operations) =>
      operations.length === 0
        ? [...availableApiKeyOperations]
        : operations.filter((operation) => availableApiKeyOperations.includes(operation))
    );
  }, [availableApiKeyOperations]);

  async function createOrg(event: FormEvent) {
    event.preventDefault();
    const response = await fetchJson<{ organization: Organization }>(`${API_BASE}/organizations`, {
      method: "POST",
      body: JSON.stringify({ name: newOrgName }),
    });
    setNewOrgName("");
    setOrganizations((items) => [...items, { ...response.organization, role: "owner" }]);
    await selectOrganization(response.organization.id);
    toast.success("Organization created");
  }

  async function selectOrganization(orgId: string) {
    await fetchJson(`${API_BASE}/auth/select-org`, {
      method: "POST",
      body: JSON.stringify({ org_id: orgId }),
    });
    setSelectedOrgId(orgId);
    setOrgName(organizations.find((organization) => organization.id === orgId)?.name || "");
    await loadAll();
  }

  async function renameOrganization(event: FormEvent) {
    event.preventDefault();
    if (!selectedOrgId) return;
    const response = await fetchJson<{ organization: Organization }>(
      `${API_BASE}/organizations/${encodeURIComponent(selectedOrgId)}`,
      {
        method: "PATCH",
        body: JSON.stringify({ name: orgName }),
      }
    );
    setOrganizations((items) =>
      items.map((item) =>
        item.id === response.organization.id ? { ...item, name: response.organization.name } : item
      )
    );
    setOrgName(response.organization.name);
    toast.success("Organization updated");
  }

  async function inviteMember(event: FormEvent) {
    event.preventDefault();
    const response = await fetchJson<{ invite: { invite_url: string } }>(
      `${API_BASE}/team/invites`,
      {
        method: "POST",
        body: JSON.stringify({ email: inviteEmail, role: inviteRole }),
      }
    );
    setInviteEmail("");
    setNewInviteLink(response.invite.invite_url);
    try {
      await navigator.clipboard.writeText(response.invite.invite_url);
      toast.success("Invite link copied");
    } catch {
      toast.success("Invite link created");
    }
    await loadAll();
  }

  async function updateMember(userId: string, role: Role) {
    await fetchJson(`${API_BASE}/team/members/${encodeURIComponent(userId)}`, {
      method: "PATCH",
      body: JSON.stringify({ role }),
    });
    await loadAll();
  }

  async function removeMember(userId: string) {
    await fetchJson(`${API_BASE}/team/members/${encodeURIComponent(userId)}`, { method: "DELETE" });
    await loadAll();
  }

  async function createApiKey(event: FormEvent) {
    event.preventDefault();
    const response = await fetchJson<{ api_key: { key: string } }>(`${API_BASE}/api-keys`, {
      method: "POST",
      body: JSON.stringify({
        name: apiKeyName,
        allowed_operations: apiKeyOperations,
        bank_scope_mode: apiKeyBankScopeMode,
        bank_ids: apiKeyBankScopeMode === "selected" ? apiKeyBankIds : null,
      }),
    });
    setApiKeyName("");
    setApiKeyOperations([...availableApiKeyOperations]);
    setApiKeyBankScopeMode("all");
    setApiKeyBankIds([]);
    setNewApiKey(response.api_key.key);
    await loadAll();
  }

  function toggleApiKeyOperation(operation: ApiKeyOperationName, checked: boolean) {
    setApiKeyOperations((operations) =>
      checked
        ? Array.from(new Set([...operations, operation]))
        : operations.filter((item) => item !== operation)
    );
  }

  function toggleApiKeyBank(bankId: string, checked: boolean) {
    setApiKeyBankIds((bankIds) =>
      checked
        ? Array.from(new Set([...bankIds, bankId]))
        : bankIds.filter((item) => item !== bankId)
    );
  }

  async function revokeApiKey(id: string) {
    await fetchJson(`${API_BASE}/api-keys/${encodeURIComponent(id)}`, { method: "DELETE" });
    await loadAll();
  }

  async function copyApiKey(id: string) {
    const response = await fetchJson<{ api_key: { key: string } }>(
      `${API_BASE}/api-keys/${encodeURIComponent(id)}`
    );
    await navigator.clipboard.writeText(response.api_key.key);
    toast.success("API key copied");
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">{t("organizationSettings")}</h1>
            <p className="text-sm text-muted-foreground">
              {currentOrg?.name || t("noOrganizationSelected")}
            </p>
          </div>
          <Button variant="outline" onClick={() => router.push("/dashboard")}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Dashboard
          </Button>
        </div>

        <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
          <Card>
            <CardHeader>
              <h2 className="text-lg font-medium">Organizations</h2>
            </CardHeader>
            <CardContent className="space-y-4">
              <Select value={selectedOrgId} onValueChange={selectOrganization}>
                <SelectTrigger>
                  <SelectValue placeholder={t("selectOrganization")} />
                </SelectTrigger>
                <SelectContent>
                  {organizations.map((organization) => (
                    <SelectItem key={organization.id} value={organization.id}>
                      {organization.name} ({organization.role})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <form className="flex gap-2" onSubmit={renameOrganization}>
                <Input
                  value={orgName}
                  onChange={(event) => setOrgName(event.target.value)}
                  placeholder={t("organizationName")}
                  disabled={!canOwner}
                />
                <Button
                  type="submit"
                  size="icon"
                  disabled={!canOwner || !orgName.trim() || orgName.trim() === currentOrg?.name}
                >
                  <Save className="h-4 w-4" />
                </Button>
              </form>
              <form className="flex gap-2" onSubmit={createOrg}>
                <Input
                  value={newOrgName}
                  onChange={(event) => setNewOrgName(event.target.value)}
                  placeholder={t("newOrganization")}
                />
                <Button type="submit" size="icon" disabled={!newOrgName.trim()}>
                  <Plus className="h-4 w-4" />
                </Button>
              </form>
              <Button variant="outline" className="w-full" onClick={loadAll} disabled={loading}>
                <RefreshCw className="mr-2 h-4 w-4" />
                Refresh
              </Button>
            </CardContent>
          </Card>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <h2 className="text-lg font-medium">Team</h2>
              </CardHeader>
              <CardContent className="space-y-4">
                {canAdmin && (
                  <form
                    className="grid gap-2 md:grid-cols-[1fr_150px_auto]"
                    onSubmit={inviteMember}
                  >
                    <Input
                      type="email"
                      value={inviteEmail}
                      onChange={(event) => setInviteEmail(event.target.value)}
                      placeholder="Email"
                    />
                    <Select
                      value={inviteRole}
                      onValueChange={(value) => setInviteRole(value as Role)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="member">member</SelectItem>
                        <SelectItem value="admin">admin</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button type="submit" disabled={!inviteEmail.trim()}>
                      <UserPlus className="mr-2 h-4 w-4" />
                      Invite
                    </Button>
                  </form>
                )}

                {newInviteLink && (
                  <div className="space-y-2 rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-950">
                    <div className="font-medium">{t("inviteLinkCreated")}</div>
                    <p>{t("inviteLinkOneTime")}</p>
                    <div className="flex items-center gap-2">
                      <code className="min-w-0 flex-1 truncate">{newInviteLink}</code>
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => navigator.clipboard.writeText(newInviteLink)}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                )}

                <div className="divide-y rounded-md border">
                  {members.map((member) => (
                    <div
                      key={member.user_id}
                      className="grid gap-3 p-3 md:grid-cols-[1fr_150px_auto] md:items-center"
                    >
                      <div>
                        <div className="font-medium">{member.email || member.user_id}</div>
                        <div className="text-xs text-muted-foreground">{member.user_id}</div>
                      </div>
                      <Select
                        value={member.role}
                        disabled={!canOwner}
                        onValueChange={(value) => updateMember(member.user_id, value as Role)}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="owner">owner</SelectItem>
                          <SelectItem value="admin">admin</SelectItem>
                          <SelectItem value="member">member</SelectItem>
                        </SelectContent>
                      </Select>
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={!canOwner}
                        onClick={() => removeMember(member.user_id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>

                {invites.length > 0 && (
                  <div className="space-y-2">
                    <h3 className="text-sm font-medium">Invites</h3>
                    {invites.map((invite) => (
                      <div
                        key={invite.id}
                        className="flex items-center justify-between rounded-md border p-3 text-sm"
                      >
                        <span>
                          {invite.email} ({invite.role})
                        </span>
                        <span className="text-muted-foreground">
                          {invite.revoked_at
                            ? "revoked"
                            : invite.accepted_at
                              ? "accepted"
                              : "pending"}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <h2 className="text-lg font-medium">{t("apiKeys")}</h2>
              </CardHeader>
              <CardContent className="space-y-4">
                <form className="space-y-3" onSubmit={createApiKey}>
                  <div className="grid gap-2 md:grid-cols-[1fr_auto]">
                    <Input
                      value={apiKeyName}
                      onChange={(event) => setApiKeyName(event.target.value)}
                      placeholder={t("keyName")}
                    />
                    <Button
                      type="submit"
                      disabled={!apiKeyName.trim() || apiKeyOperations.length === 0}
                    >
                      <KeyRound className="mr-2 h-4 w-4" />
                      Create
                    </Button>
                  </div>
                  <div className="rounded-md border p-3">
                    <div className="mb-2 flex items-center justify-between gap-2">
                      <span className="text-sm font-medium">Operations</span>
                      <div className="flex gap-1">
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => setApiKeyOperations([...availableApiKeyOperations])}
                        >
                          All allowed
                        </Button>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => setApiKeyOperations([])}
                        >
                          None
                        </Button>
                      </div>
                    </div>
                    <div className="grid max-h-56 gap-2 overflow-y-auto pr-1 md:grid-cols-2">
                      {availableApiKeyOperations.map((operation) => (
                        <label key={operation} className="flex min-w-0 items-center gap-2 text-sm">
                          <Checkbox
                            checked={apiKeyOperations.includes(operation)}
                            onCheckedChange={(checked) =>
                              toggleApiKeyOperation(operation, checked === true)
                            }
                          />
                          <span className="truncate">{operation}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                  <div className="rounded-md border p-3">
                    <div className="mb-2 flex items-center justify-between gap-2">
                      <span className="text-sm font-medium">Banks</span>
                      <Select
                        value={apiKeyBankScopeMode}
                        onValueChange={(value) =>
                          setApiKeyBankScopeMode(value as "all" | "selected")
                        }
                      >
                        <SelectTrigger className="w-36">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All banks</SelectItem>
                          <SelectItem value="selected">Selected</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    {apiKeyBankScopeMode === "selected" && (
                      <div className="grid max-h-40 gap-2 overflow-y-auto pr-1 md:grid-cols-2">
                        {banks.length === 0 ? (
                          <span className="text-sm text-muted-foreground">No banks yet</span>
                        ) : (
                          banks.map((bank) => {
                            const bankId = bank.bank_id || bank.id || "";
                            if (!bankId) return null;
                            return (
                              <label
                                key={bankId}
                                className="flex min-w-0 items-center gap-2 text-sm"
                              >
                                <Checkbox
                                  checked={apiKeyBankIds.includes(bankId)}
                                  onCheckedChange={(checked) =>
                                    toggleApiKeyBank(bankId, checked === true)
                                  }
                                />
                                <span className="truncate">{bank.name || bankId}</span>
                              </label>
                            );
                          })
                        )}
                      </div>
                    )}
                  </div>
                </form>
                {newApiKey && (
                  <div className="flex items-center gap-2 rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-950">
                    <code className="min-w-0 flex-1 truncate">{newApiKey}</code>
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={() => navigator.clipboard.writeText(newApiKey)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                )}
                <div className="divide-y rounded-md border">
                  {apiKeys.map((apiKey) => (
                    <div
                      key={apiKey.id}
                      className="grid gap-3 p-3 md:grid-cols-[1fr_160px_auto] md:items-center"
                    >
                      <div>
                        <div className="font-medium">{apiKey.name}</div>
                        <div className="text-xs text-muted-foreground">
                          {apiKey.allowed_operations?.length
                            ? `${apiKey.allowed_operations.length} operations`
                            : t("allAllowedOperations")}
                          {" · "}
                          {apiKey.bank_scope_mode === "selected"
                            ? `${apiKey.scoped_bank_ids?.length ?? 0} banks`
                            : "all banks"}
                        </div>
                      </div>
                      <span className="text-sm text-muted-foreground">
                        {apiKey.revoked_at ? "revoked" : "active"}
                      </span>
                      <div className="flex justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          disabled={!apiKey.can_view_secret || Boolean(apiKey.revoked_at)}
                          onClick={() => copyApiKey(apiKey.id)}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          disabled={Boolean(apiKey.revoked_at)}
                          onClick={() => revokeApiKey(apiKey.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </main>
  );
}

async function fetchJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(withBasePath(path), {
    ...init,
    headers: { "Content-Type": "application/json", ...init.headers },
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) throw new Error(data?.error || `Request failed: ${response.status}`);
  return data as T;
}
