class SceneSummaryBuilder:

    @staticmethod
    def build(
        faces,
        objects,
        text
    ):

        messages = []

        # Faces

        if faces:

            names = []

            for face in faces:

                names.append(
                    face.name
                )

            messages.append(
                f"Detected {', '.join(names)}"
            )

        # Objects

        if objects:

            labels = []

            for obj in objects:

                labels.append(
                    obj.label
                )

            messages.append(
                f"Objects nearby: {', '.join(labels)}"
            )

        # Text

        if text:

            messages.append(
                f"Visible text: {text}"
            )

        return ". ".join(messages)