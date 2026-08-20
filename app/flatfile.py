import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config" / "bancolombia_layout.json"
EXPORT_DIR = Path(__file__).parent / "data" / "inscripciones"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_layout():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _clean(value):
    return str(value or "").replace(";", ",").replace("\n", " ").strip()


def generar_archivo_plano(creadores, filename):
    """creadores: filas sqlite3.Row con columnas de la tabla creadores.
    Devuelve la ruta del archivo generado, usando el layout configurable
    en config/bancolombia_layout.json (ver advertencia dentro de ese archivo)."""
    layout = load_layout()
    delimiter = layout["delimiter"]
    line_ending = layout["line_ending"]
    encoding = layout.get("encoding", "utf-8")
    fields = layout["fields"]

    lines = []
    for creador in creadores:
        row = dict(creador)
        values = [_clean(row.get(f["key"], "")) for f in fields]
        lines.append(delimiter.join(values))

    content = line_ending.join(lines) + line_ending
    path = EXPORT_DIR / filename
    with open(path, "w", encoding=encoding, newline="") as f:
        f.write(content)
    return path
