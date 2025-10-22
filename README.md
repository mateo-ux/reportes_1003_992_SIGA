# TalentoTech Data Updater

Actualización automática de datos desde SIGA API a PostgreSQL.

## 🚀 Características

- Reporte 1003: Aspirantes inscritos (64K+ registros)
- Reporte 992: Estudiantes de 6 periodos académicos (40K+ registros)
- API REST para ejecución remota
- Ejecución local y en Render

## 📊 Estructura de Base de Datos

### Tabla `aspirantes`
- Datos de aspirantes inscritos
- 64,249 registros

### Tabla `estudiantes` 
- Datos de estudiantes por periodo académico
- 40,149 registros consolidados
- 6 periodos: 2024090208, 2024091608, 2024100708, 2024101510, 2025011112, 2025012710

## 🛠️ Instalación Local

1. Clonar repositorio:
```bash
git clone <tu-repositorio>
cd render_1003