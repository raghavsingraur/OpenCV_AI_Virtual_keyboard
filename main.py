import cv2
from cvzone.HandTrackingModule import HandDetector
import pyautogui
from time import sleep
import pygame
import pygetwindow as gw
from pynput.keyboard import Controller, Key

# Initialize pygame and sound
pygame.init()
click_sound = pygame.mixer.Sound('click_sound.wav')

# Initialize video capture
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Set video width
cap.set(4, 720)  # Set video height

# Initialize hand detector
detector = HandDetector(detectionCon=0.8, maxHands=2)

# Define the keys layout
keys = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"],
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "Enter"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "Shift"],
    ["Space"]
]

# Initialize finalText as an empty string
finalText = ""

keyboard = Controller()

# Map button text to pynput key constants
key_map = {
    "Backspace": Key.backspace,
    "Enter": Key.enter,
    "Space": Key.space,
    "Shift": Key.shift,
    # Add mappings for other keys if necessary
}

# Function to draw all buttons on the screen
def drawALL(img, buttonList, highlighted_button=None):
    overlay = img.copy()  # Create a copy of the image to draw on

    for button in buttonList:
        x, y = button.pos
        w, h = button.size

        # Highlight button if it's the currently pressed button
        color = (175, 0, 255) if button == highlighted_button else (0, 0, 0)
        cv2.rectangle(overlay, button.pos, (x + w, y + h), color, cv2.FILLED)  # Color rectangle

        # Get the size of the text
        text_size = cv2.getTextSize(button.text, cv2.FONT_HERSHEY_PLAIN, button.font_scale, 2)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2

        # Put the text in the center
        cv2.putText(overlay, button.text, (text_x, text_y), cv2.FONT_HERSHEY_PLAIN, button.font_scale, (255, 255, 255),
                    2)  # White text

    # Blend the overlay with the original image to make the keys semi-transparent
    alpha = 0.5  # Transparency factor
    img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    return img

# Class to represent each button
class Button():
    def __init__(self, pos, text, size=[70, 70], font_scale=2.5):
        self.pos = pos
        self.text = text
        self.size = size
        self.font_scale = font_scale

buttonList = []

# Define button positions and sizes
for j, key in enumerate(keys[0]):
    if key == "Backspace":
        buttonList.append(Button([75 * j + 50, 50], key, [120, 70], font_scale=1.5))
    else:
        buttonList.append(Button([75 * j + 50, 50], key))

for j, key in enumerate(keys[1]):
    buttonList.append(Button([75 * j + 65, 140], key))

for j, key in enumerate(keys[2]):
    if key == "Enter":
        buttonList.append(Button([75 * j + 80, 230], key, [120, 70]))
    else:
        buttonList.append(Button([75 * j + 80, 230], key))

for j, key in enumerate(keys[3]):
    if key == "Shift":
        buttonList.append(Button([75 * j + 95, 320], key, [130, 70]))
    else:
        buttonList.append(Button([75 * j + 95, 320], key))

buttonList.append(Button([300, 410], "Space", [500, 70]))  # Adjusted size for Space

# Function to activate the window with a specific title
def activate_window(title):
    windows = gw.getWindowsWithTitle(title)
    if windows:
        window = windows[0]
        window.activate()
        sleep(1)  # Delay to ensure the window is activated

# Activate the target window (change the title as needed)
activate_window('Untitled - Notepad')  # Replace with the title of your notebook or text editor

# Variable to track the previously pressed button
previous_button = None

# Main loop
while True:
    success, img = cap.read()
    if not success:
        break

    hands, img = detector.findHands(img)  # Detect hands and landmarks

    lmList = []
    if hands:
        lmList = hands[0]['lmList']  # List of 21 landmark points

    img = drawALL(img, buttonList, highlighted_button=previous_button)

    if lmList:
        for button in buttonList:
            x, y = button.pos
            w, h = button.size

            # Check if the index finger (landmark 8) and middle finger (landmark 12) are over the button
            if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                distance, _, _ = detector.findDistance(lmList[8][:2], lmList[12][:2], img)

                if distance < 30:  # Adjust this value based on testing
                    key_to_press = key_map.get(button.text, button.text)  # Get the corresponding pynput key

                    if isinstance(key_to_press, Key):
                        keyboard.press(key_to_press)
                        sleep(0.1)  # Short delay to avoid double typing
                        keyboard.release(key_to_press)
                    else:
                        keyboard.press(key_to_press)
                        sleep(0.1)  # Short delay to avoid double typing
                        keyboard.release(key_to_press)

                    cv2.rectangle(img, button.pos, (x + w, y + h), (175, 0, 255), cv2.FILLED)  # Highlight key in purple

                    # Calculate text position again for the highlighted button
                    text_size = cv2.getTextSize(button.text, cv2.FONT_HERSHEY_PLAIN, button.font_scale, 2)[0]
                    text_x = x + (w - text_size[0]) // 2
                    text_y = y + (h + text_size[1]) // 2

                    cv2.putText(img, button.text, (text_x, text_y), cv2.FONT_HERSHEY_PLAIN, button.font_scale,
                                (255, 255, 255), 2)  # White text

                    # Play sound effect if a button is pressed
                    if previous_button != button:
                        click_sound.play()
                        previous_button = button

                    # Only update finalText and simulate input if both fingers are together
                    if distance < 40:  # Both fingers are close
                        # Update finalText based on button pressed
                        if button.text == "Backspace":
                            finalText = finalText[:-1]
                        elif button.text == "Enter":
                            finalText += "\n"
                        elif button.text == "Space":
                            finalText += " "
                        else:
                            finalText += button.text

                        # Simulate keyboard input
                        pyautogui.write(button.text)
                        sleep(0.05)  # Reduced delay for faster typing response

    # Adjust the position and size of the text box
    text_box_y1 = 550
    text_box_y2 = 650
    text_box_height = text_box_y2 - text_box_y1

    # Draw the text box
    cv2.rectangle(img, (50, text_box_y1), (700, text_box_y2), (175, 0, 175), cv2.FILLED)

    # Adjust text size to fit within the text box
    text_size = cv2.getTextSize(finalText, cv2.FONT_HERSHEY_PLAIN, 3, 5)[0]
    if text_size[0] > 650:  # If text width exceeds the box width, scale down
        scale_factor = 650 / text_size[0]
        font_scale = 3 * scale_factor
    else:
        font_scale = 3

    # Display the text on the screen
    cv2.putText(img, finalText, (60, text_box_y2 - 20),
                cv2.FONT_HERSHEY_PLAIN, font_scale, (255, 255, 255), 5)

    # Display the image
    cv2.imshow('Video', img)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
