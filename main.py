import cv2
import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

class ImageSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Image Enhancement System")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f0f0f0")
        
        # State variables
        self.original_img = None
        self.current_img = None  
        self.processed_img = None
        self.img_ref_a = None
        self.img_ref_b = None
        
        self.setup_gui()

    def setup_gui(self):
        # Top Control Panel
        control_frame = Frame(self.root, bg="#d0d0d0", pady=10)
        control_frame.pack(side=TOP, fill=X)

        self.btn_style = {
            "font": ("Arial", 10, "bold"),
            "width": 15,
            "cursor": "hand2",
            "bg": "#7a7a7a",
            "fg": "#ffffff",
            "activebackground": "#5e5e5e",
            "activeforeground": "#ffffff",
            "relief": "flat"
        }

        Button(control_frame, text="Upload Image", command=self.upload_image, **self.btn_style).pack(side=LEFT, padx=10)
        Button(control_frame, text="Reset to Original", command=self.reset_image, **self.btn_style).pack(side=LEFT, padx=5)
        Button(control_frame, text="Save Result", command=self.save_image, **self.btn_style).pack(side=RIGHT, padx=10)

        # Main Layout
        main_content = Frame(self.root, bg="#f0f0f0")
        main_content.pack(fill=BOTH, expand=True)

        # Scrollable Sidebar
        sidebar_container = Frame(main_content, width=250)
        sidebar_container.pack(side=LEFT, fill=Y)
        canvas = Canvas(sidebar_container, width=250, bg="#e0e0e0")
        scrollbar = Scrollbar(sidebar_container, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = Frame(canvas, bg="#e0e0e0")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Sidebar Controls
        self.create_section_label(scrollable_frame, "Sampling & Quantization")
        self.sample_scale = Scale(scrollable_frame, from_=0.25, to=2.0, resolution=0.25, 
                                  orient=HORIZONTAL, label="Resolution Scale", bg="#e0e0e0")
        self.sample_scale.set(1.0)
        self.sample_scale.pack(fill=X, pady=2)
        self.bit_depth = Scale(scrollable_frame, from_=1, to=8, orient=HORIZONTAL, 
                               label="Bit Depth (Quantization)", bg="#e0e0e0")
        self.bit_depth.set(8)
        self.bit_depth.pack(fill=X, pady=2)
        Button(scrollable_frame, text="Apply Re-sampling", command=self.apply_sampling_quantization, **self.btn_style).pack(fill=X, pady=5)

        self.create_section_label(scrollable_frame, "Geometric Transformations")
        self.angle = Scale(scrollable_frame, from_=-180, to=180, orient=HORIZONTAL, 
                           label="Rotation Angle", bg="#e0e0e0")
        self.angle.pack(fill=X, pady=2)
        Button(scrollable_frame, text="Rotate Image", command=self.apply_rotation, **self.btn_style).pack(fill=X, pady=5)

        self.create_section_label(scrollable_frame, "Intensity Adjustments")
        Button(scrollable_frame, text="Negative Transformation", command=self.apply_negative, **self.btn_style).pack(fill=X, pady=2)
        self.gamma_val = Scale(scrollable_frame, from_=0.1, to=3.0, resolution=0.1, 
                               orient=HORIZONTAL, label="Gamma Correction", bg="#e0e0e0")
        self.gamma_val.set(1.0)
        self.gamma_val.pack(fill=X, pady=2)
        Button(scrollable_frame, text="Apply Gamma", command=self.apply_gamma, **self.btn_style).pack(fill=X, pady=5)

        self.create_section_label(scrollable_frame, "Contrast & Analysis")
        Button(scrollable_frame, text="Equalize Histogram", command=self.apply_histogram_eq, **self.btn_style).pack(fill=X, pady=2)
        Button(scrollable_frame, text="View Histogram", command=self.show_histogram, **self.btn_style).pack(fill=X, pady=2)

        # Display Area
        display_container = Frame(main_content, bg="#f0f0f0")
        display_container.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

        # Original Image Panel
        frame_a = LabelFrame(display_container, text=" Original Input ", bg="#f9f9f9")
        frame_a.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        self.panelA = Label(frame_a, bg="#f9f9f9")
        self.panelA.pack(fill=BOTH, expand=True)

        # Processed Image Panel
        frame_b = LabelFrame(display_container, text=" Enhanced Result ", bg="#f9f9f9")
        frame_b.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        self.panelB = Label(frame_b, bg="#f9f9f9")
        self.panelB.pack(fill=BOTH, expand=True)

    def create_section_label(self, parent, text):
        lbl = Label(parent, text=text, font=("Arial", 10, "bold"), bg="#e0e0e0", fg="#2F2F2F", pady=5)
        lbl.pack(anchor=W)
        ttk.Separator(parent, orient=HORIZONTAL).pack(fill=X, pady=2)

    # ------------------ CORE METHODS ------------------
    def upload_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            self.original_img = cv2.imread(path)
            self.current_img = self.original_img.copy()
            self.show_on_panel(self.original_img, self.panelA, True)
            self.show_on_panel(self.original_img, self.panelB, False)

    def reset_image(self):
        if self.original_img is not None:
            self.current_img = self.original_img.copy()
            self.processed_img = None
            self.show_on_panel(self.current_img, self.panelB, False)

    def show_on_panel(self, img, panel, is_primary=True):
        if img is None: return
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w = rgb_img.shape[:2]
        display_size = 600
        scaling = min(display_size/w, display_size/h)
        new_w, new_h = int(w * scaling), int(h * scaling)
        resized = cv2.resize(rgb_img, (new_w, new_h))
        pil_img = Image.fromarray(resized)
        tk_img = ImageTk.PhotoImage(pil_img)
        if is_primary:
            self.img_ref_a = tk_img
        else:
            self.img_ref_b = tk_img
        panel.config(image=tk_img)
        panel.image = tk_img

    def apply_sampling_quantization(self):
        if self.original_img is None: return
        scale = self.sample_scale.get()
        h, w = self.original_img.shape[:2]
        down = cv2.resize(self.original_img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_LINEAR)
        sampled = cv2.resize(down, (w, h), interpolation=cv2.INTER_NEAREST)
        bits = self.bit_depth.get()
        levels = 2**bits
        quantized = (np.floor_divide(sampled, 256//levels) * (256//levels)).astype('uint8')
        self.processed_img = quantized
        self.show_on_panel(self.processed_img, self.panelB, False)

    def apply_rotation(self):
        if self.original_img is None: return
        h, w = self.original_img.shape[:2]
        M = cv2.getRotationMatrix2D((w//2, h//2), self.angle.get(), 1.0)
        self.processed_img = cv2.warpAffine(self.original_img, M, (w, h))
        self.show_on_panel(self.processed_img, self.panelB, False)

    def apply_negative(self):
        if self.original_img is None: return
        self.processed_img = 255 - self.original_img
        self.show_on_panel(self.processed_img, self.panelB, False)

    def apply_gamma(self):
        if self.original_img is None: return
        gamma = self.gamma_val.get()
        invGamma = 1.0 / gamma
        table = np.array([((i/255.0)**invGamma)*255 for i in range(256)]).astype("uint8")
        self.processed_img = cv2.LUT(self.original_img, table)
        self.show_on_panel(self.processed_img, self.panelB, False)

    def apply_histogram_eq(self):
        if self.original_img is None: return
        if len(self.original_img.shape)==3:
            ycrcb = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2YCrCb)
            ycrcb[:,:,0] = cv2.equalizeHist(ycrcb[:,:,0])
            self.processed_img = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
        else:
            self.processed_img = cv2.equalizeHist(self.original_img)
        self.show_on_panel(self.processed_img, self.panelB, False)

    def show_histogram(self):
        if self.original_img is None: return
        img = self.processed_img if self.processed_img is not None else self.original_img
        plt.figure(figsize=(6,4))
        colors = ('b','g','r')
        for i, col in enumerate(colors):
            hist = cv2.calcHist([img],[i],None,[256],[0,256])
            plt.plot(hist, color=col)
        plt.title("Image Histogram")
        plt.xlabel("Intensity")
        plt.ylabel("Frequency")
        plt.show()

    def save_image(self):
        if self.processed_img is not None:
            path = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG","*.png"),("JPG","*.jpg")])
            if path:
                cv2.imwrite(path, self.processed_img)
                messagebox.showinfo("Success","Enhanced image saved successfully!")
        else:
            messagebox.showwarning("Warning","Nothing to save! Apply an effect first.")

if __name__ == "__main__":
    try:
        if 'root' in globals() and root:
            root.destroy()
    except:
        pass
    root = Tk()
    app = ImageSystem(root)
    root.mainloop()