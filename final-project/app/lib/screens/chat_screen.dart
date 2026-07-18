import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';

import '../models/chat_message.dart';
import '../services/api_service.dart';
import '../widgets/message_bubble.dart';
import 'eval_screen.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ApiService _api = ApiService();
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  late final String _threadId;
  final List<ChatMessage> _messages = [];
  List<String> _codes = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _threadId = const Uuid().v4();
    _loadCodes();
  }

  Future<void> _loadCodes() async {
    try {
      final codes = await _api.getCodes();
      setState(() => _codes = codes);
    } catch (_) {
      // Non-critical: the hint row is just a convenience.
    }
  }

  Future<void> _send() async {
    final question = _controller.text.trim();
    if (question.isEmpty || _isLoading) return;

    setState(() {
      _messages.add(ChatMessage(isUser: true, text: question));
      _isLoading = true;
      _controller.clear();
    });
    _scrollToBottom();

    try {
      final result = await _api.ask(question, _threadId);
      setState(() {
        _messages.add(ChatMessage(
          isUser: false,
          text: result.answer,
          sources: result.sources,
        ));
      });
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(
          isUser: false,
          text: "Erreur lors de la communication avec le serveur : $e",
        ));
      });
    } finally {
      setState(() => _isLoading = false);
      _scrollToBottom();
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Assistant Juridique Marocain'),
        actions: [
          IconButton(
            tooltip: 'Évaluation (jeu de questions)',
            icon: const Icon(Icons.checklist),
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const EvalScreen()),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          if (_codes.isNotEmpty)
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 8, 12, 0),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  'Base documentaire : ${_codes.join(", ")}',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ),
            ),
          Expanded(
            child: _messages.isEmpty
                ? const Center(
                    child: Padding(
                      padding: EdgeInsets.all(24),
                      child: Text(
                        'Posez une question de droit marocain (Code de la Famille, Code du Travail).',
                        textAlign: TextAlign.center,
                      ),
                    ),
                  )
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(12),
                    itemCount: _messages.length,
                    itemBuilder: (context, index) => MessageBubble(message: _messages[index]),
                  ),
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                  SizedBox(width: 10),
                  Text("L'assistant réfléchit..."),
                ],
              ),
            ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      decoration: const InputDecoration(
                        hintText: 'Votre question...',
                        border: OutlineInputBorder(),
                      ),
                      onSubmitted: (_) => _send(),
                      enabled: !_isLoading,
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton.filled(
                    onPressed: _isLoading ? null : _send,
                    icon: const Icon(Icons.send),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
