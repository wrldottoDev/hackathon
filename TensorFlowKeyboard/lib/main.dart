import 'package:flutter/widgets.dart';

import 'keyboard/alerts/local_alert_notification_service.dart';
import 'keyboard/keyboard_app.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await LocalAlertNotificationService.instance.initialize();
  runApp(const KeyboardApp.application());
}

@pragma('vm:entry-point')
Future<void> keyboardEntrypoint() async {
  WidgetsFlutterBinding.ensureInitialized();
  await LocalAlertNotificationService.instance.initialize();
  runApp(const KeyboardApp.keyboard());
}
