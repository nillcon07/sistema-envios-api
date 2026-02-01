# 📦 Sistema de Envíos - API REST

API profesional para gestión de envíos de paquetería con **FastAPI** y **PostgreSQL**.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

---

## 🚀 Demo en Vivo

**API:** [https://tu-url.onrender.com](https://tu-url.onrender.com)  
**Documentación:** [https://tu-url.onrender.com/docs](https://tu-url.onrender.com/docs)

---

## ✨ Características

- ✅ **CRUD completo** de pedidos de envío
- ✅ **PostgreSQL** en la nube (Neon)
- ✅ **API REST** con FastAPI
- ✅ **Documentación automática** (Swagger UI)
- ✅ **Sin POO** - Solo funciones procedurales
- ✅ **Connection Pooling** para mejor rendimiento
- ✅ **Validaciones robustas** de datos
- ✅ **Deploy fácil** en Render

---

## 📖 Documentación

- [Guía de Deploy en Render](GUIA_DEPLOY_RENDER.md)
- [Documentación Completa](README_POSTGRES.md)
- [Migración de datos](migrar_a_postgres.py)

---

## 🎯 Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Información de la API |
| `GET` | `/health` | Health check |
| `POST` | `/pedidos` | Crear pedido |
| `GET` | `/pedidos` | Listar todos los pedidos |
| `POST` | `/pedidos/consultar/codigo` | Buscar por código |
| `PUT` | `/pedidos/estado` | Actualizar estado |
| `POST` | `/pedidos/devolucion` | Registrar devolución |

---

## 🚀 Inicio Rápido

### Instalación Local

```bash
# Clonar el repositorio
git clone https://github.com/TU-USUARIO/sistema-envios-api.git
cd sistema-envios-api

# Instalar dependencias
pip install -r requirements_postgres.txt

# Ejecutar el servidor
python main_postgres.py
```

La API estará disponible en: `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

---

## 🌐 Deploy en Render

Sigue la [Guía de Deploy en Render](GUIA_DEPLOY_RENDER.md) para subir tu API a la nube en minutos.

---

## 📊 Estructura de la Base de Datos

```sql
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    codigo_tracking VARCHAR(50) UNIQUE NOT NULL,
    nombre_cliente VARCHAR(200) NOT NULL,
    direccion VARCHAR(300) NOT NULL,
    provincia VARCHAR(100) NOT NULL,
    estado VARCHAR(100) NOT NULL DEFAULT 'Pendiente',
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` (usa `.env.example` como plantilla):

```env
DB_HOST=tu-host-postgresql
DB_PORT=5432
DB_NAME=tu-database
DB_USER=tu-usuario
DB_PASSWORD=tu-password
DB_SSLMODE=require
```

---

## 📝 Ejemplo de Uso

### Crear un pedido

```bash
curl -X POST "https://tu-api.onrender.com/pedidos" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_cliente": "Juan Perez",
    "direccion": "Av Libertador 1234",
    "provincia": "Buenos Aires"
  }'
```

### Respuesta

```json
{
  "exito": true,
  "mensaje": "Envío creado exitosamente",
  "pedido": {
    "contador": 1,
    "codigo": "ENV001",
    "cliente": "Juan Perez",
    "direccion": "Av Libertador 1234",
    "provincia": "Buenos Aires",
    "estado": "Pendiente",
    "fecha": "01/02/2026 14:30"
  },
  "nuevo_contador": 1
}
```

---

## 🛠️ Tecnologías

- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web moderno
- **[PostgreSQL](https://www.postgresql.org/)** - Base de datos relacional
- **[Neon](https://neon.tech/)** - PostgreSQL serverless
- **[Render](https://render.com/)** - Hosting en la nube
- **[psycopg2](https://www.psycopg.org/)** - Driver PostgreSQL
- **[Pydantic](https://docs.pydantic.dev/)** - Validación de datos

---

## 📂 Estructura del Proyecto

```
sistema-envios-api/
├── logica_envios_postgres.py    # Lógica de negocio
├── main_postgres.py              # API FastAPI
├── migrar_a_postgres.py          # Script de migración
├── requirements_postgres.txt     # Dependencias
├── runtime.txt                   # Versión de Python
├── render.yaml                   # Configuración Render
├── .gitignore                    # Archivos ignorados
├── .env.example                  # Plantilla de variables
├── README.md                     # Este archivo
├── README_POSTGRES.md            # Documentación detallada
└── GUIA_DEPLOY_RENDER.md         # Guía de deploy
```

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

---

## 👨‍💻 Autor

Desarrollado con ❤️ manteniendo un estilo procedural (sin POO).

---

## 📞 Soporte

¿Problemas o preguntas?

- 📖 Lee la [documentación completa](README_POSTGRES.md)
- 🚀 Consulta la [guía de deploy](GUIA_DEPLOY_RENDER.md)
- 🐛 Abre un [issue](https://github.com/TU-USUARIO/sistema-envios-api/issues)

---

⭐ Si te gustó este proyecto, dale una estrella en GitHub!
