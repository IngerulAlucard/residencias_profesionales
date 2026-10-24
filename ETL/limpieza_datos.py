"""Limpieza inicial y segura de los CSV de clientes, licencias y transacciones.
No modifica los CSV originales. Genera archivos preparados, un archivo de
relaciones revisables y un reporte de datos que requieren atención.
"""


from __future__ import annotations

import csv
import re
import unicodedata
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

BASE = Path(__file__).resolve().parent
FUENTES = BASE / "project_sources"
SALIDA = BASE / "datos_limpios"


def leer_csv(nombre: str) -> list[dict[str, str]]:
    with (FUENTES / nombre).open("r", encoding="utf-8-sig", newline="") as archivo:
        return [
            {clave: (valor or "").strip() for clave, valor in fila.items()}
            for fila in csv.DictReader(archivo)
        ]


def guardar_csv(ruta: Path, filas: list[dict[str, object]]) -> None:
    if not filas:
        return
    with ruta.open("w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)


def normalizar_correo(valor: str) -> str:
    return valor.strip().casefold()


def clave_nombre(valor: str) -> str:
    """Normaliza para comparar nombres; no cambia el nombre mostrado."""
    sin_acentos = unicodedata.normalize("NFKD", valor)
    sin_acentos = "".join(c for c in sin_acentos if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", sin_acentos.casefold())


def convertir_fecha(valor: str) -> tuple[str, str]:
    """Devuelve fecha ISO y observación; deja vacías las fechas ambiguas."""
    valor = valor.strip()
    if not valor:
        return "", "fecha vacía"
    try:
        return date.fromisoformat(valor).isoformat(), ""
    except ValueError:
        pass

    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", valor)
    if not m:
        return "", "formato de fecha no reconocido"
    a, b, anio = map(int, m.groups())
    if a > 12 and b <= 12:  # DD/MM/AAAA inequívoco
        dia, mes = a, b
    elif b > 12 and a <= 12:  # MM/DD/AAAA inequívoco
        mes, dia = a, b
    elif a <= 12 and b <= 12:
        return "", "fecha ambigua: requiere confirmar día y mes"
    else:
        return "", "fecha inválida"
    try:
        return date(anio, mes, dia).isoformat(), ""
    except ValueError:
        return "", "fecha inválida"


def convertir_importe(valor: str) -> tuple[str, str]:
    """Acepta números con coma de miles y punto decimal; no adivina otros formatos."""
    original = valor.strip()
    if not original:
        return "", "importe vacío"
    limpio = original.replace("$", "").replace(" ", "")
    if not re.fullmatch(r"\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?", limpio):
        return "", "formato de importe no reconocido"
    try:
        return format(Decimal(limpio.replace(",", "")), ".2f"), ""
    except InvalidOperation:
        return "", "importe inválido"


def registrar(reporte: list[dict[str, str]], archivo: str, fila: str,
              campo: str, valor: str, problema: str) -> None:
    reporte.append({"archivo": archivo, "registro_origen": fila,
                    "campo": campo, "valor_original": valor,
                    "observacion": problema})


def limpiar_campos(filas: list[dict[str, str]], archivo: str,
                   campos_fecha: list[str], campos_importe: list[str],
                   reporte: list[dict[str, str]]) -> list[dict[str, object]]:
    resultado: list[dict[str, object]] = []
    for fila in filas:
        nuevo: dict[str, object] = dict(fila)  # conserva columnas originales limpias de espacios
        identificador = (fila.get("id_cliente") or fila.get("id_licencia")
                         or fila.get("id_transaccion") or "")
        for campo in campos_fecha:
            valor, aviso = convertir_fecha(fila.get(campo, ""))
            nuevo[campo + "_normalizada"] = valor
            if aviso:
                registrar(reporte, archivo, identificador, campo,
                          fila.get(campo, ""), aviso)
        for campo in campos_importe:
            valor, aviso = convertir_importe(fila.get(campo, ""))
            nuevo[campo + "_numerico"] = valor
            if aviso:
                registrar(reporte, archivo, identificador, campo,
                          fila.get(campo, ""), aviso)
        resultado.append(nuevo)
    return resultado


def duplicados(filas: list[dict[str, str]], campo: str) -> set[str]:
    conteo: dict[str, int] = {}
    for fila in filas:
        valor = fila.get(campo, "").strip().casefold()
        if valor:
            conteo[valor] = conteo.get(valor, 0) + 1
    return {valor for valor, cantidad in conteo.items() if cantidad > 1}


def main() -> None:
    SALIDA.mkdir(exist_ok=True)
    reporte: list[dict[str, str]] = []
    clientes = leer_csv("04-clientes.csv")
    licencias = leer_csv("05-licencias.csv")
    transacciones = leer_csv("06-transacciones.csv")

    # Correos: quitar espacios y uniformar mayúsculas/minúsculas para comparar.
    for fila in clientes:
        fila["correo"] = normalizar_correo(fila.get("correo", ""))
    for fila in transacciones:
        fila["cliente_email"] = normalizar_correo(fila.get("cliente_email", ""))

    clientes_limpios = limpiar_campos(clientes, "clientes.csv", ["fecha_registro"], [], reporte)
    licencias_limpias = limpiar_campos(
        licencias, "licencias.csv",
        ["fecha_compra", "fecha_inicio", "fecha_vencimiento"], ["precio"], reporte)
    transacciones_limpias = limpiar_campos(
        transacciones, "transacciones.csv", ["fecha_transaccion"], ["monto"], reporte)

    # Claves de cliente que son únicas; si un correo/nombre corresponde a varios,
    # no se asigna automáticamente y queda para revisión.
    por_correo: dict[str, list[str]] = {}
    por_nombre: dict[str, list[str]] = {}
    for fila in clientes:
        cid = fila["id_cliente"]
        correo = fila.get("correo", "")
        if correo:
            por_correo.setdefault(correo, []).append(cid)
        for campo in ("empresa", "razon_social"):
            llave = clave_nombre(fila.get(campo, ""))
            if llave:
                por_nombre.setdefault(llave, []).append(cid)

    relaciones_transacciones: list[dict[str, str]] = []
    for fila in transacciones:
        email = fila.get("cliente_email", "")
        ids = sorted(set(por_correo.get(email, []))) if email else []
        cid = ids[0] if len(ids) == 1 else ""
        if not cid:
            registrar(reporte, "transacciones.csv", fila.get("id_transaccion", ""),
                      "cliente_email", email,
                      "correo vacío, sin coincidencia o asociado a más de un cliente")
        relaciones_transacciones.append({
            "id_transaccion": fila.get("id_transaccion", ""),
            "id_cliente_sugerido": cid,
            "cliente_email": email,
            "resultado": "coincidencia única" if cid else "revisar"
        })

    relaciones_licencias: list[dict[str, str]] = []
    for fila in licencias:
        llave = clave_nombre(fila.get("cliente", ""))
        ids = sorted(set(por_nombre.get(llave, []))) if llave else []
        cid = ids[0] if len(ids) == 1 else ""
        if not cid:
            registrar(reporte, "licencias.csv", fila.get("id_licencia", ""),
                      "cliente", fila.get("cliente", ""),
                      "nombre vacío, sin coincidencia exacta normalizada o ambiguo; revisar equivalencia")
        relaciones_licencias.append({
            "id_licencia": fila.get("id_licencia", ""),
            "id_cliente_sugerido": cid,
            "cliente_origen": fila.get("cliente", ""),
            "resultado": "coincidencia única" if cid else "revisar"
        })

    # Reportar campos vacíos y claves que deben revisarse; no borrar filas.
    for nombre, filas, campos in [
        ("clientes.csv", clientes, ["telefono", "estado"]),
        ("licencias.csv", licencias, ["cliente"]),
        ("transacciones.csv", transacciones, ["cliente_email"]),
    ]:
        for campo in campos:
            for fila in filas:
                if not fila.get(campo, ""):
                    ident = fila.get("id_cliente") or fila.get("id_licencia") or fila.get("id_transaccion", "")
                    registrar(reporte, nombre, ident, campo, "", "dato faltante; no se completó automáticamente")

    for nombre, filas, clave in [
        ("clientes.csv", clientes, "correo"),
        ("transacciones.csv", transacciones, "folio"),
    ]:
        repetidos = duplicados(filas, clave)
        for fila in filas:
            if fila.get(clave, "").strip().casefold() in repetidos:
                ident = fila.get("id_cliente") or fila.get("id_transaccion", "")
                registrar(reporte, nombre, ident, clave, fila.get(clave, ""),
                          "valor repetido; revisar antes de decidir si es duplicado real")

    guardar_csv(SALIDA / "clientes_limpios.csv", clientes_limpios)
    guardar_csv(SALIDA / "licencias_limpias.csv", licencias_limpias)
    guardar_csv(SALIDA / "transacciones_limpias.csv", transacciones_limpias)
    guardar_csv(SALIDA / "relacion_licencias_clientes.csv", relaciones_licencias)
    guardar_csv(SALIDA / "relacion_transacciones_clientes.csv", relaciones_transacciones)
    guardar_csv(SALIDA / "reporte_revision.csv", reporte or [{
        "archivo": "", "registro_origen": "", "campo": "", "valor_original": "", "observacion": "sin excepciones"
    }])
    print(f"Listo. Se generaron archivos en: {SALIDA}")
    print(f"Excepciones para revisar: {len(reporte)} (consulta reporte_revision.csv)")


if __name__ == "__main__":
    main()
