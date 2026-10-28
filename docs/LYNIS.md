# Estación 6 — Auditoría de configuración del sistema: Lynis

Objetivo

- Auditar la configuración de seguridad de un sistema Linux y obtener recomendaciones de hardening priorizables.

¿Para qué sirve en la práctica?

- Lynis revisa cientos de aspectos (cuentas, permisos, servicios, kernel, registros, criptografía) y resume el resultado en un *Hardening index* de 0 a 100. A diferencia de OpenSCAP no evalúa contra un benchmark formal, sino contra un conjunto de buenas prácticas.

## Requerimientos

- Docker con `docker compose`. Se usa solo el servicio `lynis` (imagen Debian 12 que se construye localmente, ~130 MB). Lynis audita **el propio contenedor**.
- Preparación del entorno, desde la carpeta raíz del repositorio:

```bash
mkdir -p data/lynis && chmod 777 data/lynis
docker compose build lynis
```

## Instrucciones a seguir

1. Ejecutar la auditoría (el contenedor se crea, audita y se elimina):

```bash
docker compose run --rm --entrypoint "" lynis sh -c \
  'lynis audit system --quick --no-colors --logfile /report/lynis.log --report-file /report/lynis-report.dat; chmod 644 /report/*'
```

`--quick` evita que Lynis se detenga a esperar Enter entre secciones; el `chmod` permite leer los reportes desde el equipo.

2. Revisar los resultados:

```bash
grep hardening_index data/lynis/lynis-report.dat
grep -E '^warning' data/lynis/lynis-report.dat
grep -E '^suggestion' data/lynis/lynis-report.dat
```

Cada sugerencia tiene un código (p. ej. `AUTH-9230`); su explicación está en `https://cisofy.com/lynis/controls/<código>/`.

3. **Remediación y nueva auditoría:** aplicar dos o tres recomendaciones en un contenedor interactivo y volver a auditar **en la misma sesión** (los cambios se pierden al salir):

```bash
docker compose run --rm --entrypoint "" lynis bash
# dentro del contenedor: aplicar los cambios, por ejemplo
#   apt-get update && apt-get install -y <paquete recomendado>
#   editar /etc/login.defs, permisos de archivos, etc.
lynis audit system --quick --no-colors --report-file /report/lynis-despues.dat
chmod 644 /report/*
exit
```

## Ejercicios

1. Registrar el *Hardening index*, la cantidad de pruebas realizadas, advertencias y sugerencias.
2. Elegir las 10 sugerencias más importantes y clasificarlas por prioridad (alta / media / baja), justificando con el riesgo que mitiga cada una.
3. Aplicar al menos dos recomendaciones y demostrar con la nueva auditoría cómo cambió el índice.
4. ¿Qué limitaciones tiene auditar un contenedor en lugar de un servidor real? Mencionar dos pruebas de Lynis que no tienen sentido en un contenedor.

## Reporte

Seguir el formato común del [README](../README.md#reporte). Adjuntar `data/lynis/lynis-report.dat`, `lynis-despues.dat` y la lista de cambios aplicados.

Notas

- Para auditar una VM o servidor real: `sudo apt install lynis` y `sudo lynis audit system`.

Solución de problemas

- `no such service: lynis`: verificar que el `docker-compose.yml` sea la versión actualizada.
- `Permission denied` al leer los reportes: faltó el `chmod 644 /report/*`.
