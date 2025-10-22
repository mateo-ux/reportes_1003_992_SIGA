# Reportes SIGA - API de Actualización

API para actualizar datos desde SIGA hacia PostgreSQL, ejecutable desde Google Apps Script.

## 🚀 Características

- Actualización de Reporte 1003 (Aspirantes)
- Actualización de Reporte 992 (Estudiantes - 6 periodos)
- API REST para ejecución remota
- Compatible con Google Apps Script

## 📊 Endpoints

### `POST /api/update`
Ejecuta la actualización de datos en segundo plano.

**Ejemplo de respuesta:**
```json
{
  "status": "success",
  "message": "Actualización iniciada en segundo plano",
  "check_status": "/api/status"
}