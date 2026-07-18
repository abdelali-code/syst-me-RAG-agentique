import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:rag_juridique_app/main.dart';

void main() {
  testWidgets('Chat screen renders with input field', (WidgetTester tester) async {
    await tester.pumpWidget(const RagJuridiqueApp());

    expect(find.text('Assistant Juridique Marocain'), findsOneWidget);
    expect(find.byType(TextField), findsOneWidget);
    expect(find.byIcon(Icons.send), findsOneWidget);
  });
}
