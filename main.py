import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from pynput.keyboard import Controller
import time

# Initialize
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Width
cap.set(4, 720)   # Height
keyboard = Controller()

detector = HandDetector(detectionCon=0.8, maxHands=1)

# Keyboard layout
keys = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]
]

# Button class
class Button:
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text
        self.is_pressed = False

# Create buttons
button_list = []
for i, row in enumerate(keys):
    for j, key in enumerate(row):
        button_list.append(Button([100 * j + 50, 100 * i + 50], key))

# Main loop
final_text = ""
click_cooldown = 0

while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture image")
        break
    
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)
    
    # Draw semi-transparent keyboard
    overlay = img.copy()
    for button in button_list:
        x, y = button.pos
        w, h = button.size
        
        # Button appearance
        color = (255, 0, 255)  # Default purple
        if button.is_pressed:
            color = (0, 255, 0)  # Green when pressed
        
        cv2.rectangle(overlay, (x, y), (x + w, y + h), color, cv2.FILLED)
        cv2.putText(overlay, button.text, (x + 20, y + 60), 
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
    
    # Apply transparency
    alpha = 0.5
    img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
    
    # Text display box
    cv2.rectangle(img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)
    cv2.putText(img, final_text, (60, 425), 
                cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
    
    # Hand detection and interaction
    if hands:
        lm_list = hands[0]['lmList']
        
        for button in button_list:
            x, y = button.pos
            w, h = button.size
            
            # Check if finger is over button
            if x < lm_list[8][0] < x + w and y < lm_list[8][1] < y + h:
                cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), 
                            (175, 0, 175), 2)
                
                # Check for click (distance between index and middle finger)
                length, _, _ = detector.findDistance(8, 12, img, draw=False)
                
                if length < 40 and not button.is_pressed and click_cooldown == 0:
                    button.is_pressed = True
                    final_text += button.text
                    keyboard.press(button.text)
                    click_cooldown = 10  # Cooldown frames
                elif length >= 40:
                    button.is_pressed = False
    
    # Cooldown timer
    if click_cooldown > 0:
        click_cooldown -= 1
    
    # Display
    cv2.imshow("Virtual Keyboard", img)
    
    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()