# Estación 3 — Análisis dinámico de aplicaciones web (DAST): OWASP ZAP

Objetivo

- Auditar el portal de proveedores ([APP.md](APP.md)) **en ejecución**, desde afuera y sin ver el código, como lo haría un atacante; y relacionar los hallazgos con su causa.

¿Para qué sirve en la práctica?

- Detectar vulnerabilidades que solo se ven cuando la aplicación responde a peticiones: inyecciones, XSS, exposición de archivos, cabeceras de seguridad faltantes, cookies inseguras.

## Requerimientos

- Docker con `docker compose`. Se usan los servicios `app` (~230 MB), `redis` (~40 MB) y `zap` (**~3,7 GB**: conviene descargarla con buena conexión).
- Preparación del entorno, desde la carpeta raíz del repositorio:

```bash
mkdir -p data/zap-reports && chmod 777 data/zap-reports   # ZAP corre con un usuario no-root (uid 1000)
docker compose pull zap redis
docker compose build app
```

## Instrucciones a seguir

1. Levantar el portal y recorrerlo en el navegador (`http://localhost:8080`) para conocer sus funciones:

```bash
docker compose up -d app redis
```

2. **Escaneo pasivo** (*baseline*): recorre el portal y analiza las respuestas sin atacarlo.

```bash
docker compose run --rm --entrypoint "" zap \
  zap-baseline.py -t http://app:80 -r baseline.html -J baseline.json -I
```

Los reportes quedan en `data/zap-reports/`. Abrir `baseline.html` en el navegador.

3. **Escaneo activo**: envía ataques reales (inyecciones, XSS, *path traversal*). Solo contra el laboratorio. Tarda entre 10 y 20 minutos.

```bash
docker compose run --rm --entrypoint "" zap \
  zap-full-scan.py -t http://app:80 -r full.html -J full.json -I -m 2
```

4. **Verificación manual:** para cada alerta de riesgo alto o medio, reproducirla con el navegador o `curl` usando el *payload* que figura en el reporte (campo *Attack*). Por ejemplo:

```bash
curl "http://localhost:8080/saludo?nombre=<b>prueba</b>"
```

Guardar capturas o salidas como evidencia.

5. **Remediación:** corregir en `app/app.py` al menos tres vulnerabilidades confirmadas (y, si se puede, agregar cabeceras de seguridad con una función decorada con `@app.after_request`). Reconstruir y repetir el escaneo activo como `full-despues.html`:

```bash
docker compose up -d --build app redis
docker compose run --rm --entrypoint "" zap \
  zap-full-scan.py -t http://app:80 -r full-despues.html -I -m 2
```

6. Al terminar: `docker compose down`.

## Ejercicios

1. **Inventario:** tabla con cada alerta (nombre, riesgo, confianza, URL y parámetro afectado, CWE). Agrupar las que tengan la misma causa.
2. **Pasivo vs. activo:** ¿qué encontró cada escaneo? ¿Por qué el activo no se usa sobre sistemas en producción sin autorización?
3. **Verificación:** reproducir manualmente las alertas de riesgo alto y medio. ¿Alguna es un falso positivo?
4. **Impacto:** para las dos alertas más graves, describir qué podría lograr un atacante en este portal (qué datos obtiene, qué puede ejecutar).
5. **Remediación:** demostrar con el escaneo posterior qué alertas desaparecieron. ¿Apareció alguna nueva a raíz de los cambios?
6. **Límites:** el portal tiene funciones que ZAP no llegó a probar o que probó sin detectar problemas. Identificar al menos una revisando la lista de funciones de [APP.md](APP.md) y explicar por qué el escaneo automático no la cubrió.

## Reporte

Seguir el formato común del [README](../README.md#reporte). Adjuntar los reportes de `data/zap-reports/`, la evidencia de la verificación manual y el código modificado.

Notas y seguridad

- No ejecutar ZAP contra servicios fuera del laboratorio sin autorización escrita.
- `-I` evita que el script termine con código de error cuando hay advertencias. `-m 2` limita el recorrido inicial (*spider*) a 2 minutos.

Solución de problemas

- `Job report failed to generate report: NoSuchFileException`: se pasó una ruta absoluta a `-r`/`-J`; usar solo el nombre del archivo.
- `Permission denied` al escribir el reporte: `chmod 777 data/zap-reports`.
- `Name or service not known` para `app`: el portal no está levantado (`docker compose up -d app redis`).
