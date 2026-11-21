# Solución de problemas

- **401/4401 en WebSocket:** verifica el encabezado `Authorization: Bearer ...` y que el valor coincida con `OCTAVIO_ACCESS_TOKEN`.
- **Conexión local rechazada:** arranca Uvicorn en el puerto 8000 y confirma `GET /health`.
- **`invalid_audio`:** manda `audio_b64` válido en Base64 y un `sequence` entero no negativo.
- **`invalid_audio_size`:** divide audio en bloques que no excedan `OCTAVIO_MAX_AUDIO_CHUNK_BYTES` tras decodificarlos.
- **No hay transcripción ni voz en modo mock:** es intencional. El mock valida transporte y no simula percepción o generación de audio.
- **Render reinicia sesiones:** las sesiones actuales se guardan en memoria y desaparecen al reiniciar; una sola instancia es el límite actual.
