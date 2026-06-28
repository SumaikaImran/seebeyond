import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import 'api_config.dart';

class BlindAssistResult {
  const BlindAssistResult({required this.summary, required this.text});

  final String summary;
  final String text;

  factory BlindAssistResult.fromJson(Map<String, dynamic> json) {
    return BlindAssistResult(
      summary: json['summary'] as String? ?? 'No scene summary available.',
      text: json['text'] as String? ?? '',
    );
  }
}

class BlindAssistService {
  static Future<BlindAssistResult> analyze(File imageFile) async {
    final request = http.MultipartRequest(
      'POST',
      ApiConfig.uri('/api/blind-assist/analyze'),
    );
    request.files.add(
      await http.MultipartFile.fromPath('file', imageFile.path),
    );

    final streamed = await request.send().timeout(const Duration(seconds: 60));
    final response = await http.Response.fromStream(streamed);
    if (response.statusCode != 200) {
      throw Exception(
        'Scene assistant failed ${response.statusCode}: ${response.body}',
      );
    }

    return BlindAssistResult.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }
}
