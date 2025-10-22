# ExportarAExcel.py
import psycopg
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

class ExportadorExcel:
    def __init__(self):
        load_dotenv()
        self.database_url = os.getenv('DATABASE_URL')
        
    def conectar_bd(self):
        """Conectar a la base de datos"""
        print("🗄️ Conectando a la base de datos...")
        try:
            conn = psycopg.connect(self.database_url)
            print("✅ Conectado a PostgreSQL")
            return conn
        except Exception as e:
            print(f"❌ Error conectando a la BD: {e}")
            return None

    def obtener_estadisticas_tablas(self, conn):
        """Obtener estadísticas de ambas tablas"""
        print("📊 Obteniendo estadísticas de las tablas...")
        estadisticas = {}
        
        try:
            with conn.cursor() as cur:
                # Estadísticas tabla aspirantes
                cur.execute("SELECT COUNT(*) FROM aspirantes;")
                estadisticas['aspirantes_total'] = cur.fetchone()[0]
                
                cur.execute("""
                    SELECT COUNT(DISTINCT departamento) as departamentos,
                           COUNT(DISTINCT programa_interes) as programas,
                           COUNT(DISTINCT municipio) as municipios
                    FROM aspirantes;
                """)
                deptos, programas, municipios = cur.fetchone()
                estadisticas['aspirantes_departamentos'] = deptos
                estadisticas['aspirantes_programas'] = programas
                estadisticas['aspirantes_municipios'] = municipios
                
                # Estadísticas tabla estudiantes
                cur.execute("SELECT COUNT(*) FROM estudiantes;")
                estadisticas['estudiantes_total'] = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(DISTINCT cod_periodo_academico) FROM estudiantes;")
                estadisticas['estudiantes_periodos'] = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(DISTINCT programa_codigo) FROM estudiantes;")
                estadisticas['estudiantes_programas'] = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(DISTINCT sede) FROM estudiantes;")
                estadisticas['estudiantes_sedes'] = cur.fetchone()[0]
            
            return estadisticas
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return None

    def exportar_aspirantes_a_excel(self, conn, nombre_archivo):
        """Exportar tabla aspirantes a Excel"""
        print("📋 Exportando tabla 'aspirantes' a Excel...")
        
        try:
            # Consulta para obtener todos los datos de aspirantes
            query = """
                SELECT 
                    asp_codigo,
                    asp_numero_inscripcion,
                    tipo_documento,
                    documento_numero,
                    nombres,
                    apellidos,
                    correo_electronico,
                    fecha_nacimiento,
                    fecha_expedicion_documento,
                    identidad_genero,
                    telefono_celular,
                    departamento,
                    municipio,
                    estrato_residencia,
                    situacion_laboral,
                    grupo_etnico,
                    nivel_educativo,
                    victima_conflicto,
                    discapacidad,
                    dedicacion_horas_proceso,
                    tiene_computador,
                    programa_interes,
                    modalidad_formacion,
                    disponibilidad_horario,
                    departamento_formacion,
                    url_documento_cargado,
                    asp_fecha_registro,
                    asp_fecha_aprobacion,
                    inscripcion_aprobada,
                    fecha_importacion
                FROM aspirantes
                ORDER BY asp_codigo;
            """
            
            # Leer datos con pandas
            df = pd.read_sql_query(query, conn)
            
            # Crear archivo Excel con múltiples hojas
            with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
                # Hoja principal con todos los datos
                df.to_excel(writer, sheet_name='Aspirantes_Completo', index=False)
                
                # Hoja resumen por departamento
                resumen_deptos = df.groupby('departamento').agg({
                    'asp_codigo': 'count',
                    'municipio': 'nunique'
                }).reset_index()
                resumen_deptos.columns = ['Departamento', 'Total Aspirantes', 'Municipios']
                resumen_deptos = resumen_deptos.sort_values('Total Aspirantes', ascending=False)
                resumen_deptos.to_excel(writer, sheet_name='Resumen_Departamentos', index=False)
                
                # Hoja resumen por programa de interés
                resumen_programas = df.groupby('programa_interes').agg({
                    'asp_codigo': 'count',
                    'departamento': 'nunique'
                }).reset_index()
                resumen_programas.columns = ['Programa de Interés', 'Total Aspirantes', 'Departamentos']
                resumen_programas = resumen_programas.sort_values('Total Aspirantes', ascending=False)
                resumen_programas.to_excel(writer, sheet_name='Resumen_Programas', index=False)
                
                # Hoja resumen por estado de aprobación
                resumen_aprobacion = df.groupby('inscripcion_aprobada').agg({
                    'asp_codigo': 'count'
                }).reset_index()
                resumen_aprobacion.columns = ['Estado Aprobación', 'Total Aspirantes']
                resumen_aprobacion.to_excel(writer, sheet_name='Resumen_Aprobacion', index=False)
            
            print(f"✅ Aspirantes exportados: {len(df):,} registros")
            return True
            
        except Exception as e:
            print(f"❌ Error exportando aspirantes: {e}")
            return False

    def exportar_estudiantes_a_excel(self, conn, nombre_archivo):
        """Exportar tabla estudiantes a Excel"""
        print("📋 Exportando tabla 'estudiantes' a Excel...")
        
        try:
            # Consulta para obtener todos los datos de estudiantes
            query = """
                SELECT 
                    cod_periodo_academico,
                    tipo_documento_estudiante,
                    documento_estudiante,
                    nombres_estudiante,
                    apellidos_estudiante,
                    estado_en_ciclo,
                    fecha_matricula,
                    per_email,
                    per_telefono_movil,
                    periodo_academico,
                    programa_codigo,
                    programa_academico,
                    materia_codigo,
                    materia_nombre,
                    grupo,
                    sede,
                    horarios,
                    cedula_docente,
                    docente,
                    observacion,
                    fecha_importacion
                FROM estudiantes
                ORDER BY cod_periodo_academico, documento_estudiante;
            """
            
            # Leer datos con pandas
            df = pd.read_sql_query(query, conn)
            
            # Crear archivo Excel con múltiples hojas
            with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
                # Hoja principal con todos los datos
                df.to_excel(writer, sheet_name='Estudiantes_Completo', index=False)
                
                # Hoja resumen por periodo académico
                resumen_periodos = df.groupby('cod_periodo_academico').agg({
                    'documento_estudiante': 'count',
                    'programa_codigo': 'nunique',
                    'sede': 'nunique'
                }).reset_index()
                resumen_periodos.columns = ['Periodo Académico', 'Total Estudiantes', 'Programas', 'Sedes']
                resumen_periodos = resumen_periodos.sort_values('Periodo Académico')
                resumen_periodos.to_excel(writer, sheet_name='Resumen_Periodos', index=False)
                
                # Hoja resumen por programa
                resumen_programas = df.groupby(['programa_codigo', 'programa_academico']).agg({
                    'documento_estudiante': 'count',
                    'cod_periodo_academico': 'nunique',
                    'sede': 'nunique'
                }).reset_index()
                resumen_programas.columns = ['Código Programa', 'Programa Académico', 'Total Estudiantes', 'Periodos', 'Sedes']
                resumen_programas = resumen_programas.sort_values('Total Estudiantes', ascending=False)
                resumen_programas.to_excel(writer, sheet_name='Resumen_Programas', index=False)
                
                # Hoja resumen por estado en ciclo
                resumen_estado = df.groupby('estado_en_ciclo').agg({
                    'documento_estudiante': 'count'
                }).reset_index()
                resumen_estado.columns = ['Estado en Ciclo', 'Total Estudiantes']
                resumen_estado = resumen_estado.sort_values('Total Estudiantes', ascending=False)
                resumen_estado.to_excel(writer, sheet_name='Resumen_Estado', index=False)
                
                # Hoja resumen por sede
                resumen_sede = df.groupby('sede').agg({
                    'documento_estudiante': 'count',
                    'programa_codigo': 'nunique'
                }).reset_index()
                resumen_sede.columns = ['Sede', 'Total Estudiantes', 'Programas']
                resumen_sede = resumen_sede.sort_values('Total Estudiantes', ascending=False)
                resumen_sede.to_excel(writer, sheet_name='Resumen_Sedes', index=False)
            
            print(f"✅ Estudiantes exportados: {len(df):,} registros")
            return True
            
        except Exception as e:
            print(f"❌ Error exportando estudiantes: {e}")
            return False

    def exportar_resumen_comparativo(self, conn_aspirantes, conn_estudiantes, nombre_archivo):
        """Exportar resumen comparativo entre aspirantes y estudiantes"""
        print("📊 Exportando resumen comparativo...")
        
        try:
            # Leer datos de ambas tablas
            query_aspirantes = "SELECT departamento, programa_interes FROM aspirantes;"
            query_estudiantes = "SELECT sede, programa_academico FROM estudiantes;"
            
            df_aspirantes = pd.read_sql_query(query_aspirantes, conn_aspirantes)
            df_estudiantes = pd.read_sql_query(query_estudiantes, conn_estudiantes)
            
            with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
                # Resumen comparativo de distribución geográfica
                deptos_aspirantes = df_aspirantes['departamento'].value_counts().reset_index()
                deptos_aspirantes.columns = ['Departamento', 'Aspirantes']
                
                sedes_estudiantes = df_estudiantes['sede'].value_counts().reset_index()
                sedes_estudiantes.columns = ['Sede', 'Estudiantes']
                
                # Crear hoja comparativa
                comparativa = pd.DataFrame({
                    'Métrica': [
                        'Total Registros',
                        'Departamentos/Sedes Únicos',
                        'Programas Únicos',
                        'Fecha de Exportación'
                    ],
                    'Aspirantes': [
                        len(df_aspirantes),
                        df_aspirantes['departamento'].nunique(),
                        df_aspirantes['programa_interes'].nunique(),
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ],
                    'Estudiantes': [
                        len(df_estudiantes),
                        df_estudiantes['sede'].nunique(),
                        df_estudiantes['programa_academico'].nunique(),
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ]
                })
                
                comparativa.to_excel(writer, sheet_name='Resumen_Comparativo', index=False)
                deptos_aspirantes.to_excel(writer, sheet_name='Aspirantes_Por_Depto', index=False)
                sedes_estudiantes.to_excel(writer, sheet_name='Estudiantes_Por_Sede', index=False)
            
            print("✅ Resumen comparativo exportado")
            return True
            
        except Exception as e:
            print(f"❌ Error exportando resumen comparativo: {e}")
            return False

    def ejecutar_exportacion_completa(self):
        """Ejecutar exportación completa de ambos reportes"""
        print("🚀 INICIANDO EXPORTACIÓN A EXCEL")
        print("=" * 50)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Nombres de archivos
        archivo_aspirantes = f"reporte_aspirantes_{timestamp}.xlsx"
        archivo_estudiantes = f"reporte_estudiantes_{timestamp}.xlsx"
        archivo_comparativo = f"resumen_comparativo_{timestamp}.xlsx"
        
        conn = self.conectar_bd()
        if not conn:
            return False
        
        try:
            # 1. Obtener estadísticas
            stats = self.obtener_estadisticas_tablas(conn)
            if stats:
                print(f"\n📈 ESTADÍSTICAS DE LA BASE DE DATOS:")
                print(f"   📋 Aspirantes: {stats['aspirantes_total']:,} registros")
                print(f"     ├── Departamentos: {stats['aspirantes_departamentos']}")
                print(f"     ├── Programas: {stats['aspirantes_programas']}")
                print(f"     └── Municipios: {stats['aspirantes_municipios']}")
                print(f"   👨‍🎓 Estudiantes: {stats['estudiantes_total']:,} registros")
                print(f"     ├── Periodos: {stats['estudiantes_periodos']}")
                print(f"     ├── Programas: {stats['estudiantes_programas']}")
                print(f"     └── Sedes: {stats['estudiantes_sedes']}")
            
            # 2. Exportar aspirantes
            print(f"\n📥 EXPORTANDO ASPIRANTES...")
            if not self.exportar_aspirantes_a_excel(conn, archivo_aspirantes):
                return False
            
            # 3. Exportar estudiantes
            print(f"\n📥 EXPORTANDO ESTUDIANTES...")
            if not self.exportar_estudiantes_a_excel(conn, archivo_estudiantes):
                return False
            
            # 4. Exportar resumen comparativo
            print(f"\n📊 EXPORTANDO RESUMEN COMPARATIVO...")
            if not self.exportar_resumen_comparativo(conn, conn, archivo_comparativo):
                return False
            
            # Resultados finales
            print(f"\n🎉 EXPORTACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 50)
            print(f"📁 Archivos generados:")
            print(f"   📋 {archivo_aspirantes}")
            print(f"   👨‍🎓 {archivo_estudiantes}")
            print(f"   📊 {archivo_comparativo}")
            print(f"🕒 Hora de exportación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en exportación: {e}")
            return False
        finally:
            conn.close()

def main():
    """Interfaz principal"""
    print("📊 EXPORTADOR DE REPORTES A EXCEL")
    print("=" * 50)
    print("REPORTES DISPONIBLES:")
    print("   1. 📋 Reporte Aspirantes (Tabla 'aspirantes')")
    print("   2. 👨‍🎓 Reporte Estudiantes (Tabla 'estudiantes')")
    print("   3. 📈 Resumen Comparativo (Ambas tablas)")
    print()
    print("💡 CARACTERÍSTICAS:")
    print("   - Múltiples hojas por archivo")
    print("   - Resúmenes estadísticos")
    print("   - Formato Excel optimizado")
    print()
    
    # Verificar dependencias
    try:
        import pandas as pd
        import openpyxl
    except ImportError as e:
        print("❌ Faltan dependencias. Instala con:")
        print("   pip install pandas openpyxl")
        return
    
    exportador = ExportadorExcel()
    
    print("¿Continuar con la exportación completa? (s/N): ", end="")
    confirmar = input().strip().lower()
    
    if confirmar not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Exportación cancelada")
        return
    
    print()
    success = exportador.ejecutar_exportacion_completa()
    
    if success:
        print("\n✅ ¡Exportación completada exitosamente!")
        print("💡 Los archivos Excel están listos para su análisis.")
    else:
        print("\n❌ ¡Error en la exportación!")

if __name__ == "__main__":
    main()