import 'package:flutter/widgets.dart';

import 'keyboard/keyboard_app.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const KeyboardApp());
}

@pragma('vm:entry-point')
void keyboardEntrypoint() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const KeyboardApp());
}
