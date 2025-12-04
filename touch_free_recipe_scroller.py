import cv2
import time
import pyautogui
import mediapipe as mp
import numpy as np

TOP_ZONE_RATIO = 0.18
BOTTOM_ZONE_RATIO = 0.82
DWELL_MS = 450
COOLDOWN_MS = 350
SCROLL_AMOUNT = 60
WINDOW_NAME = "Touch-Free Recipe Scroller"

PINCH_DIST_RATIO = 0.08
PINCH_DWELL_MS = 300
PINCH_COOLDOWN_MS = 1000
FIVE_PINCH_DIST_RATIO = 0.09
FIVE_PINCH_INDEX_RATIO = 0.06
FIVE_PINCH_MIN_NEAR_COUNT = 3

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True

mp_hands = mp.solutions.hands

def main():
    cap = cv2.VideoCapture(0)
    last_pulse_t = 0.0
    zone = None
    zone_entry_t = 0.0
    last_shot_t = 0.0
    pinch_active = False
    pinch_entry_t = 0.0

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=0,
    ) as hands:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            top_y = int(h * TOP_ZONE_RATIO)
            bottom_y = int(h * BOTTOM_ZONE_RATIO)

            cv2.line(frame, (0, top_y), (w, top_y), (0, 255, 0), 2)
            cv2.line(frame, (0, bottom_y), (w, bottom_y), (0, 0, 255), 2)
            cv2.putText(frame, "UP zone", (10, max(20, top_y - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, "DOWN zone", (10, min(h - 10, bottom_y + 25)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False
            results = hands.process(rgb)

            tip_y = None
            tip_x = None
            thumb_x = None
            thumb_y = None
            mid_x = None
            mid_y = None
            ring_x = None
            ring_y = None
            pink_x = None
            pink_y = None
            if results.multi_hand_landmarks:
                hand = results.multi_hand_landmarks[0]
                ix = int(hand.landmark[8].x * w)
                iy = int(hand.landmark[8].y * h)
                tip_x, tip_y = ix, iy
                cv2.circle(frame, (ix, iy), 6, (255, 255, 0), -1)
                tx = int(hand.landmark[4].x * w)
                ty = int(hand.landmark[4].y * h)
                thumb_x, thumb_y = tx, ty
                color = (0, 255, 255)
                cv2.line(frame, (ix, iy), (tx, ty), color, 2)
                mx = int(hand.landmark[12].x * w)
                my = int(hand.landmark[12].y * h)
                mid_x, mid_y = mx, my
                rx = int(hand.landmark[16].x * w)
                ry = int(hand.landmark[16].y * h)
                ring_x, ring_y = rx, ry
                px = int(hand.landmark[20].x * w)
                py = int(hand.landmark[20].y * h)
                pink_x, pink_y = px, py
                cv2.line(frame, (tx, ty), (mx, my), (255, 200, 0), 2)
                cv2.line(frame, (tx, ty), (rx, ry), (255, 150, 0), 2)
                cv2.line(frame, (tx, ty), (px, py), (255, 100, 0), 2)

            now = time.time()
            new_zone = None
            if tip_y is not None:
                if tip_y <= top_y:
                    new_zone = "top"
                elif tip_y >= bottom_y:
                    new_zone = "bottom"

            if new_zone != zone:
                zone = new_zone
                zone_entry_t = now

            status = "IDLE"
            if zone in ("top", "bottom"):
                if (now - zone_entry_t) * 1000 >= DWELL_MS and (now - last_pulse_t) * 1000 >= COOLDOWN_MS:
                    amount = SCROLL_AMOUNT if zone == "top" else -SCROLL_AMOUNT
                    try:
                        pyautogui.scroll(amount)
                        last_pulse_t = now
                        status = "SCROLL UP" if zone == "top" else "SCROLL DOWN"
                    except Exception:
                        status = "SCROLL ERROR"

            pinch_now = False
            di = dm = dr = dp = None
            near_count = 0
            if None not in (thumb_x, thumb_y, tip_x, tip_y, mid_x, mid_y, ring_x, ring_y, pink_x, pink_y):
                di = ((tip_x - thumb_x) ** 2 + (tip_y - thumb_y) ** 2) ** 0.5 / float(min(w, h))
                dm = ((mid_x - thumb_x) ** 2 + (mid_y - thumb_y) ** 2) ** 0.5 / float(min(w, h))
                dr = ((ring_x - thumb_x) ** 2 + (ring_y - thumb_y) ** 2) ** 0.5 / float(min(w, h))
                dp = ((pink_x - thumb_x) ** 2 + (pink_y - thumb_y) ** 2) ** 0.5 / float(min(w, h))
                near_count = int(dm is not None and dm <= FIVE_PINCH_DIST_RATIO) + int(dr is not None and dr <= FIVE_PINCH_DIST_RATIO) + int(dp is not None and dp <= FIVE_PINCH_DIST_RATIO)
                index_ok = di is not None and di <= FIVE_PINCH_INDEX_RATIO
                if index_ok and near_count >= FIVE_PINCH_MIN_NEAR_COUNT:
                    pinch_now = True

            if pinch_now != pinch_active:
                pinch_active = pinch_now
                pinch_entry_t = now

            if pinch_active:
                if (now - pinch_entry_t) * 1000 >= PINCH_DWELL_MS and (now - last_shot_t) * 1000 >= PINCH_COOLDOWN_MS:
                    try:
                        img = pyautogui.screenshot()
                        shot = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                        cv2.imshow("Screenshot Preview", shot)
                        last_shot_t = now
                        status = "SHOT"
                    except Exception:
                        status = "SHOT ERROR"

            cv2.putText(frame, status, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            if di is not None:
                cv2.putText(frame, f"near={near_count} di={di:.3f} dm={dm:.3f} dr={dr:.3f} dp={dp:.3f}", (10, 55),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 2)

            cv2.imshow(WINDOW_NAME, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
