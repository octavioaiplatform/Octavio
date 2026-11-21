# Hoja de ruta

1. **Base backend:** API de salud, personajes externos, sesiones en memoria, protocolo WebSocket, proveedor simulado y pruebas.
2. **Realtime:** consultar documentación oficial vigente, confirmar autenticación, modelo, eventos, formatos y límites; implementar el adaptador solo después.
3. **Cliente Unreal:** generar proyecto con la versión instalada, crear mapa/personaje/UI y componentes de comunicación y audio.
4. **Integración y medición:** probar voz a voz y cortes de respuesta, medir latencia por etapa y documentar los límites observados.
5. **Render:** desplegar el backend y validar WSS desde el cliente.
6. **Fase 2:** personalidad contextual, memoria controlada y persistencia con PostgreSQL cuando el producto lo requiera.
