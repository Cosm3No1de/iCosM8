import tkinter as tk
from tkinter import ttk, font, messagebox
import subprocess
import platform
import re
import os
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk  # NUEVO: para iconos

# Configuración inicial
VERSION = "2.9"
SUPPORTED_IOS_VERSIONS = ["14", "15", "16"]
SCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")

# Paleta de colores unificada
COLORS = {
    "primary": "#4E79A7",  # Azul principal unificado
    "secondary": "#59A14F",  # Verde
    "danger": "#E15759",  # Rojo
    "warning": "#EDC948",  # Amarillo
    "dark": "#3E3E3E",  # Gris oscuro
    "light": "#F0F0F0",  # Fondo claro
    "text": "#333333",  # Texto oscuro
    "highlight": "#BAB0AC"  # Resaltado
}

# --- NUEVO: Función para tooltips ---
def add_tooltip(widget, text):
    tooltip = tk.Toplevel(widget)
    tooltip.withdraw()
    tooltip.overrideredirect(True)
    label = tk.Label(tooltip, text=text, background="#FFFFE0", relief="solid",
                     borderwidth=1, font=("Segoe UI", 8))
    label.pack()
    def enter(event):
        x, y, _, _ = widget.bbox("insert") if hasattr(widget, "bbox") else (0, 0, 0, 0)
        x += widget.winfo_rootx() + 30
        y += widget.winfo_rooty() + 20
        tooltip.geometry(f"+{x}+{y}")
        tooltip.deiconify()
    def leave(event):
        tooltip.withdraw()
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)

class iCosM8Tool:
    def __init__(self, root):
        self.root = root
        self.icon_images = {}  # NUEVO: para mantener referencias a iconos
        self.setup_ui()
        self.setup_styles()
        self.create_widgets()
        
    def setup_ui(self):
        self.root.title(f"iCosM8 TOOL v{VERSION}")
        self.root.geometry("950x750")  # Más grande para iconos y mejor espaciado
        self.root.minsize(900, 700)
        self.root.configure(bg=COLORS["light"])
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=10)

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_create("iCosM8Uniform", parent="clam", settings={
            ".": {
                "configure": {
                    "background": COLORS["light"],
                    "foreground": COLORS["text"],
                    "font": ("Segoe UI", 10)
                }
            },
            "TButton": {
                "configure": {
                    "padding": 8,
                    "font": ("Segoe UI", 10, "bold"),
                    "anchor": "center",
                    "relief": "flat",
                    "borderwidth": 0,
                    "width": 18
                },
                "map": {
                    "background": [("active", COLORS["highlight"])],
                    "foreground": [("active", "white")]
                }
            },
            "Primary.TButton": {"configure": {"background": COLORS["primary"], "foreground": "white"}},
            "Secondary.TButton": {"configure": {"background": COLORS["secondary"], "foreground": "white"}},
            "Danger.TButton": {"configure": {"background": COLORS["danger"], "foreground": "white"}},
            "Warning.TButton": {"configure": {"background": COLORS["warning"], "foreground": COLORS["text"]}},
            "Dark.TButton": {"configure": {"background": COLORS["dark"], "foreground": "white"}},
            "TNotebook.Tab": {
                "configure": {
                    "padding": [15, 5],
                    "font": ("Segoe UI", 10, "bold"),
                    "background": COLORS["light"]
                },
                "map": {
                    "background": [("selected", "white")],
                    "expand": [("selected", [1, 1, 1, 0])]
                }
            }
        })
        self.style.theme_use("iCosM8Uniform")
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Header profesional con logo ficticio
        header_frame = ttk.Frame(main_frame, style="Dark.TButton")
        header_frame.pack(fill="x", pady=(0, 10))
        # Logo ficticio (puedes poner la ruta de tu logo aquí)
        try:
            logo_img = Image.open("logo.png").resize((36,36))
            self.logo_tk = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(header_frame, image=self.logo_tk, background=COLORS["dark"])
            logo_label.pack(side="left", padx=(10,5))
        except:
            pass  # Si no hay logo, omite
        
        ttk.Label(header_frame, text=f"iCosM8 TOOL v{VERSION}", 
                 font=("Segoe UI", 14, "bold"), 
                 foreground="white",
                 background=COLORS["dark"]).pack(side="left", padx=10)
        # Botón de ayuda
        help_btn = ttk.Button(header_frame, text="?", style="Warning.TButton", command=self.mostrar_ayuda, width=3)
        help_btn.pack(side="right", padx=8)
        add_tooltip(help_btn, "Ayuda y preguntas frecuentes")
        
        # Panel de pestañas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        # Cargar iconos (puedes usar tus propios PNG)
        iconos = {
            "detect": "icon_detect.png",
            "passcode": "icon_passcode.png",
            "hello": "icon_hello.png",
            "restore": "icon_restore.png",
            "ipwndfu": "icon_ipwndfu.png",
            "checkra1n": "icon_checkra1n.png"
        }
        for k, v in iconos.items():
            try:
                img = Image.open(v).resize((20,20))
                self.icon_images[k] = ImageTk.PhotoImage(img)
            except:
                self.icon_images[k] = None  # Si no hay icono, se omite
        
        for version in SUPPORTED_IOS_VERSIONS:
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=f"iOS {version}")
            
            # Agrupador de acciones principales
            acciones_frame = ttk.LabelFrame(tab, text="Acciones principales", padding=(10,8))
            acciones_frame.pack(fill="x", pady=5)
            
            btn1 = ttk.Button(acciones_frame, text=" Detectar", style="Dark.TButton",
                      image=self.icon_images["detect"], compound="left",
                      command=self.detectar_vulnerabilidad)
            btn1.pack(fill="x", pady=3)
            add_tooltip(btn1, "Detecta si el dispositivo es vulnerable y está conectado")
            
            ttk.Separator(acciones_frame).pack(fill="x", pady=5)
            
            btn2 = ttk.Button(acciones_frame, text=" Bypass Passcode", style="Primary.TButton",
                      image=self.icon_images["passcode"], compound="left",
                      command=lambda v=version: self.ejecutar_bypass_passcode(v))
            btn2.pack(fill="x", pady=2)
            add_tooltip(btn2, "Realiza el bypass del código de acceso en el dispositivo")
            
            btn3 = ttk.Button(acciones_frame, text=" Bypass Hello", style="Primary.TButton",
                      image=self.icon_images["hello"], compound="left",
                      command=lambda v=version: self.ejecutar_bypass_hello(v))
            btn3.pack(fill="x", pady=2)
            add_tooltip(btn3, "Realiza el bypass de la pantalla Hello en el dispositivo")
            
            btn4 = ttk.Button(acciones_frame, text=" Restaurar", style="Danger.TButton",
                      image=self.icon_images["restore"], compound="left",
                      command=lambda v=version: self.restaurar_dispositivo(v))
            btn4.pack(fill="x", pady=3)
            add_tooltip(btn4, "Restaura el dispositivo a estado de fábrica")
            
            ttk.Separator(acciones_frame).pack(fill="x", pady=5)
            
            # Agrupador de utilidades
            util_frame = ttk.LabelFrame(tab, text="Utilidades avanzadas", padding=(10,8))
            util_frame.pack(fill="x", pady=5)
            
            btn5 = ttk.Button(util_frame, text=" Ejecutar IPWNDFU", style="Secondary.TButton",
                      image=self.icon_images["ipwndfu"], compound="left",
                      command=self.ejecutar_ipwndfu)
            btn5.pack(fill="x", pady=2)
            add_tooltip(btn5, "Ejecuta el modo DFU avanzado (ipwndfu)")
            
            btn6 = ttk.Button(util_frame, text=" Ejecutar checkra1n", style="Primary.TButton",
                      image=self.icon_images["checkra1n"], compound="left",
                      command=self.ejecutar_checkra1n)
            btn6.pack(fill="x", pady=2)
            add_tooltip(btn6, "Ejecuta el exploit checkra1n para jailbreak")
        
        # Área de resultados
        ttk.Label(main_frame, text="Registro:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        self.resultado_text = ScrolledText(main_frame, height=12, font=("Consolas", 9),
                                         wrap="word", padx=10, pady=10)
        self.resultado_text.pack(fill="both", expand=True)
        self.resultado_text.tag_config("error", foreground=COLORS["danger"])
        self.resultado_text.tag_config("success", foreground=COLORS["secondary"])
        self.resultado_text.config(state="disabled")
        
        # Barra de estado mejorada
        self.status_bar = ttk.Frame(main_frame, height=24)
        self.status_bar.pack(fill="x")
        
        self.status_label = ttk.Label(self.status_bar, text="Listo", font=("Segoe UI", 9, "italic"))
        self.status_label.pack(side="left")
        
        self.progress = ttk.Progressbar(self.status_bar, mode="indeterminate", length=120)
        self.progress.pack(side="right", padx=8)
    
    # ===== Funciones principales =====
    def mostrar_salida(self, texto, tipo="normal"):
        self.resultado_text.config(state="normal")
        self.resultado_text.insert("end", texto + "\n", tipo)
        self.resultado_text.see("end")
        self.resultado_text.config(state="disabled")
        self.root.update()
    
    def mostrar_notificacion(self, mensaje, tipo="info"):
        color = {"info": "#4E79A7", "error": "#E15759", "success": "#59A14F", "warning": "#EDC948"}.get(tipo, "#4E79A7")
        notif = tk.Toplevel(self.root)
        notif.overrideredirect(True)
        notif.configure(bg=color)
        notif.attributes("-topmost", True)
        tk.Label(notif, text=mensaje, bg=color, fg="white", font=("Segoe UI", 10, "bold")).pack(padx=20, pady=10)
        notif.update_idletasks()
        w, h = notif.winfo_width(), notif.winfo_height()
        x = self.root.winfo_x() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_y() + 60
        notif.geometry(f"+{x}+{y}")
        notif.after(2200, notif.destroy)

    def ejecutar_comando(self, comando, timeout=60):
        self.progress.start()
        self.status_label.config(text="Ejecutando...")
        try:
            proceso = subprocess.run(comando, shell=True, 
                                   timeout=timeout,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
            if proceso.stdout:
                self.mostrar_salida(proceso.stdout)
            if proceso.stderr:
                self.mostrar_salida(proceso.stderr, "error")
            return proceso.returncode
        except subprocess.TimeoutExpired:
            self.mostrar_salida(f"Timeout ({timeout}s)", "error")
            self.mostrar_notificacion("Tiempo de espera agotado", "error")
            return -1
        except Exception as e:
            self.mostrar_salida(str(e), "error")
            self.mostrar_notificacion("Error inesperado", "error")
            return -1
        finally:
            self.progress.stop()
            self.status_label.config(text="Listo")
    
    def detectar_vulnerabilidad(self):
        self.mostrar_salida("\n[Detectando dispositivo...]")
        if platform.system() != "Linux":
            self.mostrar_salida("Error: Solo Linux", "error")
            self.mostrar_notificacion("Solo compatible con Linux", "warning")
            return
        ret = self.ejecutar_comando("lsusb -v")
        if ret == 0:
            self.mostrar_salida("Dispositivo detectado", "success")
            self.mostrar_notificacion("Dispositivo detectado", "success")
    
    def ejecutar_bypass_passcode(self, version):
        self.mostrar_salida(f"\n[Bypass Passcode iOS {version}]")
        script = os.path.join(SCRIPT_DIR, f"ios{version}", "passcode_bypass.py")
        if os.path.exists(script):
            ret = self.ejecutar_comando(f"sudo python3 {script}", 120)
            self.mostrar_salida("Completado" if ret == 0 else "Falló", 
                               "success" if ret == 0 else "error")
            self.mostrar_notificacion("Bypass Passcode completado" if ret == 0 else "Falló", 
                                      "success" if ret == 0 else "error")
        else:
            self.mostrar_salida("Script no encontrado", "error")
            self.mostrar_notificacion("Script no encontrado", "error")
    
    def ejecutar_bypass_hello(self, version):
        self.mostrar_salida(f"\n[Bypass Hello iOS {version}]")
        script = os.path.join(SCRIPT_DIR, f"ios{version}", "hello_bypass.py")
        if os.path.exists(script):
            ret = self.ejecutar_comando(f"sudo python3 {script}", 120)
            self.mostrar_salida("Completado" if ret == 0 else "Falló", 
                               "success" if ret == 0 else "error")
            self.mostrar_notificacion("Bypass Hello completado" if ret == 0 else "Falló", 
                                      "success" if ret == 0 else "error")
        else:
            self.mostrar_salida("Script no encontrado", "error")
            self.mostrar_notificacion("Script no encontrado", "error")
    
    def restaurar_dispositivo(self, version):
        self.mostrar_salida(f"\n[Restaurando iOS {version}]")
        cmd = "idevicerestore -e -l" if version in ["14", "15"] else "futurerestore --latest-sep --latest-baseband"
        ret = self.ejecutar_comando(f"sudo {cmd}", 300)
        self.mostrar_salida("Completado" if ret == 0 else "Falló", 
                           "success" if ret == 0 else "error")
        self.mostrar_notificacion("Restauración completada" if ret == 0 else "Falló", 
                                  "success" if ret == 0 else "error")
    
    def ejecutar_ipwndfu(self):
        self.mostrar_salida("\n[Ejecutando IPWNDFU]")
        ret = self.ejecutar_comando("sudo python3 ipwndfu/ipwndfu -p", 120)
        self.mostrar_salida("IPWNDFU completado" if ret == 0 else "Falló", 
                            "success" if ret == 0 else "error")
        self.mostrar_notificacion("IPWNDFU completado" if ret == 0 else "Falló", 
                                  "success" if ret == 0 else "error")
    
    def ejecutar_checkra1n(self):
        self.mostrar_salida("\n[Ejecutando checkra1n]")
        ret = self.ejecutar_comando("sudo checkra1n -c", 180)
        self.mostrar_salida("Completado" if ret == 0 else "Falló", 
                           "success" if ret == 0 else "error")
        self.mostrar_notificacion("Checkra1n completado" if ret == 0 else "Falló", 
                                  "success" if ret == 0 else "error")

    # NUEVO: Ayuda emergente
    def mostrar_ayuda(self):
        messagebox.showinfo("Ayuda", 
            "iCosM8 TOOL\n\n"
            "- Usa los botones según la acción deseada.\n"
            "- Pasa el mouse sobre los botones para ver su función.\n"
            "- Solo compatible con Linux y ejecuta como root para todas las funciones.\n"
            "- Para más información, consulta la documentación oficial.")

if __name__ == "__main__":
    if platform.system() != "Linux":
        messagebox.showerror("Error", "Solo compatible con Linux")
        exit()
    if os.geteuid() != 0:
        messagebox.showwarning("Advertencia", "Ejecutar como root para todas las funciones")
    os.makedirs(SCRIPT_DIR, exist_ok=True)
    for v in SUPPORTED_IOS_VERSIONS:
        os.makedirs(os.path.join(SCRIPT_DIR, f"ios{v}"), exist_ok=True)
    root = tk.Tk()
    app = iCosM8Tool(root)
    root.update()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f'+{x}+{y}')
    root.mainloop()
