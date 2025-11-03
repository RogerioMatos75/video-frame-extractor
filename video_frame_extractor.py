import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import glob
try:
    import cv2
except ImportError:
    # This will be caught later in the __main__ block
    pass

class FrameExtractorApp:
    def __init__(self, master):
        self.master = master
        master.title("Video to Line Art Pipeline")
        master.resizable(False, False)

        self.video_path = ""
        self.ffmpeg_path = tk.StringVar(value="ffmpeg")
        self.convert_to_lines_var = tk.BooleanVar(value=True)

        # --- UI Elements ---
        main_frame = tk.Frame(master, padx=10, pady=10)
        main_frame.pack()

        # Video selection
        video_frame = tk.LabelFrame(main_frame, text="1. Select Video File")
        video_frame.pack(fill="x", padx=5, pady=5)

        self.entry_video_path = tk.Entry(video_frame, width=60)
        self.entry_video_path.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        self.button_browse_video = tk.Button(video_frame, text="Browse...", command=self.select_video)
        self.button_browse_video.pack(side="left", padx=5, pady=5)

        # FFmpeg path
        ffmpeg_frame = tk.LabelFrame(main_frame, text="2. FFmpeg Executable Path")
        ffmpeg_frame.pack(fill="x", padx=5, pady=5)

        self.entry_ffmpeg_path = tk.Entry(ffmpeg_frame, textvariable=self.ffmpeg_path, width=60)
        self.entry_ffmpeg_path.pack(fill="x", expand=True, padx=5, pady=5)
        
        # Options Frame
        options_frame = tk.LabelFrame(main_frame, text="3. Pipeline Options")
        options_frame.pack(fill="x", padx=5, pady=5)

        self.check_convert = tk.Checkbutton(
            options_frame,
            text="Convert to Line Art after extraction",
            variable=self.convert_to_lines_var
        )
        self.check_convert.pack(anchor="w", padx=5, pady=2)

        # Start Button
        self.button_extract = tk.Button(main_frame, text="Start Pipeline", command=self.start_pipeline_thread, height=2, bg="#dff0d8")
        self.button_extract.pack(fill="x", padx=5, pady=10)

        # Status bar
        self.status_label = tk.Label(master, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def select_video(self):
        self.video_path = filedialog.askopenfilename(
            title="Select a video file",
            filetypes=(("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*"))
        )
        if self.video_path:
            self.entry_video_path.delete(0, tk.END)
            self.entry_video_path.insert(0, self.video_path)
            self.status_label.config(text=f"Selected: {os.path.basename(self.video_path)}")

    def start_pipeline_thread(self):
        if not self.video_path:
            messagebox.showerror("Error", "Please select a video file first.")
            return

        self.button_extract.config(state="disabled")
        self.status_label.config(text="Starting pipeline...")

        thread = threading.Thread(target=self.run_pipeline, daemon=True)
        thread.start()

    def run_pipeline(self):
        # Step 1: Extract Frames
        extract_success = self._extract_frames()

        if not extract_success:
            self.button_extract.config(state="normal")
            if not self.status_label.cget("text").startswith("Error"):
                 self.status_label.config(text="Ready")
            return

        # Step 2: Optionally convert to lines
        if self.convert_to_lines_var.get():
            convert_success = self._convert_to_lines()
            if not convert_success:
                self.button_extract.config(state="normal")
                if not self.status_label.cget("text").startswith("Error"):
                    self.status_label.config(text="Ready")
                return

        # All steps finished
        final_message = "Frame extraction complete."
        if self.convert_to_lines_var.get():
            final_message = "Pipeline complete! Frames extracted and converted to line art."

        self.status_label.config(text="Done!")
        messagebox.showinfo("Success", final_message)
        self.button_extract.config(state="normal")
        self.status_label.config(text="Ready")

    def _extract_frames(self):
        video_path = self.video_path
        output_folder = "output"
        fps = 15
        ffmpeg_executable = self.ffmpeg_path.get()

        self.status_label.config(text=f"Step 1/2: Extracting frames from {os.path.basename(video_path)}...")
        self.master.update_idletasks()

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        command = [
            ffmpeg_executable, '-i', video_path, '-vf', f'fps={fps}',
            os.path.join(output_folder, 'frame_%05d.jpg')
        ]

        try:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
            subprocess.run(command, check=True, capture_output=True, text=True, startupinfo=si)
            return True
        except FileNotFoundError:
            self.status_label.config(text="Error: FFmpeg not found.")
            messagebox.showerror("Error", f"ffmpeg not found at '{ffmpeg_executable}'.")
            return False
        except subprocess.CalledProcessError as e:
            self.status_label.config(text="Error during frame extraction.")
            messagebox.showerror("Error", f"Error during FFmpeg execution:\n{e.stderr}")
            return False

    def _convert_to_lines(self, input_folder='output', output_folder='output_linhas'):
        self.status_label.config(text="Step 2/2: Converting frames to line art...")
        self.master.update_idletasks()

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        image_files = sorted(glob.glob(os.path.join(input_folder, '*.jpg')))
        if not image_files:
            self.status_label.config(text="Error: No frames found to convert.")
            messagebox.showerror("Error", f"No .jpg files found in the '{input_folder}' directory to convert.")
            return False

        total_files = len(image_files)
        for i, image_path in enumerate(image_files):
            frame = cv2.imread(image_path)
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
            edges = cv2.Canny(blurred_frame, 50, 150)

            # Invert colors: white lines on black bg -> black lines on white bg
            inverted_edges = cv2.bitwise_not(edges)

            base_filename = os.path.basename(image_path)
            output_path = os.path.join(output_folder, base_filename)
            cv2.imwrite(output_path, inverted_edges)
            self.status_label.config(text=f"Step 2/2: Converting... ({i+1}/{total_files})")
            self.master.update_idletasks()

        return True

if __name__ == '__main__':
    try:
        import cv2
    except ImportError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Missing Dependency",
            "OpenCV library not found.\nPlease activate the virtual environment and install dependencies:\npip install -r requirements.txt"
        )
    else:
        root = tk.Tk()
        app = FrameExtractorApp(root)
        root.mainloop()