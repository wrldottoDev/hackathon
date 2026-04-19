# TensorFlowKeyboard

Base de un Custom Keyboard (IME) en Flutter con host nativo Android.

## Qué quedó implementado

- `MethodChannel` entre Flutter y Kotlin en `tensorflow_keyboard/ime`.
- `InputMethodService` nativo que monta un `FlutterView` como `InputView`.
- `FlutterEngine` reutilizable para el IME con entrypoint dedicado `keyboardEntrypoint`.
- Layout Flutter en `lib/keyboard/` con:
  - fila superior de `Alertas de Seguridad`
  - teclado QWERTY básico
  - botón de `Modo Seguro` por long press
  - vista previa local del texto enviado al canal nativo

## Estructura principal

- Flutter:
  - `lib/main.dart`
  - `lib/keyboard/keyboard_app.dart`
  - `lib/keyboard/keyboard_screen.dart`
  - `lib/keyboard/keyboard_controller.dart`
  - `lib/keyboard/keyboard_method_channel.dart`
  - `lib/keyboard/widgets/`

- Android:
  - `android/app/src/main/kotlin/com/tensorflowkeyboard/app/MainActivity.kt`
  - `android/app/src/main/kotlin/com/tensorflowkeyboard/app/ime/KeyboardInputMethodService.kt`
  - `android/app/src/main/kotlin/com/tensorflowkeyboard/app/ime/KeyboardFlutterEngineStore.kt`
  - `android/app/src/main/kotlin/com/tensorflowkeyboard/app/ime/KeyboardMethodChannelHandler.kt`

## Flujo

1. Flutter renderiza el teclado.
2. Cada tecla invoca el `MethodChannel`.
3. Kotlin recibe la acción en `KeyboardMethodChannelHandler`.
4. `KeyboardInputMethodService` aplica `commitText`, `backspace`, `enter` o activa `Modo Seguro`.

## Nota técnica importante

`FlutterView` fuera de `FlutterActivity` es una integración avanzada. El scaffold actual está orientado a una UI de teclado pura en Flutter. Si más adelante integras plugins que dependen de `Activity` o Platform Views, tendrás que extender el host nativo con más wiring del ciclo de vida.

## Build

En este entorno no estaban disponibles `flutter`, `dart` ni `kotlinc`, así que no pude compilar ni probar el proyecto. Cuando tengas el SDK:

```bash
cd TensorFlowKeyboard
flutter pub get
flutter run
```
