# Estación 4 — Auditoría de red: nmap, tcpdump e iperf3

Objetivo

- Relevar qué servicios expone la red del portal de proveedores ([APP.md](APP.md)), evaluar si están protegidos, verificar si la información viaja cifrada y medir la capacidad de la red.

¿Para qué sirve en la práctica?

- **nmap**: inventario de hosts, puertos abiertos y versiones de servicios (superficie de ataque). Sus *scripts* (NSE) permiten interrogar servicios específicos.
- **tcpdump**: captura de tráfico para verificar qué información viaja en claro.
- **iperf3**: medición de rendimiento (ver [IPERF3.md](IPERF3.md)), evidencia para evaluar capacidad y SLAs.

## Requerimientos

- Docker con `docker compose`. Se usan los servicios `app` (~230 MB), `redis` (~40 MB), `nettools` (imagen *netshoot*, ~890 MB) e `iperf3-server` (~130 MB).
- Opcional: `nmap` instalado en el equipo (host).
- Preparación del entorno, desde la carpeta raíz del repositorio:

```bash
mkdir -p data/red && chmod 777 data/red
docker compose pull redis nettools iperf3-server
docker compose build app
```

## Instrucciones a seguir

1. Levantar los servicios:

```bash
docker compose up -d app redis nettools iperf3-server
```

2. **Descubrimiento de hosts** en la red del laboratorio (`lab_net`):

```bash
# dirección IP del contenedor nettools (p. ej. 172.21.0.4/16)
docker compose exec nettools ip -4 addr show eth0

# reemplazar por la subred obtenida, terminada en .0/24 (p. ej. 172.21.0.0/24)
docker compose exec nettools nmap -sn 172.21.0.0/24 | tee data/red/hosts.txt
```

3. **Puertos y versiones**, primero con los 1000 puertos más comunes y después con todos:

```bash
docker compose exec nettools nmap -Pn -sV app redis iperf3-server | tee data/red/nmap-comunes.txt
docker compose exec nettools nmap -Pn -sV -p- app redis iperf3-server | tee data/red/nmap-todos.txt
```

4. **Evaluar un servicio expuesto: Redis**, primero con el script de nmap y después conectándose sin credenciales:

```bash
docker compose exec nettools nmap -p 6379 --script redis-info redis | tee data/red/redis-info.txt
docker compose exec nettools sh -c 'printf "INFO keyspace\r\nKEYS *\r\nQUIT\r\n" | nc redis 6379' | tee data/red/redis-acceso.txt
```

5. **Superficie expuesta en el equipo** (desde el host, si tiene nmap):

```bash
nmap -Pn -sT -p- --open localhost | tee data/red/nmap-host.txt
```

6. **Captura de tráfico**: capturar mientras se navega el portal y se inicia sesión.

```bash
docker compose exec nettools bash
# dentro del contenedor
timeout 15 tcpdump -i any port 80 -w /tmp/captura.pcap &
curl -s http://app/ > /dev/null
curl -s -d 'usuario=proveedor&clave=yerba2025' http://app/login
wait
tcpdump -A -r /tmp/captura.pcap | grep -aE 'GET|POST|usuario=|Cookie'
exit
```

Conservar la captura como evidencia (se puede abrir con Wireshark):

```bash
docker compose cp nettools:/tmp/captura.pcap data/red/captura.pcap
```

7. **Rendimiento** con iperf3: seguir [IPERF3.md](IPERF3.md).

8. Al terminar: `docker compose down`.

## Ejercicios

1. **Inventario:** tabla con cada host de `lab_net`, su IP, puertos abiertos, servicio y versión. ¿Qué servicios exponen su versión? ¿Por qué es un riesgo?
2. **Alcance:** comparar los dos escaneos de puertos. ¿Qué servicio no aparece con la configuración por defecto y por qué? ¿Qué implica para una auditoría que use la configuración por defecto de una herramienta?
3. **Redis:** ¿qué información obtuvieron sin credenciales? ¿Qué podría hacer un atacante con ese acceso? ¿Qué información sobre el equipo anfitrión revela? Proponer al menos tres controles.
4. **Tráfico:** mostrar con la captura qué datos sensibles viajan en texto plano (credenciales, cookie de sesión). ¿Qué atributos le faltan a la cookie? ¿Qué controles recomiendan?
5. **Host:** comparar lo que se ve desde adentro de la red (pasos 2 y 3) con lo publicado en el equipo (paso 5). ¿Qué servicios del laboratorio quedan expuestos fuera de la red interna y cuáles no?
6. **Rendimiento:** registrar los resultados de iperf3 (TCP y UDP) y responder los ejercicios de [IPERF3.md](IPERF3.md).

## Reporte

Seguir el formato común del [README](../README.md#reporte). Adjuntar los archivos de `data/red/`.

Notas y seguridad

- No interceptar tráfico de terceros ni escanear redes fuera del laboratorio. En el paso 5, no profundizar sobre puertos del equipo que no sean del laboratorio.

Solución de problemas

- `service "nettools" is not running`: ejecutar `docker compose up -d nettools`.
- Si `docker compose run nettools ...` se queda colgado: el servicio tiene `entrypoint: sleep infinity`; usar `docker compose exec`.
- `nmap -sn` tarda mucho: se usó la subred /16 completa; usar la /24 como indica el paso 2.
