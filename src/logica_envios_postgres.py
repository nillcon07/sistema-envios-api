import psycopg2
from psycopg2 import pool
import os

# CONFIGURACIÓN DE CONEXIÓN A POSTGRESQL
DB_PASSWORD = os.getenv('DB_PASSWORD')
if not DB_PASSWORD:
    # Esto previene que la app arranque si olvidaste configurar la variable en Render
    raise ValueError("❌ ERROR CRÍTICO: La variable de entorno DB_PASSWORD no está configurada.")

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'ep-crimson-butterfly-aht6exsh-pooler.c-3.us-east-1.aws.neon.tech'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'neondb'),
    'user': os.getenv('DB_USER', 'neondb_owner'),
    'password': DB_PASSWORD, #variable validada
    'sslmode': os.getenv('DB_SSLMODE', 'require')
}

connection_pool = None

def inicializar_pool():
    global connection_pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **DB_CONFIG)
        return True, "Pool conectado" if connection_pool else (False, "Error pool")
    except Exception as e:
        return False, f"Error conexión: {str(e)}"

def obtener_conexion():
    return connection_pool.getconn() if connection_pool else None

def liberar_conexion(conn):
    if connection_pool and conn:
        connection_pool.putconn(conn)

# --- LÓGICA DE VALIDACIÓN (Sin cambios, se mantiene tu buena lógica) ---

def sacar_acentos(entrada):
    acentos = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
               ("Á", "A"), ("É", "E"), ("Í", "I"), ("Ó", "O"), ("Ú", "U"))
    for i, j in acentos:
        entrada = entrada.replace(i, j)
    return entrada

def validar_nombre(nombre):
    if not nombre.strip(): return False, "El nombre no puede estar vacío"
    for c in nombre:
        if not c.isalpha() and c != " ": return False, "El nombre solo puede contener letras"
    return True, ""

def validar_direccion(direccion):
    if not direccion.strip(): return False, "La dirección es obligatoria"
    for c in direccion:
        if not c.isalnum() and c != " ": return False, "Dirección inválida (solo letras/números)"
    return True, ""

def validar_provincia(provincia):
    PROVINCIAS = (
        "Buenos Aires", "Catamarca", "Chaco", "Chubut", "Cordoba", "Corrientes",
        "Entre Rios", "Formosa", "Jujuy", "La Pampa", "La Rioja", "Mendoza",
        "Misiones", "Neuquen", "Rio Negro", "Salta", "San Juan", "San Luis",
        "Santa Cruz", "Santa Fe", "Santiago Del Estero", "Tierra Del Fuego", "Tucuman", "CABA"
    )
    if not provincia: return False, "Provincia requerida"
    prov_norm = sacar_acentos(provincia.strip().title())
    if prov_norm in PROVINCIAS:
        return True, prov_norm
    return False, f"La provincia '{provincia}' no está permitida en el sistema."

# --- FUNCIONES DE BASE DE DATOS ---

def inicializar_base_datos():
    exito, msg = inicializar_pool()
    if not exito: return False, msg
    
    conn = obtener_conexion()
    if not conn: return False, "No se pudo obtener conexión"
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id SERIAL PRIMARY KEY,
                codigo_tracking VARCHAR(50) UNIQUE NOT NULL,
                nombre_cliente VARCHAR(200) NOT NULL,
                direccion VARCHAR(300) NOT NULL,
                provincia VARCHAR(100) NOT NULL,
                estado VARCHAR(100) DEFAULT 'Pendiente',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        return True, "DB Inicializada"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        liberar_conexion(conn)

def obtener_ultimo_contador():
    conn = obtener_conexion()
    if not conn: return 0
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM pedidos")
        res = cursor.fetchone()
        return res[0] if res[0] else 0
    finally:
        liberar_conexion(conn)

def agregar_envio(contador, nombre_cliente, direccion, provincia):
    ok_nom, msg_nom = validar_nombre(nombre_cliente)
    if not ok_nom: return {'exito': False, 'mensaje': msg_nom}
    
    ok_dir, msg_dir = validar_direccion(direccion)
    if not ok_dir: return {'exito': False, 'mensaje': msg_dir}
    
    ok_prov, prov_limpia = validar_provincia(provincia)
    if not ok_prov: return {'exito': False, 'mensaje': prov_limpia}
    
    nuevo_id = contador + 1
    codigo = f"ENV{nuevo_id:03d}"
    
    conn = obtener_conexion()
    if not conn: return {'exito': False, 'mensaje': "Error de conexión DB"}
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pedidos (codigo_tracking, nombre_cliente, direccion, provincia, estado)
            VALUES (%s, %s, %s, %s, 'Pendiente')
        """, (codigo, sacar_acentos(nombre_cliente.title()), sacar_acentos(direccion.title()), prov_limpia))
        conn.commit()
        return {'exito': True, 'mensaje': 'Envío registrado', 'nuevo_contador': nuevo_id}
    except Exception as e:
        conn.rollback()
        return {'exito': False, 'mensaje': str(e)}
    finally:
        liberar_conexion(conn)

def listar_todos_envios():
    conn = obtener_conexion()
    if not conn: return {'pedidos': []}
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT codigo_tracking, nombre_cliente, direccion, provincia, estado FROM pedidos ORDER BY id DESC")
        filas = cursor.fetchall()
        pedidos = [{'codigo': f[0], 'cliente': f[1], 'direccion': f[2], 'provincia': f[3], 'estado': f[4]} for f in filas]
        return {'pedidos': pedidos}
    finally:
        liberar_conexion(conn)

def cambiar_estado_manual(codigo, nuevo_estado):
    ESTADOS_VALIDOS = ["Pendiente", "Despachado", "En Camino", "Entregado", "Cancelado"]
    
    if nuevo_estado not in ESTADOS_VALIDOS:
        return {'exito': False, 'mensaje': 'Estado no válido'}

    conn = obtener_conexion()
    if not conn: return {'exito': False, 'mensaje': "Error de conexión DB"}
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT estado FROM pedidos WHERE codigo_tracking = %s", (codigo,))
        res = cursor.fetchone()
        if not res: return {'exito': False, 'mensaje': 'Pedido no encontrado'}
        
        estado_actual = res[0]
        if estado_actual == "Entregado" and nuevo_estado == "Cancelado":
            return {'exito': False, 'mensaje': 'Error: No se puede cancelar un pedido ya entregado'}

        cursor.execute("UPDATE pedidos SET estado = %s WHERE codigo_tracking = %s", (nuevo_estado, codigo))
        conn.commit()
        return {'exito': True}
    except Exception as e:
        return {'exito': False, 'mensaje': str(e)}
    finally:
        liberar_conexion(conn)
