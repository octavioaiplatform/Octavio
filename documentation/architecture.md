# Arquitectura inicial

## Decisión de despliegue

- **Unreal Engine 5** es el cliente 3D ejecutado por el jugador. No es una web.
- **Render** aloja el backend FastAPI. En producción, el cliente se conecta mediante WSS.
- El Blueprint fija Python 3.13.12 para que Render no elija una versión distinta de la probada localmente.
- **OpenAI Realtime** se integra detrás de `AIProvider`; la clave vive solo en el entorno del backend.
- **PostgreSQL** queda fuera de la primera demo. Las sesiones actuales viven en memoria y se pierden al reiniciar el proceso.

## Flujo

1. Unreal abre `/ws` con un token de acceso de desarrollo o de despliegue.
2. El cliente envía `session.create` con el personaje seleccionado.
3. El backend carga la definición YAML, crea la sesión y responde `session.created` y `session.ready`.
4. Los eventos y bloques de audio pasan por el protocolo OCTAVIO.
5. Un proveedor normaliza los eventos del motor de IA para el cliente.

El primer proveedor es simulado: valida el transporte y los límites de audio, pero no transcribe ni genera audio. La integración real se documentará cuando se comprueben los eventos y formatos de Realtime en fuentes oficiales.

## Límites actuales

- Las sesiones en memoria funcionan para una sola instancia. No escalar Render a varias instancias hasta definir almacenamiento compartido o afinidad de sesión.
- Los WebSockets pueden cerrarse cuando Render reemplaza una instancia; el cliente tendrá que reconectar y crear o reanudar la sesión.
- El token compartido actual es una protección de desarrollo, no autenticación de producción por usuario.
- Los formatos y frecuencia del audio del protocolo son provisionales hasta completar la revisión de Realtime y la conversión necesaria en el cliente.
- Los recursos de Unreal (mapa, personaje, animaciones y UI) requieren generar el proyecto con la instalación real del motor; no se inventa un `.uproject` ni un identificador de módulo.
