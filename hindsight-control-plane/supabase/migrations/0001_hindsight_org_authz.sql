create table if not exists organizations (
  id text primary key,
  name text not null,
  config jsonb not null default '{}',
  created_at timestamptz not null default now()
);

do $$
begin
  if not exists (select 1 from pg_type where typname = 'organization_role') then
    create type organization_role as enum ('owner', 'admin', 'member');
  end if;
end $$;

create table if not exists organization_members (
  org_id text not null references organizations(id) on delete cascade,
  user_id uuid not null,
  email text,
  role organization_role not null,
  created_at timestamptz not null default now(),
  primary key (org_id, user_id)
);

create table if not exists organization_invites (
  id uuid primary key default gen_random_uuid(),
  org_id text not null references organizations(id) on delete cascade,
  email text not null,
  role organization_role not null default 'member',
  token_hash text not null unique,
  expires_at timestamptz not null,
  accepted_at timestamptz,
  revoked_at timestamptz,
  created_by_user_id uuid not null,
  created_at timestamptz not null default now()
);

create table if not exists hindsight_api_keys (
  id uuid primary key default gen_random_uuid(),
  org_id text not null references organizations(id) on delete cascade,
  created_by_user_id uuid,
  name text not null,
  key_hash text not null unique,
  encrypted_key text,
  role organization_role not null default 'member',
  allowed_operations jsonb,
  expires_at timestamptz,
  revoked_at timestamptz,
  created_at timestamptz not null default now()
);

alter table hindsight_api_keys add column if not exists encrypted_key text;

create table if not exists hindsight_api_key_operation_scopes (
  api_key_id uuid not null references hindsight_api_keys(id) on delete cascade,
  operation text not null,
  bank_scope_mode text not null default 'all' check (bank_scope_mode in ('all', 'selected')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (api_key_id, operation)
);

create table if not exists hindsight_api_key_operation_bank_scopes (
  api_key_id uuid not null,
  operation text not null,
  bank_id text not null,
  bank_internal_id text not null,
  primary key (api_key_id, operation, bank_internal_id),
  foreign key (api_key_id, operation)
    references hindsight_api_key_operation_scopes(api_key_id, operation)
    on delete cascade
);

create table if not exists hindsight_api_key_created_banks (
  api_key_id uuid not null references hindsight_api_keys(id) on delete cascade,
  bank_id text not null,
  bank_internal_id text not null,
  created_at timestamptz not null default now(),
  primary key (api_key_id, bank_internal_id)
);

create index if not exists organization_members_user_id_idx on organization_members(user_id);
create index if not exists organization_invites_org_id_idx on organization_invites(org_id);
create index if not exists hindsight_api_keys_org_id_idx on hindsight_api_keys(org_id);
create index if not exists hindsight_api_key_operation_bank_scopes_bank_id_idx on hindsight_api_key_operation_bank_scopes(bank_id);
create index if not exists hindsight_api_key_operation_bank_scopes_bank_internal_id_idx on hindsight_api_key_operation_bank_scopes(bank_internal_id);
create index if not exists hindsight_api_key_created_banks_bank_id_idx on hindsight_api_key_created_banks(bank_id);
create index if not exists hindsight_api_key_created_banks_bank_internal_id_idx on hindsight_api_key_created_banks(bank_internal_id);

alter table organizations enable row level security;
alter table organization_members enable row level security;
alter table organization_invites enable row level security;
alter table hindsight_api_keys enable row level security;
alter table hindsight_api_key_operation_scopes enable row level security;
alter table hindsight_api_key_operation_bank_scopes enable row level security;
alter table hindsight_api_key_created_banks enable row level security;

grant usage on type organization_role to anon, authenticated, service_role;

grant select on organizations to anon, authenticated;
grant select on organization_members to anon, authenticated;
grant select on organization_invites to anon, authenticated;
grant select on hindsight_api_keys to anon, authenticated;
grant select on hindsight_api_key_operation_scopes to anon, authenticated;
grant select on hindsight_api_key_operation_bank_scopes to anon, authenticated;
grant select on hindsight_api_key_created_banks to anon, authenticated;

grant all on organizations to service_role;
grant all on organization_members to service_role;
grant all on organization_invites to service_role;
grant all on hindsight_api_keys to service_role;
grant all on hindsight_api_key_operation_scopes to service_role;
grant all on hindsight_api_key_operation_bank_scopes to service_role;
grant all on hindsight_api_key_created_banks to service_role;
