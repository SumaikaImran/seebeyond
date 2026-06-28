enum VoiceIntent { read, object, currency, people, scene, help, stop, unknown }

class IntentDetector {
  static VoiceIntent detect(String text) {
    text = text.toLowerCase();

    if (text.contains('currency') || text.contains('money') ||
        text.contains('note') || text.contains('rupee') ||
        text.contains('dollar') || text.contains('cash')) {
      return VoiceIntent.currency;
    }
    if (text.contains('person') || text.contains('people') ||
        text.contains('who') || text.contains('face')) {
      return VoiceIntent.people;
    }
   

if (text.contains('scene') ||
    text.contains('describe') ||
    text.contains('surrounding')) {
  return VoiceIntent.scene;
}
    if (text.contains('object') || text.contains('what is') ||
        text.contains('identify')) {
      return VoiceIntent.object;
    }
    if (text.contains('read') || text.contains('scan') ||
        text.contains('text') || text.contains('what does') ||
        text.contains('ocr')) {
      return VoiceIntent.read;
    }
    if (text.contains('help') || text.contains('what can')) {
      return VoiceIntent.help;
    }
    if (text.contains('stop') || text.contains('quit') ||
        text.contains('cancel')) {
      return VoiceIntent.stop;
    }
    return VoiceIntent.unknown;
  }
}