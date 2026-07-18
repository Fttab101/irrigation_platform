# Instrucciones de Despliegue en Render

Esta guía explica paso a paso cómo desplegar la Plataforma de Diseño de Riego y Fertirrigación (FastAPI + PostgreSQL + PostGIS) en Render.

## 1. Preparación del Repositorio Local
Antes de desplegar, asegúrate de que el código está en un repositorio Git (GitHub, GitLab o Bitbucket).

```bash
cd /ruta/a/irrigation_platform
git init
git add .
git commit -m "Inicialización del proyecto de riego"
git branch -M main
git remote add origin <URL_DE_TU_REPOSITORIO>
git push -u origin main
```

## 2. Crear la Base de Datos PostgreSQL con PostGIS
Dado que usamos PostGIS, la base de datos debe tener esta extensión habilitada.

1. Inicia sesión en [Render.com](https://render.com).
2. Haz clic en **New +** y selecciona **PostgreSQL**.
3. Rellena los datos básicos:
   - **Name**: `riego_db`
   - **Database**: `riego_db`
   - **User**: `postgres` (o el que prefieras)
   - **PostgreSQL Version**: 15 o superior.
4. **IMPORTANTE**: Una vez creada, ve a la configuración de la base de datos en Render, abre un terminal (psql) o conéctate remotamente y ejecuta el siguiente comando para habilitar PostGIS:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```
5. Copia la URL interna de la base de datos (**Internal Database URL**).

## 3. Despliegue de la API (Web Service)
1. En el panel de Render, haz clic en **New +** y selecciona **Web Service**.
2. Conecta el repositorio de GitHub/GitLab que creaste en el Paso 1.
3. Rellena los campos de configuración:
   - **Name**: `irrigation-api`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Desplázate hacia abajo hasta **Environment Variables** (Variables de Entorno).
   Añade la siguiente variable:
   - **Key**: `DATABASE_URL`
   - **Value**: Pega la URL interna de la base de datos (copiada en el paso 2).
5. Haz clic en **Create Web Service**.

## 4. Verificación
Una vez que el estado de Render pase a "Live", haz clic en la URL proporcionada (ej. `https://irrigation-api-xxxx.onrender.com`).
Deberías ver el mensaje de bienvenida.

Para acceder a la documentación interactiva y probar los algoritmos de cálculo, añade `/docs` a la URL:
👉 `https://irrigation-api-xxxx.onrender.com/docs`

Allí podrás introducir datos agronómicos y la API devolverá automáticamente la Dosis Bruta de Riego, Agua Fácilmente Disponible e Intervalos.
