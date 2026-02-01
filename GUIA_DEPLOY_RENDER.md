# 🚀 GUÍA COMPLETA: Deploy en Render

Esta guía te llevará paso a paso para subir tu API a **Render** (gratis y fácil).

---

## 📋 REQUISITOS PREVIOS

✅ Cuenta en [GitHub](https://github.com) (gratis)  
✅ Cuenta en [Render](https://render.com) (gratis)  
✅ Tu base de datos PostgreSQL en Neon funcionando  

---

## 🎯 PASO 1: Preparar el código

### 1.1 Crear un repositorio en GitHub

1. Ve a [GitHub](https://github.com) e inicia sesión
2. Haz clic en el botón **"New"** (nuevo repositorio)
3. Nombre: `sistema-envios-api` (o el que prefieras)
4. Descripción: `API de gestión de envíos con FastAPI y PostgreSQL`
5. Deja como **Público** o **Privado** (ambos funcionan con Render)
6. **NO** marques "Add a README file"
7. Haz clic en **"Create repository"**

### 1.2 Subir el código a GitHub

Abre tu terminal en la carpeta del proyecto y ejecuta:

```bash
# Inicializar git (si no lo has hecho)
git init

# Agregar todos los archivos
git add .

# Hacer el primer commit
git commit -m "Initial commit - Sistema de envíos API"

# Conectar con tu repositorio de GitHub
# Reemplaza USUARIO con tu nombre de usuario de GitHub
git remote add origin https://github.com/USUARIO/sistema-envios-api.git

# Subir el código
git branch -M main
git push -u origin main
```

**✅ Tu código ya está en GitHub!**

---

## 🎯 PASO 2: Configurar Render

### 2.1 Crear cuenta en Render

1. Ve a [Render.com](https://render.com)
2. Haz clic en **"Get Started"**
3. Regístrate con tu cuenta de GitHub (recomendado)

### 2.2 Crear un nuevo Web Service

1. En el dashboard de Render, haz clic en **"New +"**
2. Selecciona **"Web Service"**
3. Conecta tu repositorio de GitHub:
   - Si es la primera vez, autoriza a Render a acceder a tus repos
   - Busca `sistema-envios-api` y haz clic en **"Connect"**

### 2.3 Configurar el Web Service

Completa el formulario con estos valores:

**Name (Nombre):**
```
sistema-envios-api
```

**Region (Región):**
```
Oregon (US West) o el más cercano a ti
```

**Branch (Rama):**
```
main
```

**Runtime:**
```
Python 3
```

**Build Command:**
```
pip install -r requirements_postgres.txt
```

**Start Command:**
```
uvicorn main_postgres:app --host 0.0.0.0 --port $PORT
```

**Instance Type:**
```
Free (gratis)
```

### 2.4 Agregar las Variables de Entorno

**¡MUY IMPORTANTE!** Antes de hacer clic en "Create Web Service", ve a la sección **"Environment Variables"** y agrega:

| Key (Nombre) | Value (Valor) |
|--------------|---------------|
| `DB_HOST` | `ep-crimson-butterfly-aht6exsh-pooler.c-3.us-east-1.aws.neon.tech` |
| `DB_PORT` | `5432` |
| `DB_NAME` | `neondb` |
| `DB_USER` | `neondb_owner` |
| `DB_PASSWORD` | `npg_XsZEkIfy58xG` |
| `DB_SSLMODE` | `require` |

Para agregar cada variable:
1. Haz clic en **"Add Environment Variable"**
2. Escribe el **Key** (nombre)
3. Escribe el **Value** (valor)
4. Repite para cada variable

### 2.5 Crear el servicio

Haz clic en **"Create Web Service"** al final de la página.

**Render empezará a deployar tu app** (tarda 2-5 minutos).

---

## 🎯 PASO 3: Verificar el Deploy

### 3.1 Esperar a que termine

Verás los logs en tiempo real. Espera a ver este mensaje:

```
==> Your service is live 🎉
```

### 3.2 Obtener la URL de tu API

Render te asignará una URL como:
```
https://sistema-envios-api.onrender.com
```

### 3.3 Probar la API

Abre tu navegador y ve a:

```
https://TU-URL.onrender.com/docs
```

Deberías ver la **documentación interactiva de tu API** (Swagger UI).

---

## 🧪 PASO 4: Probar los Endpoints

### 4.1 Health Check

```bash
curl https://TU-URL.onrender.com/health
```

Deberías recibir:
```json
{
  "status": "ok",
  "database": "PostgreSQL conectado",
  "tiene_datos": false,
  "mensaje": "API funcionando correctamente"
}
```

### 4.2 Crear un pedido de prueba

Ve a la documentación interactiva:
```
https://TU-URL.onrender.com/docs
```

1. Busca el endpoint **POST /pedidos**
2. Haz clic en **"Try it out"**
3. Edita el JSON de ejemplo:
```json
{
  "nombre_cliente": "Juan Perez",
  "direccion": "Av Libertador 1234",
  "provincia": "Buenos Aires"
}
```
4. Haz clic en **"Execute"**

**¡Si funciona, tu API está deployada correctamente!** 🎉

---

## 📊 PASO 5: Migrar tus datos (OPCIONAL)

Si tenías datos en `pedidos.txt` y quieres migrarlos:

### Opción 1: Usar el script de migración localmente

```bash
# 1. Configura las variables de entorno localmente
export DB_HOST=ep-crimson-butterfly-aht6exsh-pooler.c-3.us-east-1.aws.neon.tech
export DB_PORT=5432
export DB_NAME=neondb
export DB_USER=neondb_owner
export DB_PASSWORD=npg_XsZEkIfy58xG
export DB_SSLMODE=require

# 2. Ejecuta el script de migración
python migrar_a_postgres.py
```

### Opción 2: Insertar datos manualmente

Usa la interfaz de Swagger en `/docs` para crear pedidos uno por uno.

---

## 🔧 CONFIGURACIÓN ADICIONAL

### Habilitar Auto-Deploy

Render puede hacer deploy automático cada vez que hagas push a GitHub:

1. En Render, ve a tu servicio
2. Ve a **Settings**
3. En **Build & Deploy**, verifica que **Auto-Deploy** esté en **Yes**

Ahora cada vez que hagas:
```bash
git add .
git commit -m "Actualización"
git push
```

**Render hará deploy automáticamente** 🚀

### Ver los Logs

Para ver los logs en tiempo real:

1. En Render, ve a tu servicio
2. Haz clic en **"Logs"** en el menú superior

---

## ⚡ TROUBLESHOOTING

### Error: "Your service is not responding"

**Causa:** El puerto no está configurado correctamente.

**Solución:** Verifica que el Start Command sea:
```
uvicorn main_postgres:app --host 0.0.0.0 --port $PORT
```

### Error: "connection to server failed"

**Causa:** Las variables de entorno de la base de datos no están configuradas.

**Solución:**
1. Ve a **Settings → Environment**
2. Verifica que todas las variables (`DB_HOST`, `DB_PORT`, etc.) estén correctas
3. Haz clic en **"Manual Deploy → Deploy latest commit"**

### Error: "No module named 'psycopg2'"

**Causa:** El Build Command no está instalando las dependencias.

**Solución:** Verifica que el Build Command sea:
```
pip install -r requirements_postgres.txt
```

### La app se "duerme" después de 15 minutos

**Causa:** El plan Free de Render pone a dormir las apps inactivas.

**Solución:**
- Opción 1: Actualizar a plan de pago ($7/mes)
- Opción 2: Usar un servicio como [UptimeRobot](https://uptimerobot.com) para hacer ping cada 10 minutos (gratis)

---

## 📱 COMPARTIR TU API

Tu API ahora tiene una URL pública:

```
https://TU-URL.onrender.com
```

Puedes compartir:
- **Documentación:** `https://TU-URL.onrender.com/docs`
- **Health Check:** `https://TU-URL.onrender.com/health`
- **Endpoint de ejemplo:** `https://TU-URL.onrender.com/pedidos`

---

## 🔐 SEGURIDAD

### Proteger tus credenciales

✅ **NUNCA** hagas commit de archivos `.env` con credenciales  
✅ Usa variables de entorno en Render  
✅ Agrega `.env` al `.gitignore`  

### Agregar autenticación (OPCIONAL)

Para agregar autenticación básica a tu API:

```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

(Esto ya está fuera del scope de esta guía, pero hay tutoriales en la documentación de FastAPI)

---

## 🎓 RECURSOS ADICIONALES

- [Documentación de Render](https://render.com/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL en Render](https://render.com/docs/databases)

---

## 📞 SOPORTE

Si tienes problemas:
1. Revisa los logs en Render
2. Verifica las variables de entorno
3. Asegúrate de que tu base de datos PostgreSQL esté accesible

---

## 🎉 ¡FELICIDADES!

Tu API de Sistema de Envíos ya está **en la nube** y accesible desde cualquier parte del mundo.

**URL de ejemplo final:**
- API: `https://sistema-envios-api.onrender.com`
- Docs: `https://sistema-envios-api.onrender.com/docs`

---

## 📝 CHECKLIST FINAL

- [ ] Código subido a GitHub
- [ ] Web Service creado en Render
- [ ] Variables de entorno configuradas
- [ ] Deploy exitoso (servicio en "Live")
- [ ] Health check funciona
- [ ] Documentación accesible en `/docs`
- [ ] Primer pedido creado correctamente

**¡Todo listo!** 🚀
