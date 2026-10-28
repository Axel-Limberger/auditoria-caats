# Estación 2 — Análisis de dependencias, secretos e imágenes (SCA): Trivy

Objetivo

- Detectar vulnerabilidades conocidas (CVE) en las dependencias del portal de proveedores ([APP.md](APP.md)) y en la imagen de contenedor con la que se despliega, además de secretos expuestos y errores de configuración.

¿Para qué sirve en la práctica?

- La mayor parte del software de una aplicación son bibliotecas de terceros y paquetes del sistema operativo. Trivy los inventaría y los compara con bases públicas de vulnerabilidades (NVD, GitHub Advisories, avisos de cada distribución). También busca credenciales en el código y malas configuraciones en el `Dockerfile`.

## Requerimientos

- Docker con `docker compose`. Se usan los servicios `trivy` (~270 MB) y `app` (se construye localmente, ~230 MB).
- Conexión a internet: Trivy descarga su base de vulnerabilidades al ejecutarse.
- El escaneo de imagen monta el socket de Docker (`/var/run/docker.sock`); funciona en Linux y en Docker Desktop.
- Preparación del entorno, desde la carpeta raíz del repositorio:

```bash
mkdir -p data/trivy && chmod 777 data/trivy
docker compose pull trivy
docker compose build app
```

## Instrucciones a seguir

1. **Dependencias** (`app/requirements.txt`):

```bash
docker compose run --rm --entrypoint "" trivy trivy fs /project
docker compose run --rm --entrypoint "" -v $(pwd)/data/trivy:/report trivy \
  trivy fs --format json --output /report/dependencias.json /project
```

2. **Secretos y configuración** (código y `Dockerfile`):

```bash
docker compose run --rm --entrypoint "" -v $(pwd)/data/trivy:/report trivy \
  trivy fs --scanners secret,misconfig --format table --output /report/secretos-config.txt /project
cat data/trivy/secretos-config.txt
```

3. **Imagen completa** que se despliega (sistema operativo + paquetes Python + secretos):

```bash
docker compose run --rm --entrypoint "" -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/data/trivy:/report trivy \
  trivy image --format json --output /report/imagen.json lab-app

# resumen en pantalla, solo severidades altas
docker compose run --rm --entrypoint "" -v /var/run/docker.sock:/var/run/docker.sock trivy \
  trivy image --severity HIGH,CRITICAL lab-app
```

4. **Inventario de software (SBOM)** en formato estándar CycloneDX:

```bash
docker compose run --rm --entrypoint "" -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/data/trivy:/report trivy \
  trivy image --format cyclonedx --output /report/sbom.json lab-app
```

5. **Remediación:** actualizar `app/requirements.txt` según la columna *Fixed Version* (y quitar lo que la aplicación no use), corregir el `Dockerfile`, reconstruir y verificar que el portal sigue funcionando:

```bash
docker compose up -d --build app redis
curl http://localhost:8080/hello
curl "http://localhost:8080/proveedores?q=Trans"
```

Repetir los pasos 1 y 2 guardando los resultados como `dependencias-despues.json` y `secretos-config-despues.txt`.

6. Al terminar: `docker compose down`.

## Ejercicios

1. **Dependencias:** tabla con cada CVE (paquete, versión instalada y corregida, severidad). Para los CRITICAL y HIGH, explicar qué riesgo concreto implican para **este** portal.
2. **Uso real:** ¿todas las dependencias de `requirements.txt` se usan en `app.py`? ¿Qué recomendaría un auditor sobre las que no se usan?
3. **Secretos:** ¿qué credenciales se encontraron y dónde? Más allá de borrarlas del código, ¿qué hay que hacer con una credencial que estuvo expuesta?
4. **Configuración:** explicar cada hallazgo `DS-…` del `Dockerfile` y proponer la corrección.
5. **Priorización:** el escaneo de imagen reporta más de 200 vulnerabilidades. Proponer un criterio para priorizarlas (severidad, si hay versión corregida, si el paquete se usa, si es explotable por red) y aplicarlo para elegir las 10 primeras a resolver.
6. **Remediación:** demostrar con los escaneos posteriores qué se resolvió, y que la aplicación sigue funcionando.
7. ¿Para qué le sirve un SBOM a un auditor? ¿Por qué el resultado de Trivy puede cambiar de un día para otro sin modificar el código?

## Reporte

Seguir el formato común del [README](../README.md#reporte). Adjuntar los archivos de `data/trivy/` y el `requirements.txt` y `Dockerfile` corregidos.

Notas

- Trivy puede producir falsos positivos; contrastar con los avisos de seguridad de cada paquete.
- Anotar en el reporte la fecha del escaneo: la base de vulnerabilidades se actualiza a diario.

Solución de problemas

- `unable to initialize the image scanner`: falta montar `/var/run/docker.sock` o la imagen `lab-app` no está construida (`docker compose build app`).
- La app no arranca después de actualizar dependencias: `docker compose logs app`.
