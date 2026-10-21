# Prototipo funcional SYSTEMKW

La aplicación organiza los archivos de presentación, estilos, lógica y datos por separado:

- `index.html`: estructura de la interfaz.
- `css/styles.css`: estilos visuales.
- `js/app.js`: navegación, filtros, dashboard, asociaciones y exportación.
- `data/clientes.json`, `data/licencias.json` y `data/transacciones.json`: datos derivados de los CSV proporcionados.

## Cómo ejecutarlo en Windows

1. Descomprime la carpeta completa.
2. Haz doble clic en `iniciar.bat`.
3. Se abrirá el navegador en `http://localhost:8000`.
4. Para cerrar el servidor, vuelve a la ventana negra y presiona `Ctrl + C`.

Se requiere Python instalado. Si prefieres, abre una terminal dentro de esta carpeta y ejecuta `python -m http.server 8000`; después visita `http://localhost:8000`.

El prototipo es de consulta. Los clientes, licencias y transacciones se mantienen en archivos separados y se relacionan en la aplicación cuando existe una coincidencia única. Los casos no confirmados se señalan para revisión. Las notificaciones se calculan por fecha de vencimiento; no se envían correos.
