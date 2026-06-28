import serial
import time
from PIL import Image

# Config
COM_PORT = 'COM5' # Ardiuno port
BAUD_RATE = 9600 # Must match arduino Serial.begin() in .ino 
IMG_PATH = 'test_image1.png' 
OUTPUT_PATH = 'received_image1.png'


def send_image():
    try:
        # 1. Open and prep the image
        print(f"Abriendo imagen: {IMG_PATH}")
        img = Image.open(IMG_PATH)

        # Convert to grayscale 
        img = img.convert('L')

        # Optional: resize for test 
        width, height = 64, 64
        img = img.resize((width, height))
        print(f"Imagen ajustada a {width}x{height} pixeles.")
    
        # 2. Extract data (bytes array)
        pixels = list(img.getdata())
        byte_data = bytearray(pixels)

        # 3. Init serial conn
        print(f"Conectando al puerto {COM_PORT}...")
        serial_connection = serial.Serial(COM_PORT, BAUD_RATE, timeout=0.5)
        time.sleep(2) # Pause to let arduino rest after opening the port    

        # 3.5 Handshake protocol
        print("Sincronizando con hardware...")
        sync_byte = b'\xFF' # Testbyte size

        while True:
            serial_connection.write(sync_byte)
            response = serial_connection.read(1)
            
            if response == sync_byte:
                print("Protocol handshake exitoso, el hardware esta operando correctamente.")
                break
        
        # Wait a moment if it doesnt respond
        time.sleep(0.1)
        serial_connection.reset_input_buffer()
        serial_connection.reset_output_buffer()

        # Clean buffer to delete noise/interference

        # 4. Transmit data
        total_bytes = len(byte_data)
        print(f"Iniciando transmision de {total_bytes} bytes...")

        received_pixels = []

        # Transmit and receive byte by byte 
        for i, byte_val in enumerate(byte_data):
            # Send ONE byte
            serial_connection.write(bytes([byte_val]))

            # Wait and read ONE byte back
            received_byte = serial_connection.read(1)

            if received_byte:
                received_pixels.append(ord(received_byte))
            else:
                # If no byte comes back within the timeout, save a black pixel (0)
                print(f"Atencion, timeout leyendo bytes {i}. puede que se pierdan datos.")
                received_pixels.append(0)

            # Small visual progress in the console every 500 bytes
            if (i+1) % 500 == 0 and i > 0:
                print(f"Enviado {i}/{total_bytes} bytes...")

        print("Transmision completada exitosamente.")
        serial_connection.close()

        # 5. Reconstruct and save the receive image
        print("Reconstruyendo la imagen recibida...")
        received_img = Image.new('L', (width, height))
        received_img.putdata(received_pixels)
        received_img.save(OUTPUT_PATH)
        print(f"Proceso exitoso, imagen guardada como '{OUTPUT_PATH}'.")

    except Exception as e:
        print(f"Ocurrio un error: {e}")

if __name__ == "__main__":
    send_image()