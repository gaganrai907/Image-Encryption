# Image Encryption GUI

This project now includes a simple GUI app for image encryption and decryption using XOR.

## Features

- Encrypt tab:
  - Upload original image
  - Save encrypted image
  - Save generated key file (`.csv`)
- Decrypt tab:
  - Upload encrypted image
  - Upload key file (`.csv`)
  - Save decrypted image

## Run

From the `chatoic` folder:

```powershell
& "c:\BIT\6th Sem\Projects\Image Encryption\.venv\Scripts\python.exe" gui_app.py
```

## Notes

- Keep the generated key file safe. Decryption works only with the matching key.
- If image shape and key shape do not match, the app will show an error.
- Supported image types include `png`, `jpg`, `jpeg`, `bmp`, `tiff`, and `webp`.