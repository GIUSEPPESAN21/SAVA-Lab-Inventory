# Changelog

## v1.0.0 — Producto inicial

Primera versión estable de SAVA Lab Inventory (evolucionó desde el borrador
inicial hacia un producto estructurado, probado y documentado).

### Añadido
- Suite de pruebas automatizadas (`tests/`, `pytest`) para las reglas de
  negocio de autenticación, préstamos y resolución de códigos de barras.
- Integración continua en GitHub Actions (`.github/workflows/ci.yml`):
  chequeo de sintaxis + pruebas en cada push/PR.
- Importación masiva de inventario por CSV (`Inventario → Importar CSV
  masivo`), con plantilla descargable y una sola sincronización a GitHub
  por lote (en vez de una por fila).
- Filtros de categoría, ubicación y tipo en el catálogo de inventario.
- Página "Mi perfil" para ver los propios datos y cambiar la contraseña.
- Gráficas de analítica (salidas por día, items activos por categoría) en
  Reportes.
- Baja en cascada de un contenedor maestro y sus items hijos, bloqueada si
  alguno tiene préstamos abiertos.
- Validación estructural de la jerarquía maestro/hijo al crear o editar
  items (un hijo siempre debe apuntar a un maestro existente y activo).

### Corregido
- **Bug de robustez crítico**: cualquier función que leyera `st.secrets`
  fallaba con `StreamlitSecretNotFoundError` si no existía ningún archivo
  `secrets.toml`, tumbando módulos completos (autenticación, notificaciones,
  almacenamiento). Ahora todo el acceso a secrets pasa por
  `core.config.safe_secret`, que siempre degrada a un valor por defecto.
- El historial de auditoría (`item_history`) registraba la cantidad
  **absoluta** como `quantity_change` en cada edición; ahora registra el
  **delta real** (nueva cantidad − cantidad anterior).

## v0.1.0 — Borrador inicial

Primer borrador funcional: inventario jerárquico (maestro/hijo), login por
roles (estudiante/profesor/maestro), préstamos (salida/reingreso) y
persistencia en Excel sincronizado a GitHub.
