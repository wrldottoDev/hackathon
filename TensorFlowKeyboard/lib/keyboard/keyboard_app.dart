import 'package:flutter/material.dart';

import '../app/screens/app_bootstrap_screen.dart';
import 'keyboard_screen.dart';

enum KeyboardAppMode {
  application,
  keyboard,
}

class KeyboardApp extends StatelessWidget {
  const KeyboardApp({
    super.key,
    this.mode = KeyboardAppMode.keyboard,
  });

  const KeyboardApp.application({
    super.key,
  }) : mode = KeyboardAppMode.application;

  const KeyboardApp.keyboard({
    super.key,
  }) : mode = KeyboardAppMode.keyboard;

  final KeyboardAppMode mode;

  @override
  Widget build(BuildContext context) {
    final scheme = ColorScheme.fromSeed(
      seedColor: const Color(0xFF0F5A4F),
      brightness: Brightness.light,
    );

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Teclado Seguro Local',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: scheme,
        scaffoldBackgroundColor: const Color(0xFFF3F0E8),
      ),
      home: mode == KeyboardAppMode.application
          ? const AppBootstrapScreen()
          : const KeyboardScreen(),
    );
  }
}
