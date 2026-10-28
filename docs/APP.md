# App — Portal de proveedores (aplicación objetivo)

Esta no es una estación: es el sistema que auditan las estaciones 1 (SAST), 2 (Trivy), 3 (ZAP) y 4 (red).

> **Advertencia:** la aplicación contiene fallas de seguridad **intencionales** para practicar auditoría. No exponerla fuera de la red del laboratorio.

## Descripción

Portal web de **Yerbatera del Alto Paraná S.A.** para sus proveedores (Flask servida con gunicorn). Archivos en `./app`:

- `app.py`: código de la aplicación.
- `requirements.txt`: dependencias Python.
- `Dockerfile`: cómo se construye la imagen `lab-app`.
- `documentos/`: documentos que el portal publica.

| Ruta | Función |
|---|---|
| `/` | Página principal con los enlaces del portal |
| `/proveedores?q=…` | Búsqueda de proveedores por razón social |
| `/saludo?nombre=…` | Mensaje de bienvenida |
| `/login` | Ingreso de usuarios (formulario) |
| `/consulta-dns?host=…` | Diagnóstico de conectividad: resuelve un nombre de host |
| `/documentos?archivo=…` | Descarga de documentos (p. ej. `manual.txt`) |
| `/importar` | Importación de proveedores en formato YAML (POST) |
| `/visitas` | Contador de visitas (usa el servicio `redis`) |
| `/hello` | Respuesta de prueba |

Credenciales de prueba: usuario `proveedor`, contraseña `yerba2025`.

Se publica en `http://localhost:8080`. Dentro de la red del laboratorio se accede como `http://app`.

## Instrucciones a seguir

1. Construir y levantar la aplicación (con `redis` para el contador de visitas):

```bash
docker compose up -d --build app redis
```

2. Probar que responde:

```bash
curl http://localhost:8080/hello
```

o abrir `http://localhost:8080` en el navegador.

3. Después de modificar `app.py`, `requirements.txt` o el `Dockerfile`, repetir el paso 1 para reconstruir la imagen.

Solución de problemas

- Si el puerto 8080 está ocupado, detener el proceso que lo ocupa o cambiar el mapeo de puertos en `docker-compose.yml` (p. ej. `"8081:80"`).
- `docker compose logs app` muestra los errores de arranque (por ejemplo, una dependencia incompatible tras actualizar `requirements.txt`).
- "Contador no disponible" en `/visitas`: el servicio `redis` no está levantado. El resto del portal funciona igual.
