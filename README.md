# OCTAVIO

OCTAVIO conecta un cliente de videojuego con personajes de IA por voz. La arquitectura inicial mantiene el videojuego en Unreal Engine 5 y aloja el backend Python en Render.

## Estado

La primera versión incluye el backend FastAPI, un protocolo WebSocket versionable, el personaje Marcos y conexión de servidor a servidor con OpenAI Realtime. Render debe guardar la clave secreta; Unreal nunca recibe la clave de OpenAI.

El proyecto ejecutable de Unreal se añadirá después de validar el entorno Unreal instalado. No se incluyen claves ni datos privados.

## Arquitectura

```text
Unreal Engine 5 (cliente 3D)
        │ WSS en producción / WS local
        ▼
Backend FastAPI en Render
        │ WebSocket seguro de OpenAI Realtime
        ▼
OpenAI Realtime (fase posterior)
```

Render aloja el backend; Unreal es el frontend interactivo 3D del juego, no una web. La clave del proveedor de IA se guarda como variable secreta del backend y nunca en Unreal.

## Desarrollo local

Requiere Python 3.12 o posterior compatible.

Configuración rápida desde PowerShell:

```powershell
 ./scripts/setup.ps1
 ./scripts/start-backend.ps1
```

En otra terminal, comprueba el servicio con `./scripts/health-check.ps1`.

Configuración manual:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item ..\.env.example .\.env
uvicorn app.main:app --reload
```

El servicio escucha en `http://127.0.0.1:8000`. Salud: `GET /health`. La documentación local de FastAPI está en `/docs`.

Para WebSocket local, usa `ws://127.0.0.1:8000/ws` con `Authorization: Bearer local-dev-token`. En Render usa `wss://<servicio>.onrender.com/ws` y configura `OCTAVIO_ACCESS_TOKEN` como secreto.

## Render

El archivo `render.yaml` define el servicio web y la comprobación de salud. Render genera `OCTAVIO_ACCESS_TOKEN`; añade `OPENAI_API_KEY` como secreto y usa `OPENAI_REALTIME_MODEL=gpt-realtime-2.1`. El audio entrante debe ser PCM mono a 24 kHz. No uses el token local en un despliegue público.

## Protocolo

Consulta [`documentation/protocol.md`](documentation/protocol.md) para el sobre de eventos y los eventos iniciales. El transporte de audio está descrito como provisional hasta verificar formatos y límites directamente con la documentación oficial de Realtime en la fase de integración.

## Pruebas

```powershell
cd backend
pip install -r requirements-dev.txt
pytest
```

## Estructura

- `backend/`: API, sesiones, personajes, contexto y proveedores de IA.
- `documentation/`: arquitectura, protocolo, instalación y hoja de ruta.
- `infrastructure/`: contenedor para despliegues alternativos y desarrollo local.
- `apps/unreal-demo/`: reservado para el proyecto generado con Unreal Engine.
