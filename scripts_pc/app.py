import customtkinter as ctk
from tkinter import filedialog
import threading
import os
from PIL import Image

# Import transmitter module
from transmitter import send_and_receive_image

# Tkinter config
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ImageTransmitterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Serial Image Transmitter")
        self.geometry("850x600")

        self.selected_image_path = None

        # Received image counter
        self.transmission_count = 1

        # Create output dir
        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)

        # Initial grid config
        self.grid_columnconfigure(0, weight=1) # Left
        self.grid_columnconfigure(1, weight=1) # Center
        self.grid_columnconfigure(2, weight=1) # Right
        self.grid_rowconfigure(1, weight=1)    # Main row

        # Title
        self.lbl_title = ctk.CTkLabel(self, text="Hardware Image Transmitter", font=ctk.CTkFont(size=22, weight="bold"))
        self.lbl_title.grid(row=0, column=0, columnspan=3, pady=(20, 10))

        # Left column: initial image
        self.frame_left = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_left.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.lbl_initial_title = ctk.CTkLabel(self.frame_left, text="Image to convert")
        self.lbl_initial_title.pack(pady=5)

        # Initial image placeholder
        self.canvas_initial = ctk.CTkLabel(self.frame_left, text="INITIAL\nIMAGE", width=220, height=220, fg_color="gray25", corner_radius=10)
        self.canvas_initial.pack(pady=10)

        # Select image button
        self.btn_select = ctk.CTkButton(self.frame_left, text="1. Select Image", command=self.select_image)
        self.btn_select.pack(pady=10)

        # Central column: options
        self.frame_center = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_center.grid(row=1, column=1, padx=10, pady=10, sticky="n")

        self.lbl_options = ctk.CTkLabel(self.frame_center, text="Options", font=ctk.CTkFont(size=18, underline=True))
        self.lbl_options.pack(pady=(40, 10))

        self.switch_grayscale = ctk.CTkSwitch(self.frame_center, text="Grayscale")
        self.switch_grayscale.select() # Set by default
        self.switch_grayscale.pack(pady=10)

        # Right column: received image
        self.frame_right = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_right.grid(row=1, column=2, padx=20, pady=10, sticky="nsew")

        self.lbl_received_title = ctk.CTkLabel(self.frame_right, text="Received image")
        self.lbl_received_title.pack(pady=5)

        # Received image placeholder
        self.canvas_received = ctk.CTkLabel(self.frame_right, text="RECEIVED\nIMAGE", width=220, height=220, fg_color="gray25", corner_radius=10)
        self.canvas_received.pack(pady=10)

        self.btn_send = ctk.CTkButton(self.frame_right, text="2. Start Transmission", command=self.start_transmission_thread, fg_color="green", state="disabled")
        self.btn_send.pack(pady=10)

        # Lower row: logger
        self.frame_bottom = ctk.CTkFrame(self)
        self.frame_bottom.grid(row=2, column=0, columnspan=3, padx=20, pady=20, sticky="nsew")
        
        self.logger = ctk.CTkTextbox(self.frame_bottom, height=120, state="disabled")
        self.logger.pack(padx=10, pady=10, fill="both", expand=True)

    # APP LOGIC

    def select_image(self):
        # Select image to transmit
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            self.selected_image_path = file_path
            file_name = os.path.basename(file_path)
            self.lbl_initial_title.configure(text=file_name, text_color="white")

            # Initial image preview
            try: 
                pil_img = Image.open(file_path)
                ctk_img = ctk.CTkImage(dark_image=pil_img, size=(220, 220))
                self.canvas_initial.configure(image=ctk_img, text="")
            except Exception as e:
                self.log_message(f"Error cargando miniatura: {e}")

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
        # generate dinamic output name: 1, 2, 3...
        output_name = f"received_image_{self.transmission_count}.png"
        # Abs route for outputs
        output_path = os.path.join(self.output_dir, output_name)

        # Calls the transmitter.py module
        send_and_receive_image(
            IMG_PATH=self.selected_image_path,
            OUTPUT_PATH=output_name,
            COM_PORT='COM5', # Arduino port
            BAUD_RATE=9600,
            LOG_CALLBACK=self.log_message
        )

        # Update received title and update counter
        self.after(0, lambda: self.lbl_received_title.configure(text=output_name, text_color="white"))
        self.after(0, lambda: self.display_received_image(output_path))
        self.transmission_count += 1

        # Enable buttons again after process ends
        self.after(0, lambda: self.btn_send.configure(state="normal"))
        self.after(0, lambda: self.btn_select.configure(state="normal"))
    
    def display_received_image(self, path):
        # Load processed image after transmission ends
        try: 
            if os.path.exists(path):
                pil_img = Image.open(path)
                ctk_img = ctk.CTkImage(dark_image=pil_img, size=(220, 220))
                self.canvas_received.configure(image=ctk_img, text="")
        except Exception as e:
            self.log_message(f"Error al mostrar imagen recibida: {e}")

if __name__ == "__main__":
    app = ImageTransmitterApp()
    app.mainloop()