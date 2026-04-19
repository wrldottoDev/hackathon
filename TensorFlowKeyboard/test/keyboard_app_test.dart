import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tensorflow_keyboard/keyboard/keyboard_app.dart';

void main() {
  testWidgets('renders keyboard shell with security alerts', (tester) async {
    await tester.pumpWidget(const KeyboardApp());
    await tester.pump();

    expect(find.text('Teclado Seguro Local'), findsOneWidget);
    expect(find.text('Reglas de Alerta'), findsOneWidget);

    await tester.scrollUntilVisible(
      find.text('Mantén: Modo Seguro'),
      300,
      scrollable: find.byType(Scrollable).first,
    );

    expect(find.text('Mantén: Modo Seguro'), findsOneWidget);
    expect(find.text('Espacio'), findsOneWidget);
  });
}
