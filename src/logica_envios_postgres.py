import psycopg2
from psycopg2 import pool
import datetime
import os

# =====================================================
# CONFIGURACIÓN DE CONEXIÓN A POSTGRESQL
# =====================================================

# Usa variables de entorno para las credenciales (seguro para producción)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'ep-crimson-butterfly-aht6exsh-pooler.c-3.us-east-1.aws.neon.tech'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'neondb'),
    'user': os.getenv('DB_USER', 'neondb_owner'),
    'password': os.getenv('DB_PASSWORD', 'npg_XsZEkIfy58xG'),
    'sslmode': os.getenv('DB_SSLMODE', 'require')
}

# Pool de conexiones para mejor performance
connection_pool = None

def inicializar_pool():
    """Inicializa el pool de conexiones a PostgreSQL"""
    global connection_pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1,  # mínimo de conexiones
            10,  # máximo de conexiones
            **DB_CONFIG
        )
        if connection_pool:
            return True, "Pool de conexiones creado exitosamente"
        return False, "Error al crear el pool"
    except Exception as e:
        return False, f"Error al conectar a PostgreSQL: {str(e)}"


def obtener_conexion():
    """Obtiene una conexión del pool"""
    if connection_pool:
        return connection_pool.getconn()
    return None


def liberar_conexion(conn):
    """Devuelve una conexión al pool"""
    if connection_pool and conn:
        connection_pool.putconn(conn)


# =====================================================
# INICIALIZACIÓN DE BASE DE DATOS
# =====================================================

def crear_tabla_pedidos():
    """
    Crea la tabla 'pedidos' si no existe.
    Retorna: (exito: bool, mensaje: str)
    """
    sql_crear_tabla = """
    CREATE TABLE IF NOT EXISTS pedidos (
        id SERIAL PRIMARY KEY,
        codigo_tracking VARCHAR(50) UNIQUE NOT NULL,
        nombre_cliente VARCHAR(200) NOT NULL,
        direccion VARCHAR(300) NOT NULL,
        provincia VARCHAR(100) NOT NULL,
        estado VARCHAR(100) NOT NULL DEFAULT 'Pendiente',
        fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Índices para mejorar búsquedas
    CREATE INDEX IF NOT EXISTS idx_codigo_tracking ON pedidos(codigo_tracking);
    CREATE INDEX IF NOT EXISTS idx_nombre_cliente ON pedidos(nombre_cliente);
    CREATE INDEX IF NOT EXISTS idx_estado ON pedidos(estado);
    CREATE INDEX IF NOT EXISTS idx_fecha_creacion ON pedidos(fecha_creacion);
    """
    
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(sql_crear_tabla)
        conn.commit()
        cursor.close()
        return True, "Tabla 'pedidos' creada/verificada exitosamente"
    
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Error al crear tabla: {str(e)}"
    
    finally:
        if conn:
            liberar_conexion(conn)


def inicializar_base_datos():
    """
    Inicializa el pool de conexiones y crea la tabla si no existe.
    Retorna: (exito: bool, mensaje: str)
    """
    # Inicializar pool
    exito_pool, msg_pool = inicializar_pool()
    if not exito_pool:
        return False, msg_pool
    
    # Crear tabla
    exito_tabla, msg_tabla = crear_tabla_pedidos()
    if not exito_tabla:
        return False, msg_tabla
    
    return True, "Base de datos inicializada correctamente"


# =====================================================
# FUNCIONES DE VALIDACIÓN (SIN CAMBIOS)
# =====================================================

def validar_opcion(seleccion, rango1, rango2):
    """Valida si una selección está dentro de un rango."""
    try:
        seleccion_int = int(seleccion)
        if rango1 <= seleccion_int <= rango2:
            return True, seleccion_int, ""
        else:
            return False, None, f"El valor debe estar entre {rango1} y {rango2}"
    except ValueError:
        return False, None, "El valor debe ser un número entero"


def validar_nombre(nombre):
    """Valida que el nombre solo contenga letras y espacios."""
    if nombre.strip() == "":
        return False, "El nombre no puede estar vacío"
    
    for c in nombre:
        if not c.isalpha() and c != " ":
            return False, "El nombre solo puede contener letras y espacios"
    
    return True, ""


def validar_direccion(direccion):
    """Valida que la dirección no esté vacía."""
    if direccion.strip() == "":
        return False, "La dirección no puede estar vacía"
    
    for c in direccion:
        if not c.isalnum() and c != " ":
            return False, "La dirección solo puede contener letras, números y espacios"
    
    return True, ""


def validar_provincia(provincia):
    """Valida que la provincia esté en la lista de provincias argentinas."""
    provincias = (
        "Buenos Aires", "Catamarca", "Chaco", "Chubut", "Cordoba", "Corrientes",
        "Entre Rios", "Formosa", "Jujuy", "La Pampa", "La Rioja", "Mendoza",
        "Misiones", "Neuquen", "Rio Negro", "Salta", "San Juan", "San Luis",
        "Santa Cruz", "Santa Fe", "Santiago Del Estero", "Tierra Del Fuego", "Tucuman"
    )
    
    provincia_sin_acentos = sacar_acentos(provincia)
    if provincia_sin_acentos in provincias:
        return True, ""
    else:
        return False, "Provincia no válida"


def validar_codigo_envio(codigo):
    """Valida que el código tenga formato ENVXXX."""
    codigo = codigo.upper()
    if codigo[:3] != "ENV":
        return False, "El código debe comenzar con ENV"
    if not codigo[3:].isdigit():
        return False, "El código debe tener números después de ENV"
    if len(codigo[3:]) < 3:
        return False, "El código debe tener al menos 3 dígitos (ej: ENV001)"
    
    return True, ""


def validar_horario(fecha_str):
    """Valida y formatea una fecha en formato DD/MM/AAAA HH:MM"""
    fecha = fecha_str.replace("/", " ").replace(":", " ").replace("-", " ")
    
    try:
        partes = fecha.split()
        if len(partes) != 5:
            return False, "", "Formato incorrecto. Use DD/MM/AAAA HH:MM"
        
        d, m, y, hora, minuto = map(int, partes)
        
        if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0):
            n = 29
        else:
            n = 28
        
        dias_posibles = (31, n, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        
        if y <= 0 or y > 9999:
            return False, "", "Año inválido"
        if m <= 0 or m > 12:
            return False, "", "Mes inválido"
        if d < 1 or d > dias_posibles[m - 1]:
            return False, "", "Día inválido"
        if hora < 0 or hora > 23:
            return False, "", "Hora inválida"
        if minuto < 0 or minuto > 59:
            return False, "", "Minuto inválido"
        
        fecha_formateada = f"{d:02d}/{m:02d}/{y} {hora:02d}:{minuto:02d}"
        return True, fecha_formateada, ""
        
    except ValueError:
        return False, "", "Formato incorrecto. Use DD/MM/AAAA HH:MM"


# =====================================================
# FUNCIONES AUXILIARES
# =====================================================

def sacar_acentos(entrada):
    """Elimina acentos de una cadena de texto."""
    acentos = (
        ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
        ("Á", "A"), ("É", "E"), ("Í", "I"), ("Ó", "O"), ("Ú", "U")
    )
    for i, j in acentos:
        entrada = entrada.replace(i, j)
    return entrada


def formato_fechas():
    """Retorna la fecha y hora actual en formato DD/MM/AAAA HH:MM"""
    fecha_original = datetime.datetime.now()
    fecha_final = f"{fecha_original.day:02d}/{fecha_original.month:02d}/{fecha_original.year} {fecha_original.hour:02d}:{fecha_original.minute:02d}"
    return fecha_final


def codigo_envio(numero):
    """
    Genera un código de envío único incrementando el contador.
    Retorna: (codigo: str, nuevo_contador: int)
    """
    numero += 1
    codigo = f"ENV{numero:03d}"
    return codigo, numero


# =====================================================
# FUNCIONES DE BASE DE DATOS
# =====================================================

def obtener_ultimo_contador():
    """
    Obtiene el último ID usado en la tabla pedidos.
    Retorna: numero_contador (int)
    """
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM pedidos")
        resultado = cursor.fetchone()
        cursor.close()
        
        if resultado[0] is None:
            return 0
        return resultado[0]
    
    except Exception as e:
        print(f"Error al obtener contador: {e}")
        return 0
    
    finally:
        if conn:
            liberar_conexion(conn)


def base_datos_tiene_datos():
    """
    Verifica si la tabla pedidos tiene datos.
    Retorna: bool
    """
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        resultado = cursor.fetchone()
        cursor.close()
        
        return resultado[0] > 0
    
    except Exception as e:
        print(f"Error al verificar datos: {e}")
        return False
    
    finally:
        if conn:
            liberar_conexion(conn)


# =====================================================
# FUNCIONES PRINCIPALES (LÓGICA DE NEGOCIO)
# =====================================================

def agregar_envio(contador, nombre_cliente, direccion, provincia):
    """
    Crea un nuevo envío y lo guarda en PostgreSQL.
    
    Retorna: dict con la estructura:
        {
            'exito': bool,
            'mensaje': str,
            'pedido': dict o None,
            'nuevo_contador': int
        }
    """
    # Validar nombre
    es_valido, msg_error = validar_nombre(nombre_cliente)
    if not es_valido:
        return {
            'exito': False,
            'mensaje': msg_error,
            'pedido': None,
            'nuevo_contador': contador
        }
    
    # Validar dirección
    es_valido, msg_error = validar_direccion(direccion)
    if not es_valido:
        return {
            'exito': False,
            'mensaje': msg_error,
            'pedido': None,
            'nuevo_contador': contador
        }
    
    # Validar provincia
    es_valido, msg_error = validar_provincia(provincia)
    if not es_valido:
        return {
            'exito': False,
            'mensaje': msg_error,
            'pedido': None,
            'nuevo_contador': contador
        }
    
    # Generar código
    codigo, nuevo_contador = codigo_envio(contador)
    
    nombre_cliente = sacar_acentos(nombre_cliente.title())
    direccion = sacar_acentos(direccion.title())
    provincia = sacar_acentos(provincia.title())
    
    estado = "Pendiente"
    
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO pedidos (codigo_tracking, nombre_cliente, direccion, provincia, estado)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, codigo_tracking, nombre_cliente, direccion, provincia, estado, fecha_creacion
        """, (codigo, nombre_cliente, direccion, provincia, estado))
        
        resultado = cursor.fetchone()
        conn.commit()
        cursor.close()
        
        pedido = {
            'contador': resultado[0],
            'codigo': resultado[1],
            'cliente': resultado[2],
            'direccion': resultado[3],
            'provincia': resultado[4],
            'estado': resultado[5],
            'fecha': resultado[6].strftime('%d/%m/%Y %H:%M')
        }
        
        return {
            'exito': True,
            'mensaje': 'Envío creado exitosamente',
            'pedido': pedido,
            'nuevo_contador': resultado[0]
        }
    
    except Exception as e:
        if conn:
            conn.rollback()
        return {
            'exito': False,
            'mensaje': f'Error al guardar pedido: {str(e)}',
            'pedido': None,
            'nuevo_contador': contador
        }
    
    finally:
        if conn:
            liberar_conexion(conn)


def consultar_envio_por_codigo(codigo):
    """
    Busca un envío por su código de tracking.
    
    Retorna: dict con la estructura:
        {
            'encontrado': bool,
            'pedido': dict o None,
            'mensaje': str
        }
    """
    es_valido, msg_error = validar_codigo_envio(codigo)
    if not es_valido:
        return {
            'encontrado': False,
            'pedido': None,
            'mensaje': msg_error
        }
    
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, codigo_tracking, nombre_cliente, direccion, provincia, estado, fecha_creacion
            FROM pedidos
            WHERE UPPER(codigo_tracking) = UPPER(%s)
        """, (codigo,))
        
        resultado = cursor.fetchone()
        cursor.close()
        
        if resultado:
            pedido = {
                'contador': resultado[0],
                'codigo': resultado[1],
                'cliente': resultado[2],
                'direccion': resultado[3],
                'provincia': resultado[4],
                'estado': resultado[5],
                'fecha': resultado[6].strftime('%d/%m/%Y %H:%M')
            }
            
            return {
                'encontrado': True,
                'pedido': pedido,
                'mensaje': 'Pedido encontrado'
            }
        else:
            return {
                'encontrado': False,
                'pedido': None,
                'mensaje': 'No se encontró un pedido con ese código'
            }
    
    except Exception as e:
        return {
            'encontrado': False,
            'pedido': None,
            'mensaje': f'Error al consultar: {str(e)}'
        }
    
    finally:
        if conn:
            liberar_conexion(conn)


def consultar_envios_por_cliente(nombre_cliente):
    """
    Busca todos los envíos de un cliente.
    
    Retorna: dict con la estructura:
        {
            'encontrados': int,
            'pedidos': list,
            'mensaje': str
        }
    """
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, codigo_tracking, nombre_cliente, direccion, provincia, estado, fecha_creacion
            FROM pedidos
            WHERE LOWER(nombre_cliente) LIKE LOWER(%s)
            ORDER BY fecha_creacion DESC
        """, (f'%{nombre_cliente}%',))
        
        resultados = cursor.fetchall()
        cursor.close()
        
        pedidos_encontrados = []
        for resultado in resultados:
            pedido = {
                'contador': resultado[0],
                'codigo': resultado[1],
                'cliente': resultado[2],
                'direccion': resultado[3],
                'provincia': resultado[4],
                'estado': resultado[5],
                'fecha': resultado[6].strftime('%d/%m/%Y %H:%M')
            }
            pedidos_encontrados.append(pedido)
        
        if pedidos_encontrados:
            return {
                'encontrados': len(pedidos_encontrados),
                'pedidos': pedidos_encontrados,
                'mensaje': f'Se encontraron {len(pedidos_encontrados)} pedido(s)'
            }
        else:
            return {
                'encontrados': 0,
                'pedidos': [],
                'mensaje': 'No se encontraron pedidos para ese cliente'
            }
    
    except Exception as e:
        return {
            'encontrados': 0,
            'pedidos': [],
            'mensaje': f'Error al consultar: {str(e)}'
        }
    
    finally:
        if conn:
            liberar_conexion(conn)


def consultar_envios_por_fecha(fecha_inicio, fecha_fin):
    """
    Busca envíos en un rango de fechas.
    
    Retorna: dict con la estructura:
        {
            'encontrados': int,
            'pedidos': list,
            'mensaje': str
        }
    """
    # Validar fechas
    es_valido_inicio, fecha_inicio_fmt, msg_error = validar_horario(fecha_inicio)
    if not es_valido_inicio:
        return {
            'encontrados': 0,
            'pedidos': [],
            'mensaje': f'Fecha inicio inválida: {msg_error}'
        }
    
    es_valido_fin, fecha_fin_fmt, msg_error = validar_horario(fecha_fin)
    if not es_valido_fin:
        return {
            'encontrados': 0,
            'pedidos': [],
            'mensaje': f'Fecha fin inválida: {msg_error}'
        }
    
    # Convertir formato DD/MM/YYYY HH:MM a timestamp para PostgreSQL
    try:
        fecha_inicio_dt = datetime.datetime.strptime(fecha_inicio_fmt, '%d/%m/%Y %H:%M')
        fecha_fin_dt = datetime.datetime.strptime(fecha_fin_fmt, '%d/%m/%Y %H:%M')
    except ValueError as e:
        return {
            'encontrados': 0,
            'pedidos': [],
            'mensaje': f'Error en formato de fecha: {str(e)}'
        }
    
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, codigo_tracking, nombre_cliente, direccion, provincia, estado, fecha_creacion
            FROM pedidos
            WHERE fecha_creacion BETWEEN %s AND %s
            ORDER BY fecha_creacion DESC
        """, (fecha_inicio_dt, fecha_fin_dt))
        
        resultados = cursor.fetchall()
        cursor.close()
        
        pedidos_encontrados = []
        for resultado in resultados:
            pedido = {
                'contador': resultado[0],
                'codigo': resultado[1],
                'cliente': resultado[2],
                'direccion': resultado[3],
                'provincia': resultado[4],
                'estado': resultado[5],
                'fecha': resultado[6].strftime('%d/%m/%Y %H:%M')
            }
            pedidos_encontrados.append(pedido)
        
        if pedidos_encontrados:
            return {
                'encontrados': len(pedidos_encontrados),
                'pedidos': pedidos_encontrados,
                'mensaje': f'Se encontraron {len(pedidos_encontrados)} pedido(s)'
            }
        else:
            return {
                'encontrados': 0,
                'pedidos': [],
                'mensaje': 'No se encontraron pedidos en ese rango de fechas'
            }
    
    except Exception as e:
        return {
            'encontrados': 0,
            'pedidos': [],
            'mensaje': f'Error al consultar: {str(e)}'
        }
    
    finally:
        if conn:
            liberar_conexion(conn)


def listar_todos_envios():
    """
    Lista todos los envíos de la base de datos.
    
    Retorna: dict con la estructura:
        {
            'total': int,
            'pedidos': list,
            'mensaje': str
        }
    """
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, codigo_tracking, nombre_cliente, direccion, provincia, estado, fecha_creacion
            FROM pedidos
            ORDER BY fecha_creacion DESC
        """)
        
        resultados = cursor.fetchall()
        cursor.close()
        
        pedidos = []
        for resultado in resultados:
            pedido = {
                'contador': resultado[0],
                'codigo': resultado[1],
                'cliente': resultado[2],
                'direccion': resultado[3],
                'provincia': resultado[4],
                'estado': resultado[5],
                'fecha': resultado[6].strftime('%d/%m/%Y %H:%M')
            }
            pedidos.append(pedido)
        
        return {
            'total': len(pedidos),
            'pedidos': pedidos,
            'mensaje': f'Se encontraron {len(pedidos)} pedido(s) en total'
        }
    
    except Exception as e:
        return {
            'total': 0,
            'pedidos': [],
            'mensaje': f'Error al listar: {str(e)}'
        }
    
    finally:
        if conn:
            liberar_conexion(conn)


def cambiar_estado_manual(codigo, nuevo_estado):
    """Cambia el estado de un pedido a un valor específico"""
    conn = obtener_conexion()
    if not conn:
        return {'exito': False, 'mensaje': 'Error de conexión a BD'}

    try:
        cursor = conn.cursor()
        
        # Verificar que el pedido existe
        cursor.execute("SELECT codigo_tracking FROM pedidos WHERE codigo_tracking = %s", (codigo,))
        if not cursor.fetchone():
            return {'exito': False, 'mensaje': 'Pedido no encontrado'}

        # Actualizar estado
        cursor.execute("UPDATE pedidos SET estado = %s WHERE codigo_tracking = %s", (nuevo_estado, codigo))
        conn.commit()
        cursor.close()
        
        return {'exito': True, 'mensaje': f'Estado actualizado a: {nuevo_estado}'}

    except Exception as e:
        conn.rollback()
        return {'exito': False, 'mensaje': str(e)}
    finally:
        liberar_conexion(conn)

def obtener_estadisticas():
    """Calcula métricas del sistema"""
    conn = obtener_conexion()
    if not conn:
        return {'total_pedidos': 0, 'total_provincias': 0}

    try:
        cursor = conn.cursor()
        # Contar total de pedidos
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total_pedidos = cursor.fetchone()[0]
        
        # Contar provincias únicas (lugares distintos a los que hemos enviado)
        cursor.execute("SELECT COUNT(DISTINCT provincia) FROM pedidos")
        total_provincias = cursor.fetchone()[0]
        
        cursor.close()
        return {'total_pedidos': total_pedidos, 'total_provincias': total_provincias}
    except:
        return {'total_pedidos': 0, 'total_provincias': 0}
    finally:
        liberar_conexion(conn)


def procesar_devolucion(codigo, motivo):
    """
    Procesa la devolución de un pedido ya entregado.
    
    Retorna: dict con la estructura:
        {
            'exito': bool,
            'mensaje': str,
            'pedido_devuelto': dict o None
        }
    """
    es_valido, msg_error = validar_codigo_envio(codigo)
    if not es_valido:
        return {
            'exito': False,
            'mensaje': msg_error,
            'pedido_devuelto': None
        }
    
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        # Primero verificamos el estado actual
        cursor.execute("""
            SELECT id, codigo_tracking, nombre_cliente, direccion, provincia, estado, fecha_creacion
            FROM pedidos
            WHERE UPPER(codigo_tracking) = UPPER(%s)
        """, (codigo,))
        
        resultado = cursor.fetchone()
        
        if not resultado:
            cursor.close()
            return {
                'exito': False,
                'mensaje': 'No se encontró un pedido con ese código',
                'pedido_devuelto': None
            }
        
        estado_actual = resultado[5]
        
        # Verificar si ya fue devuelto
        if "Devuelto" in estado_actual:
            cursor.close()
            return {
                'exito': False,
                'mensaje': 'Este pedido ya ha sido devuelto anteriormente',
                'pedido_devuelto': None
            }
        
        # Verificar si está entregado
        if estado_actual != "Entregado":
            cursor.close()
            return {
                'exito': False,
                'mensaje': 'El envío todavía no ha sido entregado, no se puede devolver',
                'pedido_devuelto': None
            }
        
        # Procesar devolución
        nuevo_estado = f"Devuelto, causa: {motivo.capitalize()}"
        
        cursor.execute("""
            UPDATE pedidos
            SET estado = %s
            WHERE UPPER(codigo_tracking) = UPPER(%s)
            RETURNING id, codigo_tracking, nombre_cliente, direccion, provincia, estado, fecha_creacion
        """, (nuevo_estado, codigo))
        
        resultado_actualizado = cursor.fetchone()
        conn.commit()
        cursor.close()
        
        pedido_devuelto = {
            'contador': resultado_actualizado[0],
            'codigo': resultado_actualizado[1],
            'cliente': resultado_actualizado[2],
            'direccion': resultado_actualizado[3],
            'provincia': resultado_actualizado[4],
            'estado': resultado_actualizado[5],
            'fecha': resultado_actualizado[6].strftime('%d/%m/%Y %H:%M')
        }
        
        return {
            'exito': True,
            'mensaje': f'Devolución registrada: {pedido_devuelto["estado"]}',
            'pedido_devuelto': pedido_devuelto
        }
    
    except Exception as e:
        if conn:
            conn.rollback()
        return {
            'exito': False,
            'mensaje': f'Error al procesar devolución: {str(e)}',
            'pedido_devuelto': None
        }
    
    finally:
        if conn:
            liberar_conexion(conn)

def avanzar_estado(codigo):
    """Avanza el estado del pedido al siguiente paso lógico"""
    conn = obtener_conexion()
    if not conn:
        return {'exito': False, 'mensaje': 'Error de conexión a BD'}

    try:
        cursor = conn.cursor()
        
        # 1. Averiguar estado actual
        cursor.execute("SELECT estado FROM pedidos WHERE codigo_tracking = %s", (codigo,))
        resultado = cursor.fetchone()
        
        if not resultado:
            return {'exito': False, 'mensaje': 'Pedido no encontrado'}
            
        estado_actual = resultado[0]
        nuevo_estado = estado_actual
        
        # 2. Máquina de estados simple
        if estado_actual == "Pendiente":
            nuevo_estado = "En Camino"
        elif estado_actual == "En Camino":
            nuevo_estado = "Entregado"
        elif estado_actual == "Entregado":
            return {'exito': False, 'mensaje': 'El pedido ya fue entregado'}
        else:
            return {'exito': False, 'mensaje': f'No se puede avanzar desde: {estado_actual}'}

        # 3. Actualizar
        cursor.execute("UPDATE pedidos SET estado = %s WHERE codigo_tracking = %s", (nuevo_estado, codigo))
        conn.commit()
        cursor.close()
        
        return {'exito': True, 'mensaje': f'Actualizado a: {nuevo_estado}', 'nuevo_estado': nuevo_estado}

    except Exception as e:
        conn.rollback()
        return {'exito': False, 'mensaje': str(e)}
    finally:
        liberar_conexion(conn)
