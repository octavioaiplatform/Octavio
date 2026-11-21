# Protocolo OCTAVIO v1

Cada mensaje de aplicación es un objeto JSON con `event_id`, `session_id`, `timestamp`, `type` y `payload`. Se permiten extensiones futuras mediante nuevos tipos; los campos desconocidos del sobre se rechazan en esta primera versión para detectar errores de cliente temprano.

Ejemplo:

```json
{
  "event_id": "uuid",
  "session_id": null,
  "timestamp": "2026-11-20T12:00:00Z",
  "type": "session.create",
  "payload": {"character_id": "marcos", "player_id": "player-1"}
}
```

## Eventos iniciales

Cliente → backend: `session.create`, `session.end`, `npc.interaction.start`, `npc.interaction.stop`, `audio.input`, `audio.interrupt`, `player.context.update`, `ping`.

Backend → cliente: `session.created`, `session.ready`, `conversation.started`, `speech.detected`, `audio.output`, `npc.transcript.delta`, `response.completed`, `npc.state.changed`, `error`, `pong`.

Audio de entrada usa `payload.audio_b64` y `payload.sequence`. El backend limita el bloque decodificado a 64 KiB por defecto. Para OpenAI Realtime, Unreal debe enviar PCM16 mono a 24 kHz; el servidor devuelve `audio.output` en PCM16 mono a 24 kHz. El cliente debe reproducir los fragmentos en el orden recibido.

## Transporte

- Desarrollo local: `ws://127.0.0.1:8000/ws`.
- Render: `wss://<servicio>.onrender.com/ws`.
- Autenticación inicial: `Authorization: Bearer <OCTAVIO_ACCESS_TOKEN>` en el handshake.
- Nunca incluir la clave de proveedor en eventos enviados por el cliente.
