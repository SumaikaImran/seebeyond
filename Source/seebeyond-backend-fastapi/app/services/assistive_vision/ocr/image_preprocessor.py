import cv2

class OCRImagePreprocessor:

    @staticmethod
    def preprocess(frame):
        h, w = frame.shape[:2]

        max_dim = 1920

        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)

            frame = cv2.resize(
                frame,
                (
                    int(w * scale),
                    int(h * scale)
                ),
                interpolation=cv2.INTER_AREA
            )

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

        enhanced = clahe.apply(gray)

        return cv2.cvtColor(
            enhanced,
            cv2.COLOR_GRAY2BGR
        )