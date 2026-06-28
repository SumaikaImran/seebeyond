import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import 'api_config.dart';

class CurrencyDetection {
  const CurrencyDetection({
    required this.className,
    required this.value,
    required this.confidence,
  });

  final String className;
  final int value;
  final double confidence;

  factory CurrencyDetection.fromJson(Map<String, dynamic> json) {
    return CurrencyDetection(
      className: json['class_name'] as String? ?? 'unknown note',
      value: (json['value'] as num?)?.toInt() ?? 0,
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0,
    );
  }
}

class CurrencyResult {
  const CurrencyResult({
    required this.count,
    required this.totalAmount,
    required this.detections,
  });

  final int count;
  final int totalAmount;
  final List<CurrencyDetection> detections;

  factory CurrencyResult.fromJson(Map<String, dynamic> json) {
    final items = json['detections'] as List<dynamic>? ?? [];
    return CurrencyResult(
      count: (json['count'] as num?)?.toInt() ?? items.length,
      totalAmount: (json['total_amount'] as num?)?.toInt() ?? 0,
      detections: items
          .map(
            (item) => CurrencyDetection.fromJson(item as Map<String, dynamic>),
          )
          .toList(),
    );
  }
}

class CurrencyService {
  static Future<CurrencyResult> analyze(File imageFile) async {
    final request = http.MultipartRequest(
      'POST',
      ApiConfig.uri('/api/currency/analyze'),
    );
    request.files.add(
      await http.MultipartFile.fromPath('file', imageFile.path),
    );

    final streamed = await request.send().timeout(const Duration(seconds: 45));
    final response = await http.Response.fromStream(streamed);

    if (response.statusCode != 200) {
      throw Exception(
        'Currency detection failed ${response.statusCode}: ${response.body}',
      );
    }

    return CurrencyResult.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }
}
