import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import os
import platform
import subprocess
import threading
import time  # Para posibles animaciones o esperas
import requests  # Importa la biblioteca requests

# Paleta de colores mejorada
COLORS = {
    "primary": "#3498db",      # Azul más moderno
    "secondary": "#2ecc71",    # Verde más vibrante
    "danger": "#e74c3c",       # Rojo más intenso
    "warning": "#f39c12",      # Naranja más llamativo
    "dark": "#34495e",         # Gris oscuro elegante
    "light": "#ecf0f1",        # Gris claro suave
    "text": "#2c3e50",         # Texto oscuro legible
    "highlight": "#bdc3c7",    # Gris para resaltar
    "ramdisk": "#9b59b6"       # Morado distintivo para Ramdisk
}

# Tooltip sencillo
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 30
        y = self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#FFFFE0", relief="solid", borderwidth=1,
                         font=("Segoe UI", 9))
        label.pack(ipadx=4)

    def hide(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class iCosM8ToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("iCosM8 TOOL v3.1")
        self.root.geometry("950x750")  # Aumentar altura para el nuevo botón
        self.root.configure(bg=COLORS["light"])
        self.icon_images = {}
        self.ramdisk_path = tk.StringVar()
        self.registro_mensaje = None  # Inicializa self.registro_mensaje
        # Variables de información del dispositivo
        self.device_model = tk.StringVar(value="Desconocido")
        self.device_ecid = tk.StringVar(value="Desconocido")
        self.device_imei = tk.StringVar(value="Desconocido")
        self.device_ios = tk.StringVar(value="Desconocido")
        self.setup_styles()
        self.cargar_iconos()
        self.script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
        self.tool_config = {
            "checkra1n_command": "sudo checkra1n",
            "paldra1n_command": "sudo palera1n --tweaks", # Ejemplo de comando palera1n
            "bypass_passcode_script": os.path.join(self.script_dir, "bypass_passcode.py"),
            "bypass_hello_tool": os.path.join(self.script_dir, "bypass_hello.sh"), # Ejemplo como script sh
            "boot_ramdisk_command": "sudo python3 /ruta/a/tu/script_boot_ramdisk.py", # Comando base
            "restore_command": "sudo irestore -w" # Comando base para restauración, ajustar según herramienta
        }
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", padding=10, font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.configure("Primary.TButton", background=COLORS["primary"], foreground="white")
        style.configure("Secondary.TButton", background=COLORS["secondary"], foreground="white")
        style.configure("Danger.TButton", background=COLORS["danger"], foreground="white")
        style.configure("Warning.TButton", background=COLORS["warning"], foreground="black")
        style.configure("Dark.TButton", background=COLORS["dark"], foreground="white")
        style.configure("Ramdisk.TButton", background=COLORS["ramdisk"], foreground="white")
        style.configure("TLabel", background=COLORS["light"], foreground=COLORS["text"])
        style.configure("TFrame", background=COLORS["light"])
        style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("Highlight.TFrame", background=COLORS["highlight"])
        style.configure("Highlight.TLabel", background=COLORS["highlight"], foreground=COLORS["dark"])

    def cargar_iconos(self):
        iconos = {
            "detect": "icon_detect.png",
            "ipwndfu": "icon_ipwndfu.png",
            "checkra1n": "icon_checkra1n.png",
            "palera1n": "icon_palera1n.png",
            "passcode": "icon_passcode.png",
            "hello": "icon_hello.png",
            "restore": "icon_restore.png",
            "ramdisk": "icon_ramdisk.png",
            "boot": "icon_boot.png"
        }
        script_dir = os.path.dirname(os.path.abspath(__file__))
        for k, v in iconos.items():
            try:
                img_path = os.path.join(script_dir, v)
                img = Image.open(img_path).resize((24, 24))
                self.icon_images[k] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error al cargar icono {v}: {e}")
                self.icon_images[k] = None

    def create_widgets(self):
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="iCosM8 TOOL v3.1", font=("Segoe UI", 18, "bold"),
                  background=COLORS["dark"], foreground="white").pack(side="left", fill="x", expand=True, padx=15, pady=10)
        help_btn = ttk.Button(header, text="?", style="Warning.TButton", command=self.mostrar_ayuda, width=3)
        help_btn.pack(side="right", padx=15, pady=10)
        Tooltip(help_btn, "Ayuda y preguntas frecuentes")

        # Área de información del dispositivo
        self.info_frame = ttk.LabelFrame(self.root, text="Información del dispositivo", padding=(15, 10))
        self.info_frame.pack(fill="x", padx=15, pady=(0, 15))
        self._crear_info_dispositivo(self.info_frame)

        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Acciones principales
        self.create_actions_frame(main_frame)

        # Área de resultados
        ttk.Label(main_frame, text="Registro:", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(15, 5))
        self.resultado_text = ScrolledText(main_frame, height=15, font=("Consolas", 9), wrap="word",
                                            bg=COLORS["light"], fg=COLORS["text"], borderwidth=1, relief="solid")
        self.resultado_text.pack(fill="both", expand=True, pady=(0, 15))
        self.resultado_text.tag_config("error", foreground=COLORS["danger"])
        self.resultado_text.tag_config("success", foreground=COLORS["secondary"])
        self.resultado_text.config(state="disabled")

        # Barra de estado
        status_bar = ttk.Frame(self.root, height=30, style="Highlight.TFrame")
        status_bar.pack(fill="x", side="bottom")
        self.status_label = ttk.Label(status_bar, text="Listo", font=("Segoe UI", 10, "italic"), anchor="w",
                                     style="Highlight.TLabel")
        self.status_label.pack(side="left", padx=15)
        self.progress = ttk.Progressbar(status_bar, mode="indeterminate", length=150)
        self.progress.pack(side="right", padx=15)
        self.progress.stop()

    def _crear_info_dispositivo(self, parent):
        info_labels = [("Modelo:", self.device_model), ("ECID:", self.device_ecid),
                       ("IMEI:", self.device_imei), ("iOS:", self.device_ios)]
        for i, (texto, variable) in enumerate(info_labels):
            ttk.Label(parent, text=texto, style="TLabel", font=("Segoe UI", 10)).grid(row=i // 2, column=(i % 2) * 2, sticky="e", padx=10, pady=5)
            ttk.Entry(parent, textvariable=variable, state="readonly", width=25, font=("Segoe UI", 10),
                      foreground=COLORS["text"]).grid(row=i // 2, column=(i % 2) * 2 + 1, sticky="w", padx=10, pady=5)

    def create_actions_frame(self, parent):
        acciones_frame = ttk.LabelFrame(parent, text="Acciones principales", padding=(15, 10))
        acciones_frame.pack(fill="x", pady=10)

        # Fila 1: Detección e IPWNDFU
        frame_row1 = ttk.Frame(acciones_frame)
        frame_row1.pack(fill="x", pady=5)
        self._crear_boton(frame_row1, "detect", "Detectar Dispositivo", self.detectar_dispositivo, style="Primary.TButton").pack(side="left", fill="x", expand=True, padx=(0, 5))
        self._crear_boton(frame_row1, "ipwndfu", "Ejecutar IPWNDFU", self.ejecutar_ipwndfu, style="Primary.TButton").pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Fila 2: checkra1n y palera1n
        frame_row2 = ttk.Frame(acciones_frame)
        frame_row2.pack(fill="x", pady=5)
        self._crear_boton(frame_row2, "checkra1n", "Ejecutar checkra1n", self.ejecutar_checkra1n, style="Secondary.TButton").pack(side="left", fill="x", expand=True, padx=(0, 5))
        self._crear_boton(frame_row2, "palera1n", "Ejecutar palera1n", self.ejecutar_palera1n, style="Secondary.TButton").pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Fila 3: RamDisk
        ramdisk_frame = ttk.Frame(acciones_frame)
        ramdisk_frame.pack(fill="x", pady=5)
        btn_cargar_ramdisk = ttk.Button(ramdisk_frame, text="Cargar RamDisk", style="Ramdisk.TButton",
                                        image=self.icon_images.get("ramdisk"), compound="left",
                                        command=self.cargar_ramdisk)
        btn_cargar_ramdisk.pack(side="left", padx=(0, 5))
        Tooltip(btn_cargar_ramdisk, "Selecciona el archivo RamDisk para el dispositivo")
        self.entry_ramdisk = ttk.Entry(ramdisk_frame, textvariable=self.ramdisk_path, state="readonly",
                                       font=("Segoe UI", 10), foreground=COLORS["text"])
        self.entry_ramdisk.pack(side="left", fill="x", expand=True)
        btn_boot_ramdisk = ttk.Button(ramdisk_frame, text="Boot RamDisk", style="Ramdisk.TButton",
                                      image=self.icon_images.get("boot"), compound="left",
                                      command=self.boot_ramdisk)
        btn_boot_ramdisk.pack(side="left", padx=(5, 0))
        Tooltip(btn_boot_ramdisk, "Bootear el RamDisk seleccionado en el dispositivo")

        # Fila 4: Bypass Passcode y Hello
        frame_row4 = ttk.Frame(acciones_frame)
        frame_row4.pack(fill="x", pady=5)
        self._crear_boton(frame_row4, "passcode", "Bypass Passcode", self.ejecutar_bypass_passcode, style="Warning.TButton").pack(side="left", fill="x", expand=True, padx=(0, 5))
        self._crear_boton(frame_row4, "hello", "Bypass Hello", self.ejecutar_bypass_hello, style="Warning.TButton").pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Fila 5: Restaurar
        frame_row5 = ttk.Frame(acciones_frame)
        frame_row5.pack(fill="x", pady=5)
        self._crear_boton(frame_row5, "restore", "Restaurar Dispositivo", self.restaurar_dispositivo, style="Danger.TButton").pack(fill="x", pady=3)

        # Fila adicional para el botón de registro (puedes ajustarlo donde prefieras)
        registro_frame = ttk.Frame(acciones_frame)
        registro_frame.pack(fill="x", pady=5)
        registro_btn = ttk.Button(registro_frame, text="Registro de Usuario", command=self.mostrar_panel_registro)
        registro_btn.pack(fill="x")
        Tooltip(registro_btn, "Abrir panel de registro de usuario")

    def _crear_boton(self, parent, icon_key, texto, comando, style="Primary.TButton"):
        if self.icon_images.get(icon_key):
            btn = ttk.Button(parent, text=f" {texto}", style=style,
                             image=self.icon_images[icon_key], compound="left", command=comando)
        else:
            btn = ttk.Button(parent, text=f" {texto}", style=style, command=comando)
        Tooltip(btn, texto)
        return btn

    def mostrar_panel_registro(self):
        registro_window = tk.Toplevel(self.root)
        registro_window.title("Registro de Usuario")

        ttk.Label(registro_window, text="Nombre de Usuario:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        username_entry = ttk.Entry(registro_window)
        username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(registro_window, text="Contraseña:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        password_entry = ttk.Entry(registro_window, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(registro_window, text="Confirmar Contraseña:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        confirm_password_entry = ttk.Entry(registro_window, show="*")
        confirm_password_entry.grid(row=2, column=1, padx=5, pady=5)

        registro_button = ttk.Button(registro_window, text="Registrarse",
                                     command=lambda: self.registrar_usuario(username_entry.get(),
                                                                              password_entry.get(),
                                                                              confirm_password_entry.get()))
        registro_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        self.registro_mensaje = ttk.Label(registro_window, text="")
        self.registro_mensaje.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def registrar_usuario(self, username, password, confirm_password):
        if not username or notpassword or not confirm_password:
            self.registro_mensaje.config(text="Por favor, complete todos los campos.", foreground=COLORS["danger"])
            return
        if password != confirm_password:
            self.registro_mensaje.config(text="Las contraseñas no coinciden.", foreground=COLORS["danger"])
            return

        # URL del backend (ajústala si tu backend está en otra dirección)
        backend_url = "http://localhost:5000/register"
        data = {"username": username, "password": password}

        try:
            response = requests.post(backend_url, json=data)
            response.raise_for_status()  # Lanza una excepción para códigos de error HTTP (4xx o 5xx)
            response_data = response.json()
            if response_data.get("success"):
                self.registro_mensaje.config(text="Registro exitoso.", foreground=COLORS["secondary"])
            else:
                error_message = response_data.get("error", "Error desconocido durante el registro.")
                self.registro_mensaje.config(text=f"Error al registrar: {error_message}", foreground=COLORS["danger"])
        except requests.exceptions.ConnectionError:
            self.registro_mensaje.config(text="No se pudo conectar al servidor de registro.", foreground=COLORS["danger"])
        except requests.exceptions.RequestException as e:
            self.registro_mensaje.config(text=f"Error de conexión o respuesta del servidor: {e}", foreground=COLORS["danger"])
        except ImportError:
            self.registro_mensaje.config(text="La biblioteca 'requests' no está instalada.", foreground=COLORS["danger"])

    def detectar_dispositivo(self):
        self.mostrar_salida("Detectando dispositivo...", "normal")
        self.status_label.config(text="Detectando...")
        threading.Thread(target=self._detectar_dispositivo_thread).start()

    def _detectar_dispositivo_thread(self):
        time.sleep(1) # Simulación de detección
        self.root.after(0, self._simular_info_dispositivo)

    def _simular_info_dispositivo(self):
        # Simula datos detectados
        self.device_model.set("iPhone 8 Plus")
        self.device_ecid.set("0x987654321FEDCBA")
        self.device_imei.set("351234567890123")
        self.device_ios.set("17.1.1")
        self._accion_finalizada("Dispositivo detectado.", "success")

    def ejecutar_ipwndfu(self):
        self._ejecutar_comando_thread("Ejecutando IPWNDFU...", ["sudo", "irecovery", "-q"], "IPWNDFU completado.")

    def ejecutar_checkra1n(self):
        self._ejecutar_comando_thread("Ejecutando checkra1n...", self.tool_config["checkra1n_command"].split(), "checkra1n completado.")

    def ejecutar_palera1n(self):
        self._ejecutar_comando_thread("Ejecutando palera1n...", self.tool_config["paldra1n_command"].split(), "palera1n completado.")

    def ejecutar_bypass_passcode(self):
        script_path = self.tool_config["bypass_passcode_script"]
        if os.path.exists(script_path):
            self._ejecutar_comando_thread("Bypass Passcode...", ["sudo", "python3", script_path], "Bypass Passcode completado.")
        else:
            self._accion_finalizada(f"Error: Script no encontrado: {script_path}", "error")

    def ejecutar_bypass_hello(self):
        script_path = self.tool_config["bypass_hello_tool"]
        if os.path.exists(script_path):
            # Adaptar según si es un script ejecutable o necesita intérprete
            if script_path.endswith(".py"):
                self._ejecutar_comando_thread("Bypass Hello...", ["sudo", "python3", script_path], "Bypass Hello completado.")
            elif script_path.endswith(".sh"):
                self._ejecutar_comando_thread("Bypass Hello...", ["sudo", "bash", script_path], "Bypass Hello completado.")
            else:
                self._ejecutar_comando_thread("Bypass Hello...", ["sudo", script_path], "Bypass Hello completado.")
        else:
            self._accion_finalizada(f"Error: Herramienta no encontrada: {script_path}", "error")

    def restaurar_dispositivo(self):
        ruta_ipsw = filedialog.askopenfilename(title="Seleccionar archivo IPSW", filetypes=[("Archivos IPSW", "*.ipsw")])
        if ruta_ipsw:
            comando = self.tool_config["restore_command"].split() + [ruta_ipsw]
            self._ejecutar_comando_thread(f"Restaurando con {os.path.basename(ruta_ipsw)}...", comando, "Restauración completada.")
        else:
            self.mostrar_salida("Restauración cancelada por el usuario.", "warning")
            self.status_label.config(text="Listo")

    def cargar_ramdisk(self):
        ruta = filedialog.askopenfilename(title="Seleccionar RamDisk",
                                        filetypes=[("Archivos RamDisk", "*.img *.dmg *.bin"), ("Todos los archivos", "*.*")])
        if ruta:
            self.ramdisk_path.set(ruta)
            self.mostrar_salida(f"RamDisk seleccionado: {ruta}", "normal")

    def boot_ramdisk(self):
        ramdisk_file = self.ramdisk_path.get()
        if not ramdisk_file:
            messagebox.showerror("Error", "Por favor, selecciona un archivo RamDisk primero.")
            return
        comando = self.tool_config["boot_ramdisk_command"].split() + [ramdisk_file]
        self._ejecutar_comando_thread(f"Booting RamDisk: {os.path.basename(ramdisk_file)}...", comando, "Boot de RamDisk completado.")

    def _ejecutar_comando_thread(self, mensaje_inicio, comando, mensaje_fin):
        self.mostrar_salida(mensaje_inicio, "normal")
        self.status_label.config(text=mensaje_inicio)
        self.progress.start()
        threading.Thread(target=self._ejecutar_comando, args=(comando, mensaje_fin)).start()

    def _ejecutar_comando(self, comando, mensaje_fin):
        try:
            proceso = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            while True:
                linea = proceso.stdout.readline()
                if not linea:
                    break
                self.mostrar_salida(linea.strip(), "normal")
            stdout, stderr = proceso.communicate()
            retorno = proceso.wait()
            if retorno == 0:
                self._accion_finalizada(mensaje_fin, "success")
            else:
                self._accion_finalizada(f"Error: {stderr.strip()}", "error")
        except FileNotFoundError:
            self._accion_finalizada(f"Error: Comando no encontrado: {comando[0]}", "error")
        except PermissionError:
            self._accion_finalizada(f"Error: Permiso denegado al ejecutar: {comando[0]}", "error")
        except Exception as e:
            self._accion_finalizada(f"Error inesperado: {e}", "error")
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.status_label.config, {"text": "Listo"})

    def mostrar_salida(self, texto, tipo="normal"):
        self.resultado_text.config(state="normal")
        self.resultado_text.insert("end", texto + "\n", tipo)
        self.resultado_text.see("end")
        self.resultado_text.config(state="disabled")

    def _accion_finalizada(self, mensaje, tipo="success"):
        self.mostrar_salida(mensaje, tipo)
        self.mostrar_notificacion(mensaje, tipo)

    def mostrar_notificacion(self, mensaje, tipo="info"):
        color = {"info": COLORS["primary"], "error": COLORS["danger"], "success": COLORS["secondary"], "warning": COLORS["warning"]}.get(tipo, COLORS["primary"])
        notif = tk.Toplevel(self.root)
        notif.overrideredirect(True)
        notif.configure(bg=color)
        notif.attributes("-topmost", True)
        tk.Label(notif, text=mensaje, bg=color, fg="white", font=("Segoe UI", 10, "bold")).pack(padx=20, pady=10)
        notif.update_idletasks()
        w = notif.winfo_width()
        x = self.root.winfo_x() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_y() + 60
        notif.geometry(f"+{x}+{y}")
        notif.after(2000, notif.destroy)

    def mostrar_ayuda(self):
        messagebox.showinfo("Ayuda", "iCosM8 TOOL v3.1\n\n- Selecciona las acciones deseadas.\n- Asegúrate de tener las herramientas necesarias instaladas y configuradas.\n- Los scripts de bypass deben estar en la carpeta 'scripts'.\n- Ejecuta como root para algunas funciones.\n- Consulta la documentación para más detalles.")

if __name__ == "__main__":
    if platform.system() != "Linux":
        messagebox.showerror("Error", "Esta herramienta está optimizada para Linux.")
        exit()
    root = tk.Tk()
    app = iCosM8ToolGUI(root)
    root.mainloop()