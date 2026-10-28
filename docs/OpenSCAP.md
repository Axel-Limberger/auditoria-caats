# Estación 5 — Cumplimiento contra benchmarks: OpenSCAP

Objetivo

- Evaluar si un sistema operativo cumple un estándar de hardening reconocido (benchmark CIS) y generar el reporte de cumplimiento como evidencia.

¿Para qué sirve en la práctica?

- Las auditorías de cumplimiento no preguntan "¿es seguro?" sino "¿cumple con el estándar acordado?". OpenSCAP evalúa automáticamente cientos de controles de perfiles como **CIS**, **STIG** o **ANSSI** y, para cada control fallido, indica la remediación.

## Requerimientos

- Docker con `docker compose` y `tar` (Linux, macOS, o Git Bash / WSL en Windows).
- Imagen `lab-openscap` (se construye localmente, **~1,4 GB**) y la imagen `ubuntu:24.04` (~120 MB), que es el sistema a auditar.
- Preparación del entorno, desde la carpeta raíz del repositorio:

```bash
mkdir -p data/openscap && chmod 777 data/openscap
docker compose build openscap
docker pull ubuntu:24.04
```

## Instrucciones a seguir

Se audita el sistema de archivos de una imagen Ubuntu 24.04. Así todos obtienen el mismo resultado sin importar el equipo, y no se necesitan privilegios sobre el propio sistema.

1. Extraer el sistema de archivos de la imagen:

```bash
mkdir -p data/rootfs-ubuntu2404
docker create --name objetivo ubuntu:24.04
docker export objetivo | tar -x -C data/rootfs-ubuntu2404
docker rm objetivo
rm -f data/rootfs-ubuntu2404/.dockerenv   # si queda, OpenSCAP marca las reglas como "no aplicables"
```

2. Consultar los perfiles disponibles para Ubuntu 24.04:

```bash
docker run --rm lab-openscap oscap info --profiles /usr/share/xml/scap/ssg/content/ssg-ubuntu2404-ds.xml
```

3. Evaluar el perfil **CIS Nivel 1 – Servidor**:

```bash
docker run --rm \
  -v $(pwd)/data/rootfs-ubuntu2404:/target:ro \
  -v $(pwd)/data/openscap:/report lab-openscap \
  oscap-chroot /target xccdf eval \
    --profile xccdf_org.ssgproject.content_profile_cis_level1_server \
    --report /report/cis-l1.html \
    --results /report/cis-l1.xml \
    /usr/share/xml/scap/ssg/content/ssg-ubuntu2404-ds.xml
```

El comando termina con código 2 cuando hay controles que fallan; es normal. Abrir `data/openscap/cis-l1.html` en el navegador.

4. Repetir el paso 3 con el perfil `cis_level2_server`, guardando `cis-l2.html` y `cis-l2.xml`.

5. Al terminar, borrar el sistema de archivos extraído: `rm -rf data/rootfs-ubuntu2404`.

## Ejercicios

1. Resumen de resultados del Nivel 1: cantidad de controles aprobados, fallidos y no aplicables, y el puntaje.
2. Elegir 5 controles fallidos (priorizando severidad *high*): qué exige el control, qué riesgo mitiga y qué remediación propone el reporte.
3. ¿Por qué tantos controles dan "no aplicable"? (pista: qué le falta a una imagen de contenedor respecto de un servidor real).
4. Comparar el Nivel 1 con el Nivel 2: ¿cuántos controles más exige? Elegir uno que agregue el Nivel 2 y discutir su costo operativo.
5. Una empresa dice "cumplimos CIS". ¿Qué preguntas haría un auditor antes de aceptar esa afirmación?

## Reporte

Seguir el formato común del [README](../README.md#reporte). Adjuntar `data/openscap/cis-l1.html` y `cis-l2.html` (los `.xml` son la evidencia completa, pero no hace falta imprimirlos).

## Variante opcional: auditar el propio equipo

Solo en un equipo de laboratorio con Debian 12/13 o Ubuntu 22.04/24.04. El servicio `openscap` del `docker-compose.yml` monta `/` del equipo en `/host` (solo lectura) y corre como `privileged`.

| SO del equipo | Datastream | Perfil |
|---|---|---|
| Debian 12 | `ssg-debian12-ds.xml` | `standard` |
| Debian 13 | `ssg-debian13-ds.xml` | `standard` o `cis_level1_server` |
| Ubuntu 22.04 | `ssg-ubuntu2204-ds.xml` | `standard` o `cis_level1_server` |
| Ubuntu 24.04 | `ssg-ubuntu2404-ds.xml` | `cis_level1_server` |

```bash
# ejemplo para Ubuntu 24.04
R=xccdf_org.ssgproject.content_rule_
docker compose run --rm --entrypoint "" -v $(pwd)/data/openscap:/report openscap \
  oscap-chroot /host xccdf eval \
    --profile xccdf_org.ssgproject.content_profile_cis_level1_server \
    --skip-rule ${R}file_permissions_unauthorized_world_writable \
    --skip-rule ${R}file_permissions_ungroupowned \
    --skip-rule ${R}no_files_unowned_by_user \
    --skip-rule ${R}dir_perms_world_writable_sticky_bits \
    --report /report/host.html \
    /usr/share/xml/scap/ssg/content/ssg-ubuntu2404-ds.xml
```

Las cuatro reglas omitidas recorren todo el disco con un script que corre *fuera* del chroot: dentro del contenedor eso incluye `/host` completo, y el reporte llega a cientos de MB con nombres de archivos personales. Pueden verificarse a mano con `find / -xdev -type f -perm -0002`.

Notas y seguridad

- No aplicar remediaciones automáticas (`--remediate`) sobre un equipo real: pueden afectar su funcionamiento.

Solución de problemas

- **Todas las reglas dan `notapplicable`**: quedó el archivo `.dockerenv` en el sistema extraído, o el datastream no corresponde al SO evaluado.
- **`Unable to find image 'lab-openscap'`**: falta `docker compose build openscap`.
- **`tar: Cannot mknod`** u otras advertencias al extraer: se pueden ignorar.
