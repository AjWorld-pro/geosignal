# Geosginal

Geo-based mobile network intelligence platform. Search any location to see available networks (2G/3G/4G/5G), signal strength, providers, BTS towers, and coverage quality — all on an interactive map.

## Quick Start

```bash
py manage.py runserver
# Open http://localhost:8000 — login: admin
```

## Pages

| Page | Purpose |
|---|---|
| Dashboard | Search location → see all networks + map |
| Networks | Search location → see network types & providers |
| Coverage | Search location → see BTS towers & measurements |
| Analytics | Search location → see congestion & signal stats |
| Reports, Saved Scans, Notifications, Settings | Account management |
| Admin pages | User management, monitoring, data, security logs |

## Deploy to Vercel

1. Push to GitHub
2. Add Postgres (Vercel Postgres or Neon)
3. Set env vars in Vercel: `SECRET_KEY`, `USE_POSTGRES=True`
