import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tensorflow_keyboard/keyboard/keyboard_app.dart';

void main() {
  testWidgets('renders compact keyboard shell with number row', (tester) async {
    await tester.pumpWidget(const KeyboardApp());
    await tester.pump();

    expect(find.text('1'), findsOneWidget);
    expect(find.text('Q'), findsOneWidget);

    expect(find.text('Seguro'), findsOneWidget);
    expect(find.text('Espacio'), findsOneWidget);
  });
}
