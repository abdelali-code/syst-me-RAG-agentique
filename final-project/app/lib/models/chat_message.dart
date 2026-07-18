class Source {
  final String code;
  final String article;

  Source({required this.code, required this.article});

  factory Source.fromJson(Map<String, dynamic> json) {
    return Source(
      code: json['code'] as String,
      article: json['article'] as String,
    );
  }
}

class ChatMessage {
  final bool isUser;
  final String text;
  final List<Source> sources;

  ChatMessage({
    required this.isUser,
    required this.text,
    this.sources = const [],
  });
}
