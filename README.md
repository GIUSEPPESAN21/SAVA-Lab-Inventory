# SAVA Lab Inventory

Sistema de gestión de inventario y préstamos (salida/reingreso) para laboratorios
de ingeniería, con códigos de barras jerárquicos (contenedor maestro + ítems
hijos) y control de acceso por roles usando correo institucional
(estudiante / profesor / perfil maestro).

> Borrador inicial generado a partir de la evolución del proyecto
> [Software-Rapi-tienda-SAVA](https://github.com/GIUSEPPESAN21/Software-Rapi-tienda-SAVA),
> adaptado de un punto de venta de tienda a un sistema de préstamos de
> laboratorio. Ver la sección "Diferencias con la app de tienda" abajo.

## Conceptos clave

- **Contenedor maestro**: un código de barras pegado a una caja, gabinete o kit
  que agrupa varios productos. No tiene cantidad propia.
- **Ítem hijo**: un código de barras individual que vive dentro de un
  contenedor maestro (`parent_id` apunta al maestro).
- **Ítem individual (standalone)**: un producto con código propio que no
  pertenece a ningún contenedor.
- **Disponibilidad en vivo**: `disponible = cantidad_total - préstamos abiertos`.
  La cantidad total solo cambia por alta/ajuste/baja; cada salida y reingreso
  queda registrado en el libro mayor de préstamos (`loans`), nunca se resta
  directamente.

## Roles

| Rol | Puede |
|---|---|
| Estudiante | Ver catálogo, escanear y pedir salida a su nombre, ver y reingresar sus propios préstamos |
| Profesor | Todo lo anterior + alta/edición/baja de ítems, registrar salida/reingreso de cualquier usuario, ver todos los préstamos y reportes |
| Maestro | Todo lo anterior + gestión de usuarios y roles, lista blanca de profesores, auditoría completa, exportar base de datos |

**Seguridad del registro:** nadie elige su rol al registrarse. Toda cuenta nace
`estudiante`; solo nace `profesor` si su correo ya está en la lista blanca
(gestionada por un `maestro`). El rol `maestro` nunca se auto-asigna: la
primera cuenta maestra se siembra desde los Secrets de Streamlit
(`MASTER_EMAIL` / `MASTER_INITIAL_PASSWORD`) la primera vez que arranca la app.

## Arquitectura

- **Frontend/backend**: Streamlit (multipágina moderna con `st.navigation`).
- **Base de datos**: un archivo Excel (`SAVA_LAB_DB.xlsx`) que vive en el
  repositorio **privado** `GIUSEPPESAN21/SAVA-Lab-Database`. Cada escritura se
  guarda localmente y se sincroniza a GitHub vía API en un hilo de fondo
  (mismo mecanismo, ya probado en producción, de la app de tienda).
- **Autenticación**: contraseñas con `bcrypt`, sesión con `st.session_state`.

```
app.py                 Punto de entrada: config, CSS, sesión, navegación por rol
core/
  storage.py            Capa de datos: Excel local + sync a GitHub
  auth.py                Registro, login, reglas de rol
  barcode.py             Resolución de códigos maestro/hijo/individual
  loans.py               Checkout / checkin / vencidos
  notifications.py       Alertas WhatsApp opcionales (Twilio)
  reports.py             Analítica y exportación a Excel
views/
  login.py, inicio.py, escanear.py, inventario.py,
  prestamos.py, usuarios.py, reportes.py, acerca_de.py
```

## Configuración (Secrets de Streamlit)

Copia `.streamlit/secrets.toml.example`, complétalo con tus valores reales y
pégalo en Streamlit Cloud → tu app → Settings → Secrets (o guárdalo como
`.streamlit/secrets.toml` en local; ese archivo está en `.gitignore` y nunca
debe subirse al repositorio).

El `GITHUB_TOKEN` debe ser un *fine-grained personal access token* con acceso
**únicamente** al repositorio `SAVA-Lab-Database` y permiso
"Contents: Read and write". No reutilices tokens con acceso a otros
repositorios.

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Diferencias con la app de tienda (Software-Rapi-tienda-SAVA)

Este proyecto es un borrador nuevo, no un fork directo. Se reutilizó el patrón
de persistencia (Excel + GitHub) porque ya está validado en producción, pero
se rediseñó el modelo de negocio:

- Ventas/fiado → reemplazado por préstamos con salida y reingreso.
- Sin login → login obligatorio con roles y correo institucional.
- Descuento directo de stock al vender → libro mayor de préstamos abiertos
  (más auditable para activos que se devuelven).
- Un solo nivel de producto → jerarquía contenedor maestro / ítems hijos.
- Módulo de IA (Gemini) de la app de tienda no se incluye: no se usaba en
  ninguna pantalla de esa app (código muerto detectado en el análisis previo).

## Licencia

MIT. Ver [LICENSE](LICENSE).
