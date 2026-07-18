import 'package:flutter/material.dart';

import 'screens/chat_screen.dart';

void main() {
  runApp(const RagJuridiqueApp());
}

class RagJuridiqueApp extends StatelessWidget {
  const RagJuridiqueApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Assistant Juridique Marocain',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
      ),
      home: const ChatScreen(),
    );
  }
}
