
from tkinter import Tk, Label, Button, filedialog, messagebox, Scale, HORIZONTAL, Frame, Canvas, Scrollbar, VERTICAL, RIGHT, LEFT, Y, BOTH
from PIL import Image, ImageTk
import os

class ThumbnailApp:
    def __init__(self, master):
        self.master = master
        self._setup_window()
        self._init_vars()
        self._build_interface()

    def _setup_window(self):
        self.master.title("🎨 Créateur de Miniature YouTube")
        self.master.geometry("1024x800")
        self.master.configure(bg="#f9f9f9")
        self.master.resizable(True, True)

        self.canvas = Canvas(self.master, bg="#f9f9f9", highlightthickness=0)
        self.scrollbar = Scrollbar(self.master, orient=VERTICAL, command=self.canvas.yview)
        self.frame = Frame(self.canvas, bg="#f9f9f9")
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _init_vars(self):
        self.bg_path = self.center_path = self.logo_path = self.banner_path = self.output_path = None
        self.preview_image = None
        self.controls = {}

    def _build_interface(self):
        Label(self.frame, text="Générateur de Miniature YouTube", font=("Segoe UI", 22, "bold italic"),
              bg="#f9f9f9", fg="#222").pack(pady=20)

        container = Frame(self.frame, bg="#f9f9f9")
        container.pack(padx=30, pady=5)

        fields = [
            ("Image de fond", self.select_bg),
            ("Image centrale", self.select_center),
            ("Logo", self.select_logo),
            ("Bannière de titre", self.select_banner)
        ]
        for label, command in fields:
            self._create_input_row(container, label, command)

        sliders = [
            ("Taille de la bannière (%)", 10, 100, 80, "banner_size_scale"),
            ("Position horizontale du logo", 0, 100, 100, "logo_pos_scale"),
            ("Position verticale du logo", -100, 300, 0, "logo_y_scale"),
            ("Position verticale de la bannière", -100, 300, 0, "banner_y_scale"),
            ("Taille du logo (%)", 10, 200, 100, "logo_size_scale"),
            ("Rotation du logo (°)", -180, 180, 0, "logo_rotation_scale"),
            ("Opacité du logo (%)", 0, 100, 100, "logo_opacity_scale")
        ]
        Label(container, text="Paramètres de position et taille", font=("Segoe UI", 12, "underline"), bg="#f9f9f9", fg="#555").pack(pady=(10, 0))
        for text, minv, maxv, default, name in sliders:
            self._add_slider(container, text, minv, maxv, default, name)

        Label(self.frame, text="🖼️ Appuie ici pour générer ta miniature PNG", bg="#f9f9f9", fg="#666", font=("Segoe UI", 10)).pack(pady=(20, 5))
        Button(self.frame, text="✅ Créer la miniature", command=self.create_thumbnail,
               bg="#388E3C", fg="white", font=("Segoe UI", 12, "bold"), relief="raised", height=2).pack(pady=15, fill="x", padx=100)

        self.preview_canvas = Canvas(self.frame, width=960, height=540, bg="#fefefe", bd=2, relief="ridge")
        self.preview_canvas.pack(pady=10)

        Button(self.frame, text="🔄 Mettre à jour l'aperçu", command=self.update_preview,
               bg="#2196F3", fg="white", font=("Segoe UI", 11, "bold"), relief="flat").pack(pady=(0, 30), padx=100, fill="x")

    def _create_input_row(self, parent, label_text, command):
        row = Frame(parent, bg="#f9f9f9")
        row.pack(fill="x", pady=6)
        Label(row, text=label_text, font=("Segoe UI", 11, "bold"), bg="#f9f9f9", width=20, anchor="w", fg="#333").pack(side="left")
        Button(row, text="Parcourir", command=command, width=15, font=("Segoe UI", 10), bg="#eeeeee", relief="flat").pack(side="left", padx=10)
        status = Label(row, text="❌", bg="#f9f9f9", font=("Segoe UI", 11))
        status.pack(side="left")
        self.controls[label_text] = status

    def _add_slider(self, parent, label_text, min_val, max_val, default_val, var_name):
        frame = Frame(parent, bg="#f9f9f9")
        frame.pack(fill="x", pady=10)
        Label(frame, text=label_text, font=("Segoe UI", 11, "bold"), bg="#f9f9f9", fg="#444").pack(anchor="w")
        scale = Scale(frame, from_=min_val, to=max_val, orient=HORIZONTAL, length=850, bg="#f0f0f0", relief="groove",
                      highlightthickness=0, troughcolor="#cccccc", font=("Segoe UI", 9),
                      showvalue=True, command=lambda val: self.update_preview())
        scale.set(default_val)
        scale.pack()
        setattr(self, var_name, scale)

    def _on_mousewheel(self, event):
        move = -1 if event.delta > 0 or event.num == 4 else 1
        self.canvas.yview_scroll(move, "units")

    def select_bg(self):
        self.bg_path = self._select_file("Image de fond")
        self.controls["Image de fond"].config(text="✅" if self.bg_path else "❌")
        self.update_preview()

    def select_center(self):
        self.center_path = self._select_file("Image centrale")
        self.controls["Image centrale"].config(text="✅" if self.center_path else "❌")
        self.update_preview()

    def select_logo(self):
        self.logo_path = self._select_file("Logo")
        self.controls["Logo"].config(text="✅" if self.logo_path else "❌")
        self.update_preview()

    def select_banner(self):
        self.banner_path = self._select_file("Bannière de titre")
        self.controls["Bannière de titre"].config(text="✅" if self.banner_path else "❌")
        self.update_preview()

    def _select_file(self, title):
        return filedialog.askopenfilename(title=title, filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp *.gif")])

    def create_thumbnail(self):
        if not all([self.bg_path, self.center_path, self.logo_path, self.banner_path]):
            messagebox.showerror("Erreur", "Tu dois sélectionner les 4 images avant de continuer.")
            return

        self.output_path = filedialog.asksaveasfilename(defaultextension=".png", title="Enregistrer la miniature",
                                                        filetypes=[("Image PNG", "*.png")])
        if self.output_path:
            try:
                self._generate_image(self.output_path)
                messagebox.showinfo("Succès", "Miniature créée avec succès !")
            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur s'est produite :\n{e}")

    def update_preview(self):
        try:
            temp_path = "preview_temp.png"
            if all([self.bg_path, self.center_path, self.logo_path, self.banner_path]):
                self._generate_image(temp_path)
                preview = Image.open(temp_path).resize((960, 540), Image.Resampling.LANCZOS)
                self.preview_image = ImageTk.PhotoImage(preview)
                self.preview_canvas.create_image(0, 0, anchor="nw", image=self.preview_image)
        except Exception:
            pass

    def _generate_image(self, output_path):
        bg = Image.open(self.bg_path).convert("RGBA")
        center = Image.open(self.center_path).convert("RGBA")
        logo = Image.open(self.logo_path).convert("RGBA")
        banner = Image.open(self.banner_path).convert("RGBA")

        bw, bh = bg.size
        margin = 28
        tw, th = bw - 2 * margin, bh - 2 * margin

        center = center.resize((tw, th), Image.Resampling.LANCZOS)
        lx = int(margin + (tw - int(tw * 0.4)) * self.logo_pos_scale.get() / 100)
        ly = margin + self.logo_y_scale.get()
        logo_scale = self.logo_size_scale.get() / 100
        logo_width = int(tw * 0.4 * logo_scale)
        logo_height = int(logo.height * (logo_width / logo.width))
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
        logo = logo.rotate(self.logo_rotation_scale.get(), expand=True)
        if logo.mode != 'RGBA':
            logo = logo.convert('RGBA')
        alpha = logo.split()[3].point(lambda p: int(p * self.logo_opacity_scale.get() / 100))
        logo.putalpha(alpha)

        bs = self.banner_size_scale.get() / 100
        bwid = int(bw * bs)
        bht = int(banner.height * (bwid / banner.width))
        banner = banner.resize((bwid, bht), Image.Resampling.LANCZOS)
        bx = (bw - bwid) // 2
        by = bh - bht + self.banner_y_scale.get()

        final = bg.copy()
        final.paste(center, (margin, margin), center)
        final.paste(logo, (lx, ly), logo)
        final.paste(banner, (bx, by), banner)
        final.save(output_path, "PNG")

if __name__ == "__main__":
    root = Tk()
    app = ThumbnailApp(root)
    root.mainloop()
