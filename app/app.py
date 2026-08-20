import os
import sys
from pathlib import Path
from datetime import date
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                    session, send_from_directory, flash, abort)

import db
from pdf import generar_cuenta_cobro, DATA_DIR as PDF_DIR
from flatfile import generar_archivo_plano, EXPORT_DIR as FLATFILE_DIR, load_layout


def _load_dotenv(path):
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv(Path(__file__).parent / ".env")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
SECRET_KEY = os.environ.get("SECRET_KEY")

if not ADMIN_PASSWORD or not SECRET_KEY:
    sys.exit(
        "Faltan variables de entorno. Copia app/.env.example a app/.env, define "
        "ADMIN_PASSWORD y SECRET_KEY, y vuelve a correr con esas variables cargadas "
        "(ver README para el comando exacto). No se define una clave por defecto "
        "porque esta herramienta maneja datos bancarios y de identificacion."
    )

app = Flask(__name__)
app.secret_key = SECRET_KEY

TIPOS_DOCUMENTO = ["CC", "CE", "NIT", "PA"]
TIPOS_CUENTA = ["AHORROS", "CORRIENTE", "DEPOSITO_ELECTRONICO"]


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("autenticado"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["autenticado"] = True
            return redirect(request.args.get("next") or url_for("dashboard"))
        flash("Contrasena incorrecta.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def dashboard():
    creadores = db.list_creadores()
    cuentas = db.list_cuentas_cobro()
    pendientes_inscripcion = [c for c in creadores if not c["inscrito_en_banco"]]
    return render_template(
        "dashboard.html",
        creadores=creadores,
        cuentas=cuentas,
        pendientes_inscripcion=pendientes_inscripcion,
    )


def _creador_form_data(form):
    return {
        "nombre_completo": form["nombre_completo"].strip(),
        "tipo_documento": form["tipo_documento"],
        "numero_documento": form["numero_documento"].strip(),
        "email": form.get("email", "").strip(),
        "telefono": form.get("telefono", "").strip(),
        "banco": form["banco"].strip(),
        "codigo_banco": form.get("codigo_banco", "").strip(),
        "tipo_cuenta": form["tipo_cuenta"],
        "numero_cuenta": form["numero_cuenta"].strip(),
    }


@app.route("/creadores/nuevo", methods=["GET", "POST"])
@login_required
def creador_nuevo():
    if request.method == "POST":
        db.create_creador(_creador_form_data(request.form))
        flash("Creador guardado.", "ok")
        return redirect(url_for("dashboard"))
    return render_template(
        "creador_form.html", creador=None,
        tipos_documento=TIPOS_DOCUMENTO, tipos_cuenta=TIPOS_CUENTA,
    )


@app.route("/creadores/<int:creador_id>/editar", methods=["GET", "POST"])
@login_required
def creador_editar(creador_id):
    creador = db.get_creador(creador_id)
    if not creador:
        abort(404)
    if request.method == "POST":
        db.update_creador(creador_id, _creador_form_data(request.form))
        flash("Datos actualizados.", "ok")
        return redirect(url_for("dashboard"))
    return render_template(
        "creador_form.html", creador=creador,
        tipos_documento=TIPOS_DOCUMENTO, tipos_cuenta=TIPOS_CUENTA,
    )


@app.route("/liquidar/<int:creador_id>", methods=["GET", "POST"])
@login_required
def liquidar(creador_id):
    creador = db.get_creador(creador_id)
    if not creador:
        abort(404)

    if request.method == "POST":
        concepto = request.form["concepto"].strip()
        try:
            monto = int(request.form["monto"].replace(".", "").replace(",", ""))
        except ValueError:
            flash("El monto debe ser un numero.", "error")
            return redirect(url_for("liquidar", creador_id=creador_id))

        fecha = date.today().strftime("%d/%m/%Y")
        consecutivo = db.next_consecutivo()
        pdf_filename = generar_cuenta_cobro(consecutivo, creador, concepto, monto, fecha)
        db.create_cuenta_cobro(creador_id, concepto, monto, fecha, pdf_filename)
        flash("Cuenta de cobro generada.", "ok")
        return redirect(url_for("descargar_cuenta_cobro", filename=pdf_filename))

    return render_template("liquidar.html", creador=creador)


@app.route("/cuentas-cobro/descargar/<path:filename>")
@login_required
def descargar_cuenta_cobro(filename):
    return send_from_directory(PDF_DIR, filename, as_attachment=False)


@app.route("/inscripcion", methods=["GET", "POST"])
@login_required
def inscripcion():
    layout = load_layout()

    if request.method == "POST":
        ids = [int(i) for i in request.form.getlist("creador_id")]
        if not ids:
            flash("Selecciona al menos un creador.", "error")
            return redirect(url_for("inscripcion"))

        conn = db.get_conn()
        placeholders = ",".join("?" * len(ids))
        rows = conn.execute(
            f"SELECT * FROM creadores WHERE id IN ({placeholders})", ids
        ).fetchall()
        conn.close()

        filename = f"inscripcion-cuentas-{date.today().strftime('%Y%m%d')}.txt"
        generar_archivo_plano(rows, filename)
        db.marcar_inscritos(ids)
        flash(
            "Archivo generado. Revisalo contra la plantilla oficial de Bancolombia "
            "ANTES de subirlo a la Sucursal Virtual Empresas.", "warn",
        )
        return redirect(url_for("descargar_inscripcion", filename=filename))

    creadores = [c for c in db.list_creadores() if not c["inscrito_en_banco"]]
    return render_template("inscripcion.html", creadores=creadores, layout=layout)


@app.route("/inscripcion/descargar/<path:filename>")
@login_required
def descargar_inscripcion(filename):
    return send_from_directory(FLATFILE_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True, port=5050)
