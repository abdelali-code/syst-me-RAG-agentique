import 'package:flutter/material.dart';

import '../models/eval_item.dart';
import 'source_chips.dart';

class EvalItemCard extends StatelessWidget {
  final int index;
  final EvalItem item;

  const EvalItemCard({super.key, required this.index, required this.item});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 6),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Chip(
                  label: Text(item.category, style: const TextStyle(fontSize: 11)),
                  visualDensity: VisualDensity.compact,
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Q$index. ${item.question}',
                    style: theme.textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600),
                  ),
                ),
                _StatusIndicator(status: item.status, elapsedMs: item.elapsedMs),
              ],
            ),
            const SizedBox(height: 8),
            if (item.status == EvalStatus.done) ...[
              Text(item.answer ?? ''),
              SourceChips(sources: item.sources),
            ] else if (item.status == EvalStatus.error)
              Text(
                "Erreur : ${item.error}",
                style: TextStyle(color: theme.colorScheme.error),
              ),
          ],
        ),
      ),
    );
  }
}

class _StatusIndicator extends StatelessWidget {
  final EvalStatus status;
  final int? elapsedMs;

  const _StatusIndicator({required this.status, required this.elapsedMs});

  @override
  Widget build(BuildContext context) {
    switch (status) {
      case EvalStatus.pending:
        return const Icon(Icons.schedule, size: 16, color: Colors.grey);
      case EvalStatus.running:
        return const SizedBox(
          width: 14,
          height: 14,
          child: CircularProgressIndicator(strokeWidth: 2),
        );
      case EvalStatus.done:
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.check_circle, size: 16, color: Colors.green),
            if (elapsedMs != null) ...[
              const SizedBox(width: 4),
              Text('${(elapsedMs! / 1000).toStringAsFixed(1)}s',
                  style: const TextStyle(fontSize: 11, color: Colors.grey)),
            ],
          ],
        );
      case EvalStatus.error:
        return const Icon(Icons.error, size: 16, color: Colors.red);
    }
  }
}
