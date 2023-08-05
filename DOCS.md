# Installation Guide

1) Clone: `git clone https://github.com/innerbots/lesst` 
2) Configure bot settings:
    1) Rename `app.ini.example` to `app.ini`. Don't worry, app.ini already added to gitignore.
    2) Configure app.ini variables.
3) Configure system:
    - Install postgreSQL, systemd, Python 3.11, poetry, nats-server and nats cli.

4) Configure Postgres & alembic:
    - PSQL: `CREATE DATABASE lesst;`
    - Create migrations: `alembic init --template async migrations`
    - Add alembic.ini to gitignore
    - Open alembic.ini -> `sqlalchemy.url = postgresql+asyncpg://user:pass@localhost/lesst`
    - `alembic revision --autogenerate -m "init"`
    - `alembic upgrade head`

5) Configure environment with poetry:
    - Note: You need to have Poetry installed: `pip install poetry`
    - Install dependencies: `poetry install`
    - Run app: `poetry run app`
    - Update dependencies*: `poetry update`

6) Configure nats-server:
    - Install nats-server: https://docs.nats.io/running-a-nats-service/introduction/installation.
    - Install nats-cli: https://github.com/nats-io/natscli/.
    - Install nats-top: https://github.com/nats-io/nats-top/releases.
    - Server: `nats-server -c nats.conf`
    - Stream: `nats stream add`
      - **Stream name:** lesst
      - **Subjects:** *
      - **Storage:** file
      - **Replication:** 1
      - **Retention Policy:** Interest
      - **Discard Policy:** New
      - **Stream messages limit:** -1
      - **Per subject messages limit:** -1
      - **Total stream size:** -1
      - **Message TTL:** -1
      - **Max message size:** -1
      - **Duplicate tracking time window:** 2m0s
      - **Allow message Roll-ups:** No
      - **Allow message deletion:** No
      - **Allow purging subjects or the entire stream:** Yes
   - Consumer: `nats consumer add`
     - **Consumer name:** aiogram
     - **Delivery target:** <Press Enter>
     - **Start policy:** all
     - **Acknowledgement policy:** explicit
     - **Replay policy:** original
     - **Filter Stream by subject:** <Press Enter>
     - **Max allowed deliveries:** -1
     - **Max acknowledgement pending:** 0
     - **Deliver headers only without bodies:** No
     - **Add a retry backoff policy:** No
     - **Select a stream:** lesst
   - Bucket (optional): `nats kv add name --history=5 --storage=file`

7) It is highly recommended for deployment (Ubuntu / Debian):
    - Systemd service for lesst app:
      - `cp lesst_nats.service etc/systemd/system/lesst_nats.service`
      - `sudo systemctl enable lesst_nats.service`
      - `sudo systemctl start lesst_nats.service`
      - Check status: `sudo systemctl status lesst_nats.service`
    - Systemd service for nats server:
      - `cp lesst.service etc/systemd/system/lesst.service`
      - `sudo systemctl enable lesst.service`
      - `sudo systemctl start lesst.service`
      - Check status: `sudo systemctl status lesst.service`

**If you started app, and no errors occurred, after submitting /start command to your Bot, welcome message
should be sent.**

✔ **Well Done!**
