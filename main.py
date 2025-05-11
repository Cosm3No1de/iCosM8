import tkinter as tk
from tkinter import ttk, font, messagebox, filedialog
import subprocess
import platform
import os
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk  # Para manipulación de imágenes e iconos
import threading # Importa la biblioteca threading

# Configuración inicial
VERSION = "2.9"
SUPPORTED_IOS_VERSIONS = ["14", "15", "16"] # Lista de versiones de iOS soportadas (ya no se usa para pestañas)
SCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")

# Paleta de colores unificada para la interfaz
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

# --- NUEVO: Función para tooltips (mensajes emergentes al pasar el ratón) ---
def add_tooltip(widget, text):
    """
    Añade un tooltip a un widget de Tkinter.

    Args:
        widget: El widget al que se le añadirá el tooltip.
        text: El texto que se mostrará en el tooltip.
    """
    tooltip = tk.Toplevel(widget)
    tooltip.withdraw() # Oculta la ventana del tooltip inicialmente
    tooltip.overrideredirect(True) # Elimina los bordes y la barra de título
    label = tk.Label(tooltip, text=text, background="#FFFFE0", relief="solid",
                     borderwidth=1, font=("Segoe UI", 8))
    label.pack()
    def enter(event):
        # Calcula la posición para mostrar el tooltip cerca del widget
        x, y, _, _ = widget.bbox("insert") if hasattr(widget, "bbox") else (0, 0, 0, 0)
        x += widget.winfo_rootx() + 30
        y += widget.winfo_rooty() + 20
        tooltip.geometry(f"+{x}+{y}")
        tooltip.deiconify() # Muestra el tooltip
    def leave(event):
        tooltip.withdraw() # Oculta el tooltip al salir del widget
    widget.bind("<Enter>", enter) # Vincula el evento de entrar con el ratón
    widget.bind("<Leave>", leave) # Vincula el evento de salir con el ratón

class iCosM8Tool:
    def __init__(self, root):
        """
        Inicializa la clase principal de la aplicación.

        Args:
            root: La ventana raíz de Tkinter.
        """
        self.root = root
        self.icon_images = {}  # NUEVO: Diccionario para almacenar las referencias a los iconos cargados
        self.dispositivo_info = None # NUEVO: Variable para almacenar la información del dispositivo detectado
        self.ramdisk_path = tk.StringVar() # Variable para almacenar la ruta del RamDisk
        self.setup_ui()
        self.setup_styles()
        self.create_widgets()

    def setup_ui(self):
        """
        Configura la ventana principal de la aplicación.
        """
        self.root.title(f"iCosM8 TOOL v{VERSION}")
        self.root.geometry("450x600")  # Ajustando la altura y un poco el ancho para el nuevo botón y entrada
        self.root.minsize(400, 550) # Tamaño mínimo de la ventana
        self.root.configure(bg=COLORS["light"]) # Color de fondo de la ventana
        default_font = font.nametofont("TkDefaultFont") # Obtiene la fuente por defecto
        default_font.configure(family="Segoe UI", size=10) # Establece la fuente por defecto

    def setup_styles(self):
        """
        Define los estilos personalizados para los widgets de la aplicación.
        """
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
                    "width": 18 # Ancho estándar para los botones
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
            "TNotebook.Tab": { # ESTO YA NO SE USA PORQUE ELIMINAMOS LAS PESTAÑAS
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
        """
        Crea los widgets de la interfaz de usuario.
        """
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
        except FileNotFoundError:
            pass  # Si no hay logo, se omite

        ttk.Label(header_frame, text=f"iCosM8 TOOL v{VERSION}",
                  font=("Segoe UI", 14, "bold"),
                  foreground="white",
                  background=COLORS["dark"]).pack(side="left", padx=10)
        # Botón de ayuda
        help_btn = ttk.Button(header_frame, text="?", style="Warning.TButton", command=self.mostrar_ayuda, width=3)
        help_btn.pack(side="right", padx=8)
        add_tooltip(help_btn, "Ayuda y preguntas frecuentes")

        # Frame para la información del dispositivo (NUEVO)
        self.info_frame = ttk.LabelFrame(main_frame, text="Información del dispositivo", padding=(10, 8))
        self.info_frame.pack(fill="x", pady=5)

        self.lbl_version = ttk.Label(self.info_frame, text="Versión iOS: Desconectado")
        self.lbl_version.pack(fill="x", pady=2)
        self.lbl_modelo = ttk.Label(self.info_frame, text="Modelo: Desconectado")
        self.lbl_modelo.pack(fill="x", pady=2)
        self.lbl_ecid = ttk.Label(self.info_frame, text="ECID: Desconectado")
        self.lbl_ecid.pack(fill="x", pady=2)
        self.lbl_serial = ttk.Label(self.info_frame, text="Número de Serie: Desconectado")
        self.lbl_serial.pack(fill="x", pady=2)

        # Frame para las acciones principales (sin pestañas, adaptándose a la info del dispositivo)
        acciones_frame = ttk.LabelFrame(main_frame, text="Acciones principales", padding=(10,8))
        acciones_frame.pack(fill="x", pady=5)

        btn_detectar = ttk.Button(acciones_frame, text=" Detectar Dispositivo", style="Dark.TButton",
                                    image=self.icon_images.get("detect"), compound="left",
                                    command=self.detectar_dispositivo_info) # NUEVA función para detectar e info
        btn_detectar.pack(fill="x", pady=3)
        add_tooltip(btn_detectar, "Detecta el dispositivo conectado y su información")

        btn_ipwndfu = ttk.Button(acciones_frame, text=" Ejecutar IPWNDFU", style="Secondary.TButton",
                                  image=self.icon_images.get("ipwndfu"), compound="left",
                                  command=self.ejecutar_ipwndfu)
        btn_ipwndfu.pack(fill="x", pady=2)
        add_tooltip(btn_ipwndfu, "Ejecuta el modo DFU avanzado (ipwndfu)")

        # Frame para RamDisk
        ramdisk_frame = ttk.Frame(acciones_frame)
        ramdisk_frame.pack(fill="x", pady=2)

        btn_ramdisk = ttk.Button(ramdisk_frame, text=" Cargar RamDisk", style="Secondary.TButton",
                                 command=self.cargar_ramdisk)
        btn_ramdisk.pack(side="left", padx=(0, 5))
        add_tooltip(btn_ramdisk, "Selecciona el archivo RamDisk para el dispositivo")

        self.entry_ramdisk = ttk.Entry(ramdisk_frame, textvariable=self.ramdisk_path)
        self.entry_ramdisk.pack(side="left", fill="x", expand=True)
        self.entry_ramdisk.config(state="disabled") # Inicialmente deshabilitado

        btn_checkra1n = ttk.Button(acciones_frame, text=" Ejecutar checkra1n", style="Primary.TButton",
                                    image=self.icon_images.get("checkra1n"), compound="left",
                                    command=self.ejecutar_checkra1n_interfaz) # Cambiado el nombre de la función
        btn_checkra1n.pack(fill="x", pady=2)
        add_tooltip(btn_checkra1n, "Ejecuta el exploit checkra1n para jailbreak")

        ttk.Separator(acciones_frame).pack(fill="x", pady=5)

        self.btn_bypass_passcode = ttk.Button(acciones_frame, text=" Bypass Passcode", style="Primary.TButton",
                                            image=self.icon_images.get("passcode"), compound="left",
                                            command=self.ejecutar_bypass_passcode) # Sin el argumento de versión
        self.btn_bypass_passcode.pack(fill="x", pady=2)
        add_tooltip(self.btn_bypass_passcode, "Realiza el bypass del código de acceso en el dispositivo")
        self.btn_bypass_passcode.config(state="disabled") # Inicialmente deshabilitado

        self.btn_bypass_hello = ttk.Button(acciones_frame, text=" Bypass Hello", style="Primary.TButton",
                                         image=self.icon_images.get("hello"), compound="left",
                                         command=self.ejecutar_bypass_hello) # Sin el argumento de versión
        self.btn_bypass_hello.pack(fill="x", pady=2)
        add_tooltip(self.btn_bypass_hello, "Realiza el bypass de la pantalla Hello en el dispositivo")
        self.btn_bypass_hello.config(state="disabled") # Inicialmente deshabilitado

        self.btn_restaurar = ttk.Button(acciones_frame, text=" Restaurar", style="Danger.TButton",
                                       image=self.icon_images.get("restore"), compound="left",
                                       command=self.restaurar_dispositivo) # Sin el argumento de versión
        self.btn_restaurar.pack(fill="x", pady=3)
        add_tooltip(self.btn_restaurar, "Restaura el dispositivo a estado de fábrica")
        self.btn_restaurar.config(state="disabled") # Inicialmente deshabilitado

        # Área de resultados
        ttk.Label(main_frame, text="Registro:", font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self.resultado_text = ScrolledText(main_frame, height=8, font=("Consolas", 9),
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

        # Cargar iconos (puedes usar tus propios PNG)
        iconos = {
            "detect": "icon_detect.png",
            "ipwndfu": "icon_ipwndfu.png",
            "checkra1n": "icon_checkra1n.png",
            "passcode": "icon_passcode.png",
            "hello": "icon_hello.png",
            "restore": "icon_restore.png"
        }
        for k, v in iconos.items():
            try:
                img = Image.open(v).resize((20,20))
                self.icon_images[k] = ImageTk.PhotoImage(img)
            except FileNotFoundError:
                self.icon_images[k] = None  # Si no hay icono, se omite

    def cargar_ramdisk(self):
        """
        Abre un diálogo para que el usuario seleccione el archivo RamDisk.
        """
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo RamDisk",
            filetypes=(("Archivos IMG4", "*.img4"), ("Todos los archivos", "*.*"))
        )
        if file_path:
            self.ramdisk_path.set(file_path)
            self.entry_ramdisk.config(state="normal")
            self.mostrar_salida(f"Archivo RamDisk seleccionado: {file_path}")
            self.entry_ramdisk.config(state="disabled")

    def mostrar_salida(self, texto, tipo="normal"):
        """
        Muestra texto en el área de resultados.

        Args:
            texto: El texto a mostrar.
            tipo: El tipo de texto ("normal", "error", "success").
        """
        self.resultado_text.config(state="normal")
        self.resultado_text.insert("end", texto + "\n", tipo)
        self.resultado_text.see("end")
        self.resultado_text.config(state="disabled")
        self.root.update() # Fuerza la actualización de la interfaz

    def mostrar_notificacion(self, mensaje, tipo="info"):
        """
        Muestra una notificación emergente.

        Args:
            mensaje: El mensaje a mostrar.
            tipo: El tipo de notificación ("info", "error", "success", "warning").
        """
        color = {"info": "#4E79A7", "error": "#E15759", "success": "#59A14F", "warning": "#EDC948"}.get(tipo, "#4E79A7")
        notif = tk.Toplevel(self.root)
        notif.overrideredirect(True)
        notif.configure(bg=color)
        notif.attributes("-topmost", True) # La notificacion se muestra sobre las demas ventanas
        tk.Label(notif, text=mensaje, bg=color, fg="white", font=("Segoe UI",10, "bold")).pack(padx=20, pady=10)
        notif.update_idletasks()
        w, h = notif.winfo_width(), notif.winfo_height()
        x = self.root.winfo_x() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_y() + 60
        notif.geometry(f"+{x}+{y}")
        notif.after(2200, notif.destroy) # La notificacion se cierra despues de 2.2 segundos

    def ejecutar_comando(self, comando, timeout=60):
        """
        Ejecuta un comando en el sistema operativo.

        Args:
            comando: El comando a ejecutar (como una cadena).
            timeout: El tiempo máximo de espera para la ejecución del comando (en segundos).

        Returns:
            El código de retorno del comando. -1 si hay un error.
        """
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
        except FileNotFoundError as e:
            self.mostrar_salida(f"Error: No se encontró el comando. Asegúrate de que esté instalado y en el PATH. Detalle: {e}", "error")
            self.mostrar_notificacion("Error: Comando no encontrado", "error")
            return -1
        except Exception as e:
            self.mostrar_salida(str(e), "error")
            self.mostrar_notificacion("Error inesperado", "error")
            return -1
        finally:
            self.progress.stop()
            self.status_label.config(text="Listo")

    def detectar_dispositivo_info(self):
        """
        Detecta el dispositivo conectado, obtiene su información y actualiza la interfaz.
        """
        self.mostrar_salida("\n[Detectando dispositivo...]")
        if platform.system() != "Linux":
            self.mostrar_salida("Error: Solo Linux", "error")
            self.mostrar_notificacion("Solo compatible con Linux", "warning")
            return

        # Primero, un chequeo rápido de la conexión
        ret = self.ejecutar_comando("lsusb -v")
        if ret != 0:
            self.mostrar_salida("Error: Dispositivo no detectado o no hay permisos.", "error")
            self.mostrar_notificacion("Dispositivo no detectado", "error")
            self.limpiar_info_dispositivo() # Limpia la info en la UI
            return

        self.mostrar_salida("Dispositivo detectado, obteniendo información...", "success")
        self.dispositivo_info = self.obtener_info_dispositivo() # Obtiene la info del dispositivo
        if self.dispositivo_info:
            self.actualizar_info_dispositivo_ui() # Actualiza la UI con la info
            self.habilitar_botones_por_version() # Habilita los botones según la versión
        else:
            self.mostrar_salida("No se pudo obtener la información del dispositivo.", "error")
            self.limpiar_info_dispositivo()

    def obtener_info_dispositivo(self):
        """
        Obtiene información del dispositivo iOS conectado usando ideviceinfo.

        Returns:
            Un diccionario con la información del dispositivo, o None si no se puede obtener.
        """
        self.mostrar_salida("\n[Obteniendo información del dispositivo...]")
        if platform.system() != "Linux":
            self.mostrar_salida("Error: Solo Linux para obtener info detallada", "error")
            self.mostrar_notificacion("Solo compatible con Linux para info detallada", "warning")
            return None

        try:
            comando = "ideviceinfo -k ProductVersion -k ProductType -k UniqueChipID -k SerialNumber"
            proceso = subprocess.run(comando, shell=True, capture_output=True, text=True, timeout=10)
            if proceso.returncode == 0:
                info = {}
                salida = proceso.stdout.strip().split('\n')
                for linea in salida:
                    if ":" in linea:
                        key, value = linea.split(":", 1)
                        info[key.strip()] = value.strip()
                self.mostrar_salida("Información del dispositivo obtenida", "success")
                return info
            else:
                self.mostrar_salida(f"Error al obtener información: {proceso.stderr.strip()}", "error")
                self.mostrar_notificacion("Error al obtener información del dispositivo", "error")
                return None
        except FileNotFoundError:
            self.mostrar_salida("Error: 'ideviceinfo' no encontrado. Asegúrate de tener instaladas las herramientas.", "error")
            self.mostrar_notificacion("Error: 'ideviceinfo' no encontrado", "error")
            return None
        except subprocess.TimeoutExpired:
            self.mostrar_salida("Timeout al obtener información del dispositivo", "error")
            self.mostrar_notificacion("Timeout al obtener información del dispositivo", "error")
            return None
        except Exception as e:
            self.mostrar_salida(f"Error inesperado al obtener información: {e}", "error")
            self.mostrar_notificacion("Error inesperado al obtener información del dispositivo", "error")
            return None

    def actualizar_info_dispositivo_ui(self):
        """
        Actualiza la interfaz de usuario con la información del dispositivo.
        """
        if self.dispositivo_info:
            self.lbl_version.config(text=f"Versión iOS: {self.dispositivo_info.get('ProductVersion', 'Desconocido')}")
            self.lbl_modelo.config(text=f"Modelo: {self.dispositivo_info.get('ProductType', 'Desconocido')}")
            self.lbl_ecid.config(text=f"ECID: {self.dispositivo_info.get('UniqueChipID', 'Desconocido')}")
            self.lbl_serial.config(text=f"Número de Serie: {self.dispositivo_info.get('SerialNumber', 'Desconocido')}")
        else:
            self.limpiar_info_dispositivo()

    def limpiar_info_dispositivo(self):
        """
        Limpia la información del dispositivo mostrada en la interfaz.
        """
        self.lbl_version.config(text=f"Versión iOS: Desconectado")
        self.lbl_modelo.config(text=f"Modelo: Desconectado")
        self.lbl_ecid.config(text=f"ECID: Desconectado")
        self.lbl_serial.config(text=f"Número de Serie: Desconectado")
        self.dispositivo_info = None

    def habilitar_botones_por_version(self):
        """
        Habilita o deshabilita los botones de acción según la versión de iOS detectada.
        """
        if self.dispositivo_info:
            version = self.dispositivo_info.get("ProductVersion", "")
            # Aquí iría la lógica para determinar qué botones habilitar según la versión
            # Por ejemplo:
            if version.startswith("14.") or version.startswith("15.") or version.startswith("16."):
                self.btn_bypass_passcode.config(state="normal")
                self.btn_bypass_hello.config(state="normal")
                self.btn_restaurar.config(state="normal")
                # También podríamos habilitar el botón de RamDisk si es relevante para esta versión
                # self.btn_ramdisk.config(state="normal")
            else:
                self.btn_bypass_passcode.config(state="disabled")
                self.btn_bypass_hello.config(state="disabled")
                self.btn_restaurar.config(state="disabled")
                # self.btn_ramdisk.config(state="disabled")
        else:
            # Si no hay dispositivo detectado, deshabilita todos los botones de acción
            self.btn_bypass_passcode.config(state="disabled")
            self.btn_bypass_hello.config(state="disabled")
            self.btn_restaurar.config(state="disabled")
            # self.btn_ramdisk.config(state="disabled")

    def cargar_ramdisk(self):
        """
        Abre un diálogo para que el usuario seleccione el archivo RamDisk.
        """
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo RamDisk",
            filetypes=(("Archivos IMG4", "*.img4"), ("Todos los archivos", "*.*"))
        )
        if file_path:
            self.ramdisk_path.set(file_path)
            self.entry_ramdisk.config(state="normal")
            self.mostrar_salida(f"Archivo RamDisk seleccionado: {file_path}")
            self.entry_ramdisk.config(state="disabled")

    def ejecutar_bypass_passcode(self):
        """
        Ejecuta el bypass del código de acceso en el dispositivo.
        """
        if not self.dispositivo_info:
            self.mostrar_salida("Error: No hay dispositivo detectado.", "error")
            self.mostrar_notificacion("Conecte un dispositivo primero", "error")
            return
        version = self.dispositivo_info.get("ProductVersion", "")
        self.mostrar_salida(f"\n[Bypass Passcode iOS {version}]")
        script_dir_version = os.path.join(SCRIPT_DIR, f"ios{version.split('.')[0]}")
        script = os.path.join(script_dir_version, "passcode_bypass.py") # Usa solo la parte principal de la versión
        if os.path.exists(script):
            threading.Thread(target=self.ejecutar_comando, args=(f"sudo python3 {script}", 120)).start()
            self.mostrar_salida("Ejecutando bypass passcode en segundo plano...")
        else:
            self.mostrar_salida(f"Script no encontrado: {script}", "error")
            self.mostrar_notificacion("Script no encontrado", "error")

    def ejecutar_bypass_hello(self):
        """
        Ejecuta el bypass de la pantalla Hello en el dispositivo.
        """
        if not self.dispositivo_info:
            self.mostrar_salida("Error: No hay dispositivo detectado.", "error")
            self.mostrar_notificacion("Conecte un dispositivo primero", "error")
            return
        version = self.dispositivo_info.get("ProductVersion", "")
        self.mostrar_salida(f"\n[Bypass Hello iOS {version}]")
        script_dir_version = os.path.join(SCRIPT_DIR, f"ios{version.split('.')[0]}")
        script = os.path.join(script_dir_version, "hello_bypass.py") # Asume un script diferente para hello
        if os.path.exists(script):
            threading.Thread(target=self.ejecutar_comando, args=(f"sudo python3 {script}", 180)).start()
            self.mostrar_salida("Ejecutando bypass hello en segundo plano...")
        else:
            self.mostrar_salida(f"Script no encontrado: {script}", "error")
            self.mostrar_notificacion("Script no encontrado", "error")

    def restaurar_dispositivo(self):
        """
        Ejecuta la restauración del dispositivo.
        """
        if not self.dispositivo_info:
            self.mostrar_salida("Error: No hay dispositivo detectado.", "error")
            self.mostrar_notificacion("Conecte un dispositivo primero", "error")
            return
        version = self.dispositivo_info.get("ProductVersion", "")
        self.mostrar_salida(f"\n[Restaurando Dispositivo iOS {version}]")
        script_dir_version = os.path.join(SCRIPT_DIR, f"ios{version.split('.')[0]}")
        script = os.path.join(script_dir_version, "restore.py") # Asume un script de restauración
        if os.path.exists(script):
            threading.Thread(target=self.ejecutar_comando, args=(f"sudo python3 {script}", 300)).start()
            self.mostrar_salida("Ejecutando restauración en segundo plano...")
        else:
            self.mostrar_salida(f"Script no encontrado: {script}", "error")
            self.mostrar_notificacion("Script no encontrado", "error")

    def ejecutar_ipwndfu(self):
        """
        Ejecuta el script para poner el dispositivo en modo IPWNDFU.
        """
        self.mostrar_salida("\n[Ejecutando IPWNDFU]")
        script = os.path.join(SCRIPT_DIR, "ipwndfu.py") # Asume un script general para ipwndfu
        if os.path.exists(script):
            threading.Thread(target=self.ejecutar_comando, args=(f"sudo python3 {script}", 120)).start()
            self.mostrar_salida("Ejecutando IPWNDFU en segundo plano...")
        else:
            self.mostrar_salida(f"Script no encontrado: {script}", "error")
            self.mostrar_notificacion("Script no encontrado", "error")

    def ejecutar_checkra1n_interfaz(self):
        """
        Función llamada al hacer clic en el botón "Ejecutar checkra1n".
        Inicia la ejecución del script checkra1n.py en un hilo separado.
        """
        threading.Thread(target=self.ejecutar_checkra1n_script_threaded).start()
        self.mostrar_salida("Iniciando checkra1n en segundo plano...")

    def ejecutar_checkra1n_script_threaded(self):
        """
        Ejecuta el script checkra1n.py en un hilo.
        """
        script_path = os.path.join(SCRIPT_DIR, "checkra1n.py")
        kernel_path = filedialog.askopenfilename(title="Seleccionar archivo del kernel/payload")
        if not kernel_path:
            self.mostrar_salida("Operación de checkra1n cancelada por el usuario.\n")
            return

        ramdisk_path = filedialog.askopenfilename(title="Seleccionar archivo del ramdisk")
        if not ramdisk_path:
            self.mostrar_salida("Operación de checkra1n cancelada por el usuario.\n")
            return

        comando = f"sudo python3 {script_path} \"{kernel_path}\" \"{ramdisk_path}\""
        self.mostrar_salida(f"Ejecutando: {comando}\n")

        try:
            proceso = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            while True:
                linea = proceso.stdout.readline()
                if not linea:
                    break
                self.mostrar_salida(linea.strip())
            stdout, stderr = proceso.communicate()
            if stderr:
                self.mostrar_salida(f"\nError de checkra1n:\n{stderr}", "error")
            else:
                self.mostrar_salida("\ncheckra1n completado (ver registro para detalles).", "success")
                self.mostrar_notificacion("checkra1n completado", "success")
        except FileNotFoundError:
            self.mostrar_salida(f"\nError: No se encontró el script en la ruta: {script_path}", "error")
            self.mostrar_notificacion("Error: Script checkra1n no encontrado", "error")
        except Exception as e:
            self.mostrar_salida(f"\nError inesperado al ejecutar checkra1n: {e}", "error")
            self.mostrar_notificacion("Error al ejecutar checkra1n", "error")
        finally:
            self.progress.stop()
            self.status_label.config(text="Listo")

    def mostrar_ayuda(self):
        """
        Muestra un cuadro de mensaje con información de ayuda.
        """
        messagebox.showinfo("Ayuda", "Esta herramienta está diseñada para realizar varias funciones en dispositivos iOS.\n\n"
                                    "- Conecte su dispositivo y haga clic en 'Detectar Dispositivo' para obtener información.\n"
                                    "- Los botones de acción se habilitarán según la versión de iOS detectada.\n"
                                    "- Asegúrese de tener instaladas las dependencias necesarias (ideviceinfo, etc.).\n\n"
                                    "Para más ayuda, consulte la documentación o póngase en contacto con el desarrollador.")

        def mostrar_ayuda(self):

            messagebox.showinfo("Ayuda", "Esta herramienta está diseñada para realizar varias funciones en dispositivos iOS.\n\n"
                                    "- Conecte su dispositivo y haga clic en 'Detectar Dispositivo' para obtener información.\n"
                                    "- Los botones de acción se habilitarán según la versión de iOS detectada.\n"
                                    "- Asegúrese de tener instaladas las dependencias necesarias (ideviceinfo, etc.).\n\n"
                                    "Para más ayuda, consulte la documentación o póngase en contacto con el desarrollador.")

if __name__ == "__main__":
    root = tk.Tk()
    app = iCosM8Tool(root)
    root.mainloop()
