# CAATs de análisis de datos

Estaciones 7 (calidad de datos) y 8 (pruebas analíticas) del laboratorio: alternativa libre a ACL / IDEA con pandas.

Desde la carpeta raíz del repositorio:

```bash
chmod -R a+rwX analisis-datos
docker compose build datos
docker compose run --rm datos python generar_datos.py
docker compose up -d datos      # JupyterLab en http://localhost:8888
```

Abrir `01_calidad_de_datos.ipynb` (estación 7) o `02_pruebas_analiticas.ipynb` (estación 8).

Guía completa: [docs/DATOS.md](../docs/DATOS.md).
