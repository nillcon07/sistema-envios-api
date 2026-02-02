
# 📦 Sistema de Envíos UADE - Fullstack

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Render](https://img.shields.io/badge/Deploy-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

Una solución completa para la gestión de paquetería que incluye una **API REST robusta** y un **Frontend moderno** con diseño *Glassmorphism*.

---

## 🚀 Demo en Vivo

👉 **[Ver Aplicación Desplegada](https://sistemaseguimientoenviosapi.onrender.com)**

> *⚠️ Nota: Al estar alojado en el plan gratuito de Render, la primera carga puede demorar unos segundos en "despertar" el servidor.*

---

## ✨ Características Principales

### 🎨 Frontend (Nuevo)
* **Interfaz Visual:** Panel de control web para crear y rastrear pedidos sin código.
* **Diseño Moderno:** Estilo "Glassmorphism" con animaciones y feedback visual.
* **Single Page Application:** Interactúa con la API en tiempo real usando JavaScript vainilla (sin frameworks pesados).

### ⚙️ Backend (API)
* **FastAPI:** Alto rendimiento y documentación automática.
* **PostgreSQL:** Persistencia de datos en la nube (Neon Tech).
* **Arquitectura Procedural:** Lógica de negocio limpia y directa.
* **Validaciones:** Control estricto de datos con Pydantic.

---

## 🛠️ Estructura del Proyecto

El proyecto ha sido reorganizado para mayor limpieza:

```text
sistema-envios-api/
├── src/                        # 📂 CÓDIGO FUENTE
│   ├── main_postgres.py        # Punto de entrada (API + Servidor de estáticos)
│   ├── logica_envios_postgres.py # Reglas de negocio y conexión DB
│   ├── index.html              # Interfaz Gráfica (Frontend)
│   ├── requirements_postgres.txt # Dependencias
│   └── runtime.txt             # Versión de Python
├── render.yaml                 # Configuración de Deploy
├── .gitignore                  # Archivos ignorados
└── README.md                   # Documentación

```

---

## 🚀 Instalación y Ejecución Local

Sigue estos pasos para probar el proyecto en tu máquina:

1. **Clonar el repositorio:**
```bash
git clone [https://github.com/TU-USUARIO/sistema-envios-api.git](https://github.com/TU-USUARIO/sistema-envios-api.git)
cd sistema-envios-api

```


2. **Configurar entorno virtual (Opcional pero recomendado):**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

```


3. **Instalar dependencias:**
⚠️ **Importante:** Las dependencias están dentro de `src`.
```bash
cd src
pip install -r requirements_postgres.txt

```


4. **Variables de Entorno:**
Crea un archivo `.env` o configura tus variables de sistema con las credenciales de tu base de datos (Neon/PostgreSQL):
* `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`


5. **Ejecutar el servidor:**
Asegúrate de estar dentro de la carpeta `src`:
```bash
python main_postgres.py

```


6. **Abrir en el navegador:**
Ve a `http://localhost:8000` para ver la interfaz gráfica.

---

## 🌐 Endpoints de la API

Aunque tiene interfaz gráfica, la API sigue siendo 100% funcional para integraciones externas:

| Método | Endpoint | Descripción |
| --- | --- | --- |
| `GET` | `/` | Carga la Interfaz Gráfica (HTML) |
| `GET` | `/docs` | Documentación interactiva (Swagger) |
| `POST` | `/pedidos` | Crear un nuevo envío |
| `GET` | `/pedidos` | Listar todos los envíos |
| `POST` | `/pedidos/consultar/codigo` | Rastrear un pedido específico |

---

## ☁️ Despliegue en Render

Este repositorio está configurado para desplegarse automáticamente.

1. En Render, asegúrate de configurar el **Root Directory** como `src`.
2. El **Build Command** se ejecutará dentro de esa carpeta: `pip install -r requirements_postgres.txt`.
3. El **Start Command** buscará el archivo en la ruta correcta: `uvicorn main_postgres:app --host 0.0.0.0 --port $PORT`.

---

## 📄 Licencia

Proyecto desarrollado con fines educativos para la UADE.

```

```
