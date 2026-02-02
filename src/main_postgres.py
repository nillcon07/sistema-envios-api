from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse 
from pydantic import BaseModel
from typing import Optional
import logica_envios_postgres as logic

# =====================================================
# INICIALIZACIÓN DE FASTAPI
# =====================================================

app = FastAPI(
    title="Sistema de Envíos API con PostgreSQL",
    description="API para gestionar envíos de paquetería usando PostgreSQL (sin POO)",
    version="2.0.0"
)

# =====================================================
# EVENTO DE STARTUP - INICIALIZAR BASE DE DATOS
# =====================================================

@app.on_event("startup")
def startup_event():
    """Se ejecuta al iniciar el servidor - inicializa la base de datos"""
    exito, mensaje = logic.inicializar_base_datos()
    if exito:
        print(f"✅ {mensaje}")
    else:
        print(f"❌ ERROR: {mensaje}")
        raise Exception(f"No se pudo inicializar la base de datos: {mensaje}")

# =====================================================
# MODELOS DE DATOS (Pydantic para validación de entrada)
# =====================================================

class NuevoEnvio(BaseModel):
    nombre_cliente: str
    direccion: str
    provincia: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre_cliente": "Juan Perez",
                "direccion": "Av Libertador 1234",
                "provincia": "Buenos Aires"
            }
        }


class ConsultaPorCodigo(BaseModel):
    codigo: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "codigo": "ENV001"
            }
        }


class ConsultaPorCliente(BaseModel):
    nombre_cliente: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre_cliente": "Juan"
            }
        }


class ConsultaPorFecha(BaseModel):
    fecha_inicio: str
    fecha_fin: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "fecha_inicio": "01/01/2024 00:00",
                "fecha_fin": "31/12/2024 23:59"
            }
        }


class CambioEstado(BaseModel):
    codigo: str
    nuevo_estado: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "codigo": "ENV001",
                "nuevo_estado": "En camino"
            }
        }


class Devolucion(BaseModel):
    codigo: str
    motivo: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "codigo": "ENV001",
                "motivo": "Producto defectuoso"
            }
        }


# =====================================================
# ENDPOINTS
# =====================================================

@app.get("/", response_class=HTMLResponse)
def root():
    """Endpoint raíz - Carga la interfaz visual"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error: No se encontró el archivo index.html</h1>"


@app.get("/contador")
def obtener_contador():
    """Obtiene el contador actual de pedidos"""
    contador = logic.obtener_ultimo_contador()
    return {
        "contador_actual": contador,
        "proximo_codigo": f"ENV{contador + 1:03d}"
    }


@app.post("/pedidos")
def crear_pedido(envio: NuevoEnvio):
    """Crea un nuevo pedido de envío"""
    
    # Obtener contador actual
    contador = logic.obtener_ultimo_contador()
    
    # Crear el envío
    resultado = logic.agregar_envio(
        contador=contador,
        nombre_cliente=envio.nombre_cliente,
        direccion=envio.direccion,
        provincia=envio.provincia
    )
    
    if resultado['exito']:
        return {
            "exito": True,
            "mensaje": resultado['mensaje'],
            "pedido": resultado['pedido'],
            "nuevo_contador": resultado['nuevo_contador']
        }
    else:
        raise HTTPException(status_code=400, detail=resultado['mensaje'])


@app.get("/pedidos")
def listar_pedidos():
    """Lista todos los pedidos"""
    
    resultado = logic.listar_todos_envios()
    
    return {
        "total_pedidos": resultado['total'],
        "pedidos": resultado['pedidos'],
        "mensaje": resultado['mensaje']
    }


@app.post("/pedidos/consultar/codigo")
def consultar_por_codigo(consulta: ConsultaPorCodigo):
    """Consulta un pedido por su código de tracking"""
    
    resultado = logic.consultar_envio_por_codigo(consulta.codigo)
    
    if resultado['encontrado']:
        return {
            "encontrado": True,
            "pedido": resultado['pedido'],
            "mensaje": resultado['mensaje']
        }
    else:
        raise HTTPException(status_code=404, detail=resultado['mensaje'])


@app.post("/pedidos/consultar/cliente")
def consultar_por_cliente(consulta: ConsultaPorCliente):
    """Consulta todos los pedidos de un cliente"""
    
    resultado = logic.consultar_envios_por_cliente(consulta.nombre_cliente)
    
    return {
        "encontrados": resultado['encontrados'],
        "pedidos": resultado['pedidos'],
        "mensaje": resultado['mensaje']
    }


@app.post("/pedidos/consultar/fecha")
def consultar_por_fecha(consulta: ConsultaPorFecha):
    """Consulta pedidos en un rango de fechas"""
    
    resultado = logic.consultar_envios_por_fecha(
        fecha_inicio=consulta.fecha_inicio,
        fecha_fin=consulta.fecha_fin
    )
    
    return {
        "encontrados": resultado['encontrados'],
        "pedidos": resultado['pedidos'],
        "mensaje": resultado['mensaje']
    }


@app.put("/pedidos/estado")
def actualizar_estado(cambio: CambioEstado):
    """Cambia el estado de un pedido"""
    
    resultado = logic.cambiar_estado_envio(
        codigo=cambio.codigo,
        nuevo_estado=cambio.nuevo_estado
    )
    
    if resultado['exito']:
        return {
            "exito": True,
            "mensaje": resultado['mensaje'],
            "pedido_actualizado": resultado['pedido_actualizado']
        }
    else:
        raise HTTPException(status_code=400, detail=resultado['mensaje'])


@app.post("/pedidos/devolucion")
def registrar_devolucion(devolucion: Devolucion):
    """Procesa la devolución de un pedido"""
    
    resultado = logic.procesar_devolucion(
        codigo=devolucion.codigo,
        motivo=devolucion.motivo
    )
    
    if resultado['exito']:
        return {
            "exito": True,
            "mensaje": resultado['mensaje'],
            "pedido_devuelto": resultado['pedido_devuelto']
        }
    else:
        raise HTTPException(status_code=400, detail=resultado['mensaje'])


# =====================================================
# ENDPOINT DE SALUD (HEALTH CHECK)
# =====================================================

@app.get("/health")
def health_check():
    """Verifica que la API y la base de datos estén funcionando"""
    tiene_datos = logic.base_datos_tiene_datos()
    
    return {
        "status": "ok",
        "database": "PostgreSQL conectado",
        "tiene_datos": tiene_datos,
        "mensaje": "API funcionando correctamente"
    }
class SolicitudAvance(BaseModel):
    codigo: str

@app.post("/pedidos/avanzar")
def avanzar_estado_pedido(solicitud: SolicitudAvance):
    """Endpoint para mover el pedido a la siguiente etapa"""
    resultado = logic.avanzar_estado(solicitud.codigo)
    
    if resultado['exito']:
        return resultado
    else:
        raise HTTPException(status_code=400, detail=resultado['mensaje'])

# =====================================================
# EJECUCIÓN DEL SERVIDOR
# =====================================================

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Usar el puerto de la variable de entorno PORT (Render lo asigna automáticamente)
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(app, host="0.0.0.0", port=port)
