FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libopenscap25 \
       openscap-common \
       wget \
       bzip2 \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Descargar contenido SCAP manualmente desde el proyecto oficial
RUN mkdir -p /usr/share/xml/scap/ssg/content \
    && cd /tmp \
    && wget https://github.com/ComplianceAsCode/content/releases/download/v0.1.73/scap-security-guide-0.1.73.zip \
    && apt-get update \
    && apt-get install -y unzip \
    && unzip scap-security-guide-0.1.73.zip \
    && cp scap-security-guide-0.1.73/*.xml /usr/share/xml/scap/ssg/content/ \
    # 0.1.73 no incluye Ubuntu 24.04 ni Debian 13: se toman de una versión posterior
    && wget https://github.com/ComplianceAsCode/content/releases/download/v0.1.82/scap-security-guide-0.1.82.zip \
    && unzip scap-security-guide-0.1.82.zip \
    && cp scap-security-guide-0.1.82/ssg-ubuntu2404-ds.xml scap-security-guide-0.1.82/ssg-debian13-ds.xml /usr/share/xml/scap/ssg/content/ \
    && rm -rf /tmp/* \
    && apt-get remove -y unzip wget \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Instalar oscap-chroot y herramientas necesarias
RUN apt-get update \
    && apt-get install -y --no-install-recommends openscap-utils \
    && rm -rf /var/lib/apt/lists/*

# No fixed entrypoint; docker-compose sets a sleep entrypoint to keep the container alive for exec/run.
WORKDIR /
CMD ["/bin/bash"]
