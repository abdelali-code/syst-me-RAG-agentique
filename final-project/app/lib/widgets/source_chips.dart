import 'package:flutter/material.dart';

import '../models/chat_message.dart';

class SourceChips extends StatelessWidget {
  final List<Source> sources;

  const SourceChips({super.key, required this.sources});

  @override
  Widget build(BuildContext context) {
    if (sources.isEmpty) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(top: 6),
      child: Wrap(
        spacing: 6,
        runSpacing: 6,
        children: sources.map((s) {
          final label = s.article.toLowerCase() == 'none'
              ? s.code
              : '${s.code} · Article ${s.article}';
          return Chip(
            label: Text(label, style: const TextStyle(fontSize: 11)),
            visualDensity: VisualDensity.compact,
            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
          );
        }).toList(),
      ),
    );
  }
}
