import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import 'api_config.dart';

class DetectedObject {
  final String label;
  final double confidence;
  final String region;

  DetectedObject({
    required this.label,
    required this.confidence,
    required this.region,
  });

  factory DetectedObject.fromJson(Map<String, dynamic> json) {
    return DetectedObject(
      label: json['label'] as String? ?? 'unknown',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      region: json['region'] as String? ?? 'unknown',
    );
  }
}

class ObjectDetectionService {
  static Future<List<DetectedObject>> detectObjects(File imageFile) async {
    final uri = ApiConfig.uri('/api/object/detect');
    final request = http.MultipartRequest('POST', uri);
    request.files.add(
      await http.MultipartFile.fromPath('image', imageFile.path),
    );

    final streamedResponse = await request.send().timeout(
      const Duration(seconds: 60),
    );
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode != 200) {
      throw Exception(
        'Detection failed (${response.statusCode}): ${response.body}',
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final objects = data['objects'] as List<dynamic>?;

    return objects
            ?.map(
              (item) => DetectedObject.fromJson(item as Map<String, dynamic>),
            )
            .toList() ??
        [];
  }
}
