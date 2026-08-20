# Herramienta interna — Sin Intermediarios

App Flask para uso interno de LA REAL: registrar creadores UGC, liquidarlos (genera cuenta de cobro en PDF) e inscribir sus cuentas ante Bancolombia (genera archivo plano).

## Instalación

```bash
cd app
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` y define `ADMIN_PASSWORD` y `SECRET_KEY` con valores reales (no dejes los de ejemplo). La app no arranca si faltan.

## Correr la app

```bash
cd app
.venv/bin/python app.py
```

Abre `http://127.0.0.1:5050`. La primera vez crea la base de datos SQLite automáticamente en `app/data/`.

## Flujo de uso

1. **Nuevo creador**: transcribe a mano los datos del contrato firmado (nombre, documento, banco, tipo de cuenta, número de cuenta). Hoy esos datos solo existen en el contrato firmado, así que este paso lo hace un admin una vez por creador.
2. **Liquidar**: desde el panel, botón "Liquidar" junto al creador → se autocompletan sus datos bancarios → ingresas concepto y valor → se genera el PDF de la cuenta de cobro (numerada, con fecha, valor en letras y datos de pago).
3. **Inscripción de cuentas**: en "Inscripción de cuentas" seleccionas los creadores pendientes → se genera un `.txt` con sus datos en el layout configurado, y quedan marcados como inscritos.

## ⚠️ Sobre el archivo plano de Bancolombia — leer antes de usar en producción

**No teníamos a la mano el manual oficial de Bancolombia** con el layout exacto (orden de campos, separador, códigos de banco/tipo de cuenta) que exige la Sucursal Virtual Empresas para inscripción de cuentas por lote. El archivo que genera esta herramienta usa un formato de referencia definido en [`config/bancolombia_layout.json`](config/bancolombia_layout.json), **no validado contra la plantilla real de Bancolombia**.

Antes de subir un archivo real al banco:

1. Entra a Sucursal Virtual Empresas → Guías y Manuales → descarga la plantilla oficial de inscripción de cuentas.
2. Compara campo por campo (orden, separador, longitud, códigos de banco y de tipo de cuenta) contra `config/bancolombia_layout.json`.
3. Ajusta ese archivo de configuración — no hace falta tocar código Python, `flatfile.py` lee el layout desde ahí.
4. Haz una prueba con un lote pequeño antes de correr algo masivo.

El campo "código del banco" en el formulario de creador queda en blanco por defecto a propósito: hay que llenarlo con el código real que asigne Bancolombia, no un valor inventado.

## Seguridad y datos sensibles

Esta herramienta maneja **cédulas y números de cuenta bancaria**. Antes de usarla con datos reales de creadores:

- Corre esta app solo en la red interna o en la máquina del admin — el servidor de desarrollo de Flask (`app.run`) no está pensado para exponerse a internet.
- `app/data/` (la base de datos SQLite y los PDFs/archivos generados) y `app/.env` están en `.gitignore`: nunca deben subirse al repo.
- No hay cifrado de los datos bancarios en la base de datos SQLite local. Si se necesita más adelante, es la primera mejora a priorizar antes de escalar el uso del panel a más personas.
- Cambia `ADMIN_PASSWORD` por una clave fuerte y no la compartas fuera del equipo que liquida pagos.
