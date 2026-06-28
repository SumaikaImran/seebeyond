import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class OcrService {
  static const String _baseUrl = 'http://192.168.1.9:8000';

  static Future<String> readPage(File imageFile) async {
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$_baseUrl/api/ocr/read'),
    );
    request.files.add(
      await http.MultipartFile.fromPath('file', imageFile.path),
    );

    final streamed = await request.send()
        .timeout(const Duration(seconds: 90));
    final response = await http.Response.fromStream(streamed);

    print('Server response ${response.statusCode}: ${response.body}');

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      final text = data['text'] as String? ?? '';
      print('Extracted text: "$text"');
      return text;
    }
    throw Exception('OCR failed ${response.statusCode}: ${response.body}');
  }
}