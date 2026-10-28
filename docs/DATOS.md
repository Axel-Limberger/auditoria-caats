# Estaciones 7 y 8 — CAATs de análisis de datos con Python (alternativa libre a ACL / IDEA)

Objetivo

- Aplicar técnicas de auditoría asistidas por computadora sobre **datos del negocio**: evaluar la calidad de una extracción (estación 7) y ejecutar pruebas analíticas sobre el 100% de la población para detectar errores, incumplimientos de controles y posibles fraudes (estación 8).

¿Para qué sirve en la práctica?

- Es la acepción clásica de CAAT en auditoría: lo que se hace con ACL (Diligent) o IDEA (CaseWare), con herramientas libres: **pandas**, **numpy**, **scipy**, **matplotlib** y **JupyterLab**.
- Cada prueba deja una tabla de excepciones exportada a Excel como papel de trabajo, y es **re-ejecutable**: si cambian los datos, se vuelve a correr el notebook.

## Requerimientos

- Docker con `docker compose`. Se usa el servicio `datos` (imagen con Python 3.12, JupyterLab y las bibliotecas de análisis; se construye localmente, ~1,6 GB).
- Preparación del entorno, desde la carpeta raíz del repositorio:

```bash
chmod -R a+rwX analisis-datos          # el contenedor escribe resultados en esta carpeta
docker compose build datos
docker compose run --rm datos python generar_datos.py   # si el docente indicó una semilla: --semilla <n>
```

Para trabajar, levantar JupyterLab y abrir **http://localhost:8888** en el navegador:

```bash
docker compose up -d datos
```

Los notebooks, los datos y los resultados quedan en la carpeta `analisis-datos/` del repositorio: lo que se guarda en JupyterLab se conserva aunque se detenga el contenedor. Al terminar: `docker compose down`.

## El caso

**Yerbatera del Alto Paraná S.A.**, ejercicio 2025. Los archivos de `analisis-datos/datos/` son una extracción del sistema de compras y pagos:

| Archivo | Contenido |
|---|---|
| `empleados.csv` | Legajo, datos personales, CBU de sueldo, área y usuario de sistema |
| `proveedores.csv` | Maestro de proveedores |
| `facturas.csv` | Facturas de compra recibidas |
| `pagos.csv` | Órdenes de pago emitidas |

Las políticas de la empresa relevadas en entrevistas están al comienzo del notebook 2.

## Equivalencias ACL / IDEA → pandas

| ACL | IDEA | pandas |
|---|---|---|
| Verify, Statistics | Field Statistics | `info()`, `describe()`, `isna().sum()` |
| Filter / Extract | Direct Extraction | `df[condición]` |
| Stratify | Stratification | `pd.cut()` + `groupby()` |
| Summarize / Classify | Summarization | `groupby().agg()` |
| Gaps | Gap Detection | `diff()` sobre la numeración |
| Duplicates | Duplicate Key Detection | `duplicated(keep=False)` |
| Join / Relate | Join Databases | `merge(..., indicator=True)` |
| Benford | Benford's Law | función propia + `scipy.stats.chisquare` |
| Age | Aging | `.dt.dayofweek`, `.dt.hour`, resta de fechas |
| Sample (record / monetary unit) | Random / Monetary Unit Sampling | `sample(random_state=…)`, función MUS propia |
| Export | Export | `to_excel()` |
| Log (registro de comandos) | History | el propio notebook |

---

## Estación 7 — Calidad de datos

### Instrucciones a seguir

1. Abrir `01_calidad_de_datos.ipynb` y ejecutarlo celda por celda (Shift+Enter), leyendo las explicaciones.
2. Al final, el notebook genera `resultados/01_calidad.xlsx` con una hoja por prueba.
3. Resolver los ejercicios de la sección 9 del notebook, agregando celdas debajo de cada uno.

### Ejercicios

Los de la sección 9 del notebook. Como mínimo, el reporte debe responder:

1. Por cada dimensión (completitud, validez, consistencia, unicidad, integridad referencial): pruebas realizadas, cantidad de excepciones y ejemplos.
2. ¿Qué error se produce al importar los datos sin indicar tipos, y qué consecuencias tendría en una auditoría?
3. Conclusión: ¿los datos son confiables para hacer pruebas sobre los pagos? ¿Qué registros se excluyen o corrigen y qué se le pide a la empresa?

### Reporte

Seguir el formato común del [README](../README.md#reporte). Adjuntar `resultados/01_calidad.xlsx` y el notebook ejecutado con los ejercicios resueltos.

---

## Estación 8 — Pruebas analíticas y detección de fraude

### Instrucciones a seguir

1. Abrir `02_pruebas_analiticas.ipynb` y ejecutarlo sección por sección. No depende del notebook 1: carga los datos por su cuenta.
2. Al final, el notebook genera `resultados/02_pruebas_analiticas.xlsx` con una hoja por prueba y las muestras.
3. Resolver los ejercicios de la sección 13 del notebook.

### Ejercicios

Los de la sección 13 del notebook. Como mínimo, el reporte debe incluir:

1. Los 3 hallazgos más graves con formato *condición – criterio – causa – efecto – recomendación*, cuantificando el importe involucrado.
2. La reconstrucción del caso de los proveedores señalados por varias pruebas a la vez (sección 10): quién los dio de alta, quién cargó las facturas, quién aprobó los pagos y a dónde fue el dinero.
3. Un análisis de falsos positivos: qué excepciones no son necesariamente irregularidades y qué documentación pedirían para descartarlas.
4. La comparación entre muestreo aleatorio, muestreo por unidad monetaria y pruebas sobre el 100% de la población.

### Reporte

Seguir el formato común del [README](../README.md#reporte). Adjuntar `resultados/02_pruebas_analiticas.xlsx` y el notebook ejecutado con los ejercicios resueltos.

---

Solución de problemas

- El notebook no encuentra `datos/`: faltó generar los CSV (`docker compose run --rm datos python generar_datos.py`).
- `Permission denied` al guardar un notebook o el Excel: faltó el `chmod -R a+rwX analisis-datos`.
- `http://localhost:8888` no responde: verificar con `docker compose ps` que `datos` esté en ejecución y revisar `docker compose logs datos`. Si el puerto 8888 está ocupado, cambiar el mapeo en `docker-compose.yml` (p. ej. `"127.0.0.1:8889:8888"`).
