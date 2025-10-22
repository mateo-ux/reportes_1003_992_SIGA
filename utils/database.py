# utils/database.py
import psycopg
import os
from dotenv import load_dotenv

class DatabaseManager:
    def __init__(self):
        load_dotenv()
        self.database_url = os.getenv('DATABASE_URL')
    
    def connect(self):
        """Conectar a la base de datos"""
        try:
            return psycopg.connect(self.database_url)
        except Exception as e:
            print(f"❌ Error conectando a BD: {e}")
            return None
    
    def create_aspirantes_table(self, conn):
        """Crear tabla aspirantes"""
        try:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS aspirantes;")
                cur.execute("""
                    CREATE TABLE aspirantes (
                        id SERIAL PRIMARY KEY,
                        asp_codigo BIGINT UNIQUE NOT NULL,
                        -- ... (resto de la estructura que ya tienes)
                        fecha_importacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                # Crear índices...
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
    
    def create_estudiantes_table(self, conn):
        """Crear tabla estudiantes"""
        try:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS estudiantes;")
                cur.execute("""
                    CREATE TABLE estudiantes (
                        id SERIAL PRIMARY KEY,
                        cod_periodo_academico VARCHAR(20) NOT NULL,
                        -- ... (resto de la estructura que ya tienes)
                        UNIQUE(documento_estudiante, cod_periodo_academico, materia_codigo, grupo)
                    );
                """)
                # Crear índices...
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
    
    def insert_aspirantes_data(self, conn, datos):
        """Insertar datos de aspirantes"""
        # ... (tu código de inserción por lotes)
        pass
    
    def insert_estudiantes_data(self, conn, datos):
        """Insertar datos de estudiantes"""
        # ... (tu código de inserción por lotes)
        pass
    
    def get_database_stats(self, conn):
        """Obtener estadísticas de la base de datos"""
        stats = {}
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM aspirantes;")
                stats['aspirantes'] = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM estudiantes;")
                stats['estudiantes'] = cur.fetchone()[0]
        except:
            pass
        return stats