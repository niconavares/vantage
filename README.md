# VANTAGE — Network Audit Platform

> Plataforma profesional de auditoría de redes con análisis de vulnerabilidades asistido por IA y generación de informes PDF listos para cliente.

![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django) ![Vue](https://img.shields.io/badge/Vue-3-4FC08D?logo=vuedotjs) ![Celery](https://img.shields.io/badge/Celery-5.4-37814A?logo=celery) ![Claude](https://img.shields.io/badge/Claude_AI-Sonnet-FF6B35) ![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)

---

## ¿Qué es VANTAGE?

VANTAGE es una plataforma full-stack diseñada para automatizar y estructurar auditorías de seguridad en redes corporativas. Combina herramientas de escaneo estándar del sector (nmap, nuclei, masscan) con un pipeline de análisis mediante Claude AI que prioriza hallazgos, identifica cadenas de ataque y redacta narrativas de informe en español. El resultado final es un PDF profesional listo para entregar al cliente.

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        VANTAGE                              │
│                                                             │
│  Vue 3 SPA ──WebSocket──► Django Channels (Daphne)          │
│      │                         │                           │
│      │                    Celery Workers                    │
│      │                         │                           │
│      │            ┌────────────┴──────────────┐            │
│      │            │      Scanner Pipeline      │            │
│      │            │  nmap · nuclei · masscan   │            │
│      │            │  SSL · SMB · SNMP · Brute  │            │
│      │            │  Active Directory          │            │
│      │            └────────────┬──────────────┘            │
│      │                         │                           │
│      │                  Claude AI (Anthropic)               │
│      │                  Análisis + Narrativa                │
│      │                         │                           │
│      └──────────── PDF Report (WeasyPrint + Jinja2) ───────►│
│                                                             │
│  PostgreSQL · Redis · Nginx (static + proxy)               │
└─────────────────────────────────────────────────────────────┘
```

## Características

### Escaneo de red
- **Descubrimiento de hosts** con nmap y masscan — detección de hosts vivos en rangos CIDR
- **Escaneo de puertos y servicios** — detección de versiones, banners, fingerprinting OS
- **Auditoría SSL/TLS** — certificados expirados, cifrados débiles, BEAST, POODLE, DROWN
- **Escaneo de vulnerabilidades** con nuclei y nmap NSE scripts — mapeo a CVEs
- **Auditoría SMB** — shares accesibles, credenciales nulas, MS17-010 (EternalBlue)
- **Auditoría SNMP** — community strings por defecto, enumeración MIB
- **Ataques de diccionario** — SSH, FTP, HTTP Basic, Telnet, SMB con listas custom
- **Enumeración Active Directory** — usuarios, grupos, GPOs, Kerberoasting, AS-REP Roasting

### Inteligencia artificial
- **Análisis por host**: Claude AI evalúa puertos, servicios y vulnerabilidades detectadas y genera un resumen de riesgo real priorizando por contexto, no solo por CVSS teórico
- **Cadenas de ataque**: identifica cómo encadenar hallazgos para comprometer el objetivo
- **Asistente IA interactivo**: chat integrado en la UI para consultar hallazgos del engagement activo
- **Narrativas de informe**: redacción automática de resumen ejecutivo, metodología y conclusiones en español

### Informes PDF
- Generados con **WeasyPrint + Jinja2** — diseño profesional, listos para cliente
- Incluyen: portada, resumen ejecutivo, tabla de hallazgos con severidad, matriz de riesgo, detalle técnico por vulnerabilidad, credenciales encontradas y hoja de ruta de remediación
- Exportables desde la UI con un clic

### Frontend (Vue 3)
- Dashboard principal con métricas de engagement
- Mapa de red interactivo
- Gestión de engagements y jobs de escaneo
- Detalle de hosts y vulnerabilidades con historial
- Gestión de credenciales capturadas
- Asistente IA integrado
- Visor de informes

## Stack Técnico

| Capa | Tecnología |
|------|-----------|
| Backend API | Django 4.2, Django REST Framework |
| Tareas asíncronas | Celery 5.4 + Redis |
| WebSockets | Django Channels + Daphne |
| Frontend | Vue 3, Vite, Tailwind CSS |
| Base de datos | PostgreSQL 12 |
| IA | Claude AI (Anthropic SDK) — claude-sonnet-4-6 |
| Informes PDF | WeasyPrint + Jinja2 |
| Contenedores | Docker Compose + Nginx |
| Herramientas | nmap, nuclei, masscan (montadas en tools_bin/) |

## Primeros pasos

### Prerrequisitos

```bash
docker --version        # Docker 24+
docker compose version  # Compose v2
```

Coloca los binarios de nmap, nuclei y masscan en `backend/tools_bin/`:

```bash
backend/tools_bin/
├── nmap
├── nuclei
└── masscan
```

### Instalación

```bash
git clone https://github.com/niconavares/vantage.git
cd vantage
cp .env.example .env
nano .env   # Configura tu API key de Anthropic y credenciales de DB

docker compose up -d --build
```

La API estará en `http://localhost:9000` y el frontend en `http://localhost:8080`.

### Variables de entorno principales

```env
SECRET_KEY=clave-django-segura
ANTHROPIC_API_KEY=sk-ant-api03-tu-clave
CLAUDE_MODEL=claude-sonnet-4-6
DB_PASSWORD=tu-password-db
ALLOWED_HOSTS=192.168.1.x,localhost
```

## Flujo de trabajo

1. **Crear engagement** — define objetivo (nombre, cliente, rango de IPs/dominios)
2. **Lanzar escaneo** — selecciona módulos y ejecuta; progreso en tiempo real vía WebSocket
3. **Revisar hallazgos** — hosts, puertos, vulnerabilidades, credenciales con análisis IA por host
4. **Consultar asistente** — pregunta al asistente IA sobre los hallazgos del engagement
5. **Generar informe** — PDF profesional con un clic, listo para entregar al cliente

## Módulos de escaneo

```
scanner/tasks/
├── discovery.py       # Descubrimiento de hosts vivos
├── ports.py           # Escaneo de puertos y servicios
├── ssl_audit.py       # Auditoría SSL/TLS
├── vulns.py           # Escaneo de vulnerabilidades (nuclei + NSE)
├── smb.py             # Auditoría SMB
├── snmp.py            # Auditoría SNMP
├── brute.py           # Ataques de diccionario
├── active_directory.py # Enumeración AD (Kerberoasting, AS-REP)
└── orchestrator.py    # Coordinación del pipeline completo
```

## Licencia

MIT — para uso educativo y pentesting autorizado.
