import 'dart:async';
import 'package:speech_to_text/speech_to_text.dart';

class SpeechService {
  final SpeechToText _stt = SpeechToText();
  bool _initialized = false;

  static const _ignoredErrors = {
    'error_no_match',
    'error_speech_timeout',
    'error_no_recognition_service',
  };

  Future<bool> init() async {
    _initialized = await _stt.initialize(
      onError: (e) {
        if (!_ignoredErrors.contains(e.errorMsg)) {
          print('STT real error: ${e.errorMsg}');
        }
      },
      onStatus: (s) => print('STT status: $s'),
    );
    return _initialized;
  }

  bool get isListening => _stt.isListening;

  Future<void> listenForWakeWord(Function(String) onResult) async {
    if (!_initialized) return;
    if (_stt.isListening) await stop();
    try {
      await _stt.listen(
        partialResults: true,
        listenFor: const Duration(seconds: 12),
        pauseFor: const Duration(seconds: 3),
        cancelOnError: false,
        onResult: (result) {
          if (result.recognizedWords.isNotEmpty) {
            onResult(result.recognizedWords.toLowerCase());
          }
        },
      );
    } catch (e) {
      print('listenForWakeWord error: $e');
    }
  }

  Future<void> listenForCommand(Function(String) onResult) async {
    if (!_initialized) return;
    if (_stt.isListening) await stop();
    try {
      await _stt.listen(
        partialResults: false,
        listenFor: const Duration(seconds: 8),
        pauseFor: const Duration(seconds: 2),
        cancelOnError: false,
        onResult: (result) {
          if (result.finalResult && result.recognizedWords.isNotEmpty) {
            onResult(result.recognizedWords.toLowerCase());
          }
        },
      );
    } catch (e) {
      print('listenForCommand error: $e');
    }
  }

  Future<void> stop() async {
    try {
      if (_stt.isListening) await _stt.stop();
    } catch (_) {}
    await Future.delayed(const Duration(milliseconds: 400));
  }
}