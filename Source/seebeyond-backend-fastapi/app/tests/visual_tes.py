from app.utils.drawing import draw_faces

output = draw_faces(
    image,
    faces
)

cv2.imwrite(
    "output.jpg",
    output
)