import cv2

# Open the webcam
camera = cv2.VideoCapture(0)

print("Press 's' to save an image, or 'q' to quit.")

while True:
    # Read the live feed frame-by-frame
    ret, frame = camera.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Display the live preview window
    cv2.imshow("Camera Preview - Press 's' to Save", frame)

    # Wait for a key press (1 millisecond delay)
    key = cv2.waitKey(1) & 0xFF

    # If 's' is pressed, save the frame
    if key == ord('s'):
        cv2.imwrite("webcam_photo.jpg", frame)
        print("Photo saved!")
        
    # If 'q' is pressed, break out of the loop and exit
    elif key == ord('q'):
        print("Closing camera...")
        break

# Clean up and close all windows
camera.release()
cv2.destroyAllWindows()

