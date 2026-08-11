---
title: InkToWeb API
emoji: 🖋️
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# InkToWeb — Backend API

FastAPI backend for the InkToWeb bank-form-digitization demo. See the
[main project README](https://github.com/) for the full write-up.

Demo login: `admin` / `admin123` (auto-seeded on every container start).

**Storage note:** this free-tier Space uses ephemeral disk — the SQLite
database and uploaded form images reset whenever the Space restarts
(inactivity sleep/wake or a redeploy). This is expected for a demo
deployment; see `app/config.py` / `app/database.py` if migrating to a
persistent-storage or external-database setup.
