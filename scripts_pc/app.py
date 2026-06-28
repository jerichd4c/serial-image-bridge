import customtkinter as ctk
from tkinter import filedialog
import threading
import os

# Import transmitter module
from transmitter import send_and_receive_image

# Tkinter config
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ImageTransmitterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Serial Image Transmitter")
        self.geometry("600x500")

        self.selected_image_path = None

        # Layout
        self.lbl_title = ctk.CTkLabel(self, text="Hardware Image Transmitter", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_title.pack(pady=20)

        # Select img button
        self.btn_select = ctk.CTkButton(self, text="1. Select Image", command=self.select_image)
        self.btn_select.pack(pady=10)

        # Img route label
        self.lbl_path = ctk.CTkLabel(self, text="No image selected", text_color="gray")
        self.lbl_path.pack(pady=5)

        # Start byte transmission button
        self.btn_send = ctk.CTkButton(self, text="2. Start Transmission", command=self.start_transmission_thread, fg_color="green", state="disabled")
        self.btn_send.pack(pady=10)

        # Event logger textbox
        self.logger = ctk.CTkTextbox(self, width=500, height=200, state="disabled")
        self.logger.pack(pady=20) 

    def select_image(self):
        # Select image to transmit
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            self.selected_image_path = file_path
            self.lbl_path.configure(text=os.path.basename(file_path), text_color="white")
            self.btn_send.configure(state="normal") # Enable send button
            self.log_message(f"Selected file: {self.selected_image_path}")

    def log_message(self, message):
        # Calls insert log function
        self.after(0, self._insert_log, message)

    def _insert_log(self, message):
        # Add message to logger textbox
        self.logger.configure(state="normal")
        self.logger.insert("end", message + "\n")
        self.logger.see("end") # Auto-scroll 
        self.logger.configure(state="disabled") 

    def start_transmission_thread(self):
        # Start separate thread to not interrumpt transmitter process
        self.btn_send.configure(state="disabled")
        self.btn_select.configure(state="disabled")
        self.log_message("\n--- Empezando nueva transmision ---")

        # Start the thread
        thread = threading.Thread(target=self.run_transmission)
        thread.start()

    # This function runs in the background
    def run_transmission(self):
        output_name = "received_image2.png"

        # Calls the transmitter.py module
        send_and_receive_image(
            IMG_PATH=self.selected_image_path,
            OUTPUT_PATH=output_name,
            COM_PORT='COM5', # Arduino port
            BAUD_RATE=9600,
            LOG_CALLBACK=self.log_message
        )

        # Enable buttons again after process ends
        self.after(0, lambda: self.btn_send.configure(state="normal"))
        self.after(0, lambda: self.btn_select.configure(state="normal"))

if __name__ == "__main__":
    app = ImageTransmitterApp()
    app.mainloop()