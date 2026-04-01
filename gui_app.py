import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np
from PIL import Image


def read_image_array(image_path: str) -> np.ndarray:
    image = Image.open(image_path)
    return np.array(image, dtype=np.uint8)


def save_key_csv(key_array: np.ndarray, key_path: str) -> None:
    shape = key_array.shape
    with open(key_path, "w", newline="", encoding="utf-8") as key_file:
        writer = csv.writer(key_file)
        writer.writerow(["shape", *shape])

        if key_array.ndim == 2:
            flat_data = key_array.reshape(-1, 1)
        else:
            flat_data = key_array.reshape(-1, key_array.shape[-1])

        writer.writerows(flat_data.tolist())


def load_key_csv(key_path: str) -> np.ndarray:
    with open(key_path, "r", newline="", encoding="utf-8") as key_file:
        reader = csv.reader(key_file)
        rows = list(reader)

    if not rows:
        raise ValueError("Key file is empty.")

    header = rows[0]
    if len(header) < 2 or header[0].strip().lower() != "shape":
        raise ValueError("Invalid key file header.")

    try:
        shape = tuple(int(x) for x in header[1:])
    except ValueError as exc:
        raise ValueError("Invalid key shape in header.") from exc

    if len(shape) not in (2, 3):
        raise ValueError("Only 2D and 3D image shapes are supported.")

    if len(rows) == 1:
        raise ValueError("Key file does not contain pixel data.")

    try:
        data = np.array([[int(value) for value in row] for row in rows[1:]], dtype=np.uint8)
    except ValueError as exc:
        raise ValueError("Key file contains non-numeric values.") from exc

    if len(shape) == 2:
        expected_rows = shape[0] * shape[1]
        if data.shape != (expected_rows, 1):
            raise ValueError("Key data does not match grayscale image shape.")
        return data.reshape(shape)

    expected_rows = shape[0] * shape[1]
    channels = shape[2]
    if data.shape != (expected_rows, channels):
        raise ValueError("Key data does not match color image shape.")
    return data.reshape(shape)


def xor_crypt(image_array: np.ndarray, key_array: np.ndarray) -> np.ndarray:
    if image_array.shape != key_array.shape:
        raise ValueError("Image and key shape do not match.")
    return np.bitwise_xor(image_array, key_array)


class ImageCryptoGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Image Encryption and Decryption")
        self.root.geometry("680x420")
        self.root.minsize(640, 380)

        self.encrypt_input_path = tk.StringVar()
        self.encrypt_output_path = tk.StringVar(value="encrypted_image.png")
        self.encrypt_key_path = tk.StringVar(value="encryption_key.csv")

        self.decrypt_input_path = tk.StringVar()
        self.decrypt_key_path = tk.StringVar()
        self.decrypt_output_path = tk.StringVar(value="decrypted_image.png")

        self.build_ui()

    def build_ui(self) -> None:
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        encrypt_frame = ttk.Frame(notebook, padding=16)
        decrypt_frame = ttk.Frame(notebook, padding=16)
        notebook.add(encrypt_frame, text="Encrypt")
        notebook.add(decrypt_frame, text="Decrypt")

        self.build_encrypt_tab(encrypt_frame)
        self.build_decrypt_tab(decrypt_frame)

    def build_encrypt_tab(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Input Image").grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(parent, textvariable=self.encrypt_input_path, width=60).grid(row=0, column=1, padx=8, pady=(0, 8), sticky="we")
        ttk.Button(parent, text="Upload", command=self.choose_encrypt_input).grid(row=0, column=2, pady=(0, 8))

        ttk.Label(parent, text="Encrypted Image Output").grid(row=1, column=0, sticky="w", pady=8)
        ttk.Entry(parent, textvariable=self.encrypt_output_path, width=60).grid(row=1, column=1, padx=8, pady=8, sticky="we")
        ttk.Button(parent, text="Save As", command=self.choose_encrypt_output).grid(row=1, column=2, pady=8)

        ttk.Label(parent, text="Key File Output (.csv)").grid(row=2, column=0, sticky="w", pady=8)
        ttk.Entry(parent, textvariable=self.encrypt_key_path, width=60).grid(row=2, column=1, padx=8, pady=8, sticky="we")
        ttk.Button(parent, text="Save As", command=self.choose_encrypt_key_output).grid(row=2, column=2, pady=8)

        ttk.Button(parent, text="Encrypt Image", command=self.encrypt_image).grid(row=3, column=1, pady=18, sticky="e")

        parent.columnconfigure(1, weight=1)

    def build_decrypt_tab(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Encrypted Image").grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(parent, textvariable=self.decrypt_input_path, width=60).grid(row=0, column=1, padx=8, pady=(0, 8), sticky="we")
        ttk.Button(parent, text="Upload", command=self.choose_decrypt_input).grid(row=0, column=2, pady=(0, 8))

        ttk.Label(parent, text="Key File (.csv)").grid(row=1, column=0, sticky="w", pady=8)
        ttk.Entry(parent, textvariable=self.decrypt_key_path, width=60).grid(row=1, column=1, padx=8, pady=8, sticky="we")
        ttk.Button(parent, text="Upload", command=self.choose_decrypt_key).grid(row=1, column=2, pady=8)

        ttk.Label(parent, text="Decrypted Image Output").grid(row=2, column=0, sticky="w", pady=8)
        ttk.Entry(parent, textvariable=self.decrypt_output_path, width=60).grid(row=2, column=1, padx=8, pady=8, sticky="we")
        ttk.Button(parent, text="Save As", command=self.choose_decrypt_output).grid(row=2, column=2, pady=8)

        ttk.Button(parent, text="Decrypt Image", command=self.decrypt_image).grid(row=3, column=1, pady=18, sticky="e")

        parent.columnconfigure(1, weight=1)

    def choose_encrypt_input(self) -> None:
        path = filedialog.askopenfilename(
            title="Select input image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.webp"), ("All files", "*.*")],
        )
        if path:
            self.encrypt_input_path.set(path)
            base_dir = os.path.dirname(path)
            self.encrypt_output_path.set(os.path.join(base_dir, "encrypted_image.png"))
            self.encrypt_key_path.set(os.path.join(base_dir, "encryption_key.csv"))

    def choose_encrypt_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save encrypted image as",
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All files", "*.*")],
        )
        if path:
            self.encrypt_output_path.set(path)

    def choose_encrypt_key_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save key file as",
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.encrypt_key_path.set(path)

    def choose_decrypt_input(self) -> None:
        path = filedialog.askopenfilename(
            title="Select encrypted image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.webp"), ("All files", "*.*")],
        )
        if path:
            self.decrypt_input_path.set(path)
            base_dir = os.path.dirname(path)
            self.decrypt_output_path.set(os.path.join(base_dir, "decrypted_image.png"))

    def choose_decrypt_key(self) -> None:
        path = filedialog.askopenfilename(
            title="Select key file",
            filetypes=[("CSV file", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.decrypt_key_path.set(path)

    def choose_decrypt_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save decrypted image as",
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All files", "*.*")],
        )
        if path:
            self.decrypt_output_path.set(path)

    def encrypt_image(self) -> None:
        image_path = self.encrypt_input_path.get().strip()
        out_image_path = self.encrypt_output_path.get().strip()
        out_key_path = self.encrypt_key_path.get().strip()

        if not image_path or not os.path.isfile(image_path):
            messagebox.showerror("Error", "Please upload a valid input image.")
            return
        if not out_image_path:
            messagebox.showerror("Error", "Please select encrypted image output path.")
            return
        if not out_key_path:
            messagebox.showerror("Error", "Please select key file output path.")
            return

        try:
            image_array = read_image_array(image_path)
            key_array = np.random.randint(0, 256, size=image_array.shape, dtype=np.uint8)
            encrypted_array = xor_crypt(image_array, key_array)

            Image.fromarray(encrypted_array).save(out_image_path)
            save_key_csv(key_array, out_key_path)

            messagebox.showinfo(
                "Success",
                f"Encryption completed.\nEncrypted image: {out_image_path}\nKey file: {out_key_path}",
            )
        except Exception as exc:
            messagebox.showerror("Encryption Error", str(exc))

    def decrypt_image(self) -> None:
        encrypted_path = self.decrypt_input_path.get().strip()
        key_path = self.decrypt_key_path.get().strip()
        out_image_path = self.decrypt_output_path.get().strip()

        if not encrypted_path or not os.path.isfile(encrypted_path):
            messagebox.showerror("Error", "Please upload a valid encrypted image.")
            return
        if not key_path or not os.path.isfile(key_path):
            messagebox.showerror("Error", "Please upload a valid key file.")
            return
        if not out_image_path:
            messagebox.showerror("Error", "Please select decrypted image output path.")
            return

        try:
            encrypted_array = read_image_array(encrypted_path)
            key_array = load_key_csv(key_path)
            decrypted_array = xor_crypt(encrypted_array, key_array)

            Image.fromarray(decrypted_array).save(out_image_path)
            messagebox.showinfo("Success", f"Decryption completed.\nDecrypted image: {out_image_path}")
        except Exception as exc:
            messagebox.showerror("Decryption Error", str(exc))


def main() -> None:
    root = tk.Tk()
    app = ImageCryptoGUI(root)
    # Keep a reference so the app object is not garbage-collected.
    root.app = app
    root.mainloop()


if __name__ == "__main__":
    main()