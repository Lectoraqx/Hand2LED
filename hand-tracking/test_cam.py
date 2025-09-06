import cv2

for cam_id in range(3):
    cap = cv2.VideoCapture(cam_id)
    if cap.isOpened():
        print(f"เจอกล้องที่ index {cam_id}")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow(f"Camera {cam_id}", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
        cap.release()

cv2.destroyAllWindows()

