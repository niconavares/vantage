FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap netcat-openbsd curl wget git unzip \
    iputils-ping traceroute dnsutils net-tools \
    smbclient \
    openssl \
    snmp \
    hydra \
    gcc libc6-dev libpq-dev libssl-dev libffi-dev \
    libpango-1.0-0 libpangocairo-1.0-0 libcairo2 \
    libgdk-pixbuf-2.0-0 fonts-liberation \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install ProjectDiscovery tools (pre-built binaries copied from host)
COPY tools_bin/nuclei /usr/local/bin/nuclei
COPY tools_bin/httpx /usr/local/bin/httpx
COPY tools_bin/naabu /usr/local/bin/naabu
RUN chmod +x /usr/local/bin/nuclei /usr/local/bin/httpx /usr/local/bin/naabu

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p scan_results staticfiles media

EXPOSE 8000
