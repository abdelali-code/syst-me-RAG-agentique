import 'dart:convert';
import 'package:http/http.dart' as http;

import '../config.dart';
import '../models/chat_message.dart';

class ChatResult {
  final String answer;
  final String threadId;
  final List<Source> sources;

  ChatResult({required this.answer, required this.threadId, required this.sources});
}

class ApiService {
  Future<bool> getHealth() async {
    final res = await http.get(Uri.parse('$kApiBaseUrl/health'));
    return res.statusCode == 200;
  }

  Future<List<String>> getCodes() async {
    final res = await http.get(Uri.parse('$kApiBaseUrl/codes'));
    if (res.statusCode != 200) {
      throw Exception('Failed to load codes (${res.statusCode})');
    }
    final data = jsonDecode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>;
    return (data['codes'] as List).cast<String>();
  }

  Future<Map<String, List<String>>> getEvalQuestions() async {
    final res = await http.get(Uri.parse('$kApiBaseUrl/eval/questions'));
    if (res.statusCode != 200) {
      throw Exception('Failed to load eval questions (${res.statusCode})');
    }
    final data = jsonDecode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>;
    return {
      'simple': (data['simple'] as List).cast<String>(),
      'complexe': (data['complexe'] as List).cast<String>(),
    };
  }

  Future<ChatResult> ask(String question, String threadId) async {
    final res = await http.post(
      Uri.parse('$kApiBaseUrl/chat'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'question': question, 'thread_id': threadId}),
    );
    if (res.statusCode != 200) {
      throw Exception('Chat request failed (${res.statusCode}): ${res.body}');
    }
    final data = jsonDecode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>;
    final sources = (data['sources'] as List)
        .map((s) => Source.fromJson(s as Map<String, dynamic>))
        .toList();
    return ChatResult(
      answer: data['answer'] as String,
      threadId: data['thread_id'] as String,
      sources: sources,
    );
  }
}
