# Prototipo SYSTEMKW

La aplicación presenta los módulos de Dashboard, Clientes, Licencias, Transacciones y Notificaciones. Lee los archivos preparados por el script de limpieza, conserva los identificadores de origen y utiliza los archivos de relaciones para asociar registros solo cuando la coincidencia fue única.

## Preparar los datos

Desde la carpeta raíz del repositorio, ejecuta:

```bash
py limpieza_csv/limpieza_datos.py
```

El script crea o actualiza los archivos de `limpieza_csv/datos_limpios/`. Conserva los CSV originales y genera también las relaciones sugeridas y el reporte de revisión.

## Iniciar el sistema en Windows

1. Desde la carpeta raíz del repositorio, haz doble clic en `iniciar.bat`.
2. Se abrirá el sistema en `http://localhost:8000`.
3. Para detener el servidor, vuelve a la ventana de comandos y presiona `Ctrl + C`.

También puedes abrir una terminal en la carpeta raíz y ejecutar `py -m http.server 8000`; después visita `http://localhost:8000`.

La pantalla de notificaciones calcula avisos internos para licencias con vencimiento dentro de los próximos 15 días naturales. Las vencidas se identifican por separado. El sistema es de consulta y no envía correos ni modifica los registros de origen.
