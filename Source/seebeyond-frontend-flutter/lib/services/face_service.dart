import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import 'api_config.dart';

class RecognizedFace {
  const RecognizedFace({
    required this.personName,
    required this.confidence,
    required this.status,
  });

  final String? personName;
  final double confidence;
  final String status;

  factory RecognizedFace.fromJson(Map<String, dynamic> json) {
    return RecognizedFace(
      personName: json['person_name'] as String?,
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0,
      status: json['status'] as String? ?? 'unknown',
    );
  }
}

class FaceAnalyzeResult {
  const FaceAnalyzeResult({
    required this.totalFacesDetected,
    required this.totalFacesRecognized,
    required this.faces,
  });

  final int totalFacesDetected;
  final int totalFacesRecognized;
  final List<RecognizedFace> faces;

  factory FaceAnalyzeResult.fromJson(Map<String, dynamic> json) {
    final faces = json['faces'] as List<dynamic>? ?? [];
    return FaceAnalyzeResult(
      totalFacesDetected: (json['total_faces_detected'] as num?)?.toInt() ?? 0,
      totalFacesRecognized:
          (json['total_faces_recognized'] as num?)?.toInt() ?? 0,
      faces: faces
          .map((item) => RecognizedFace.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}

class FaceService {
  static Future<FaceAnalyzeResult> analyze(File imageFile) async {
    final request = http.MultipartRequest(
      'POST',
      ApiConfig.uri('/api/face/analyze'),
    );
    request.files.add(
      await http.MultipartFile.fromPath('image', imageFile.path),
    );

    final streamed = await request.send().timeout(const Duration(seconds: 45));
    final response = await http.Response.fromStream(streamed);
    if (response.statusCode != 200) {
      throw Exception(
        'Face analysis failed ${response.statusCode}: ${response.body}',
      );
    }
    return FaceAnalyzeResult.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  static Future<String> register({
    required String name,
    required File imageFile,
  }) async {
    final uri = ApiConfig.uri(
      '/api/face/register?name=${Uri.encodeQueryComponent(name)}',
    );
    final request = http.MultipartRequest('POST', uri);
    request.files.add(
      await http.MultipartFile.fromPath('image', imageFile.path),
    );

    final streamed = await request.send().timeout(const Duration(seconds: 45));
    final response = await http.Response.fromStream(streamed);
    if (response.statusCode != 200) {
      throw Exception(
        'Face registration failed ${response.statusCode}: ${response.body}',
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return data['message'] as String? ?? 'Face registered successfully';
  }
}
