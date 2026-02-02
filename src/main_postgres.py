from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse 
from pydantic import BaseModel
import logica_envios_postgres as logic
import os
import uvicorn

app = FastAPI(title="Sistema de Envíos UADE")

# Modelos Limpios
class NuevoEnvio(BaseModel):
    nombre_cliente: str
    direccion: str
    provincia: str

class CambioEstado(BaseModel):
    codigo: str
    nuevo_estado: str

@app.on_event("startup")
def startup():
    logic.inicializar_base_datos()

@app.get("/", response_class=HTMLResponse)
def root():
    try:
        with open("index.html", "r", encoding="utf-8") as f: return f.read()
    except: return "Error: index.html no encontrado"

@app.get("/pedidos")
def listar():
    return logic.listar_todos_envios()

@app.post("/pedidos")
def crear(envio: NuevoEnvio):
    contador = logic.obtener_ultimo_contador()
    res = logic.agregar_envio(contador, envio.nombre_cliente, envio.direccion, envio.provincia)
    if not res['exito']:
        raise HTTPException(status_code=400, detail=res['mensaje'])
    return res

@app.post("/pedidos/cambiar_estado")
def cambiar_estado(datos: CambioEstado):
    res = logic.cambiar_estado_manual(datos.codigo, datos.nuevo_estado)
    if not res['exito']:
        raise HTTPException(status_code=400, detail=res['mensaje'])
    return res

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
