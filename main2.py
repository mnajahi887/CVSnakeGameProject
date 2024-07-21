import math
import random
import cvzone
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from playsound3.playsound3 import playsound
import threading

# Function to play sounds in a separate thread
def play_sound(path):
    threading.Thread(target=playsound, args=(path,), daemon=True).start()

# Sound effects
food_eaten_sound = "food_eaten.mp3"
game_over_sound = "game_over.mp3"

# Set up the webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Initialize hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

class SnakeGameClass:
    def __init__(self, pathFood):
        self.points = []  # All points of the snake
        self.lengths = []  # Distance between each point
        self.currentLength = 0  # Total length of the snake
        self.allowedLength = 150  # Total allowed length
        self.previousHead = 0, 0  # Previous head point

        self.imgFood = cv2.imread(pathFood, cv2.IMREAD_UNCHANGED)
        self.hFood, self.wFood, _ = self.imgFood.shape
        self.foodPoint = 0, 0
        self.randomFoodLocation()
        self.score = 0

        self.gameOver = False

    def randomFoodLocation(self):
        self.foodPoint = random.randint(100, 1000), random.randint(100, 600)

    def update(self, imgMain, currentHead):
        if self.gameOver:
            cvzone.putTextRect(imgMain, "Game Over", [300, 400],
                               scale=7, thickness=5, offset=20, colorR=(0, 0, 255))  # Red
            cvzone.putTextRect(imgMain, f'Your Score: {self.score}', [50, 80],
                               scale=3, thickness=3, offset=10, colorR=(180, 5, 145))  #purple
        else:
            px, py = self.previousHead
            cx, cy = currentHead

            self.points.append([cx, cy])
            distance = math.hypot(cx - px, cy - py)
            self.lengths.append(distance)
            self.currentLength += distance
            self.previousHead = cx, cy

            # Length Reduction
            if self.currentLength > self.allowedLength:
                for i, length in enumerate(self.lengths):
                    self.currentLength -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength < self.allowedLength:
                        break

            # Check if Snake ate the Food
            rx, ry = self.foodPoint
            if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and \
                    ry - self.hFood // 2 < cy < ry + self.hFood // 2:
                self.randomFoodLocation()
                self.allowedLength += 50
                self.score += 1
                play_sound(food_eaten_sound)  # Play food eaten sound
                print(self.score)

            # Draw Snake with striped pattern
            if self.points:
                for i, point in enumerate(self.points):
                    if i != 0:
                        if i % 2 == 0:
                            color = (255, 0, 0)  # Blue
                        else:
                            color = (0, 255, 255)  # Yellow
                        cv2.line(imgMain, self.points[i - 1], self.points[i], color, 20)
                cv2.circle(imgMain, self.points[-1], 20, (0, 255, 255), cv2.FILLED)  # Yellow

            # Draw Food
            imgMain = cvzone.overlayPNG(imgMain, self.imgFood,
                                        (rx - self.wFood // 2, ry - self.hFood // 2))

            # Check for Collision
            pts = np.array(self.points[:-2], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(imgMain, [pts], False, (0, 255, 0), 3)  # Green
            minDist = cv2.pointPolygonTest(pts, (cx, cy), True)

            if -1 <= minDist <= 1:
                play_sound(game_over_sound)  # Play game over sound
                print("Hit")
                self.gameOver = True
                self.points = []  # All points of the snake
                self.lengths = []  # Distance between each point
                self.currentLength = 0  # Total length of the snake
                self.allowedLength = 150  # Total allowed length
                self.previousHead = 0, 0  # Previous head point

                self.randomFoodLocation()

        return imgMain

# Create a game instance with the path to the food image
game = SnakeGameClass("egg.png")

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)

    if hands:
        lmList = hands[0]['lmList']
        pointIndex = lmList[8][0:2]
        img = game.update(img, pointIndex)
    cv2.imshow("image", img)
    key = cv2.waitKey(1)
    if key == ord('r'):
        game.score = 0
        game.gameOver = False
