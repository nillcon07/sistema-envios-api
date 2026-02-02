# En logica_envios_postgres.py

# ... (imports y configuraciones de DB igual que antes) ...

# =====================================================
# LÓGICA DE VALIDACIÓN (Traída de TPO.py)
# =====================================================

def sacar_acentos(entrada):
    """Lógica original de tu TPO para normalizar texto"""
    acentos = (
        ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
        ("Á", "A"), ("É", "E"), ("Í", "I"), ("Ó", "O"), ("Ú", "U")
    )
    for i, j in acentos:
        entrada = entrada.replace(i, j)
    return entrada

def validar_provincia(provincia):
    """
    Valida contra la lista OFICIAL de provincias (Lógica TPO).
    Aunque el Frontend solo muestre 4, el Backend conoce todas.
    """
    # Lista completa de tu archivo TPO.py
    PROVINCIAS_ARGENTINA = (
        "Buenos Aires", "Catamarca", "Chaco", "Chubut", "Cordoba", "Corrientes",
        "Entre Rios", "Formosa", "Jujuy", "La Pampa", "La Rioja", "Mendoza",
        "Misiones", "Neuquen", "Rio Negro", "Salta", "San Juan", "San Luis",
        "Santa Cruz", "Santa Fe", "Santiago Del Estero", "Tierra Del Fuego", "Tucuman", "CABA"
    )
    
    # Normalizamos lo que llega (sea del dropdown o de un hacker)
    provincia_limpia = sacar_acentos(provincia.strip().title())
    
    if provincia_limpia in PROVINCIAS_ARGENTINA:
        return True, ""
    else:
        # Aquí está el valor: El backend rechaza datos basura
        return False, f"Error: '{provincia}' no es una provincia válida en Argentina."

# =====================================================
# TU LÓGICA DE NEGOCIO ACTUALIZADA
# =====================================================

def agregar_envio(contador, nombre_cliente, direccion, provincia):
    # 1. Validamos Provincia con la lógica FUERTE
    es_valida_prov, msg_prov = validar_provincia(provincia)
    if not es_valida_prov:
        return {
            'exito': False, 
            'mensaje': msg_prov, # El front recibirá este error si intentan hackear
            'pedido': None, 
            'nuevo_contador': contador
        }

    # ... (El resto de tu función agregar_envio sigue igual: validar nombre, dirección, etc.) ...
    # ... Solo asegúrate de guardar 'provincia' (o provincia_limpia) en la DB ...
