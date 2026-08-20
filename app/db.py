import sqlite3
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "sin_intermediarios.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS creadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_completo TEXT NOT NULL,
    tipo_documento TEXT NOT NULL,
    numero_documento TEXT NOT NULL,
    email TEXT,
    telefono TEXT,
    banco TEXT NOT NULL,
    codigo_banco TEXT,
    tipo_cuenta TEXT NOT NULL,
    numero_cuenta TEXT NOT NULL,
    inscrito_en_banco INTEGER NOT NULL DEFAULT 0,
    inscrito_at TEXT,
    creado_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cuentas_cobro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creador_id INTEGER NOT NULL REFERENCES creadores(id),
    consecutivo INTEGER NOT NULL,
    concepto TEXT NOT NULL,
    monto INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    pdf_filename TEXT NOT NULL,
    creado_at TEXT NOT NULL
);
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


# ---- creadores ----

def list_creadores():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM creadores ORDER BY nombre_completo").fetchall()
    conn.close()
    return rows


def get_creador(creador_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM creadores WHERE id = ?", (creador_id,)).fetchone()
    conn.close()
    return row


def create_creador(data):
    conn = get_conn()
    conn.execute(
        """INSERT INTO creadores
           (nombre_completo, tipo_documento, numero_documento, email, telefono,
            banco, codigo_banco, tipo_cuenta, numero_cuenta, creado_at)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (
            data["nombre_completo"], data["tipo_documento"], data["numero_documento"],
            data.get("email", ""), data.get("telefono", ""),
            data["banco"], data.get("codigo_banco", ""), data["tipo_cuenta"],
            data["numero_cuenta"], now_iso(),
        ),
    )
    conn.commit()
    conn.close()


def update_creador(creador_id, data):
    conn = get_conn()
    conn.execute(
        """UPDATE creadores SET
             nombre_completo=?, tipo_documento=?, numero_documento=?, email=?, telefono=?,
             banco=?, codigo_banco=?, tipo_cuenta=?, numero_cuenta=?
           WHERE id=?""",
        (
            data["nombre_completo"], data["tipo_documento"], data["numero_documento"],
            data.get("email", ""), data.get("telefono", ""),
            data["banco"], data.get("codigo_banco", ""), data["tipo_cuenta"],
            data["numero_cuenta"], creador_id,
        ),
    )
    conn.commit()
    conn.close()


def marcar_inscritos(creador_ids):
    conn = get_conn()
    conn.executemany(
        "UPDATE creadores SET inscrito_en_banco=1, inscrito_at=? WHERE id=?",
        [(now_iso(), cid) for cid in creador_ids],
    )
    conn.commit()
    conn.close()


# ---- cuentas de cobro ----

def next_consecutivo():
    conn = get_conn()
    row = conn.execute("SELECT MAX(consecutivo) AS m FROM cuentas_cobro").fetchone()
    conn.close()
    return (row["m"] or 0) + 1


def create_cuenta_cobro(creador_id, concepto, monto, fecha, pdf_filename):
    consecutivo = next_consecutivo()
    conn = get_conn()
    conn.execute(
        """INSERT INTO cuentas_cobro
           (creador_id, consecutivo, concepto, monto, fecha, pdf_filename, creado_at)
           VALUES (?,?,?,?,?,?,?)""",
        (creador_id, consecutivo, concepto, monto, fecha, pdf_filename, now_iso()),
    )
    conn.commit()
    conn.close()
    return consecutivo


def list_cuentas_cobro():
    conn = get_conn()
    rows = conn.execute(
        """SELECT cc.*, c.nombre_completo, c.numero_documento
           FROM cuentas_cobro cc JOIN creadores c ON c.id = cc.creador_id
           ORDER BY cc.creado_at DESC"""
    ).fetchall()
    conn.close()
    return rows


def get_cuenta_cobro(cuenta_id):
    conn = get_conn()
    row = conn.execute(
        """SELECT cc.*, c.nombre_completo, c.numero_documento
           FROM cuentas_cobro cc JOIN creadores c ON c.id = cc.creador_id
           WHERE cc.id = ?""",
        (cuenta_id,),
    ).fetchone()
    conn.close()
    return row
