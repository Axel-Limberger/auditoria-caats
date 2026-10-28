# Estación 1 — Análisis estático de código (SAST): Semgrep y Flake8

Objetivo

- Auditar el código fuente del portal de proveedores ([APP.md](APP.md)) sin ejecutarlo, para detectar vulnerabilidades, malas prácticas y errores antes del despliegue.

¿Para qué sirve en la práctica?

- **Semgrep** busca patrones de código inseguro (reglas de la comunidad alineadas con OWASP y CWE), incluido el seguimiento de datos que ingresa el usuario hasta funciones peligrosas (*taint analysis*).
- **Flake8** es un *linter*: detecta errores de estilo y código sospechoso.

## Requerimientos

- Docker con `docker compose`. Se usa el servicio `scanner` (imagen `python:3.11-slim`, ~190 MB) y, para verificar correcciones, `app` (~230 MB).
- Conexión a internet: Semgrep descarga sus reglas en cada ejecución.
- Preparación del entorno, desde la carpeta raíz del repositorio:

```bash
mkdir -p data/scanner && chmod 777 data/scanner
docker compose up -d scanner
docker compose exec scanner pip install flake8 semgrep
```

## Instrucciones a seguir

1. Leer el código a auditar: `app/app.py`, `app/Dockerfile` y `app/requirements.txt`.

2. Ejecutar el linter y guardar la salida:

```bash
docker compose exec scanner sh -c 'flake8 /app | tee /scanner-out/flake8.txt'
```

3. Ejecutar Semgrep, en pantalla y en JSON como evidencia:

```bash
docker compose exec scanner semgrep --config auto /app
docker compose exec scanner sh -c 'semgrep --config auto --json /app > /scanner-out/semgrep.json'
```

4. **Revisión manual:** leer `app.py` completo buscando problemas que Semgrep no haya reportado (manejo de contraseñas, datos sensibles en respuestas, configuración).

5. **Remediación:** corregir en el host (en `./app`) las vulnerabilidades elegidas en el ejercicio 3. El contenedor `scanner` monta esa carpeta en solo lectura, pero ve los cambios al instante. Volver a ejecutar Semgrep y guardar la salida como `semgrep-despues.json`:

```bash
docker compose exec scanner sh -c 'semgrep --config auto --json /app > /scanner-out/semgrep-despues.json'
```

6. Comprobar que la aplicación sigue funcionando después de los cambios:

```bash
docker compose up -d --build app redis
curl http://localhost:8080/hello
```

7. Al terminar: `docker compose down`.

## Ejercicios

1. **Inventario:** agrupar los hallazgos de Semgrep por tipo de vulnerabilidad (varias reglas pueden señalar el mismo problema). Para cada grupo: regla(s), líneas, CWE y categoría OWASP Top 10.
2. **Validación:** clasificar cada grupo como vulnerabilidad real, mala práctica o falso positivo, justificando. Pista: ¿qué código se ejecuta realmente en el contenedor? (mirar el `CMD` del `Dockerfile`).
3. **Remediación:** corregir al menos 3 vulnerabilidades distintas (por ejemplo, consultas parametrizadas, escape de la salida HTML, evitar `shell=True`) y demostrar con el segundo escaneo que desaparecieron sin romper la aplicación.
4. **Revisión manual:** documentar al menos un problema que Semgrep no detectó.
5. **Flake8:** ¿los hallazgos del linter son de seguridad? ¿Qué valor tienen igual para un auditor?
6. ¿Qué tipos de vulnerabilidad no puede detectar un análisis estático? Dar dos ejemplos relacionados con esta aplicación.

## Reporte

Seguir el formato común del [README](../README.md#reporte). Adjuntar `data/scanner/flake8.txt`, `semgrep.json` y `semgrep-despues.json`, y el código corregido (antes / después).

Notas

- Las reglas de Semgrep cambian con el tiempo: anotar la versión (`docker compose exec scanner semgrep --version`).

Solución de problemas

- `service "scanner" is not running`: ejecutar `docker compose up -d scanner`.
- `semgrep: not found`: se recreó el contenedor; repetir el `pip install` de los requerimientos.
