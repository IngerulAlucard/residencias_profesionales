-- Esquema para los CSV limpios de SYSTEMKW.
-- Datos simulados; lectura pública y solo lectura para el prototipo estático.
-- No usar estas políticas con información real o confidencial.

create table if not exists public.clientes (
  id_cliente text primary key,
  nombre_cliente text,
  razon_social text,
  rfc text,
  correo text,
  telefono text,
  empresa text,
  estado text,
  fecha_registro text,
  telefono_original text,
  fecha_registro_normalizada date
);

create table if not exists public.licencias (
  id_licencia text primary key,
  cliente text,
  producto text,
  tipo_licencia text,
  numero_licencias text,
  fecha_compra text,
  fecha_inicio text,
  fecha_vencimiento text,
  precio text,
  estatus text,
  fecha_compra_normalizada date,
  fecha_inicio_normalizada date,
  fecha_vencimiento_normalizada date,
  precio_numerico numeric(16,2)
);

create table if not exists public.transacciones (
  id_transaccion text primary key,
  cliente_email text,
  folio text,
  producto text,
  cantidad text,
  monto text,
  metodo_pago text,
  fecha_transaccion text,
  estado_pago text,
  vendedor text,
  fecha_transaccion_normalizada date,
  monto_numerico numeric(16,2)
);

create table if not exists public.relacion_licencias_clientes (
  id_licencia text primary key references public.licencias(id_licencia) on delete cascade,
  id_cliente_sugerido text references public.clientes(id_cliente) on delete set null,
  cliente_origen text,
  resultado text
);

create table if not exists public.relacion_transacciones_clientes (
  id_transaccion text primary key references public.transacciones(id_transaccion) on delete cascade,
  id_cliente_sugerido text references public.clientes(id_cliente) on delete set null,
  cliente_email text,
  resultado text
);

alter table public.clientes enable row level security;
alter table public.licencias enable row level security;
alter table public.transacciones enable row level security;
alter table public.relacion_licencias_clientes enable row level security;
alter table public.relacion_transacciones_clientes enable row level security;

revoke all on public.clientes, public.licencias, public.transacciones,
  public.relacion_licencias_clientes, public.relacion_transacciones_clientes
  from anon, authenticated;
grant usage on schema public to anon;
grant select on public.clientes, public.licencias, public.transacciones,
  public.relacion_licencias_clientes, public.relacion_transacciones_clientes to anon;

drop policy if exists "demo_read_clientes" on public.clientes;
create policy "demo_read_clientes" on public.clientes for select to anon using (true);
drop policy if exists "demo_read_licencias" on public.licencias;
create policy "demo_read_licencias" on public.licencias for select to anon using (true);
drop policy if exists "demo_read_transacciones" on public.transacciones;
create policy "demo_read_transacciones" on public.transacciones for select to anon using (true);
drop policy if exists "demo_read_relacion_licencias" on public.relacion_licencias_clientes;
create policy "demo_read_relacion_licencias" on public.relacion_licencias_clientes for select to anon using (true);
drop policy if exists "demo_read_relacion_transacciones" on public.relacion_transacciones_clientes;
create policy "demo_read_relacion_transacciones" on public.relacion_transacciones_clientes for select to anon using (true);
