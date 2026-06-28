package com.example.tts_func

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import java.io.File

class MainActivity : FlutterActivity() {
    private val CHANNEL = "com.example.tts_func/service"
    private val PERMISSION_CODE = 100

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        requestAppPermissions()

        MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            CHANNEL
        ).setMethodCallHandler { call, result ->
            when (call.method) {

                "startService" -> {
                    try {
                        startForegroundService(
                            Intent(this, AssistantService::class.java)
                        )
                        result.success(null)
                    } catch (e: Exception) {
                        result.error("SERVICE_ERROR", e.message, null)
                    }
                }

                "stopService" -> {
                    stopService(Intent(this, AssistantService::class.java))
                    result.success(null)
                }

                "capturePhoto" -> {
                    val outputFile = File(
                        cacheDir,
                        "ocr_capture_${System.currentTimeMillis()}.jpg"
                    )
                    val helper = CameraHelper(applicationContext)
                    helper.capturePhoto(outputFile.absolutePath) { path ->
                        runOnUiThread {
                            if (path != null) {
                                result.success(path)
                            } else {
                                result.error(
                                    "CAMERA_ERROR",
                                    "Native capture failed",
                                    null
                                )
                            }
                        }
                    }
                }

                else -> result.notImplemented()
            }
        }
    }

    private fun requestAppPermissions() {
        val needed = listOf(
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO,
        ).filter {
            ContextCompat.checkSelfPermission(this, it) !=
                    PackageManager.PERMISSION_GRANTED
        }
        if (needed.isNotEmpty()) {
            ActivityCompat.requestPermissions(
                this, needed.toTypedArray(), PERMISSION_CODE
            )
        }
    }
}