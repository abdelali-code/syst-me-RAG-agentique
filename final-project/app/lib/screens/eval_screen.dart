import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';

import '../models/eval_item.dart';
import '../services/api_service.dart';
import '../widgets/eval_item_card.dart';

const List<String> _kCategoryOptions = ['simple', 'complexe', 'toutes'];
const List<int?> _kLimitOptions = [3, 5, null]; // null = toutes les questions

class EvalScreen extends StatefulWidget {
  const EvalScreen({super.key});

  @override
  State<EvalScreen> createState() => _EvalScreenState();
}

class _EvalScreenState extends State<EvalScreen> {
  final ApiService _api = ApiService();
  final ScrollController _scrollController = ScrollController();

  Map<String, List<String>>? _questionsByCategory;
  String? _loadError;

  String _category = 'simple';
  int? _limit = 3;

  final List<EvalItem> _items = [];
  bool _isRunning = false;
  bool _cancelRequested = false;

  @override
  void initState() {
    super.initState();
    _loadQuestions();
  }

  Future<void> _loadQuestions() async {
    try {
      final questions = await _api.getEvalQuestions();
      setState(() => _questionsByCategory = questions);
    } catch (e) {
      setState(() => _loadError = e.toString());
    }
  }

  List<EvalItem> _buildSelection() {
    if (_questionsByCategory == null) return [];
    final categories = _category == 'toutes' ? ['simple', 'complexe'] : [_category];
    final items = <EvalItem>[];
    for (final cat in categories) {
      final questions = _questionsByCategory![cat] ?? [];
      final selected = _limit == null ? questions : questions.take(_limit!).toList();
      items.addAll(selected.map((q) => EvalItem(category: cat, question: q)));
    }
    return items;
  }

  Future<void> _run() async {
    final selection = _buildSelection();
    if (selection.isEmpty) return;

    setState(() {
      _items
        ..clear()
        ..addAll(selection);
      _isRunning = true;
      _cancelRequested = false;
    });

    for (final item in _items) {
      if (_cancelRequested) break;

      setState(() => item.status = EvalStatus.running);
      _scrollToBottom();

      final stopwatch = Stopwatch()..start();
      try {
        final result = await _api.ask(item.question, const Uuid().v4());
        stopwatch.stop();
        setState(() {
          item.answer = result.answer;
          item.sources = result.sources;
          item.elapsedMs = stopwatch.elapsedMilliseconds;
          item.status = EvalStatus.done;
        });
      } catch (e) {
        stopwatch.stop();
        setState(() {
          item.error = e.toString();
          item.status = EvalStatus.error;
        });
      }
      _scrollToBottom();
    }

    setState(() => _isRunning = false);
  }

  void _stop() => setState(() => _cancelRequested = true);

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
    final done = _items.where((i) => i.status == EvalStatus.done || i.status == EvalStatus.error).length;

    return Scaffold(
      appBar: AppBar(title: const Text('Évaluation (jeu de questions)')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (_loadError != null)
                  Text(
                    'Impossible de charger les questions : $_loadError',
                    style: TextStyle(color: Theme.of(context).colorScheme.error),
                  )
                else if (_questionsByCategory == null)
                  const LinearProgressIndicator()
                else
                  Wrap(
                    spacing: 16,
                    runSpacing: 8,
                    crossAxisAlignment: WrapCrossAlignment.center,
                    children: [
                      SegmentedButton<String>(
                        segments: _kCategoryOptions
                            .map((c) => ButtonSegment(value: c, label: Text(c)))
                            .toList(),
                        selected: {_category},
                        onSelectionChanged: _isRunning
                            ? null
                            : (s) => setState(() => _category = s.first),
                      ),
                      DropdownButton<int?>(
                        value: _limit,
                        items: _kLimitOptions
                            .map((n) => DropdownMenuItem(
                                  value: n,
                                  child: Text(n == null ? 'Toutes les questions' : '$n questions'),
                                ))
                            .toList(),
                        onChanged: _isRunning ? null : (n) => setState(() => _limit = n),
                      ),
                      FilledButton.icon(
                        onPressed: (_isRunning || _questionsByCategory == null) ? null : _run,
                        icon: const Icon(Icons.play_arrow),
                        label: const Text('Lancer'),
                      ),
                      if (_isRunning)
                        OutlinedButton.icon(
                          onPressed: _stop,
                          icon: const Icon(Icons.stop),
                          label: const Text('Arrêter'),
                        ),
                    ],
                  ),
                if (_items.isNotEmpty) ...[
                  const SizedBox(height: 10),
                  LinearProgressIndicator(value: _items.isEmpty ? 0 : done / _items.length),
                  const SizedBox(height: 4),
                  Text('$done / ${_items.length} questions traitées'),
                ],
              ],
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child: _items.isEmpty
                ? const Center(child: Text('Choisissez une catégorie puis "Lancer".'))
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    itemCount: _items.length,
                    itemBuilder: (context, index) =>
                        EvalItemCard(index: index + 1, item: _items[index]),
                  ),
          ),
        ],
      ),
    );
  }
}
