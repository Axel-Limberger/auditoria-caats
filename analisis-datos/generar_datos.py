"""Genera el conjunto de datos sintético de la práctica de CAATs de análisis de datos.

Empresa ficticia: "Yerbatera del Alto Paraná S.A." (Misiones), ejercicio 2025.
Archivos generados en ./datos/:
    empleados.csv, proveedores.csv, facturas.csv, pagos.csv

Los datos contienen errores de calidad y anomalías plantadas a propósito.
Con --clave se guarda además datos/clave_respuestas.json (solo para el docente).

Uso:
    docker compose run --rm datos python generar_datos.py              # semilla por defecto (2025)
    docker compose run --rm datos python generar_datos.py --semilla 7  # otro conjunto (p. ej. uno por grupo)
    docker compose run --rm datos python generar_datos.py --clave      # incluye la clave de respuestas
"""

import argparse
import json
import unicodedata
from datetime import date, datetime, time, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SALIDA = Path(__file__).parent / "datos"
UMBRAL_APROBACION = 500_000  # pagos >= umbral requieren aprobación de gerencia
INICIO, FIN = date(2025, 1, 1), date(2025, 12, 31)

NOMBRES = ["Juan", "María", "Carlos", "Ana", "Jorge", "Laura", "Diego", "Silvia", "Pablo", "Claudia",
           "Ricardo", "Gabriela", "Martín", "Lucía", "Sergio", "Valeria", "Hernán", "Paula", "Raúl",
           "Romina", "Gustavo", "Natalia", "Fernando", "Carolina", "Oscar", "Andrea", "Walter", "Mónica"]
APELLIDOS = ["González", "Rodríguez", "Fernández", "López", "Martínez", "Pérez", "Romero", "Sosa",
             "Álvarez", "Torres", "Ruiz", "Ramírez", "Flores", "Acosta", "Benítez", "Medina", "Suárez",
             "Herrera", "Aguirre", "Pereyra", "Gutiérrez", "Molina", "Silva", "Castro", "Rojas", "Ortiz",
             "Núñez", "Ledesma", "Duarte", "Krause", "Schmidt", "Kowalski", "Olivera", "Báez"]
LOCALIDADES = ["Posadas", "Oberá", "Eldorado", "Apóstoles", "Leandro N. Alem", "Puerto Iguazú",
               "Garupá", "Jardín América", "Montecarlo", "San Vicente"]
CALLES = ["Av. Uruguay", "Av. Mitre", "Félix de Azara", "Bolívar", "Colón", "San Martín", "Sarmiento",
          "Av. Libertad", "Belgrano", "Rivadavia", "Av. Corrientes", "Junín", "Entre Ríos", "Ayacucho"]
RUBROS = ["Transportes", "Ferretería", "Envases", "Servicios Agrícolas", "Insumos", "Maderera",
          "Distribuidora", "Talleres", "Combustibles", "Imprenta", "Limpieza", "Seguridad", "Construcciones",
          "Agroquímicos", "Repuestos", "Electricidad", "Logística", "Consultora"]
SOCIEDADES = ["S.A.", "S.R.L.", "S.A.S.", "S.H."]
BANCOS = ["007", "011", "014", "017", "072", "086", "191", "285"]  # Galicia, Nación, Provincia, ...

rng = np.random.default_rng()


# ---------------------------------------------------------------- utilidades
def sin_acentos(texto):
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()


def dv_cuit(base10):
    pesos = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    resto = 11 - sum(int(d) * p for d, p in zip(base10, pesos)) % 11
    return {11: 0, 10: None}.get(resto, resto)


def nuevo_cuit(prefijo):
    while True:
        base = f"{prefijo}{rng.integers(10_000_000, 45_000_000)}"
        dv = dv_cuit(base)
        if dv is not None:
            return f"{base[:2]}-{base[2:]}-{dv}"


def cuit_invalido(cuit):
    """Mismo CUIT con el dígito verificador alterado (error típico de tipeo)."""
    dv = int(cuit[-1])
    return cuit[:-1] + str((dv + rng.integers(1, 9)) % 10)


def dv_bloque(digitos, pesos):
    return (10 - sum(int(d) * p for d, p in zip(digitos, pesos)) % 10) % 10


def nuevo_cbu():
    b1 = rng.choice(BANCOS) + f"{rng.integers(0, 10_000):04d}"
    b1 += str(dv_bloque(b1, [7, 1, 3, 9, 7, 1, 3]))
    b2 = f"{rng.integers(0, 10**13):013d}"
    b2 += str(dv_bloque(b2, [3, 9, 7, 1, 3, 9, 7, 1, 3, 9, 7, 1, 3]))
    return b1 + b2


def domicilio():
    return f"{rng.choice(CALLES)} {rng.integers(100, 4000)}, {rng.choice(LOCALIDADES)}"


def fecha_al_azar(desde=INICIO, hasta=FIN, habil=True):
    while True:
        f = desde + timedelta(days=int(rng.integers(0, (hasta - desde).days + 1)))
        if not habil or f.weekday() < 5:
            return f


def a_dia_habil(f):
    while f.weekday() >= 5:
        f += timedelta(days=1)
    return f


def hora_habil():
    return time(int(rng.integers(8, 17)), int(rng.integers(0, 60)), int(rng.integers(0, 60)))


# ---------------------------------------------------------------- generación
def generar_empleados(clave):
    areas = (["Compras"] * 5 + ["Tesorería"] * 4 + ["Contaduría"] * 6 + ["Producción"] * 25
             + ["Ventas"] * 10 + ["Sistemas"] * 4 + ["RRHH"] * 4)
    filas, usuarios = [], set()
    for i, area in enumerate(areas, start=1):
        nombre, apellido = rng.choice(NOMBRES), rng.choice(APELLIDOS)
        usuario = sin_acentos(nombre[0] + apellido).lower()
        while usuario in usuarios:
            usuario += str(rng.integers(1, 10))
        usuarios.add(usuario)
        filas.append({
            "legajo": f"E{i:03d}", "apellido": apellido, "nombre": nombre,
            "cuit": nuevo_cuit(rng.choice(["20", "27"])), "cbu": nuevo_cbu(), "domicilio": domicilio(),
            "area": area, "usuario": usuario,
            "fecha_ingreso": fecha_al_azar(date(2008, 1, 1), date(2024, 6, 30)).isoformat(),
            "fecha_baja": None,
        })
    emp = pd.DataFrame(filas)

    # actores de los escenarios de fraude (nombres fijos para que el relato sea claro)
    emp.loc[0, ["apellido", "nombre", "usuario"]] = ["Giménez", "Marcela", "mgimenez"]   # Compras
    emp.loc[5, ["apellido", "nombre", "usuario"]] = ["Benítez", "Diego", "dbenitez"]     # Tesorería
    emp.loc[6, ["apellido", "nombre", "usuario"]] = ["Sosa", "Ricardo", "rsosa"]         # Tesorería
    emp.loc[6, "fecha_baja"] = "2025-06-30"
    for i in rng.choice(range(15, len(emp)), 4, replace=False):
        emp.loc[i, "fecha_baja"] = fecha_al_azar().isoformat()
    clave["usuario_dado_de_baja"] = "rsosa"
    return emp


def generar_proveedores(emp, clave):
    compras = emp.loc[emp.area == "Compras", "usuario"].tolist()
    filas, nombres = [], set()
    for i in range(1, 119):
        while True:
            razon = f"{rng.choice(RUBROS)} {rng.choice(LOCALIDADES)} {rng.choice(SOCIEDADES)}"
            if razon not in nombres:
                break
        nombres.add(razon)
        monotributo = rng.random() < 0.15
        filas.append({
            "id_proveedor": f"P{i:04d}", "razon_social": razon,
            "cuit": nuevo_cuit("20" if monotributo else rng.choice(["30", "33"])),
            "condicion_iva": "Monotributo" if monotributo else "Responsable Inscripto",
            "cbu": nuevo_cbu(), "domicilio": domicilio(),
            "fecha_alta": fecha_al_azar(date(2015, 1, 1), date(2024, 12, 31)).isoformat(),
            "usuario_alta": rng.choice(compras),
        })
    prov = pd.DataFrame(filas)
    mg = emp.set_index("usuario").loc["mgimenez"]
    db = emp.set_index("usuario").loc["dbenitez"]

    # proveedores fantasma
    prov.loc[len(prov)] = ["P0119", "Servicios Integrales del Norte S.R.L.", nuevo_cuit("30"),
                           "Responsable Inscripto", mg.cbu, domicilio(), "2025-03-10", "mgimenez"]
    prov.loc[len(prov)] = ["P0120", "Logística Guaraní S.A.S.", nuevo_cuit("30"),
                           "Responsable Inscripto", nuevo_cbu(), db.domicilio, "2025-05-19", "mgimenez"]
    clave["proveedor_cbu_de_empleado"] = {"P0119": "mgimenez"}
    clave["proveedor_domicilio_de_empleado"] = {"P0120": "dbenitez"}

    # proveedores duplicados: mismo CUIT, razón social escrita distinto
    dup = []
    for idx in rng.choice(range(118), 2, replace=False):
        orig = prov.loc[idx]
        nuevo_id = f"P{len(prov) + 1:04d}"
        razon = "  " + sin_acentos(orig.razon_social).upper().replace(".", "") + " "
        prov.loc[len(prov)] = [nuevo_id, razon, orig.cuit, orig.condicion_iva, orig.cbu,
                               orig.domicilio, fecha_al_azar().isoformat(), rng.choice(compras)]
        dup.append([orig.id_proveedor, nuevo_id])
    clave["proveedores_duplicados_mismo_cuit"] = dup

    # calidad: CUIT con dígito verificador inválido y CUIT faltante
    idx_inv = rng.choice(range(118), 4, replace=False)
    prov.loc[idx_inv, "cuit"] = [cuit_invalido(c) for c in prov.loc[idx_inv, "cuit"]]
    resto = [i for i in range(118) if i not in idx_inv]
    idx_nulo = rng.choice(resto, 3, replace=False)
    prov.loc[idx_nulo, "cuit"] = None
    clave["cuit_dv_invalido"] = prov.loc[idx_inv, "id_proveedor"].tolist()
    clave["cuit_faltante"] = prov.loc[idx_nulo, "id_proveedor"].tolist()

    # calidad: CBU con largo incorrecto
    idx_cbu = rng.choice([i for i in resto if i not in idx_nulo], 2, replace=False)
    prov.loc[idx_cbu, "cbu"] = [c[:-1] for c in prov.loc[idx_cbu, "cbu"]]
    clave["cbu_largo_invalido"] = prov.loc[idx_cbu, "id_proveedor"].tolist()
    return prov


def generar_facturas(emp, prov, clave):
    compras = emp.loc[emp.area == "Compras", "usuario"].tolist()
    legitimos = prov.id_proveedor[:118].tolist()
    peso = rng.lognormal(0, 1.2, len(legitimos))  # pocos proveedores concentran mucho volumen
    peso = np.minimum(peso / peso.sum(), 0.04)
    peso /= peso.sum()
    numeradores = {p: int(rng.integers(1, 3000)) for p in prov.id_proveedor}
    monotributo = set(prov.id_proveedor[prov.condicion_iva == "Monotributo"])

    def factura(id_prov, fecha, neto, usuario, alicuota=0.21):
        numeradores[id_prov] += int(rng.integers(1, 6))
        if id_prov in monotributo:  # factura C: sin IVA discriminado
            alicuota = 0
        neto = round(float(neto), 2)
        iva = round(neto * alicuota, 2)
        return {"id_proveedor": id_prov, "tipo": "C" if id_prov in monotributo else "A", "punto_venta": 2,
                "numero": numeradores[id_prov], "fecha": fecha.isoformat(), "importe_neto": neto,
                "iva": iva, "total": round(neto + iva, 2), "usuario_carga": usuario}

    filas = []
    for _ in range(3000):
        id_prov = rng.choice(legitimos, p=peso)
        neto = rng.lognormal(np.log(90_000), 1.8)
        filas.append(factura(id_prov, fecha_al_azar(), neto, rng.choice(compras),
                             0.105 if rng.random() < 0.1 else 0.21))

    # fantasma 1: montos apenas por debajo del umbral, varios redondos
    fantasma = []
    for i in range(40):
        total = rng.choice([480_000, 490_000]) if i % 5 == 0 else rng.uniform(470_000, 499_900)
        filas.append(factura("P0119", fecha_al_azar(date(2025, 3, 15)), total / 1.21, "mgimenez"))
        fantasma.append(len(filas) - 1)
    for _ in range(20):
        filas.append(factura("P0120", fecha_al_azar(date(2025, 5, 25)),
                             rng.uniform(460_000, 499_000) / 1.21, "mgimenez"))
        fantasma.append(len(filas) - 1)

    # fraccionamiento: un proveedor legítimo, varias facturas el mismo día que juntas superan el umbral
    fracc = legitimos[3]
    for f in [date(2025, 4, 8), date(2025, 9, 16)]:
        for _ in range(3):
            filas.append(factura(fracc, f, rng.uniform(430_000, 495_000) / 1.21, rng.choice(compras)))
    clave["fraccionamiento"] = {"proveedor": fracc, "fechas": ["2025-04-08", "2025-09-16"]}

    fac = pd.DataFrame(filas)
    fac["condicion"] = "pagada"
    n = len(fac)
    estados = rng.choice(["pendiente", "anulada"], size=n, p=[0.75, 0.25])
    marca = rng.random(n) < 0.07
    marca[fantasma] = False
    fac.loc[marca, "condicion"] = estados[marca]
    fac.insert(0, "id_factura", [f"F{i:05d}" for i in range(1, n + 1)])
    fac = fac.rename(columns={"condicion": "estado"})
    fac["fantasma"] = False
    fac.loc[fantasma, "fantasma"] = True

    # factura cargada dos veces (mismo proveedor/tipo/punto de venta/número)
    dups = fac[(fac.estado == "pagada") & ~fac.fantasma].sample(5, random_state=int(rng.integers(1e9)))
    copias = dups.copy()
    copias["id_factura"] = [f"F{i:05d}" for i in range(n + 1, n + 6)]
    copias.iloc[0, copias.columns.get_loc("fecha")] = (
        date.fromisoformat(copias.iloc[0].fecha) + timedelta(days=2)).isoformat()
    fac = pd.concat([fac, copias], ignore_index=True)
    clave["facturas_duplicadas"] = [[a, b] for a, b in zip(dups.id_factura, copias.id_factura)]
    clave["proveedores_fantasma_facturas"] = fac.loc[fac.fantasma, "id_factura"].tolist()
    return fac


def generar_pagos(emp, prov, fac, clave):
    tesoreria = emp[emp.area == "Tesorería"]
    cbu_prov = prov.set_index("id_proveedor").cbu
    activos = [u for u in tesoreria.usuario if u != "rsosa"]
    filas = []
    for f in fac[fac.estado == "pagada"].itertuples():
        fecha = a_dia_habil(date.fromisoformat(f.fecha) + timedelta(days=int(rng.integers(5, 40))))
        if f.id_proveedor == "P0120":
            usuario = "dbenitez"
        elif fecha <= date(2025, 6, 30) and rng.random() < 0.25:
            usuario = "rsosa"
        else:
            usuario = rng.choice(activos)
        filas.append({"id_factura": f.id_factura, "id_proveedor": f.id_proveedor,
                      "fecha_hora": datetime.combine(fecha, hora_habil()), "importe": f.total,
                      "cbu_destino": cbu_prov[f.id_proveedor], "usuario_aprueba": usuario})
    pag = pd.DataFrame(filas)
    normales = pag.index[~pag.id_proveedor.isin(["P0119", "P0120"])
                         & ~pag.id_factura.isin(sum(clave["facturas_duplicadas"], []))]
    usados = set()

    def elegir(k, pool=normales):
        idx = rng.choice([i for i in pool if i not in usados], k, replace=False)
        usados.update(idx)
        return idx

    # segregación de funciones: quien carga la factura del fantasma 1 también aprueba el pago
    sod = pag.index[pag.id_proveedor == "P0119"][:8]
    pag.loc[sod, "usuario_aprueba"] = "mgimenez"

    # pagos fuera de horario / fin de semana del fantasma 2
    raros = pag.index[pag.id_proveedor == "P0120"][:8]
    for i in raros:
        d = pag.loc[i, "fecha_hora"].date()
        if rng.random() < 0.5:
            d += timedelta(days=5 - d.weekday())  # sábado
            h = time(int(rng.integers(9, 13)), int(rng.integers(0, 60)))
        else:
            h = time(int(rng.choice([22, 23, 0, 1])), int(rng.integers(0, 60)))
        pag.loc[i, "fecha_hora"] = datetime.combine(d, h)
    clave["pagos_fuera_de_horario_ids_factura"] = pag.loc[raros, "id_factura"].tolist()

    # aprobados por un usuario después de su baja
    post = elegir(3, [i for i in normales if pag.loc[i, "fecha_hora"].date() > date(2025, 7, 15)])
    pag.loc[post, "usuario_aprueba"] = "rsosa"
    clave["aprobados_tras_baja_ids_factura"] = pag.loc[post, "id_factura"].tolist()

    # pago a un CBU distinto del registrado (uno de ellos, el CBU de un empleado)
    otro = elegir(5)
    pag.loc[otro, "cbu_destino"] = [nuevo_cbu() for _ in range(4)] + [
        emp.set_index("usuario").loc["dbenitez", "cbu"]]
    clave["pago_cbu_distinto_ids_factura"] = pag.loc[otro, "id_factura"].tolist()

    # pago anterior a la fecha de la factura
    fecha_fac = fac.set_index("id_factura").fecha
    antes = elegir(3)
    for i in antes:
        d = date.fromisoformat(fecha_fac[pag.loc[i, "id_factura"]]) - timedelta(days=int(rng.integers(3, 10)))
        pag.loc[i, "fecha_hora"] = datetime.combine(a_dia_habil(d), hora_habil())
    clave["pago_antes_de_factura_ids_factura"] = pag.loc[antes, "id_factura"].tolist()

    # pago mayor al total de la factura
    mayor = elegir(3)
    pag.loc[mayor, "importe"] = (pag.loc[mayor, "importe"] * rng.uniform(1.1, 1.5, 3)).round(2)
    clave["pago_mayor_a_factura_ids_factura"] = pag.loc[mayor, "id_factura"].tolist()

    # misma factura pagada dos veces
    dobles = elegir(4)
    copias = pag.loc[dobles].copy()
    copias["fecha_hora"] = copias.fecha_hora + pd.to_timedelta(rng.integers(7, 30, 4), unit="D")
    copias["fecha_hora"] = [datetime.combine(a_dia_habil(d.date()), d.time()) for d in copias.fecha_hora]
    pag = pd.concat([pag, copias], ignore_index=True)
    clave["factura_pagada_dos_veces"] = copias.id_factura.tolist()

    # pagos a facturas inexistentes (integridad referencial)
    huerfanos = pag.loc[elegir(2)].copy()
    huerfanos["id_factura"] = ["F09991", "F09992"]
    pag = pd.concat([pag, huerfanos], ignore_index=True)
    clave["pagos_a_facturas_inexistentes"] = ["F09991", "F09992"]

    # numeración correlativa de órdenes de pago, con faltantes y un número repetido
    pag = pag.sort_values("fecha_hora", ignore_index=True)
    numeros = np.arange(1, len(pag) + 12)
    faltan = [*rng.choice(range(100, 1000), 4, replace=False), 1500, 1501, 1502]
    numeros = [n for n in numeros if n not in faltan][: len(pag)]
    rep = int(rng.integers(2000, 2500))
    numeros[rep] = numeros[rep - 1]
    pag.insert(0, "nro_orden_pago", [f"OP-{n:06d}" for n in numeros])
    clave["ordenes_de_pago_faltantes"] = [f"OP-{n:06d}" for n in sorted(set(range(1, max(numeros) + 1)) - set(numeros))]
    clave["orden_de_pago_repetida"] = f"OP-{numeros[rep]:06d}"
    baja = pag[(pag.usuario_aprueba == "rsosa") & (pag.fecha_hora >= datetime(2025, 7, 1))]
    clave["aprobados_tras_baja_ids_factura"] = baja.id_factura.tolist()  # incluye copias de pagos duplicados
    pag["fecha_hora"] = pag.fecha_hora.dt.strftime("%Y-%m-%d %H:%M:%S")
    return pag


def ensuciar_facturas(fac, prov, clave):
    """Errores de calidad en facturas (después de generar los pagos, para no afectarlos)."""
    candidatas = fac.index[(fac.estado != "pagada") & ~fac.fantasma].tolist()
    rng.shuffle(candidatas)
    tomar = lambda k: [candidatas.pop() for _ in range(k)]

    idx = tomar(10)  # fechas en formato dd/mm/aaaa
    fac.loc[idx, "fecha"] = [date.fromisoformat(f).strftime("%d/%m/%Y") for f in fac.loc[idx, "fecha"]]
    clave["fecha_formato_distinto"] = fac.loc[idx, "id_factura"].tolist()
    idx = tomar(4)
    fac.loc[idx, "fecha"] = None
    clave["fecha_faltante"] = fac.loc[idx, "id_factura"].tolist()
    idx = tomar(3)
    fac.loc[idx, "fecha"] = ["2026-02-30", "2026-03-11", "2052-07-14"]
    clave["fecha_invalida_o_fuera_de_periodo"] = fac.loc[idx, "id_factura"].tolist()
    idx = tomar(4)
    fac.loc[idx, ["importe_neto", "iva", "total"]] = fac.loc[idx, ["importe_neto", "iva", "total"]] * -1
    fac.loc[idx[0], ["importe_neto", "iva", "total"]] = 0
    clave["importe_negativo_o_cero"] = fac.loc[idx, "id_factura"].tolist()
    idx = tomar(6)
    fac.loc[idx, "total"] = (fac.loc[idx, "total"] + rng.choice([-1000, 100, 9000, -50], 6)).round(2)
    clave["total_distinto_neto_mas_iva"] = fac.loc[idx, "id_factura"].tolist()
    idx = tomar(3)
    fac.loc[idx, "id_proveedor"] = ["P0999", "P0998", "P0999"]
    clave["factura_proveedor_inexistente"] = fac.loc[idx, "id_factura"].tolist()
    return fac.drop(columns="fantasma")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--semilla", type=int, default=2025)
    parser.add_argument("--clave", action="store_true", help="guardar datos/clave_respuestas.json")
    args = parser.parse_args()
    global rng
    rng = np.random.default_rng(args.semilla)

    clave = {"semilla": args.semilla}
    emp = generar_empleados(clave)
    prov = generar_proveedores(emp, clave)
    fac = generar_facturas(emp, prov, clave)
    pag = generar_pagos(emp, prov, fac, clave)
    fac = ensuciar_facturas(fac, prov, clave)

    SALIDA.mkdir(exist_ok=True)
    for nombre, df in [("empleados", emp), ("proveedores", prov), ("facturas", fac), ("pagos", pag)]:
        df.to_csv(SALIDA / f"{nombre}.csv", index=False)
        print(f"{nombre + '.csv':18} {len(df):5d} filas")
    clave_path = SALIDA / "clave_respuestas.json"
    if args.clave:
        clave_path.write_text(json.dumps(clave, indent=2, ensure_ascii=False, default=str))
        print(f"clave de respuestas: {clave_path}")
    else:
        clave_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
