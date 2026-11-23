import cv2
import math
import pyautogui
import mediapipe as mp

pyautogui.FAILSAFE = False

# ── Configuración ──────────────────────────────────────────────
FRAME_REDUCTION = 100
SMOOTHING = 7

screen_w, screen_h = pyautogui.size()

cap = cv2.VideoCapture(0)
cam_w, cam_h = 640, 480
cap.set(3, cam_w)
cap.set(4, cam_h)

mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils
hands    = mp_hands.Hands(max_num_hands=1,
                          min_detection_confidence=0.7,
                          min_tracking_confidence=0.7)

prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0
dragging       = False
clicking       = False
mode           = "Idle"


# ── Utilidades ─────────────────────────────────────────────────
def get_landmarks(img):
    rgb     = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    lm_list = []
    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(img, hand, mp_hands.HAND_CONNECTIONS)
        h, w, _ = img.shape
        for lm in hand.landmark:
            lm_list.append((int(lm.x * w), int(lm.y * h)))
    return lm_list


def fingers_up(lm):
    tips = [8, 12, 16, 20]
    up   = [1 if lm[4][0] > lm[3][0] else 0]
    up  += [1 if lm[t][1] < lm[t - 2][1] else 0 for t in tips]
    return up  # [pulgar, índice, medio, anular, meñique]


def distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


# ── Bucle principal ─────────────────────────────────────────────
while True:
    success, img = cap.read()
    if not success:
        break

    img  = cv2.flip(img, 1)
    lm   = get_landmarks(img)
    mode = "Idle"

    cv2.rectangle(img,
                  (FRAME_REDUCTION, FRAME_REDUCTION),
                  (cam_w - FRAME_REDUCTION, cam_h - FRAME_REDUCTION),
                  (0, 255, 0), 2)

    if lm:
        fingers = fingers_up(lm)
        ix, iy  = lm[8]
        mx, my  = lm[12]

        # ── Mover cursor: solo índice levantado ──────────────────
        if fingers[1] == 1 and fingers[2] == 0:
            mode = "Moving"
            if dragging:
                pyautogui.mouseUp()
                dragging = False

            x = int((ix - FRAME_REDUCTION) /
                    (cam_w - 2 * FRAME_REDUCTION) * screen_w)
            y = int((iy - FRAME_REDUCTION) /
                    (cam_h - 2 * FRAME_REDUCTION) * screen_h)

            curr_x = prev_x + (x - prev_x) / SMOOTHING
            curr_y = prev_y + (y - prev_y) / SMOOTHING

            pyautogui.moveTo(
                max(0, min(screen_w - 1, int(curr_x))),
                max(0, min(screen_h - 1, int(curr_y))),
                duration=0
            )
            prev_x, prev_y = curr_x, curr_y
            cv2.circle(img, (ix, iy), 12, (0, 255, 0), cv2.FILLED)

        # ── Click izquierdo: índice + medio juntos ───────────────
        elif fingers[1] == 1 and fingers[2] == 1:
            dist = distance(lm[8], lm[12])
            mode = "Clicking" if dist < 35 else "Ready to Click"
            cv2.line(img, lm[8], lm[12], (255, 255, 0), 2)

            if dist < 35 and not clicking:
                pyautogui.click()
                clicking = True
                cv2.circle(img, ((ix + mx) // 2, (iy + my) // 2),
                           12, (255, 255, 0), cv2.FILLED)
            elif dist >= 35:
                clicking = False

        # ── Click derecho: índice + anular ───────────────────────
        elif fingers[1] == 1 and fingers[3] == 1 and fingers[2] == 0:
            mode = "Right Click"
            if distance(lm[8], lm[16]) < 35:
                pyautogui.rightClick()

        # ── Drag & Drop: pulgar + índice pinzados ────────────────
        elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0:
            mode = "Dragging"
            if distance(lm[4], lm[8]) < 35:
                if not dragging:
                    pyautogui.mouseDown()
                    dragging = True
            else:
                if dragging:
                    pyautogui.mouseUp()
                    dragging = False

        else:
            if dragging:
                pyautogui.mouseUp()
                dragging = False

        # ── HUD ──────────────────────────────────────────────────
        cx, cy = pyautogui.position()
        cv2.putText(img, f"Cursor: ({cx}, {cy})",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(img, f"Mode: {mode}",
                    (cam_w - 220, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

    else:
        if dragging:
            pyautogui.mouseUp()
            dragging = False

    cv2.imshow("AI Virtual Mouse", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

if dragging:
    pyautogui.mouseUp()

cap.release()
cv2.destroyAllWindows()
