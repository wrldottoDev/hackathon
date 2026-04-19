# iOS Notes

Este scaffold incluye código Swift para una keyboard extension, pero no genera automáticamente el proyecto `.xcodeproj`.

## Pasos recomendados

1. Crea un proyecto Flutter normal cuando tengas el SDK instalado.
2. Abre `ios/Runner.xcworkspace` en Xcode.
3. Agrega un target tipo `Custom Keyboard Extension`.
4. Sustituye el `KeyboardViewController.swift` generado por el archivo de esta carpeta.
5. Si quieres compartir configuración entre la app y la extensión, agrega un `App Group`.

## Restricciones de plataforma

- iOS no expone un mecanismo equivalente a `AccessibilityService` para leer texto arbitrario de otras apps.
- Una keyboard extension puede procesar lo que el usuario escribe dentro del teclado, pero no inspeccionar libremente el contenido visual de la app anfitriona.
- El listener de notificaciones tampoco existe como servicio general de terceros en iOS.
