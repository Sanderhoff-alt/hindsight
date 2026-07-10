-- Key creation and permission replacement previously used several independent
-- PostgREST writes. Keep the key row and both scope levels in one transaction so
-- a failed restriction cannot leave the prior, broader scope active.
create or replace function replace_hindsight_api_key_permissions(
  p_api_key_id uuid,
  p_org_id text,
  p_allowed_operations jsonb,
  p_operation_scopes jsonb
)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  update hindsight_api_keys
  set allowed_operations = p_allowed_operations
  where id = p_api_key_id
    and org_id = p_org_id
    and revoked_at is null;

  if not found then
    raise exception 'Active API key not found';
  end if;

  delete from hindsight_api_key_operation_bank_scopes
  where api_key_id = p_api_key_id;

  delete from hindsight_api_key_operation_scopes
  where api_key_id = p_api_key_id;

  insert into hindsight_api_key_operation_scopes (
    api_key_id,
    operation,
    bank_scope_mode
  )
  select
    p_api_key_id,
    scope.operation,
    scope.bank_scope_mode
  from jsonb_to_recordset(coalesce(p_operation_scopes, '[]'::jsonb)) as scope(
    operation text,
    bank_scope_mode text,
    bank_scopes jsonb
  )
  where scope.operation <> 'create_bank';

  insert into hindsight_api_key_operation_bank_scopes (
    api_key_id,
    operation,
    bank_id,
    bank_internal_id
  )
  select
    p_api_key_id,
    scope.operation,
    bank.bank_id,
    bank.bank_internal_id
  from jsonb_to_recordset(coalesce(p_operation_scopes, '[]'::jsonb)) as scope(
    operation text,
    bank_scope_mode text,
    bank_scopes jsonb
  )
  cross join lateral jsonb_to_recordset(coalesce(scope.bank_scopes, '[]'::jsonb)) as bank(
    bank_id text,
    bank_internal_id text
  )
  where scope.operation <> 'create_bank'
    and scope.bank_scope_mode = 'selected';
end;
$$;

create or replace function create_hindsight_api_key(
  p_org_id text,
  p_created_by_user_id uuid,
  p_name text,
  p_key_hash text,
  p_encrypted_key text,
  p_role organization_role,
  p_allowed_operations jsonb,
  p_operation_scopes jsonb
)
returns table(id uuid)
language plpgsql
security definer
set search_path = public
as $$
declare
  new_api_key_id uuid;
begin
  insert into hindsight_api_keys (
    org_id,
    created_by_user_id,
    name,
    key_hash,
    encrypted_key,
    role,
    allowed_operations
  )
  values (
    p_org_id,
    p_created_by_user_id,
    p_name,
    p_key_hash,
    p_encrypted_key,
    p_role,
    p_allowed_operations
  )
  returning hindsight_api_keys.id into new_api_key_id;

  perform replace_hindsight_api_key_permissions(
    new_api_key_id,
    p_org_id,
    p_allowed_operations,
    p_operation_scopes
  );

  return query select new_api_key_id;
end;
$$;

revoke all on function replace_hindsight_api_key_permissions(uuid, text, jsonb, jsonb) from public;
revoke all on function create_hindsight_api_key(text, uuid, text, text, text, organization_role, jsonb, jsonb) from public;
grant execute on function replace_hindsight_api_key_permissions(uuid, text, jsonb, jsonb) to service_role;
grant execute on function create_hindsight_api_key(text, uuid, text, text, text, organization_role, jsonb, jsonb) to service_role;
