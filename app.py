##import cv2
##import numpy as np
##import serial
##import time
##from tensorflow.keras.models import load_model
##
### -------- SERIAL CONNECTION --------
##ser = serial.Serial('COM4',9600)
##time.sleep(2)
##
### -------- LOAD MODEL --------
##model = load_model("model/unet_model.h5")
##
##IMG_SIZE = 256
##
##cap = cv2.VideoCapture(0)
##
##pump_on = False
##pump_start_time = 0
##last_sent = None
##
##last_text = "Waiting for leaf..."
##
##while True:
##
##    ret, frame = cap.read()
##    if not ret:
##        break
##
##    leaf_found = False
##
##    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
##
##    lower_green = np.array([25,40,40])
##    upper_green = np.array([90,255,255])
##
##    mask = cv2.inRange(hsv, lower_green, upper_green)
##
##    contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
##
##    for cnt in contours:
##
##        area = cv2.contourArea(cnt)
##
##        if area > 2000:
##
##            leaf_found = True
##
##            x,y,w,h = cv2.boundingRect(cnt)
##
##            leaf = frame[y:y+h, x:x+w]
##
##            leaf = cv2.resize(leaf,(IMG_SIZE,IMG_SIZE))
##            leaf = leaf / 255.0
##            leaf = np.expand_dims(leaf,axis=0)
##
##            prediction = model.predict(leaf, verbose=0)[0][0]
##
##            # -------- HEALTHY --------
##            if prediction < 0.5:
##
##                label = "Healthy"
##                percent = (1 - prediction) * 100
##                color = (0,255,0)
##
##                if percent > 90 and last_sent != "2":
##                    ser.write("2".encode())
##                    print("Healthy -> Sent 2")
##                    last_sent = "2"
##
##            # -------- DISEASED --------
##            else:
##
##                label = "Diseased"
##                percent = prediction * 100
##                color = (0,0,255)
##
##                if percent > 90 and not pump_on:
##
##                    ser.write("1".encode())
##                    print("Diseased -> Sent 1")
##
##                    pump_on = True
##                    pump_start_time = time.time()
##                    last_sent = "1"
##
##            last_text = f"{label} : {percent:.2f}%"
##            print(f"{label} : {percent:.2f}%")
##
##            cv2.rectangle(frame,(x,y),(x+w,y+h),color,2)
##
##            cv2.putText(frame,last_text,(x,y-10),
##                        cv2.FONT_HERSHEY_SIMPLEX,
##                        0.7,color,2)
##
##    # -------- IDLE DISPLAY --------
##    if not leaf_found:
##
##        cv2.putText(frame,last_text,(20,40),
##                    cv2.FONT_HERSHEY_SIMPLEX,
##                    0.8,(255,255,255),2)
##
##    # -------- PUMP AUTO OFF --------
##    if pump_on:
##        if time.time() - pump_start_time > 15:
##
##            ser.write("2".encode())
##            print("Pump OFF -> Sent 2")
##
##            pump_on = False
##            last_sent = "2"
##
##    cv2.imshow("Leaf Detection",frame)
##
##    if cv2.waitKey(1) & 0xFF == 27:
##        break
##
##cap.release()
##cv2.destroyAllWindows()
##ser.close()




import cv2
import numpy as np
import serial
import time
from tensorflow.keras.models import load_model

# -------- SERIAL CONNECTION --------
try:
    ser = serial.Serial('COM17', 9600, timeout=1)
    time.sleep(3)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    print("Serial Connected Successfully")
except:
    print("Serial Connection Failed")
    ser = None

# -------- LOAD MODEL --------
model = load_model("model/unet_model.h5")

IMG_SIZE = 256

cap = cv2.VideoCapture(0)

pump_on = False
pump_start_time = 0
last_sent = None

last_text = "Waiting for leaf..."

while True:

    ret, frame = cap.read()
    if not ret:
        break

    leaf_found = False

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_green = np.array([25,40,40])
    upper_green = np.array([90,255,255])

    mask = cv2.inRange(hsv, lower_green, upper_green)

    contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:

        area = cv2.contourArea(cnt)

        if area > 2000:

            leaf_found = True

            x,y,w,h = cv2.boundingRect(cnt)

            leaf = frame[y:y+h, x:x+w]

            leaf = cv2.resize(leaf,(IMG_SIZE,IMG_SIZE))
            leaf = leaf / 255.0
            leaf = np.expand_dims(leaf,axis=0)

            prediction = model.predict(leaf, verbose=0)[0][0]

            # -------- HEALTHY --------
            if prediction < 0.5:

                label = "Healthy"
                percent = (1 - prediction) * 100
                color = (0,255,0)

                if percent > 90 and last_sent != "2":

                    if ser:
                        ser.write(b'2')
                        ser.flush()

                    print("Healthy -> Sent 2")
                    last_sent = "2"

            # -------- DISEASED --------
            else:

                label = "Diseased"
                percent = prediction * 100
                color = (0,0,255)

                if percent > 90 and not pump_on:

                    if ser:
                        ser.write(b'1')
                        ser.flush()

                    print("Diseased -> Sent 1")

                    pump_on = True
                    pump_start_time = time.time()
                    last_sent = "1"

            last_text = f"{label} : {percent:.2f}%"
            print(f"{label} : {percent:.2f}%")

            cv2.rectangle(frame,(x,y),(x+w,y+h),color,2)

            cv2.putText(frame,last_text,(x,y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,color,2)

    # -------- IDLE DISPLAY --------
    if not leaf_found:

        cv2.putText(frame,last_text,(20,40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,(255,255,255),2)

    # -------- PUMP AUTO OFF --------
    if pump_on:

        if time.time() - pump_start_time > 15:

            if ser:
                ser.write(b'2')
                ser.flush()

            print("Pump OFF -> Sent 2")

            pump_on = False
            last_sent = "2"

    cv2.imshow("Leaf Detection",frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

if ser:
    ser.close()
