# ActualizarMultiplesReportes_COMPLETO.py
import requests
import psycopg
import os
import time
import socket
from datetime import datetime
from dotenv import load_dotenv

class ActualizadorMultiReportes:
    def __init__(self):
        load_dotenv()
        self.database_url = os.getenv('DATABASE_URL')
        
        # Diferentes endpoints para probar
        self.base_urls = [
            "https://siga.talentotech2.com.co/siga_new/web/app.php/api/rest",
            "http://talentotech2prueba.datasae.com/siga_new/web/app.php/api/rest"
        ]
        self.current_base_url = None
        
        self.client_id = "talentotech2_webservice"
        self.secreto = "LcU54XCSqzRU"
        self.access_token = None
        self.auth_token = None
        
        # Credenciales desde .env
        self.siga_username = os.getenv('SIGA_USERNAME', 'api_user')
        self.siga_password = os.getenv('SIGA_PASSWORD', 'Api_user123*')
        
        # Lista de periodos académicos según los proporcionados
        self.periodos_academicos = [
            '2024090208', '2024091608', '2024100708', 
            '2024101510', '2025011112', '2025012710'
        ]

    def verificar_conectividad(self, hostname):
        """Verificar si podemos resolver el nombre de dominio"""
        print(f"🔍 Verificando conectividad a {hostname}...")
        try:
            # Intentar resolver el DNS
            ip = socket.gethostbyname(hostname)
            print(f"   ✅ DNS resuelto: {hostname} -> {ip}")
            
            # Intentar conexión TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((ip, 443 if hostname.startswith('https') else 80))
            sock.close()
            
            if result == 0:
                print(f"   ✅ Conexión TCP exitosa a {ip}")
                return True
            else:
                print(f"   ❌ No se puede conectar a {ip}")
                return False
                
        except socket.gaierror as e:
            print(f"   ❌ Error de DNS: No se puede resolver {hostname}")
            return False
        except Exception as e:
            print(f"   ❌ Error de conectividad: {e}")
            return False

    def probar_endpoints(self):
        """Probar diferentes endpoints hasta encontrar uno que funcione"""
        print("🌐 Probando endpoints disponibles...")
        
        for base_url in self.base_urls:
            hostname = base_url.split('//')[1].split('/')[0]
            print(f"   🔄 Probando: {hostname}")
            
            if self.verificar_conectividad(hostname):
                self.current_base_url = base_url
                print(f"   ✅ Endpoint seleccionado: {hostname}")
                return True
            else:
                print(f"   ❌ Endpoint no disponible: {hostname}")
        
        print("❌ Ningún endpoint está disponible")
        return False

    def conectar_bd(self):
        """Conectar a la base de datos con manejo de errores"""
        print("🗄️ Conectando a la base de datos...")
        try:
            # Mostrar información de conexión (sin contraseña)
            db_info = self.database_url.split('@')[-1] if '@' in self.database_url else self.database_url
            print(f"   🔗 Base de datos: {db_info}")
            
            conn = psycopg.connect(self.database_url)
            
            # Verificar conexión
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                print(f"   ✅ Conectado a: {version.split(',')[0]}")
            
            return conn
            
        except psycopg.OperationalError as e:
            print(f"❌ Error de conexión a la BD: {e}")
            return None
        except Exception as e:
            print(f"❌ Error inesperado en conexión BD: {e}")
            return None

    def obtener_token_acceso(self):
        """Obtener token de acceso con reintentos"""
        if not self.current_base_url:
            print("❌ No hay endpoint configurado")
            return False
            
        print("🔑 Obteniendo token de acceso...")
        
        # Configurar session con mejores timeouts
        session = requests.Session()
        session.trust_env = False  # Evitar usar proxy del sistema
        
        try:
            response = session.post(
                f"{self.current_base_url}/obtener_token",
                data={'client_id': self.client_id, 'secreto': self.secreto},
                timeout=30,
                verify=False  # Solo para testing, quitar en producción
            )
            
            if response.status_code == 200:
                datos = response.json()
                if datos.get('RESPUESTA') == '1':
                    self.access_token = datos.get('access_token')
                    print("✅ Token obtenido")
                    return True
                else:
                    print(f"❌ Error en respuesta API: {datos}")
            else:
                print(f"❌ Error HTTP: {response.status_code} - {response.text}")
                
        except requests.exceptions.SSLError as e:
            print(f"❌ Error SSL: {e}")
            print("💡 Intentando sin verificación SSL...")
            try:
                response = session.post(
                    f"{self.current_base_url}/obtener_token",
                    data={'client_id': self.client_id, 'secreto': self.secreto},
                    timeout=30,
                    verify=False
                )
                if response.status_code == 200:
                    datos = response.json()
                    if datos.get('RESPUESTA') == '1':
                        self.access_token = datos.get('access_token')
                        print("✅ Token obtenido (sin verificación SSL)")
                        return True
            except Exception as e2:
                print(f"❌ Error incluso sin SSL: {e2}")
                
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Error de conexión: {e}")
            
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            
        return False

    def autenticar_usuario(self):
        """Autenticar usuario con credenciales desde .env"""
        print("🔐 Autenticando usuario...")
        try:
            session = requests.Session()
            session.trust_env = False
            
            response = session.post(
                f"{self.current_base_url}/autenticar",
                data={'username': self.siga_username, 'password': self.siga_password},
                headers={'auth_token': self.access_token},
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                datos = response.json()
                if datos.get('RESPUESTA') == '1':
                    self.auth_token = datos.get('TOKEN')
                    print("✅ Usuario autenticado")
                    return True
                else:
                    error_msg = datos.get('ERROR', 'Error desconocido')
                    print(f"❌ Error autenticación: {error_msg}")
                    return False
            else:
                print(f"❌ Error HTTP autenticación: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error autenticación: {e}")
            return False

    def obtener_reporte_1003(self):
        """Obtener reporte 1003 - Aspirantes inscritos"""
        print("📊 Descargando reporte 1003 (Aspirantes)...")
        try:
            session = requests.Session()
            session.trust_env = False
            
            response = session.post(
                f"{self.current_base_url}/talentotech2/informacion_reporte_1003",
                json={"soloactivos": True},
                headers={
                    'token': self.access_token,
                    'token_autenticacion': self.auth_token,
                    'Content-Type': 'application/json'
                },
                timeout=120,
                verify=False
            )
            
            if response.status_code == 200:
                datos = response.json()
                if isinstance(datos, list) and len(datos) > 0:
                    print(f"✅ Reporte 1003 descargado: {len(datos):,} registros")
                    return datos
                else:
                    print(f"❌ Datos inválidos en reporte 1003: {type(datos)}")
                    return None
            else:
                print(f"❌ Error HTTP reporte 1003: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error obteniendo reporte 1003: {e}")
            return None

    def obtener_reporte_992_por_periodo(self, cod_periodo):
        """Obtener reporte 992 para un periodo académico específico"""
        print(f"   📅 Periodo {cod_periodo}...")
        try:
            session = requests.Session()
            session.trust_env = False
            
            payload = {
                "cod_periodo_academico": int(cod_periodo),
                "solo_pendientes_matricula": False
            }
            
            response = session.post(
                f"{self.current_base_url}/talentotech2/informacion_reporte_992",
                json=payload,
                headers={
                    'token': self.access_token,
                    'token_autenticacion': self.auth_token,
                    'Content-Type': 'application/json'
                },
                timeout=60,
                verify=False
            )
            
            if response.status_code == 200:
                datos = response.json()
                if isinstance(datos, list):
                    # Agregar el periodo académico a cada registro
                    for registro in datos:
                        registro['cod_periodo_academico'] = cod_periodo
                    return datos
                else:
                    print(f"     ⚠️ Datos inválidos para periodo {cod_periodo}: {type(datos)}")
                    return []
            else:
                print(f"     ⚠️ Error HTTP para periodo {cod_periodo}: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"     ⚠️ Error obteniendo periodo {cod_periodo}: {e}")
            return []

    def obtener_reporte_992_completo(self):
        """Obtener reporte 992 consolidado de todos los periodos académicos"""
        print("📊 Descargando reporte 992 (Estudiantes - Múltiples Periodos)...")
        print(f"   📚 Periodos a consultar: {len(self.periodos_academicos)}")
        
        datos_consolidados = []
        total_registros = 0
        
        for i, periodo in enumerate(self.periodos_academicos, 1):
            print(f"   {i}/{len(self.periodos_academicos)}:", end=" ")
            datos_periodo = self.obtener_reporte_992_por_periodo(periodo)
            
            if datos_periodo:
                datos_consolidados.extend(datos_periodo)
                total_registros += len(datos_periodo)
                print(f"✅ {len(datos_periodo):,} registros")
            else:
                print(f"❌ 0 registros")
            
            # Pequeña pausa entre requests
            if i < len(self.periodos_academicos):
                time.sleep(1)
        
        if datos_consolidados:
            print(f"✅ Reporte 992 consolidado: {total_registros:,} registros de {len(self.periodos_academicos)} periodos")
            return datos_consolidados
        else:
            print("❌ No se pudieron obtener datos de ningún periodo")
            return None

    def crear_tabla_aspirantes(self, conn):
        """Crear tabla para reporte 1003 - Aspirantes"""
        print("🏗️ Creando tabla 'aspirantes'...")
        try:
            with conn.cursor() as cur:
                # Eliminar tabla si existe
                cur.execute("DROP TABLE IF EXISTS aspirantes;")
                
                # Crear nueva tabla
                cur.execute("""
                    CREATE TABLE aspirantes (
                        id SERIAL PRIMARY KEY,
                        asp_codigo BIGINT UNIQUE NOT NULL,
                        asp_numero_inscripcion INTEGER,
                        tipo_documento VARCHAR(20),
                        documento_numero VARCHAR(30),
                        nombres VARCHAR(150),
                        apellidos VARCHAR(150),
                        correo_electronico VARCHAR(200),
                        fecha_nacimiento DATE,
                        fecha_expedicion_documento DATE,
                        identidad_genero VARCHAR(50),
                        telefono_celular VARCHAR(30),
                        departamento VARCHAR(150),
                        municipio VARCHAR(150),
                        estrato_residencia VARCHAR(30),
                        situacion_laboral VARCHAR(100),
                        grupo_etnico VARCHAR(100),
                        nivel_educativo VARCHAR(100),
                        victima_conflicto VARCHAR(20),
                        discapacidad VARCHAR(150),
                        dedicacion_horas_proceso VARCHAR(20),
                        tiene_computador VARCHAR(20),
                        programa_interes VARCHAR(200),
                        modalidad_formacion VARCHAR(50),
                        disponibilidad_horario VARCHAR(50),
                        departamento_formacion VARCHAR(150),
                        url_documento_cargado TEXT,
                        asp_fecha_registro TIMESTAMP,
                        asp_fecha_aprobacion TIMESTAMP,
                        inscripcion_aprobada VARCHAR(50),
                        fecha_importacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Crear índices
                cur.execute("CREATE INDEX idx_aspirantes_codigo ON aspirantes(asp_codigo);")
                cur.execute("CREATE INDEX idx_aspirantes_documento ON aspirantes(documento_numero);")
                
            conn.commit()
            print("✅ Tabla 'aspirantes' creada")
            return True
            
        except Exception as e:
            print(f"❌ Error creando tabla aspirantes: {e}")
            conn.rollback()
            return False

    def crear_tabla_estudiantes(self, conn):
        """Crear tabla para reporte 992 - Estudiantes (múltiples periodos)"""
        print("🏗️ Creando tabla 'estudiantes'...")
        try:
            with conn.cursor() as cur:
                # Eliminar tabla si existe
                cur.execute("DROP TABLE IF EXISTS estudiantes;")
                
                # Crear nueva tabla con campo para periodo académico
                cur.execute("""
                    CREATE TABLE estudiantes (
                        id SERIAL PRIMARY KEY,
                        cod_periodo_academico VARCHAR(20) NOT NULL,
                        tipo_documento_estudiante VARCHAR(20),
                        documento_estudiante VARCHAR(30),
                        nombres_estudiante VARCHAR(150),
                        apellidos_estudiante VARCHAR(150),
                        estado_en_ciclo VARCHAR(50),
                        fecha_matricula TIMESTAMP,
                        per_email VARCHAR(200),
                        per_telefono_movil VARCHAR(30),
                        periodo_academico VARCHAR(20),
                        programa_codigo VARCHAR(20),
                        programa_academico VARCHAR(150),
                        materia_codigo VARCHAR(20),
                        materia_nombre VARCHAR(200),
                        grupo INTEGER,
                        sede VARCHAR(100),
                        horarios TEXT,
                        cedula_docente VARCHAR(20),
                        docente VARCHAR(150),
                        observacion TEXT,
                        fecha_importacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(documento_estudiante, cod_periodo_academico, materia_codigo, grupo)
                    );
                """)
                
                # Crear índices
                cur.execute("CREATE INDEX idx_estudiantes_documento ON estudiantes(documento_estudiante);")
                cur.execute("CREATE INDEX idx_estudiantes_periodo ON estudiantes(cod_periodo_academico);")
                cur.execute("CREATE INDEX idx_estudiantes_programa ON estudiantes(programa_codigo);")
                cur.execute("CREATE INDEX idx_estudiantes_materia ON estudiantes(materia_codigo);")
                
            conn.commit()
            print("✅ Tabla 'estudiantes' creada")
            return True
            
        except Exception as e:
            print(f"❌ Error creando tabla estudiantes: {e}")
            conn.rollback()
            return False

    def preparar_datos_aspirantes(self, datos):
        """Preparar datos para inserción en tabla aspirantes"""
        print("🔄 Preparando datos para tabla 'aspirantes'...")
        datos_preparados = []
        errores = 0
        
        for i, registro in enumerate(datos):
            try:
                asp_codigo = registro.get('asp_codigo')
                if not asp_codigo:
                    errores += 1
                    continue
                
                dato = (
                    asp_codigo,
                    registro.get('asp_numero_inscripcion'),
                    registro.get('tipo_documento'),
                    registro.get('documento_numero'),
                    registro.get('nombres'),
                    registro.get('apellidos'),
                    registro.get('correo_electronico'),
                    registro.get('fecha_nacimiento'),
                    registro.get('fecha_expedicion_documento'),
                    registro.get('identidad_genero'),
                    registro.get('telefono_celular'),
                    registro.get('departamento'),
                    registro.get('municipio'),
                    registro.get('estrato_residencia'),
                    registro.get('situacion_laboral'),
                    registro.get('grupo_etnico'),
                    registro.get('nivel_educativo'),
                    registro.get('victima_conflicto'),
                    registro.get('discapacidad'),
                    registro.get('dedicacion_horas_proceso'),
                    registro.get('tiene_computador'),
                    registro.get('programa_interes'),
                    registro.get('modalidad_formacion'),
                    registro.get('disponibilidad_horario'),
                    registro.get('departamento_formacion'),
                    registro.get('url_documento_cargado'),
                    registro.get('asp_fecha_registro'),
                    registro.get('asp_fecha_aprobacion'),
                    registro.get('inscripcion_aprobada')
                )
                datos_preparados.append(dato)
                
            except Exception as e:
                errores += 1
                if errores <= 3:
                    print(f"   ⚠️ Error preparando aspirante {i}: {e}")
        
        print(f"✅ Aspirantes preparados: {len(datos_preparados):,} válidos, {errores:,} errores")
        return datos_preparados

    def preparar_datos_estudiantes(self, datos):
        """Preparar datos para inserción en tabla estudiantes"""
        print("🔄 Preparando datos para tabla 'estudiantes'...")
        datos_preparados = []
        errores = 0
        
        for i, registro in enumerate(datos):
            try:
                documento = registro.get('documento_estudiante')
                periodo = registro.get('cod_periodo_academico')
                
                if not documento or not periodo:
                    errores += 1
                    continue
                
                dato = (
                    periodo,  # cod_periodo_academico
                    registro.get('tipo_documento_estudiante'),
                    documento,
                    registro.get('nombres_estudiante'),
                    registro.get('apellidos_estudiante'),
                    registro.get('estado_en_ciclo'),
                    registro.get('fecha_matricula'),
                    registro.get('per_email'),
                    registro.get('per_telefono_movil'),
                    registro.get('periodo_academico'),
                    registro.get('programa_codigo'),
                    registro.get('programa_academico'),
                    registro.get('materia_codigo'),
                    registro.get('materia_nombre'),
                    registro.get('grupo'),
                    registro.get('sede'),
                    registro.get('horarios'),
                    registro.get('cedula_docente'),
                    registro.get('docente'),
                    registro.get('observacion')
                )
                datos_preparados.append(dato)
                
            except Exception as e:
                errores += 1
                if errores <= 3:
                    print(f"   ⚠️ Error preparando estudiante {i}: {e}")
        
        print(f"✅ Estudiantes preparados: {len(datos_preparados):,} válidos, {errores:,} errores")
        return datos_preparados

    def insertar_datos_masivo(self, conn, datos_preparados, tabla, sql_insercion):
        """Inserción masiva optimizada para cualquier tabla"""
        print(f"💾 Insertando datos en tabla '{tabla}'...")
        
        if not datos_preparados:
            print(f"❌ No hay datos preparados para {tabla}")
            return False
        
        inicio = time.time()
        lote_size = 2000
        total_insertados = 0
        
        # Insertar por lotes
        for i in range(0, len(datos_preparados), lote_size):
            lote = datos_preparados[i:i + lote_size]
            
            try:
                with conn.cursor() as cur:
                    cur.executemany(sql_insercion, lote)
                conn.commit()
                
                total_insertados += len(lote)
                
                # Progreso
                porcentaje = min(100, (i + len(lote)) / len(datos_preparados) * 100)
                tiempo_transcurrido = time.time() - inicio
                velocidad = total_insertados / tiempo_transcurrido if tiempo_transcurrido > 0 else 0
                
                print(f"📦 {tabla} - Lote {i//lote_size + 1}: {len(lote):,} reg | "
                      f"Total: {total_insertados:,} | "
                      f"Progreso: {porcentaje:.1f}% | "
                      f"Velocidad: {velocidad:.0f} reg/seg")
                      
            except Exception as e:
                print(f"❌ Error insertando lote {i//lote_size + 1} en {tabla}: {e}")
                conn.rollback()
                if lote_size > 100:
                    lote_size = max(100, lote_size // 2)
                    print(f"🔧 Reduciendo tamaño de lote a {lote_size}")
                continue
        
        tiempo_total = time.time() - inicio
        if total_insertados > 0:
            print(f"✅ {tabla} - Inserción completada: {total_insertados:,} registros en {tiempo_total:.2f} segundos")
            return True
        else:
            print(f"❌ No se insertó ningún registro en {tabla}")
            return False

    def procesar_reporte_1003(self, conn, datos):
        """Procesar completo el reporte 1003"""
        print("\n" + "="*50)
        print("📋 PROCESANDO REPORTE 1003 - ASPIRANTES")
        print("="*50)
        
        # Preparar datos
        datos_preparados = self.preparar_datos_aspirantes(datos)
        if not datos_preparados:
            return False
        
        # SQL de inserción para aspirantes
        sql_aspirantes = """
            INSERT INTO aspirantes (
                asp_codigo, asp_numero_inscripcion, tipo_documento, documento_numero,
                nombres, apellidos, correo_electronico, fecha_nacimiento,
                fecha_expedicion_documento, identidad_genero, telefono_celular,
                departamento, municipio, estrato_residencia, situacion_laboral,
                grupo_etnico, nivel_educativo, victima_conflicto, discapacidad,
                dedicacion_horas_proceso, tiene_computador, programa_interes,
                modalidad_formacion, disponibilidad_horario, departamento_formacion,
                url_documento_cargado, asp_fecha_registro, asp_fecha_aprobacion,
                inscripcion_aprobada
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        
        # Insertar datos
        return self.insertar_datos_masivo(conn, datos_preparados, "aspirantes", sql_aspirantes)

    def procesar_reporte_992(self, conn, datos):
        """Procesar completo el reporte 992 consolidado"""
        print("\n" + "="*50)
        print("📋 PROCESANDO REPORTE 992 - ESTUDIANTES (MÚLTIPLES PERIODOS)")
        print("="*50)
        
        # Preparar datos
        datos_preparados = self.preparar_datos_estudiantes(datos)
        if not datos_preparados:
            return False
        
        # SQL de inserción para estudiantes con manejo de duplicados
        sql_estudiantes = """
            INSERT INTO estudiantes (
                cod_periodo_academico, tipo_documento_estudiante, documento_estudiante, 
                nombres_estudiante, apellidos_estudiante, estado_en_ciclo, fecha_matricula, 
                per_email, per_telefono_movil, periodo_academico, programa_codigo, 
                programa_academico, materia_codigo, materia_nombre, grupo, sede, 
                horarios, cedula_docente, docente, observacion
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (documento_estudiante, cod_periodo_academico, materia_codigo, grupo) 
            DO UPDATE SET
                estado_en_ciclo = EXCLUDED.estado_en_ciclo,
                fecha_matricula = EXCLUDED.fecha_matricula,
                per_email = EXCLUDED.per_email,
                per_telefono_movil = EXCLUDED.per_telefono_movil,
                periodo_academico = EXCLUDED.periodo_academico,
                programa_academico = EXCLUDED.programa_academico,
                materia_nombre = EXCLUDED.materia_nombre,
                sede = EXCLUDED.sede,
                horarios = EXCLUDED.horarios,
                cedula_docente = EXCLUDED.cedula_docente,
                docente = EXCLUDED.docente,
                observacion = EXCLUDED.observacion,
                fecha_importacion = CURRENT_TIMESTAMP;
        """
        
        # Insertar datos
        return self.insertar_datos_masivo(conn, datos_preparados, "estudiantes", sql_estudiantes)

    def ejecutar_actualizacion_completa(self):
        """Ejecutar proceso completo para ambos reportes"""
        print("🚀 INICIANDO ACTUALIZACIÓN MULTIPLE")
        print("=" * 60)
        print(f"👤 Usuario: {self.siga_username}")
        print(f"📊 Reportes: 1003 (Aspirantes) + 992 (Estudiantes - {len(self.periodos_academicos)} periodos)")
        print()
        
        tiempo_inicio = time.time()
        
        # 1. Probar endpoints primero
        if not self.probar_endpoints():
            return False
        
        print(f"🔗 Endpoint seleccionado: {self.current_base_url}")
        
        # 2. Conectar a la base de datos
        conn = self.conectar_bd()
        if not conn:
            return False
        
        # 3. Autenticación API
        if not self.obtener_token_acceso():
            conn.close()
            return False
            
        if not self.autenticar_usuario():
            conn.close()
            return False
        
        # 4. Obtener datos de ambos reportes
        print("\n📥 DESCARGANDO REPORTES...")
        datos_1003 = self.obtener_reporte_1003()
        datos_992 = self.obtener_reporte_992_completo()
        
        if not datos_1003 and not datos_992:
            print("❌ No se pudieron descargar ninguno de los reportes")
            conn.close()
            return False
        
        # 5. Crear tablas
        print("\n🏗️ CREANDO ESTRUCTURAS DE TABLAS...")
        tablas_creadas = True
        
        if datos_1003:
            tablas_creadas &= self.crear_tabla_aspirantes(conn)
        
        if datos_992:
            tablas_creadas &= self.crear_tabla_estudiantes(conn)
        
        if not tablas_creadas:
            conn.close()
            return False
        
        # 6. Procesar reportes
        resultados = {}
        
        if datos_1003:
            resultados['aspirantes'] = self.procesar_reporte_1003(conn, datos_1003)
        
        if datos_992:
            resultados['estudiantes'] = self.procesar_reporte_992(conn, datos_992)
        
        # 7. Estadísticas finales
        print("\n" + "="*60)
        print("📈 ESTADÍSTICAS FINALES")
        print("="*60)
        
        with conn.cursor() as cur:
            if datos_1003:
                cur.execute("SELECT COUNT(*) FROM aspirantes;")
                total_aspirantes = cur.fetchone()[0]
                print(f"📊 Aspirantes: {total_aspirantes:,} registros")
            
            if datos_992:
                cur.execute("SELECT COUNT(*) FROM estudiantes;")
                total_estudiantes = cur.fetchone()[0]
                cur.execute("SELECT COUNT(DISTINCT cod_periodo_academico) FROM estudiantes;")
                periodos_con_datos = cur.fetchone()[0]
                print(f"📊 Estudiantes: {total_estudiantes:,} registros")
                print(f"📚 Periodos con datos: {periodos_con_datos}/{len(self.periodos_academicos)}")
        
        conn.close()
        
        # Resultados
        tiempo_total = time.time() - tiempo_inicio
        print(f"\n🎉 ACTUALIZACIÓN COMPLETADA")
        print("=" * 50)
        if datos_1003:
            print(f"✅ Reporte 1003: {len(datos_1003):,} aspirantes descargados")
        if datos_992:
            print(f"✅ Reporte 992: {len(datos_992):,} estudiantes de {len(self.periodos_academicos)} periodos")
        print(f"⏱️ Tiempo total: {tiempo_total:.2f} segundos")
        print(f"🕒 Hora de actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return any(resultados.values())

def verificar_variables_entorno():
    """Verificar que todas las variables de entorno estén configuradas"""
    load_dotenv()
    
    variables_requeridas = ['DATABASE_URL', 'SIGA_USERNAME', 'SIGA_PASSWORD']
    faltantes = []
    
    for var in variables_requeridas:
        if not os.getenv(var):
            faltantes.append(var)
    
    return faltantes

def main():
    """Interfaz principal"""
    print("🔄 ACTUALIZADOR MÚLTIPLE - DOS REPORTES")
    print("=" * 50)
    print("REPORTES INCLUIDOS:")
    print("   1. 📋 Reporte 1003 - Aspirantes inscritos")
    print("   2. 👨‍🎓 Reporte 992 - Estudiantes (6 periodos académicos)")
    print()
    print("PERIODOS ACADÉMICOS:")
    print("   2024090208, 2024091608, 2024100708")
    print("   2024101510, 2025011112, 2025012710")
    print()
    print("💡 MEJORAS: Verificación de conectividad + 6 periodos consolidados")
    print()
    
    # Verificar variables de entorno
    variables_faltantes = verificar_variables_entorno()
    if variables_faltantes:
        print("❌ ERROR: Faltan variables en el archivo .env:")
        for var in variables_faltantes:
            print(f"   - {var}")
        return
    
    # Mostrar configuración
    db_url = os.getenv('DATABASE_URL')
    db_info = db_url.split('@')[-1] if '@' in db_url else db_url
    username = os.getenv('SIGA_USERNAME')
    
    print(f"✅ Configuración encontrada:")
    print(f"   🗄️  Base de datos: {db_info}")
    print(f"   👤 Usuario SIGA: {username}")
    print()
    
    confirmar = input("¿Continuar con la actualización múltiple? (s/N): ").strip().lower()
    if confirmar not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Operación cancelada")
        return
    
    print()
    actualizador = ActualizadorMultiReportes()
    success = actualizador.ejecutar_actualizacion_completa()
    
    if success:
        print("\n✅ ¡Base de datos actualizada exitosamente con ambos reportes!")
    else:
        print("\n❌ ¡Error en la actualización!")

if __name__ == "__main__":
    main()