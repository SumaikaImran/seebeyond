class OCRTextBuilder:

    @staticmethod
    def build(items):

        valid = []

        for item in items:

            text = item[1][0]
            confidence = item[1][1]

            if confidence < 0.5:
                continue

            points = item[0]

            top_y = min(
                p[1]
                for p in points
            )

            left_x = min(
                p[0]
                for p in points
            )

            valid.append(
                (
                    top_y,
                    left_x,
                    text
                )
            )

        valid.sort(
            key=lambda x:
            (
                round(x[0] / 25),
                x[1]
            )
        )

        return " ".join(
            item[2]
            for item in valid
        )