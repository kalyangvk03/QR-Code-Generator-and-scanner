import cv2
import glfw
import numpy as np
import pygame
import webbrowser
from OpenGL.GL import *
from OpenGL.GLU import *
from tkinter import Tk, filedialog, Button

website_opened = False  # Flag to track if a website has been opened

def detect_qr_code(image):
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(image)
    return data, bbox

def draw_bbox(bbox):
    if bbox is not None:
        bbox = bbox[0]
        glBegin(GL_LINES)
        for i in range(len(bbox)):
            glVertex2f(bbox[i][0], bbox[i][1])
            glVertex2f(bbox[(i+1) % len(bbox)][0], bbox[(i+1) % len(bbox)][1])
        glEnd()

def draw_text(text, x, y):
    pygame.init()
    font = pygame.font.SysFont('Helvetica', 18)
    text_surface = font.render(text, True, (0, 255, 0))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glRasterPos2f(x, y)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    pygame.quit()

def display(image, data, bbox):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Draw the image
    image_flipped = np.flipud(image)  # Flip the image vertically for correct rendering
    glDrawPixels(image_flipped.shape[1], image_flipped.shape[0], GL_RGB, GL_UNSIGNED_BYTE, image_flipped)

    # Draw the bounding box
    if bbox is not None:
        glColor3f(1.0, 0.0, 0.0)  # Red color for the bounding box
        draw_bbox(bbox)

    # Draw the decoded text
    if data:
        glColor3f(0.0, 1.0, 0.0)  # Green color for the text
        draw_text(data, 10, 10)

def open_website(url):
    global website_opened
    if not website_opened:
        print("Opening URL:", url)
        try:
            webbrowser.open(url, new=2)
            website_opened = True
        except Exception as e:
            print("Error opening URL:", e)

def open_image_file():
    Tk().withdraw()  # Hide the main tkinter window
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if file_path:
        image = cv2.imread(file_path)
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return None

def main():
    # Initialize GLFW
    if not glfw.init():
        return

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(800, 600, "QR Code Scanner", None, None)
    if not window:
        glfw.terminate()
        return

    # Make the window's context current
    glfw.make_context_current(window)

    # Initialize the camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        glfw.terminate()
        return

    # Set up OpenGL
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, 800, 0, 600)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    use_camera = True
    image_from_gallery = None

    # Function to handle gallery button click
    def gallery_button_click():
        nonlocal image_from_gallery, use_camera
        image_from_gallery = open_image_file()
        if image_from_gallery is not None:
            use_camera = False

    # Create a tkinter window to hold the gallery button
    gallery_window = Tk()
    gallery_window.withdraw()  # Hide the gallery window
    gallery_button = Button(gallery_window, text="Open Gallery", command=gallery_button_click)
    gallery_button.pack()

    # Function to keep the tkinter window open and handle button clicks
    def tkinter_mainloop():
        gallery_window.update_idletasks()
        gallery_window.update()
        gallery_window.after(1, tkinter_mainloop)

    # Start the tkinter mainloop to handle GUI events
    tkinter_mainloop()

    while not glfw.window_should_close(window):
        if use_camera:
            # Capture frame-by-frame from the webcam
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame from camera.")
                break

            # Process frame for QR code detection
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            data, bbox = detect_qr_code(frame)

            # Render using OpenGL
            glfw.make_context_current(window)
            display(frame, data, bbox)
            glfw.swap_buffers(window)
            glfw.poll_events()

            # Check if QR code containing a URL is detected
            if data and data.startswith('http'):
                open_website(data)

        else:
            # Display the selected image from the gallery
            data, bbox = detect_qr_code(image_from_gallery)
            if image_from_gallery is not None:
                display(image_from_gallery, data, bbox)
                glfw.swap_buffers(window)
                glfw.poll_events()
            use_camera = True  # Reset to use camera for the next iteration

    cap.release()
    glfw.terminate()

if __name__ == "__main__":
    main()
