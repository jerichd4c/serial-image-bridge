<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>

<!-- PROJECT LOGO -->
<div align="center">
  <a href="https://github.com/jerichd4c/serial-image-bridge">
    <img src="https://raw.githubusercontent.com/jerichd4c/ReflexJDBC/main/python_logo.svg" alt="Logo" width="80" height="80">
  </a>
</div>

<div align="center">

<h3 align="center">Serial Image Bridge</h3>

  <p align="center">
    A desktop app that sends an image to a microcontroller byte-by-byte over serial, using a handshake protocol, and reconstructs whatever comes back.
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#how-it-works">How It Works</a></li>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#known-limitations">Known Limitations</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

A CustomTkinter desktop app for **PC ↔ microcontroller image transmission over a serial port**. You pick an image, the app converts it to grayscale and downsamples it to 64×64, then streams it to an Arduino/ESP32 one byte at a time — reading back one byte for every byte it sends. Whatever comes back is reassembled into a PNG and shown side by side with the original, with a live log of the transmission.

It's built as a generic bridge: the PC side (this repo) only assumes the microcontroller answers a sync handshake and echoes a byte per byte received, so it can be paired with different firmware behaviors — echo the image back untouched, apply a filter on-device, etc.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### How It Works

1. **Handshake:** the app repeatedly sends a sync byte (`0xFF`) until the device echoes it back, confirming both sides are ready.
2. **Prep:** the selected image is converted to grayscale and resized to 64×64 pixels (4096 bytes total).
3. **Transfer:** each pixel byte is sent over serial and the app waits for one byte back before sending the next; a missing response is logged and recorded as a black pixel (`0`) so the image size stays consistent.
4. **Reconstruct:** the bytes read back are reassembled into a new 64×64 image and saved to `outputs/`.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![Python][Python-badge]][Python-url]
* [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — GUI
* [Pillow](https://python-pillow.org/) — image processing
* [pySerial](https://pyserial.readthedocs.io/) — serial communication

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

* Python 3
* An Arduino/ESP32 (or similar) connected over serial, running firmware that performs the handshake and echoes one byte per byte received — **this firmware is not included in this repository**, see [Known Limitations](#known-limitations).
* No `requirements.txt` is committed; install the dependencies manually:
  ```sh
  pip install customtkinter pillow pyserial
  ```

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/jerichd4c/serial-image-bridge.git
   ```
2. Install dependencies (see [Prerequisites](#prerequisites)).
3. Open `scripts_pc/app.py` and update `COM_PORT` (and `BAUD_RATE` if needed) inside `run_transmission()` to match your device — it's hardcoded to `'COM5'` at 9600 baud.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

```sh
cd scripts_pc
python app.py
```

Click **1. Select Image** to choose a PNG/JPG/BMP file, then **2. Start Transmission** to run the handshake and byte-by-byte transfer over serial. Progress and any timeouts are printed to the log panel at the bottom, and the reconstructed image appears on the right once the transfer finishes; each run is saved to `outputs/received_image_N.png`.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- KNOWN LIMITATIONS -->
## Known Limitations

* **No microcontroller firmware included:** this repo is PC-side only. You need your own Arduino/ESP32 sketch that answers the `0xFF` handshake and echoes back one byte per byte received for this to work end-to-end.
* **Hardcoded connection settings:** `COM_PORT` and `BAUD_RATE` are fixed in `app.py` rather than configurable from the UI.
* **"Grayscale" switch isn't wired up:** the UI has a Grayscale toggle, but the transmission always converts to grayscale regardless of its state.
* **Fixed image size:** every image is resized to 64×64 before sending; this isn't currently adjustable from the UI.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
[Python-badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
