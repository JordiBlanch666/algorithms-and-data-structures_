import cv2
import mediapipe as mp


class HandTracker:
    TIP_IDS = [4, 8, 12, 16, 20]  # thumb, index, middle, ring, pinky

    def __init__(self, max_hands=1, detection_confidence=0.7, tracking_confidence=0.7):
        self._mp_hands = mp.solutions.hands
        self._mp_draw = mp.solutions.drawing_utils
        self._hands = self._mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self.landmarks = []
        self.img_shape = (0, 0)

    def find_hands(self, frame: "np.ndarray", draw: bool = True) -> "np.ndarray":
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb)
        self.landmarks = []
        self.img_shape = frame.shape[:2]

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            if draw:
                self._mp_draw.draw_landmarks(frame, hand, self._mp_hands.HAND_CONNECTIONS)
            h, w = self.img_shape
            self.landmarks = [(int(lm.x * w), int(lm.y * h)) for lm in hand.landmark]

        return frame

    def get_tip(self, finger_id: int) -> tuple[int, int] | None:
        if not self.landmarks:
            return None
        return self.landmarks[finger_id]

    def fingers_up(self) -> list[int]:
        if not self.landmarks:
            return []

        fingers = []

        # Thumb: compare x axis (right hand)
        fingers.append(1 if self.landmarks[4][0] > self.landmarks[3][0] else 0)

        # Other four fingers: tip y < pip y means extended
        for tip in self.TIP_IDS[1:]:
            fingers.append(1 if self.landmarks[tip][1] < self.landmarks[tip - 2][1] else 0)

        return fingers
