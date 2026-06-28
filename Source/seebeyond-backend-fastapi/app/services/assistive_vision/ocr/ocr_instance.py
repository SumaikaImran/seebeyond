import os

os.environ["PADDLE_PDX_DISABLE_MKLDNN_MODEL_BL"] = "True"
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "False"

from paddleocr import PaddleOCR

print("Loading PaddleOCR model...")

ocr_model = PaddleOCR(
    lang="en",
    use_angle_cls=True,
    # show_log=False
)

print("PaddleOCR loaded successfully")