import qrcode
from tkinter import Tk, Label, Entry, Button, filedialog, Canvas, messagebox, colorchooser, StringVar
from PIL import Image, ImageTk
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np

def generate_qr_code(data, file_name, fill_color, back_color):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,  # Fixed box_size
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    img = img.convert('RGB')  # Convert image to RGB mode for JPEG saving
    img.save(file_name, format='JPEG')  # Save as JPEG format
    print(f"QR Code generated and saved as {file_name}")
    return img

def on_generate():
    global qr_image, qr_tk_image
    data = entry_data.get()
    if data:
        try:
            file_name = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")])
            if file_name:
                fill_color = color_chooser_fill.get()
                back_color = color_chooser_back.get()
                
                qr_image = generate_qr_code(data, file_name, fill_color, back_color)
                
                label_result.config(text=f"QR Code saved as {file_name}")
                qr_tk_image = ImageTk.PhotoImage(qr_image)
                canvas_qr.create_image(200, 200, image=qr_tk_image)
                display_qr_code()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR Code: {e}")
    else:
        messagebox.showwarning("Input Error", "Please enter data to generate QR Code.")

def display_qr_code():
    global qr_image_texture_id
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    if qr_image:
        width, height = qr_image.size
        img_data = np.array(qr_image.convert('RGBA'), dtype=np.uint8)  # Ensure image data is in RGBA format
        qr_image_texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, qr_image_texture_id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1)
        glVertex2f(-1, -1)
        glTexCoord2f(0, 0)
        glVertex2f(-1, 1)
        glTexCoord2f(1, 0)
        glVertex2f(1, 1)
        glTexCoord2f(1, 1)
        glVertex2f(1, -1)
        glEnd()

    glFlush()
    canvas_qr.after(30, display_qr_code)  # Update every 30ms

def choose_color_fill():
    color_code = colorchooser.askcolor(title="Choose QR Code Color")
    return color_code[1] if color_code else "#000000"

def choose_color_back():
    color_code = colorchooser.askcolor(title="Choose Background Color")
    return color_code[1] if color_code else "#FFFFFF"

def open_color_chooser_fill():
    global color_chooser_fill
    color = choose_color_fill()
    if color:
        color_chooser_fill.set(color)

def open_color_chooser_back():
    global color_chooser_back
    color = choose_color_back()
    if color:
        color_chooser_back.set(color)

def set_defaults():
    color_chooser_fill.set("#000000")
    color_chooser_back.set("#FFFFFF")

qr_image = None
qr_image_texture_id = None

# Set up the GUI
root = Tk()
root.title("QR Code Generator")
root.geometry("600x700")  # Adjusted window size

# Set window background color
root.configure(bg='#151B54')

# Create and style widgets
header = Label(root, text="QR Code Generator", font=("verdana", 18, "bold"), bg='#f4f4f9', pady=20)
header.pack()

label_data = Label(root, text="Enter link or text:", font=("verdana", 14), bg='#f4f4f9')
label_data.pack(pady=(5, 5))

entry_data = Entry(root, width=50, font=("Arial", 12))
entry_data.pack(pady=5)

color_chooser_fill = StringVar(value="#000000")
color_chooser_back = StringVar(value="#FFFFFF")

button_color_fill = Button(root, text="Choose QR Code Color", command=open_color_chooser_fill, font=("verdana", 12), bg="#007bff", fg="white", relief="flat")
button_color_fill.pack(pady=5)

button_color_back = Button(root, text="Choose Background Color", command=open_color_chooser_back, font=("verdana", 12), bg="#007bff", fg="white", relief="flat")
button_color_back.pack(pady=5)

button_generate = Button(root, text="Generate QR Code", command=on_generate, font=("verdana", 12), bg="#eb115b", fg="white", relief="flat")
button_generate.pack(pady=20)

label_result = Label(root, text="", font=("Helvetica", 12), bg='#f4f4f9')
label_result.pack()

canvas_qr = Canvas(root, width=400, height=400, bg="white", highlightthickness=0)
canvas_qr.pack(pady=10)

set_defaults()

root.mainloop()
