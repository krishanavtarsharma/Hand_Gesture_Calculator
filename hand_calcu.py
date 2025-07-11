# hand_calculator.py

import streamlit as st
import cv2
import mediapipe as mp

st.set_page_config(page_title="✋ Hand Gesture Calculator", layout="centered")
st.title("🤖 Hand Gesture Based Calculator")

run = st.checkbox("📷 Start Camera")
FRAME_WINDOW = st.image([])

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

font = cv2.FONT_HERSHEY_SIMPLEX

# Variables
num1 = None
num2 = None
result = None
locked = False
operation = None

def count_fingers(hand_landmarks):
    finger_tips = [8, 12, 16, 20]
    count = 0
    for tip in finger_tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            count += 1

    # Thumb (optional)
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        count += 1
    return count

def get_operation(finger_count):
    if finger_count == 1:
        return "Add"
    elif finger_count == 2:
        return "Subtract"
    elif finger_count == 3:
        return "Multiply"
    elif finger_count == 4:
        return "Divide"
    else:
        return None

while run:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            fingers = count_fingers(hand_landmarks)

            # Reset if 5 fingers
            if fingers == 5:
                num1, num2, result, locked, operation = None, None, None, False, None
                cv2.putText(frame, "🔄 Reset Done", (50, 70), font, 1, (0, 0, 255), 2)

            # Phase 1: Get first number
            elif not locked and fingers > 0:
                num1 = fingers
                cv2.putText(frame, f"Num1: {num1}", (50, 120), font, 1, (0, 255, 0), 2)

            # Lock first number with fist (0 fingers)
            elif not locked and fingers == 0 and num1 is not None:
                locked = True
                cv2.putText(frame, f"Num1 Locked: {num1}", (50, 170), font, 1, (255, 255, 0), 2)

            # Phase 2: Get second number
            elif locked and num2 is None and fingers > 0:
                num2 = fingers
                cv2.putText(frame, f"Num2: {num2}", (50, 220), font, 1, (0, 255, 255), 2)

            # Phase 3: Get Operation
            elif locked and num2 is not None:
                operation = get_operation(fingers)
                if operation:
                    if operation == "Add":
                        result = num1 + num2
                    elif operation == "Subtract":
                        result = num1 - num2
                    elif operation == "Multiply":
                        result = num1 * num2
                    elif operation == "Divide":
                        result = round(num1 / num2, 2) if num2 != 0 else "∞"

                    cv2.putText(frame, f"{num1} {operation} {num2} = {result}", (50, 280), font, 1, (255, 0, 0), 2)

    FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

else:
    cap.release()
