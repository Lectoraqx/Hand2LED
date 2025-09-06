import cv2, time, sys
import mediapipe as mp
import serial
from serial.tools import list_ports

BAUD = 9600
CAM_IDS = [0,1,2]         # ลองกล้องหลายตัว
CONF_DET = 0.7
CONF_TRK = 0.7

def open_camera(ids):
    for i in ids:
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            return cap
    print("ไม่พบกล้องที่ใช้งานได้"); sys.exit(1)

def open_arduino():
    #หาพอร์ตที่มีคำว่า Arduino/USB/ACM
    candidates = []
    for p in list_ports.comports():
        name = (p.description or "").lower()
        if any(x in name for x in ["arduino", "usb", "acm", "ch340", "wch"]):
            candidates.append(p.device)
    ports_to_try = candidates or [input("พิมพ์ COM พอร์ต (เช่น COM3): ").strip()]
    for dev in ports_to_try:
        try:
            ser = serial.Serial(dev, BAUD, timeout=1)
            time.sleep(2)
            print("เชื่อมต่อ:", dev)
            return ser
        except Exception as e:
            print("ต่อ", dev, "ไม่สำเร็จ:", e)
    print("ไม่พบ Arduino"); sys.exit(1)

def count_fingers(hand_landmarks):
    # index=8, middle=12, ring=16, pinky=20 | tip-2 = knuckle joint
    tips = [8,12,16,20]
    fc = 0
    # นิ้วโป้งเทียนแกน x
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        fc += 1
    # นิ้วอื่นเทียนแกน y
    for t in tips:
        if hand_landmarks.landmark[t].y < hand_landmarks.landmark[t-2].y:
            fc += 1
    # clamp 0..5
    return max(0, min(fc, 5))

def main():
    ser = open_arduino()
    cap = open_camera(CAM_IDS)

    mp_hands = mp.solutions.hands
    mp_draw  = mp.solutions.drawing_utils
    hands = mp_hands.Hands(min_detection_confidence=CONF_DET,
                           min_tracking_confidence=CONF_TRK)
    last_sent = -1
    same_count_frames = 0

    while True:
        ok, frame = cap.read()
        if not ok: break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            # ใช้มือแรกพอ
            hand = result.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            c = count_fingers(hand)

            # debouncing: ต้องได้ค่าเดิมซ้ำ ๆ สักเล็กน้อยก่อนค่อยส่ง
            if c == last_sent:
                same_count_frames += 1
            else:
                same_count_frames = 0

            if same_count_frames == 3 or last_sent == -1:
                try:
                    ser.write(f"{c}\n".encode())
                    last_sent = c
                except Exception as e:
                    cv2.putText(frame, f"Serial error: {e}", (10,30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

            cv2.putText(frame, f"Fingers: {c}", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        cv2.imshow("Hand Tracking -> Arduino", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    try:
        ser.close()
    except:
        pass

if __name__ == "__main__":
    main()
