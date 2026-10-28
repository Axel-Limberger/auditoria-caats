# Estación 4 (complemento) — Rendimiento de red: iperf3

Esta guía es parte de la [Estación 4 — Auditoría de red](NETTOOLS.md). Los requerimientos son los mismos.

Objetivo

- Medir throughput, retransmisiones, jitter y pérdida de paquetes entre dos puntos de la red.

¿Para qué sirve en la práctica?

- La auditoría de infraestructura no solo evalúa seguridad: también si la capacidad disponible respalda lo que se comprometió (SLAs, planes de contingencia). iperf3 genera evidencia objetiva y repetible.

## Requerimientos

- Los de la [Estación 4](NETTOOLS.md#requerimientos), con los servicios `iperf3-server` (servidor) y `nettools` (cliente) levantados: `docker compose up -d iperf3-server nettools`.

## Instrucciones a seguir

```bash
# TCP, 10 segundos
docker compose exec nettools iperf3 -c iperf3-server -t 10 | tee data/red/iperf3-tcp.txt

# TCP, 4 conexiones paralelas, en sentido inverso (el servidor envía)
docker compose exec nettools iperf3 -c iperf3-server -t 10 -P 4 -R | tee data/red/iperf3-tcp-paralelo.txt

# UDP a 100 Mbit/s: informa jitter y pérdida de paquetes
docker compose exec nettools iperf3 -c iperf3-server -u -b 100M | tee data/red/iperf3-udp.txt
```

## Ejercicios

1. Registrar throughput (TCP) y jitter / pérdida (UDP). ¿Qué indicador aporta cada protocolo?
2. Entre contenedores del mismo equipo el tráfico no pasa por la red física: ¿qué se está midiendo en realidad? ¿Cómo habría que diseñar la prueba para medir la red del aula?

Notas

- Para medir la red real, ejecutar `iperf3 -s` en otro equipo y el cliente apuntando a su IP.
