import 'dart:async';
import 'dart:io';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:tts_func/screens/face_recognition_screen.dart';
import 'package:tts_func/services/blind_assist_service.dart';
import 'package:tts_func/services/currency_service.dart';
import 'package:tts_func/services/face_service.dart';
import 'package:tts_func/services/object_detection_service.dart';
import 'package:wakelock_plus/wakelock_plus.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../services/intent_detector.dart';
import '../services/speech_service.dart';
import '../services/ocr_service.dart';

enum ListenState { sleeping, waitingCommand, processing, speaking }

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with WidgetsBindingObserver {
  final FlutterTts _tts = FlutterTts();
  final SpeechService _speech = SpeechService();
bool _isInForeground = true;  // ← add this
  CameraController? _camera;
  ListenState _listenState = ListenState.sleeping;
  String _displayText = 'Say "hey app" to begin';
  String _lastReadText = '';   // last OCR result shown on screen
  bool _loopRunning = false;
  int _cycleCount = 0;
bool _showCaptureFlash = false;  // ← add this
  static const _platform = MethodChannel('com.example.tts_func/service');

  // ─── INIT ──────────────────────────────────────────────────────────────────

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initSystem();
  }
@override
void didChangeAppLifecycleState(AppLifecycleState state) {
  switch (state) {
    case AppLifecycleState.resumed:
      _isInForeground = true;
      try { _camera?.resumePreview(); } catch (_) {}
      if (mounted) setState(() {});
      break;
    case AppLifecycleState.paused:
      _isInForeground = false;
      try { _camera?.pausePreview(); } catch (_) {}
      break;
    case AppLifecycleState.inactive:
      _isInForeground = false;
      break;
    default:
      break;
  }
}
  Future<void> _initSystem() async {
    await _startForegroundService();
     await WakelockPlus.enable(); 
    await _initTts();
    await _initCamera();
    final ok = await _speech.init();
    if (ok) {
      await _speak('Ready. Say hey app to begin.');
      _runLoop();
    } else {
      _setDisplay('Microphone unavailable');
    }
  }

  Future<void> _startForegroundService() async {
    try {
      await _platform.invokeMethod('startService');
    } catch (e) {
      print('Service error: $e');
    }
  }

  Future<void> _initTts() async {
    await _tts.setLanguage('en-US');
    await _tts.setSpeechRate(0.45);
    await _tts.setVolume(1.0);
    await _tts.setPitch(1.0);
  }

  Future<void> _initCamera() async {
    final cameras = await availableCameras();
    if (cameras.isEmpty) return;
    _camera = CameraController(
      cameras.first,
      ResolutionPreset.high,
      enableAudio: false,
    );
    await _camera!.initialize();
    if (mounted) setState(() {});
  }

  // ─── SPEAK ────────────────────────────────────────────────────────────────

  Future<void> _speak(String text) async {
    if (!mounted) return;
    await _speech.stop();
    await Future.delayed(const Duration(milliseconds: 200));

    setState(() => _listenState = ListenState.speaking);

    final completer = Completer<void>();

    final safetyTimer = Timer(
      Duration(seconds: text.length ~/ 8 + 10),
      () { if (!completer.isCompleted) completer.complete(); },
    );

    _tts.setCompletionHandler(() {
      safetyTimer.cancel();
      if (!completer.isCompleted) completer.complete();
    });

    _tts.setErrorHandler((msg) {
      safetyTimer.cancel();
      print('TTS error: $msg');
      if (!completer.isCompleted) completer.complete();
    });

    await _tts.speak(text);
    await completer.future;
    await Future.delayed(const Duration(milliseconds: 400));
  }

  void _setDisplay(String text) {
    if (mounted) setState(() => _displayText = text);
  }

  // ─── VOICE LOOP ───────────────────────────────────────────────────────────

  Future<void> _runLoop() async {
    if (_loopRunning) return;
    _loopRunning = true;
    print('Voice loop started');

    while (mounted && _loopRunning) {
      try {
        // Re-init STT every 10 cycles to prevent Android STT going stale
        _cycleCount++;
        if (_cycleCount % 10 == 0) {
          await _speech.stop();
          await _speech.init();
          await Future.delayed(const Duration(milliseconds: 300));
        }

        // Phase 1: listen for wake word
        _setDisplay('Say "hey app" to begin');
        if (mounted) setState(() => _listenState = ListenState.sleeping);
        await _camera?.pausePreview();  // save battery while just listening

        final wakeWord = await _listenOnce(forWakeWord: true);
        if (wakeWord.isEmpty || !wakeWord.contains('hey app')) continue;

        // Phase 2: wake word heard
        if (mounted) setState(() => _listenState = ListenState.waitingCommand);
        await _speak('Yes?');

        // Phase 3: listen for command
        _setDisplay('Listening for command...');
        final command = await _listenOnce(forWakeWord: false);

        if (command.isEmpty) {
          await _speak('I did not hear a command. Say "hey app" to try again.');
          continue;
        }

        // Phase 4: handle command
        if (mounted) setState(() => _listenState = ListenState.processing);
        _setDisplay('Command: $command');
        await _handleCommand(command);

      } catch (e, stack) {
        print('Loop error: $e\n$stack');
        await Future.delayed(const Duration(seconds: 1));
      }
    }

    _loopRunning = false;
    print('Voice loop ended');
  }

  Future<String> _listenOnce({required bool forWakeWord}) async {
    final completer = Completer<String>();

    void complete(String val) {
      if (!completer.isCompleted) completer.complete(val);
    }

    final timeout = forWakeWord
        ? const Duration(seconds: 12)
        : const Duration(seconds: 8);

    final timer = Timer(timeout, () {
      _speech.stop();
      complete('');
    });

    try {
      if (forWakeWord) {
        await _speech.listenForWakeWord((text) {
          if (text.contains('hey app')) {
            timer.cancel();
            complete(text);
          }
        });
      } else {
        await _speech.listenForCommand((text) {
          timer.cancel();
          complete(text);
        });
      }
    } catch (e) {
      print('listenOnce error: $e');
      timer.cancel();
      complete('');
    }

    final result = await completer.future;
    timer.cancel();
    return result;
  }

  // ─── COMMAND HANDLER ──────────────────────────────────────────────────────

  Future<void> _handleCommand(String command) async {
    final intent = IntentDetector.detect(command);
    _setDisplay('Intent: ${intent.name}');

    switch (intent) {
      case VoiceIntent.read:
        await _runOcr();           // ← real OCR connected here
        break;
      case VoiceIntent.object:
        await _runObjectDetection();
        break;
      case VoiceIntent.currency:
        await _runCurrencyDetection();
        break;
      case VoiceIntent.people:
        await _runFaceRecognition();
        break;
         case VoiceIntent.scene:
        await _runSceneAssistant();
        break;
      case VoiceIntent.help:
        await _speak(
          'You can say: read text, detect object, detect currency, or detect people.',
        );
        break;
      case VoiceIntent.stop:
        await _speak('Going to sleep. Say "hey app" to wake me up.');
        break;
      case VoiceIntent.unknown:
        await _speak('Sorry, I did not understand. Try saying "hey app" followed by a command.');
        break;
    }
  }
Future<File?> _captureForVision() async {
  String? path;

  if (_isInForeground) {
    path = await _captureWithFlutter();
  } else {
    path = await _captureNative();
  }

  if (path == null) return null;

  final file = File(path);

  if (!await file.exists()) {
    return null;
  }

  return file;
}
  // ─── OCR ──────────────────────────────────────────────────────────────────
// Add this helper — fully reinitializes camera if needed
// Native capture — works with screen locked
Future<String?> _captureNative() async {
  try {
    final String? path = await _platform.invokeMethod('capturePhoto');
    return path;
  } catch (e) {
    print('Native capture error: $e');
    return null;
  }
}

Future<void> _runCurrencyDetection() async {
  _setDisplay('Detecting currency');

  final image = await _captureForVision();

  if (image == null) {
    await _speak('Camera error');
    return;
  }

  try {
    final result =
        await CurrencyService.analyze(image);

    if (result.count == 0) {
      await _speak('No currency detected');
      return;
    }

    final speech =
        'Detected ${result.count} notes. '
        'Total amount is ${result.totalAmount} rupees';

    setState(() {
      _displayText = speech;
      _lastReadText = speech;
    });

    await _speak(speech);
  } catch (e) {
    await _speak('Currency detection failed');
  }
}
Future<void> _runFaceRecognition() async {
  _setDisplay('Detecting faces');

  final image = await _captureForVision();

  if (image == null) {
    await _speak('Camera error');
    return;
  }

  try {
    final result =
        await FaceService.analyze(image);

    if (result.totalFacesDetected == 0) {
      await _speak('No faces detected');
      return;
    }

    final names = result.faces
        .where((e) =>
            e.status == 'recognized' &&
            e.personName != null)
        .map((e) => e.personName!)
        .toList();

    String speech;

    if (names.isEmpty) {
      speech =
          '${result.totalFacesDetected} faces detected but nobody recognized';
    } else {
      speech =
          'Recognized ${names.join(', ')}';
    }

    setState(() {
      _displayText = speech;
      _lastReadText = speech;
    });

    await _speak(speech);
  } catch (e) {
    await _speak('Face recognition failed');
  }
}
Future<void> _runSceneAssistant() async {
  _setDisplay('Analyzing scene');

  final image = await _captureForVision();

  if (image == null) {
    await _speak('Camera error');
    return;
  }

  try {
    final result =
        await BlindAssistService.analyze(image);

    setState(() {
      _displayText = result.summary;
      _lastReadText = result.summary;
    });

    await _speak(result.summary);
  } catch (e) {
    await _speak('Scene analysis failed');
  }
}
Future<void> _runObjectDetection() async {
  _setDisplay('Detecting objects');

  final image = await _captureForVision();

  if (image == null) {
    await _speak('Camera error');
    return;
  }

  try {
    final objects =
        await ObjectDetectionService.detectObjects(image);

    if (objects.isEmpty) {
      await _speak('No objects detected');
      return;
    }

    final labels = objects
        .map((e) => e.label)
        .toSet()
        .join(', ');

    setState(() {
      _displayText = labels;
      _lastReadText = labels;
    });

    await _speak('Detected $labels');
  } catch (e) {
    await _speak('Object detection failed');
  }
}
Future<void> _runOcr() async {
  if (mounted) setState(() => _listenState = ListenState.processing);

  String? photoPath;

  if (_isInForeground) {
    // ── Foreground: use Flutter CameraController ──────────────────────
    // Preview stays live so user can see what's being captured
    photoPath = await _captureWithFlutter();
  } else {
    // ── Background / screen locked: use native Camera2 ────────────────
    await _speak('Scanning. Hold steady.');
    photoPath = await _captureNative();
  }

  if (photoPath == null) {
    await _speak('Camera error. Please try again.');
    _setDisplay('Camera error');
    if (mounted) setState(() => _listenState = ListenState.sleeping);
    return;
  }

  final photoFile = File(photoPath);
  final fileSize = await photoFile.length();
  print('Photo: $photoPath ($fileSize bytes)');

  if (fileSize == 0) {
    await _speak('Photo was empty. Please try again.');
    if (mounted) setState(() => _listenState = ListenState.sleeping);
    return;
  }

  _setDisplay('Reading text...');

  String text;
  try {
    text = await OcrService.readPage(photoFile);
    print('OCR result: "$text"');
  } catch (e) {
    print('OCR error: $e');
    await _speak(
      'Could not connect to server. '
      'Make sure your PC backend is running.',
    );
    _setDisplay('Server error: $e');
    if (mounted) setState(() => _listenState = ListenState.sleeping);
    return;
  }

  if (text.trim().isEmpty) {
    await _speak(
      'No text found. Make sure the text is well lit '
      'and clearly visible, then try again.',
    );
    _setDisplay('No text detected');
    if (mounted) setState(() => _listenState = ListenState.sleeping);
    return;
  }

  if (mounted) {
    setState(() {
      _lastReadText = text;
      _displayText = text;
    });
  }

  await _speak(text);
}
Future<String?> _captureWithFlutter() async {
  // Reinitialize camera if needed
  if (_camera == null || !_camera!.value.isInitialized) {
    await _initCamera();
    await Future.delayed(const Duration(milliseconds: 500));
  }

  if (_camera == null || !_camera!.value.isInitialized) {
    return null;
  }

  try {
    // Resume preview so user sees what's being framed
    try { await _camera!.resumePreview(); } catch (_) {}

    // Brief pause so user sees the frame before capture
    await Future.delayed(const Duration(milliseconds: 600));

    // Flash the screen briefly — visual feedback for capture
    if (mounted) setState(() => _showCaptureFlash = true);
    await Future.delayed(const Duration(milliseconds: 150));
    if (mounted) setState(() => _showCaptureFlash = false);

    final photo = await _camera!.takePicture();
    return photo.path;
  } catch (e) {
    print('Flutter capture error: $e');
    // Fall back to native if Flutter camera fails
    print('Falling back to native capture...');
    return await _captureNative();
  }
}
  // ─── DISPOSE ──────────────────────────────────────────────────────────────

  @override
  void dispose() {
    WakelockPlus.disable();    
    WidgetsBinding.instance.removeObserver(this);
    _loopRunning = false;
    _speech.stop();
    _tts.stop();
    _camera?.dispose();
    super.dispose();
  }

  // ─── UI ───────────────────────────────────────────────────────────────────

Color get _stateColor => switch (_listenState) {
      ListenState.sleeping => Colors.green,
      ListenState.waitingCommand => Colors.amber,
      ListenState.processing => Colors.blue,
      ListenState.speaking => Colors.orange,
    };

IconData get _stateIcon => switch (_listenState) {
      ListenState.sleeping => Icons.mic,
      ListenState.waitingCommand => Icons.hearing,
      ListenState.processing => Icons.camera_alt,
      ListenState.speaking => Icons.volume_up,
    };

String get _stateLabel => switch (_listenState) {
      ListenState.sleeping => 'Say "hey app"',
      ListenState.waitingCommand => 'Listening for command...',
      ListenState.processing => 'Reading...',
      ListenState.speaking => 'Speaking...',
    };

@override
Widget build(BuildContext context) {
  return Scaffold(
    floatingActionButton: FloatingActionButton(
  backgroundColor: Colors.blue,
  onPressed: () {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => const FaceRecognitionScreen(),
      ),
    );
  },
  child: const Icon(Icons.person_add),
),
floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
    backgroundColor: Colors.black,
    body: GestureDetector(
      onTap: () async {
        if (_listenState == ListenState.speaking) {
          await _tts.stop();
          if (mounted) setState(() => _listenState = ListenState.sleeping);
        } else if (_listenState == ListenState.sleeping) {
          await _runOcr();
        }
      },
      child: Stack(
        fit: StackFit.expand,
        children: [

          // ── Live camera preview ────────────────────────────────────
          if (_camera != null && _camera!.value.isInitialized)
            CameraPreview(_camera!)
          else
            const Center(
              child: CircularProgressIndicator(color: Colors.white),
            ),

          // ── Book framing guide ─────────────────────────────────────
          // Shows dashed rectangle so user knows where to position book
          if (_listenState == ListenState.sleeping ||
              _listenState == ListenState.waitingCommand)
            Positioned.fill(
              child: CustomPaint(
                painter: _FramingGuidePainter(),
              ),
            ),

          // ── Capture flash ──────────────────────────────────────────
          // White flash confirms photo was taken
          if (_showCaptureFlash)
            Container(color: Colors.white.withOpacity(0.6)),

          // ── Top status bar ─────────────────────────────────────────
          Positioned(
            top: 0, left: 0, right: 0,
            child: Container(
              color: Colors.black87,
              padding: EdgeInsets.only(
                top: MediaQuery.of(context).padding.top + 8,
                bottom: 12,
                left: 16,
                right: 16,
              ),
              child: Row(
                children: [
                  if (_listenState == ListenState.sleeping)
                    _PulseDot(color: _stateColor)
                  else
                    Icon(_stateIcon, color: _stateColor, size: 22),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      _stateLabel,
                      style: TextStyle(
                        color: _stateColor,
                        fontSize: 15,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                  if (_lastReadText.isNotEmpty)
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: Colors.green.withOpacity(0.3),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.green, width: 1),
                      ),
                      child: Text(
                        '${_lastReadText.split(' ').length} words',
                        style: const TextStyle(
                            color: Colors.green, fontSize: 12),
                      ),
                    ),
                ],
              ),
            ),
          ),

          // ── Processing overlay ─────────────────────────────────────
          if (_listenState == ListenState.processing)
            Container(
              color: Colors.black54,
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const CircularProgressIndicator(
                        color: Colors.white, strokeWidth: 3),
                    const SizedBox(height: 16),
                    Text(
                      _displayText,
                      style: const TextStyle(
                          color: Colors.white, fontSize: 16),
                    ),
                  ],
                ),
              ),
            ),

          // ── Result text panel ──────────────────────────────────────
          if (_lastReadText.isNotEmpty &&
              _listenState != ListenState.processing)
            Positioned(
              bottom: 0, left: 0, right: 0,
              child: Container(
                constraints: BoxConstraints(
                  maxHeight: MediaQuery.of(context).size.height * 0.45,
                ),
                decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.92),
                  border: Border(
                      top: BorderSide(color: _stateColor, width: 2)),
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 10, 16, 4),
                      child: Row(
                        children: [
                          Icon(Icons.text_fields,
                              color: _stateColor, size: 16),
                          const SizedBox(width: 6),
                          Text(
                            'Detected text',
                            style: TextStyle(
                              color: _stateColor,
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const Spacer(),
                          if (_listenState == ListenState.speaking)
                            Row(children: [
                              const Icon(Icons.volume_up,
                                  color: Colors.orange, size: 14),
                              const SizedBox(width: 4),
                              const Text('Reading aloud...',
                                  style: TextStyle(
                                      color: Colors.orange,
                                      fontSize: 11)),
                              const SizedBox(width: 8),
                              const Text('Tap to stop',
                                  style: TextStyle(
                                      color: Colors.white38,
                                      fontSize: 11)),
                            ]),
                        ],
                      ),
                    ),
                    const Divider(color: Colors.white12, height: 1),
                    Flexible(
                      child: SingleChildScrollView(
                        padding: const EdgeInsets.all(16),
                        child: Text(
                          _lastReadText,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 17,
                            height: 1.7,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

          // ── Hint when idle ─────────────────────────────────────────
          if (_listenState == ListenState.sleeping &&
              _lastReadText.isEmpty)
            Positioned(
              bottom: 30, left: 0, right: 0,
              child: Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.black54,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Text(
                    'Tap to scan  ·  Say "hey app" to use voice',
                    style: TextStyle(color: Colors.white54, fontSize: 13),
                  ),
                ),
              ),
            ),
        ],
      ),
    ),
  );
}
}
// Draws a dashed rectangle showing where to position the book
class _FramingGuidePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.5)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5;

    // Guide box — 85% width, 70% height, centered
    final left = size.width * 0.075;
    final top = size.height * 0.15;
    final right = size.width * 0.925;
    final bottom = size.height * 0.75;

    // Dashed border
    const dashLen = 12.0;
    const gapLen = 6.0;

    void drawDashedLine(Offset start, Offset end) {
      final dx = end.dx - start.dx;
      final dy = end.dy - start.dy;
      final dist = (end - start).distance;
      final steps = (dist / (dashLen + gapLen)).floor();
      for (int i = 0; i < steps; i++) {
        final t1 = i * (dashLen + gapLen) / dist;
        final t2 = (i * (dashLen + gapLen) + dashLen) / dist;
        canvas.drawLine(
          Offset(start.dx + dx * t1, start.dy + dy * t1),
          Offset(start.dx + dx * t2.clamp(0, 1),
              start.dy + dy * t2.clamp(0, 1)),
          paint,
        );
      }
    }

    drawDashedLine(Offset(left, top), Offset(right, top));     // top
    drawDashedLine(Offset(right, top), Offset(right, bottom)); // right
    drawDashedLine(Offset(right, bottom), Offset(left, bottom)); // bottom
    drawDashedLine(Offset(left, bottom), Offset(left, top));   // left

    // Corner highlights — solid bright corners
    final cornerPaint = Paint()
      ..color = Colors.white.withOpacity(0.9)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3
      ..strokeCap = StrokeCap.round;

    const cLen = 24.0;

    // Top-left
    canvas.drawLine(Offset(left, top + cLen), Offset(left, top), cornerPaint);
    canvas.drawLine(Offset(left, top), Offset(left + cLen, top), cornerPaint);
    // Top-right
    canvas.drawLine(
        Offset(right - cLen, top), Offset(right, top), cornerPaint);
    canvas.drawLine(
        Offset(right, top), Offset(right, top + cLen), cornerPaint);
    // Bottom-left
    canvas.drawLine(
        Offset(left, bottom - cLen), Offset(left, bottom), cornerPaint);
    canvas.drawLine(
        Offset(left, bottom), Offset(left + cLen, bottom), cornerPaint);
    // Bottom-right
    canvas.drawLine(
        Offset(right, bottom - cLen), Offset(right, bottom), cornerPaint);
    canvas.drawLine(
        Offset(right, bottom), Offset(right - cLen, bottom), cornerPaint);

    // Center label
    final textPainter = TextPainter(
      text: TextSpan(
        text: 'Position book within frame',
        style: TextStyle(
          color: Colors.white.withOpacity(0.6),
          fontSize: 13,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    textPainter.paint(
      canvas,
      Offset(
        (size.width - textPainter.width) / 2,
        bottom + 10,
      ),
    );
  }

  @override
  bool shouldRepaint(_FramingGuidePainter old) => false;
}
// Animated mic pulse dot
class _PulseDot extends StatefulWidget {
  final Color color;
  const _PulseDot({required this.color});
  @override
  State<_PulseDot> createState() => _PulseDotState();
}

class _PulseDotState extends State<_PulseDot>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  late Animation<double> _anim;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 1),
    )..repeat(reverse: true);
    _anim = Tween(begin: 10.0, end: 20.0).animate(
      CurvedAnimation(parent: _ctrl, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _anim,
      builder: (_, __) => Container(
        width: _anim.value * 2,
        height: _anim.value * 2,
        decoration: BoxDecoration(
          color: widget.color.withOpacity(0.6),
          shape: BoxShape.circle,
        ),
      ),
    );
  }
}

