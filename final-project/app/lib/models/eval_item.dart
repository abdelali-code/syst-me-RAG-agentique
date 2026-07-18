import 'chat_message.dart';

enum EvalStatus { pending, running, done, error }

class EvalItem {
  final String category;
  final String question;
  EvalStatus status;
  String? answer;
  List<Source> sources;
  int? elapsedMs;
  String? error;

  EvalItem({required this.category, required this.question})
      : status = EvalStatus.pending,
        sources = const [];
}
