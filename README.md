# Sin Intermediarios — LA REAL

Repositorio de la primera tanda del proyecto **Sin Intermediarios**: contenido UGC gestionado directamente con creadores.

## Contenido

- [`docs/aprendizajes.html`](docs/aprendizajes.html) — presentación (slides) con la retrospectiva de aprendizajes de esta primera tanda y los ajustes de proceso para las próximas campañas. Se abre directamente en el navegador (usa flechas o clic para avanzar, `F` para pantalla completa).
- [`app/`](app/) — herramienta interna web para el equipo de LA REAL, con dos funciones:
  1. **Liquidar UGC**: genera automáticamente la cuenta de cobro en PDF de un creador a partir de sus datos ya registrados.
  2. **Inscripción de cuentas**: genera el archivo plano (.txt) para inscribir cuentas bancarias en Bancolombia por lote.

Ver [`app/README.md`](app/README.md) para instalación, uso y advertencias importantes de seguridad y del formato bancario.

## Estado del proyecto

Herramienta interna en versión inicial, probada localmente. **Antes de usarla con datos reales de creadores**, revisa la sección de seguridad y la advertencia sobre el archivo plano de Bancolombia en `app/README.md`.
