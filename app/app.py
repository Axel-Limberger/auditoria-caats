"""Portal de proveedores de Yerbatera del Alto Paraná S.A.

ADVERTENCIA: aplicación de laboratorio con fallas de seguridad intencionales,
para practicar auditoría. No exponerla fuera de la red del laboratorio.
"""

import hashlib
import os
import sqlite3
import subprocess

import redis
import yaml
from flask import Flask, make_response, request

app = Flask(__name__)
app.config["SECRET_KEY"] = "yerba-mate-alto-parana-2025"

AWS_ACCESS_KEY_ID = "AKIA2YERBAMATEQ7ZK4N"
AWS_SECRET_ACCESS_KEY = "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"
GITHUB_TOKEN = "ghp_8fKz2LqW9xYb4TcV7nM1pR6sD3gH5jA0eU2i"

BASE_DATOS = "/tmp/portal.db"
DOCUMENTOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "documentos")
cache = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), port=6379, socket_timeout=1)

PAGINA = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>Portal de proveedores</title></head>
<body>
<h1>Portal de proveedores — Yerbatera del Alto Paraná S.A.</h1>
<ul>
  <li><a href="/proveedores?q=Transportes">Buscar proveedores</a></li>
  <li><a href="/saludo?nombre=Proveedor">Saludo de bienvenida</a></li>
  <li><a href="/login">Ingresar</a></li>
  <li><a href="/consulta-dns?host=app">Diagnóstico de conectividad</a></li>
  <li><a href="/documentos?archivo=manual.txt">Manual del proveedor</a></li>
  <li><a href="/visitas">Contador de visitas</a></li>
</ul>
<form action="/proveedores" method="get">
  <input name="q" placeholder="Razón social"><button>Buscar</button>
</form>
</body></html>
"""

FORMULARIO_LOGIN = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>Ingresar</title></head>
<body>
<h1>Ingreso de proveedores</h1>
<form action="/login" method="post">
  <input name="usuario" placeholder="Usuario">
  <input name="clave" type="password" placeholder="Contraseña">
  <button>Ingresar</button>
</form>
</body></html>
"""


def conexion():
    return sqlite3.connect(BASE_DATOS)


def inicializar_base():
    with conexion() as db:
        db.execute("CREATE TABLE IF NOT EXISTS proveedores (id INTEGER PRIMARY KEY, razon_social TEXT, cuit TEXT)")
        db.execute("CREATE TABLE IF NOT EXISTS usuarios (usuario TEXT PRIMARY KEY, clave_md5 TEXT, rol TEXT)")
        if not db.execute("SELECT COUNT(*) FROM proveedores").fetchone()[0]:
            db.executemany("INSERT INTO proveedores (razon_social, cuit) VALUES (?, ?)", [
                ("Transportes Oberá S.R.L.", "30-71234567-1"),
                ("Envases del Litoral S.A.", "30-70987654-3"),
                ("Ferretería Industrial Posadas S.A.", "33-71122334-9"),
                ("Servicios Agrícolas Eldorado S.H.", "30-71555666-0"),
            ])
            db.executemany("INSERT INTO usuarios VALUES (?, ?, ?)", [
                ("admin", hashlib.md5(b"admin123").hexdigest(), "administrador"),
                ("proveedor", hashlib.md5(b"yerba2025").hexdigest(), "proveedor"),
            ])


inicializar_base()


@app.route("/")
def index():
    return PAGINA


@app.route("/hello")
def hello():
    return "Hola desde la app de laboratorio\n"


@app.route("/proveedores")
def proveedores():
    q = request.args.get("q", "")
    consulta = f"SELECT id, razon_social, cuit FROM proveedores WHERE razon_social LIKE '%{q}%'"
    try:
        filas = conexion().execute(consulta).fetchall()
    except sqlite3.Error as error:
        return f"Error en la consulta: {error}<br>{consulta}", 500
    items = "".join(f"<li>{razon} — CUIT {cuit}</li>" for _, razon, cuit in filas)
    return f"<h1>Resultados para: {q}</h1><ul>{items}</ul>"


@app.route("/saludo")
def saludo():
    nombre = request.args.get("nombre", "proveedor")
    return f"<h1>Bienvenido/a, {nombre}</h1>"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return FORMULARIO_LOGIN
    usuario = request.form.get("usuario", "")
    clave = request.form.get("clave", "")
    fila = conexion().execute("SELECT clave_md5, rol FROM usuarios WHERE usuario = ?", (usuario,)).fetchone()
    if not fila or hashlib.md5(clave.encode()).hexdigest() != fila[0]:
        return "Usuario o contraseña incorrectos", 401
    respuesta = make_response(f"Bienvenido/a {usuario} ({fila[1]})")
    respuesta.set_cookie("sesion", f"{usuario}:{fila[1]}")
    return respuesta


@app.route("/consulta-dns")
def consulta_dns():
    host = request.args.get("host", "")
    resultado = subprocess.run(f"getent hosts {host}", shell=True, capture_output=True, text=True)
    return f"<pre>{resultado.stdout}{resultado.stderr}</pre>"


@app.route("/documentos")
def documentos():
    archivo = request.args.get("archivo", "manual.txt")
    with open(os.path.join(DOCUMENTOS, archivo)) as f:
        return f"<pre>{f.read()}</pre>"


@app.route("/importar", methods=["POST"])
def importar():
    datos = yaml.load(request.data, Loader=yaml.Loader)
    return {"proveedores_importados": len(datos or [])}


@app.route("/visitas")
def visitas():
    try:
        return f"Visitas: {cache.incr('visitas')}"
    except redis.exceptions.RedisError:
        return "Contador no disponible"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
