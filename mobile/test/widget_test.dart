import 'package:flutter_test/flutter_test.dart';

import 'package:frcaixinha/main.dart';

void main() {
  testWidgets('A tela inicial apresenta o nome e a mensagem', (tester) async {
    await tester.pumpWidget(const FRcaixinhaApp());

    expect(find.text('FRcaixinha 2.2'), findsOneWidget);
    expect(find.text('Base técnica em preparação'), findsOneWidget);
  });
}
