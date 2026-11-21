# Instalación de desarrollo

## Backend local

1. Instala Python 3.12 o posterior.
2. Ejecuta `scripts/setup.ps1` y luego `scripts/start-backend.ps1`.
3. Comprueba con `scripts/health-check.ps1`; ejecuta `.\backend\.venv\Scripts\python.exe -m pytest` desde `backend`.
4. El script crea `backend/.env` desde `.env.example` sin sobrescribir uno que ya exista.

## Render

Conecta el repositorio en Render como un servicio web. `render.yaml` configura `rootDir: backend`, fija Python 3.13.12, instala dependencias, arranca Uvicorn usando `$PORT` y define `/health` como health check. Render acepta WebSockets entrantes en servicios web; usa `wss://` para conexiones públicas. Las conexiones pueden cortarse durante un reemplazo de instancia, por lo que el cliente deberá reconectar. Define los secretos desde el panel de Render. No guardes `.env` ni credenciales en Git.

## Unreal

La carpeta `apps/unreal-demo` queda reservada. El `.uproject` se creará desde Unreal Engine instalado para asegurar que el formato, versión y módulos corresponden al motor disponible. Para Windows también se necesita Visual Studio 2022 con el conjunto de herramientas de C++ para Unreal.
