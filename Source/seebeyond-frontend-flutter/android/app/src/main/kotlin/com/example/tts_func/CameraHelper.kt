package com.example.tts_func

import android.annotation.SuppressLint
import android.content.Context
import android.graphics.ImageFormat
import android.hardware.camera2.*
import android.media.ImageReader
import android.os.Handler
import android.os.HandlerThread
import java.io.File
import java.io.FileOutputStream

class CameraHelper(private val context: Context) {

    private var cameraDevice: CameraDevice? = null
    private var captureSession: CameraCaptureSession? = null
    private var imageReader: ImageReader? = null
    private var backgroundThread: HandlerThread? = null
    private var backgroundHandler: Handler? = null

    // ── background thread for camera ops ──────────────────────────────────
    private fun startBackground() {
        backgroundThread = HandlerThread("CameraBackground").also { it.start() }
        backgroundHandler = Handler(backgroundThread!!.looper)
    }

    private fun stopBackground() {
        backgroundThread?.quitSafely()
        try { backgroundThread?.join() } catch (_: InterruptedException) {}
        backgroundThread = null
        backgroundHandler = null
    }

    // ── main capture method ───────────────────────────────────────────────
    @SuppressLint("MissingPermission")
    fun capturePhoto(outputPath: String, onDone: (String?) -> Unit) {
        startBackground()

        val manager = context.getSystemService(Context.CAMERA_SERVICE)
                as CameraManager

        // Pick back-facing camera
        val cameraId = manager.cameraIdList.firstOrNull { id ->
            manager.getCameraCharacteristics(id)
                .get(CameraCharacteristics.LENS_FACING) ==
                    CameraCharacteristics.LENS_FACING_BACK
        } ?: run {
            onDone(null)
            return
        }

        // ImageReader — receives the captured JPEG
        imageReader = ImageReader.newInstance(1920, 1080,
            ImageFormat.JPEG, 2)

        imageReader!!.setOnImageAvailableListener({ reader ->
            val image = reader.acquireLatestImage() ?: return@setOnImageAvailableListener
            try {
                val buffer = image.planes[0].buffer
                val bytes = ByteArray(buffer.remaining())
                buffer.get(bytes)
                FileOutputStream(outputPath).use { it.write(bytes) }
                onDone(outputPath)
            } catch (e: Exception) {
                onDone(null)
            } finally {
                image.close()
                closeCamera()
            }
        }, backgroundHandler)

        // Open camera
        manager.openCamera(cameraId, object : CameraDevice.StateCallback() {
            override fun onOpened(camera: CameraDevice) {
                cameraDevice = camera
                createCaptureSession(onDone)
            }
            override fun onDisconnected(camera: CameraDevice) {
                camera.close()
                cameraDevice = null
                onDone(null)
            }
            override fun onError(camera: CameraDevice, error: Int) {
                camera.close()
                cameraDevice = null
                onDone(null)
            }
        }, backgroundHandler)
    }

    private fun createCaptureSession(onDone: (String?) -> Unit) {
        val camera = cameraDevice ?: run { onDone(null); return }
        val surface = imageReader!!.surface

        camera.createCaptureSession(
            listOf(surface),
            object : CameraCaptureSession.StateCallback() {
                override fun onConfigured(session: CameraCaptureSession) {
                    captureSession = session
                    triggerCapture(session, onDone)
                }
                override fun onConfigureFailed(session: CameraCaptureSession) {
                    onDone(null)
                    closeCamera()
                }
            },
            backgroundHandler
        )
    }

    private fun triggerCapture(
        session: CameraCaptureSession,
        onDone: (String?) -> Unit
    ) {
        val camera = cameraDevice ?: run { onDone(null); return }

        val captureBuilder = camera.createCaptureRequest(
            CameraDevice.TEMPLATE_STILL_CAPTURE
        ).apply {
            addTarget(imageReader!!.surface)
            set(CaptureRequest.CONTROL_MODE, CaptureRequest.CONTROL_MODE_AUTO)
            set(CaptureRequest.CONTROL_AF_MODE,
                CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE)
            set(CaptureRequest.CONTROL_AE_MODE,
                CaptureRequest.CONTROL_AE_MODE_ON_AUTO_FLASH)
            set(CaptureRequest.JPEG_QUALITY, 90)
        }

        session.capture(captureBuilder.build(),
            object : CameraCaptureSession.CaptureCallback() {
                override fun onCaptureFailed(
                    session: CameraCaptureSession,
                    request: CaptureRequest,
                    failure: CaptureFailure
                ) {
                    onDone(null)
                    closeCamera()
                }
            },
            backgroundHandler
        )
        // Result delivered via ImageReader.OnImageAvailableListener
    }

    private fun closeCamera() {
        captureSession?.close(); captureSession = null
        cameraDevice?.close();   cameraDevice = null
        imageReader?.close();    imageReader = null
        stopBackground()
    }
}