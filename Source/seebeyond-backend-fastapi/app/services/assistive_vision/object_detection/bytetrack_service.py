from ultralytics import YOLO


class ObjectTracker:

    def __init__(
        self,
        model_path: str
    ):

        self.model = YOLO(
            model_path
        )

    def track(
        self,
        frame
    ):

        return self.model.track(
            source=frame,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False
        )