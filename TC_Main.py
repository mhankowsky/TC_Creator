from generate_ltc import make_ltc

import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # Import ttk for the progress bar

import os


def generate_ltc(fps, start_timecode, output_file, offset, rate, bits):
    """
    Wrapper around generate_ltc.py functionality.
    Args:
        fps (int): Frames per second
        start_timecode (str): Start timecode in HH:MM:SS:FF format
        output_file (str): Output file path for LTC
        offset (int): Duration offset in minutes
        rate (int): Sample rate (either 44100 or 48000)
        bits (int): Bit depth (either 8, 16, or 24)
    """
    # Build the command-line arguments as per the script
    command = [
        "python", "generate_ltc.py",  # This assumes the script is in the same directory
        "--fps", str(fps),
        "--start", start_timecode,
        "--output", output_file,
        "--duration", str(offset),
        "--rate", str(rate),
        "--bits", str(bits)
    ]
    
    # Execute the script
    subprocess.run(command, check=True)


# Create the main window
def create_gui():
    root = tk.Tk()
    root.title("LTC File Generator")

    # Input fields for user data
    tk.Label(root, text="Start Timecode (HH:MM:SS:FF):").grid(row=0, column=0, padx=10, pady=10)
    start_timecode_entry = tk.Entry(root)
    start_timecode_entry.insert(0, "00:00:00:00")  # Default start timecode
    start_timecode_entry.grid(row=0, column=1)

    tk.Label(root, text="Frames Per Second (FPS):").grid(row=1, column=0, padx=10, pady=10)
    fps_entry = tk.Entry(root)
    fps_entry.insert(0, "29.97")
    fps_entry.grid(row=1, column=1)

    tk.Label(root, text="Output Directory:").grid(row=2, column=0, padx=10, pady=10)
    output_dir_entry = tk.Entry(root)
    output_dir_entry.grid(row=2, column=1)

    tk.Label(root, text="Offset (Minutes):").grid(row=3, column=0, padx=10, pady=10)
    offsets_entry = tk.Entry(root)
    offsets_entry.insert(0, "10")
    offsets_entry.grid(row=3, column=1)

    # Dropdown menu for Rate (44100 or 48000)
    tk.Label(root, text="Sample Rate (44100 or 48000):").grid(row=4, column=0, padx=10, pady=10)
    rate_var = tk.StringVar(root)
    rate_var.set("44100")  # Default value
    rate_menu = tk.OptionMenu(root, rate_var, "44100", "48000")
    rate_menu.grid(row=4, column=1)

    # Dropdown menu for Bits (8, 16, or 24)
    tk.Label(root, text="Bit Depth (8, 16, or 24):").grid(row=5, column=0, padx=10, pady=10)
    bits_var = tk.StringVar(root)
    bits_var.set("16")  # Default value
    bits_menu = tk.OptionMenu(root, bits_var, "8", "16", "24")
    bits_menu.grid(row=5, column=1)

    def browse_output_dir():
        output_dir = filedialog.askdirectory()
        output_dir_entry.insert(0, output_dir)

    browse_button = tk.Button(root, text="Browse", command=browse_output_dir)
    browse_button.grid(row=2, column=2, padx=10)

    # Add a progress bar widget
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress_bar.grid(row=7, column=0, columnspan=3, padx=10, pady=20)

    # Function to start generating LTC files
    def start_generation():
        start_timecode = start_timecode_entry.get()
        fps = fps_entry.get()
        output_dir = output_dir_entry.get()
        offset = offsets_entry.get()
        rate = rate_var.get()  # Get the selected rate (as a string)
        bits = bits_var.get()  # Get the selected bit depth (as a string)

        # Validate inputs
        if not start_timecode or not fps or not output_dir or not offset or not rate or not bits:
            messagebox.showerror("Input Error", "Please fill all fields")
            return

        try:
            offset = int(offset.strip())
            rate = int(rate)  # Convert rate to int
            bits = int(bits)  # Convert bits to int
        except ValueError:
            messagebox.showerror("Input Error", "Offset must be valid integer")
            return

        # Check if rate and bits are valid values
        if rate not in [44100, 48000]:
            messagebox.showerror("Input Error", "Rate must be either 44100 or 48000")
            return

        if bits not in [8, 16, 24]:
            messagebox.showerror("Input Error", "Bits must be either 8, 16, or 24")
            return
        

        ##### Set Up Progress Bar 
        total_iterations = 1440 // offset
        progress_bar["maximum"] = total_iterations  # Set progress bar max value
        progress_bar["value"] = 0

        # Generate the TC files
        hour = start_timecode.split(':')[0]
        minute = start_timecode.split(':')[1]

        total_min = int((hour*60) + minute)

        try:
            iteration = 0
            while total_min < 1440:
                hour = total_min // 60  # Corrected to divide for hours
                minute = total_min % 60  # Corrected to use modulo for minutes

                duration = offset * 60

                TC_Start = f'{hour}:{minute}:00:00'
                # Adjust start timecode by the offset (this logic would depend on how you handle timecode math)
                output_file = os.path.join(output_dir, f"ltc_fps{fps}_{hour:02}h_{minute:02}m.wav")
                make_ltc(fps, TC_Start, duration, rate, bits, output_file)

                total_min = total_min + offset
                iteration += 1

                # Update the progress bar after each iteration
                progress_bar["value"] = iteration
                root.update_idletasks()  # Force the GUI to update
                root.update()
                print(f"STATUS: Iteration:{iteration}, Hour:{hour}, Min:{minute}")

            messagebox.showinfo("Success", "LTC Files Generated Successfully!")
        except Exception as e:
            messagebox.showerror("Generation Error", str(e))

    # Button to trigger generation
    generate_button = tk.Button(root, text="Generate LTC Files (This takes a while)", command=start_generation)
    generate_button.grid(row=6, column=0, columnspan=2, pady=20)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
