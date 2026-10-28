# Lab pack — Técnicas de Auditoría Asistidas por Computadora (CAATs)

## Auditoría Informática - LSI - FCEQyN - UNaM

Este repositorio contiene un laboratorio para practicar herramientas de auditoría asistida por computadora de distintos tipos: análisis de código, de dependencias, de aplicaciones web, de red, de cumplimiento, de configuración de sistemas y de datos.

La práctica se organiza en **estaciones**. Cada grupo trabaja en **una** estación: ejecuta la herramienta siguiendo su guía, resuelve los ejercicios y entrega un reporte de auditoría. Al final, cada grupo presenta sus resultados al resto.

## Estaciones

| N° | Tipo de auditoría | Herramienta | Guía | Descarga aprox. |
|---|---|---|---|---|
| 1 | Código fuente (SAST) | Semgrep, Flake8 | [SCANNER.md](docs/SCANNER.md) | 0,4 GB |
| 2 | Dependencias e imágenes (SCA) | Trivy | [TRIVY.md](docs/TRIVY.md) | 0,5 GB |
| 3 | Aplicación web en ejecución (DAST) | OWASP ZAP | [ZAP.md](docs/ZAP.md) | 4 GB |
| 4 | Red: inventario, servicios expuestos, tráfico y rendimiento | nmap, tcpdump, iperf3 | [NETTOOLS.md](docs/NETTOOLS.md), [IPERF3.md](docs/IPERF3.md) | 1,3 GB |
| 5 | Cumplimiento contra benchmarks (CIS) | OpenSCAP | [OpenSCAP.md](docs/OpenSCAP.md) | 1,5 GB |
| 6 | Configuración de sistema (hardening) | Lynis | [LYNIS.md](docs/LYNIS.md) | 0,2 GB |
| 7 | Datos: calidad de datos | Python (pandas) en JupyterLab | [DATOS.md](docs/DATOS.md#estación-7--calidad-de-datos) | 1,6 GB |
| 8 | Datos: pruebas analíticas y fraude | Python (pandas, scipy) en JupyterLab | [DATOS.md](docs/DATOS.md#estación-8--pruebas-analíticas-y-detección-de-fraude) | 1,6 GB |

Las estaciones 1 a 4 auditan el mismo sistema: un portal web de proveedores ([APP.md](docs/APP.md)). Las estaciones 7 y 8 auditan los datos de compras y pagos de la misma empresa.

## Requisitos

- Docker Engine con el plugin `docker compose` (v2). En Windows/macOS, Docker Desktop. Todas las estaciones corren en contenedores, así que todos los grupos trabajan con el mismo entorno.
- En Windows, ejecutar los comandos desde Git Bash o WSL (usan sintaxis de `bash`, como `$(pwd)`).
- Conexión a internet durante la práctica (Semgrep y Trivy descargan reglas y bases de vulnerabilidades).
- Espacio en disco según la estación (columna *Descarga aprox.*), más ~1 GB para los resultados.

## Cómo trabajar

1. Clonar el repositorio y abrir la guía de la estación asignada.
2. Preparar el entorno con los comandos de la sección *Requerimientos* de la guía. Descargan solo lo que usa esa estación; algunas imágenes pesan varios GB, así que conviene hacerlo con buena conexión.
3. Seguir las *Instrucciones a seguir* y resolver los *Ejercicios*. Todos los comandos se ejecutan desde la carpeta raíz del repositorio.
4. Guardar la evidencia en la carpeta que indica la guía (`data/...` o `analisis-datos/resultados/`).
5. Al terminar, liberar recursos con `docker compose down`.

> **Importante:** no ejecutar `docker compose up -d` ni `docker compose build` sin indicar servicios: eso descarga y construye las imágenes de **todas** las estaciones (~10 GB). Usar siempre los comandos de la guía, que nombran los servicios necesarios.

## Reporte

Cada grupo entrega un reporte de auditoría (PDF, 3 a 6 páginas más anexos) con esta estructura:

1. **Identificación:** integrantes, estación, fecha de ejecución.
2. **Objetivo y alcance:** qué se auditó, con qué herramienta (y su versión) y qué quedó fuera del alcance.
3. **Procedimiento:** pasos y comandos ejecutados, y cualquier desvío respecto de la guía.
4. **Hallazgos:** tabla con

   | N° | Hallazgo | Evidencia | Riesgo (alto / medio / bajo) y justificación | Recomendación |
   |---|---|---|---|---|

   La evidencia referencia el archivo del anexo y el fragmento relevante (línea del reporte, captura de pantalla, fila del Excel).
5. **Ejercicios:** respuesta a cada ejercicio de la guía.
6. **Remediación verificada** (cuando la guía la pide): qué se cambió y el resultado antes / después.
7. **Limitaciones:** falsos positivos encontrados y qué no puede detectar la herramienta.
8. **Conclusión:** opinión del grupo sobre el objeto auditado, como lo expresaría un auditor.

**Anexos:** los archivos de evidencia que indica la guía de la estación.

## Ética y seguridad

- Ejecutar escaneos solo contra el entorno del laboratorio. Escanear sistemas ajenos sin autorización escrita es una falta grave (y puede ser delito).
- El escaneo activo de ZAP envía ataques reales: solo contra la aplicación `app` del laboratorio.
- El portal de proveedores tiene fallas de seguridad intencionales (incluida ejecución de comandos): no publicarlo fuera del propio equipo ni cambiar el mapeo de puertos para exponerlo a la red.
- La variante "auditar el propio equipo" de OpenSCAP corre con privilegios y lee todo el disco: usarla solo en equipos de laboratorio.

## Estructura del repositorio

```
auditoria-caats/
├─ docker-compose.yml    <-- servicios de todas las estaciones
├─ README.md             <-- este documento
├─ app/                  <-- portal de proveedores (aplicación objetivo, con fallas intencionales)
├─ openscap/             <-- imagen con OpenSCAP + SCAP Security Guide
├─ lynis/                <-- imagen con Lynis
├─ analisis-datos/       <-- estaciones 7 y 8: notebooks, datos y generador
├─ docs/                 <-- guía de cada estación
└─ data/                 <-- evidencia generada por las estaciones 1 a 6
```

## Comandos útiles

```bash
docker compose ps                     # servicios en ejecución
docker compose logs -f <servicio>     # registros de un servicio
docker compose exec <servicio> bash   # abrir una terminal dentro de un servicio en ejecución
docker compose down                   # detener y eliminar los contenedores del laboratorio
docker system df                      # espacio que ocupan las imágenes descargadas
```
