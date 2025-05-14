import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import os
import platform
import subprocess
import threading
import time
import requests
import json

# Paleta de colores mejorada
COLORS = {
    "primary": "#3498db",
    "secondary": "#2ecc71",
    "danger": "#e74c3c",
    "warning": "#f39c12",
    "dark": "#34495e",
    "light": "#ecf0f1",
    "text": "#2c3e50",
    "highlight": "#bdc3c7",
    "ramdisk": "#9b59b6",
    "button_text_light": "#ffffff",
    "button_text_dark": "#ffffff",
    "terminal_bg": "#000000",
    "terminal_fg": "#a9b7c6"  # Color similar al de IntelliJ IDEA
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
        label = tk.Label(tw, text=self.text, background="#FFFFE0", relief="solid", borderwidth=1, font=("Segoe UI", 9))
        label.pack(ipadx=4)

    def hide(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
# Fin de la clase Tooltip
# ==========================================================================

class iCosM8ToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("iCosM8 TOOL v3.1")
        self.root.geometry("1200x800")  # Aumentar el ancho para el nuevo panel
        self.config = {}
        self.load_config()
        self.theme = self.config.get("theme", "light")
        self.icon_images = {}
        self.ramdisk_path = tk.StringVar(value=self.config.get("ramdisk_path", ""))
        self.device_model = tk.StringVar(value="Desconocido")
        self.device_ecid = tk.StringVar(value="Desconocido")
        self.device_imei = tk.StringVar(value="Desconocido")
        self.device_ios = tk.StringVar(value="Desconocido")
        self.serial_number = tk.StringVar(value="Desconocido")
        self.username = tk.StringVar(value="Invitado") # Ejemplo de usuario
        self.credits = tk.IntVar(value=0) # Ejemplo de créditos
        self.device_processes = tk.StringVar(value="Ninguno") # Ejemplo de procesos
        self.log_window = None
        self.resultado_text = None
        self.setup_styles()
        self.create_widgets()
        self.apply_theme()
        self.load_icons()
        self.check_dependencies()
        self.registro_mensaje = None # Inicializa self.registro_mensaje
        self.open_log_window_on_start() # Abrir la ventana de registro al inicio
    # Fin del método __init__
    # ==========================================================================

    def load_config(self):
        """Carga la configuración desde un archivo JSON."""
        config_path = "config.json"
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                try:
                    self.config = json.load(f)
                except json.JSONDecodeError:
                    self.config = {}
        else:
            self.config = {}
    # Fin del método load_config
    # ==========================================================================

    def save_config(self):
        """Guarda la configuración en un archivo JSON."""
        self.config["theme"] = self.theme
        self.config["ramdisk_path"] = self.ramdisk_path.get()
        config_path = "config.json"
        with open(config_path, "w") as f:
            json.dump(self.config, f)
    # Fin del método save_config
    # ==========================================================================

    def apply_theme(self):
        """Aplica el tema actual (modo oscuro o modo claro)."""
        bg_color = COLORS["dark"] if self.theme == "dark" else COLORS["light"]
        fg_color = COLORS["light"] if self.theme == "dark" else COLORS["text"]
        header_bg = COLORS["dark"] if self.theme == "dark" else COLORS["light"]
        header_fg = COLORS["light"] if self.theme == "dark" else COLORS["text"]
        text_area_bg = COLORS["dark"] if self.theme == "dark" else COLORS["light"]
        text_area_fg = COLORS["light"] if self.theme == "dark" else COLORS["text"]
        labelframe_bg = COLORS["dark"] if self.theme == "dark" else COLORS["light"]
        labelframe_fg = COLORS["light"] if self.theme == "dark" else COLORS["text"]
        button_fg = COLORS["button_text_dark"] if self.theme == "dark" else COLORS["button_text_light"]

        self.root.configure(bg=bg_color)
        self.style.configure("TLabel", background=bg_color, foreground=fg_color)
        self.style.configure("TEntry", background=bg_color, foreground=fg_color, insertcolor=fg_color)
        self.style.configure("TLabelframe", background=labelframe_bg, foreground=labelframe_fg)
        self.style.configure("TLabelframe.Label", background=labelframe_bg, foreground=labelframe_fg)

        # Configure button text color based on theme
        self.style.configure("Primary.TButton", foreground=COLORS["button_text_light"])
        self.style.configure("Secondary.TButton", foreground=COLORS["button_text_light"])
        self.style.configure("Danger.TButton", foreground=COLORS["button_text_light"])
        self.style.configure("Warning.TButton", background=COLORS["warning"], foreground=COLORS["text"] if self.theme == "light" else COLORS["button_text_dark"])

        # Configure the header label using style
        header_style_name = "Header.TLabel"
        self.style.configure(header_style_name, background=header_bg, foreground=header_fg, font=("Segoe UI", 18, "bold"))
        if hasattr(self, 'header_label'):
            self.header_label.config(style=header_style_name)

        if hasattr(self, 'theme_btn'):
            self.theme_btn.config(text="☀️" if self.theme == "dark" else "🌙")

        # Update user info panel colors using style
        user_panel_style_name = "UserPanel.TLabel"
        self.style.configure(user_panel_style_name, background=bg_color, foreground=fg_color)
        if hasattr(self, 'user_info_frame'):
            for label_key, label_widget in self.user_info_labels.items():
                label_widget.config(style=user_panel_style_name)

    # Fin del método apply_theme
    # ==========================================================================

    def toggle_theme(self):
        """Alterna entre el modo oscuro y el modo claro."""
        self.theme = "dark" if self.theme == "light" else "light"
        self.apply_theme()
        self.save_config()
    # Fin del método toggle_theme
    # ==========================================================================

    def setup_styles(self):
        """Configura los estilos para los widgets."""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=10, font=("Segoe UI", 10, "bold"))
        self.style.configure("Primary.TButton", background=COLORS["primary"], foreground=COLORS["button_text_light"])
        self.style.configure("Secondary.TButton", background=COLORS["secondary"], foreground=COLORS["button_text_light"])
        self.style.configure("Danger.TButton", background=COLORS["danger"], foreground=COLORS["button_text_light"])
        self.style.configure("Warning.TButton", background=COLORS["warning"], foreground=COLORS["text"])
        self.style.configure("TLabel", background=COLORS["light"], foreground=COLORS["text"])
        self.style.configure("TEntry", background=COLORS["light"], foreground=COLORS["text"], insertcolor=COLORS["text"])
        self.style.configure("TEntry.Valid", foreground=COLORS["secondary"])
        self.style.configure("TEntry.Invalid", foreground=COLORS["danger"])
        self.style.configure("TLabelframe", background=COLORS["light"], foreground=COLORS["text"])
        self.style.configure("TLabelframe.Label", background=COLORS["light"], foreground=COLORS["text"])
        self.style.configure("UserPanel.TLabel", background=COLORS["light"], foreground=COLORS["text"]) # Estilo para el panel de usuario
        self.style.configure("RegisterPanel.TLabel", background=COLORS["light"], foreground=COLORS["text"]) # Estilo para el panel de registro
        self.style.configure("RegisterPanel.TEntry", background=COLORS["light"], foreground=COLORS["text"], insertcolor=COLORS["text"]) # Estilo para los inputs de registro
        self.style.configure("RegisterPanel.TButton", background=self.style.lookup("TButton", 'background'), foreground=COLORS["text"]) # Estilo para el botón de registro
        self.style.map("Primary.TButton", background=[("active", COLORS["highlight"])])
        self.style.map("Secondary.TButton", background=[("active", COLORS["highlight"])])
        self.style.map("Danger.TButton", background=[("active", COLORS["highlight"])])
        self.style.map("Warning.TButton", background=[("active", COLORS["highlight"])])
    # Fin del método setup_styles
    # ==========================================================================

    def create_widgets(self):
        """Crea y organiza los widgets en la interfaz gráfica."""
        # Panel de usuario (lado izquierdo)
        self.user_panel = tk.Frame(self.root, width=250)
        self.user_panel.pack(side="left", fill="y", padx=10, pady=10)

        # Sección de inicio de sesión
        login_frame = ttk.LabelFrame(self.user_panel, text="Inicio de Sesión")
        login_frame.pack(fill="x", pady=10)

        ttk.Label(login_frame, text="Usuario:", style="RegisterPanel.TLabel").pack(padx=5, pady=2, anchor="w")
        self.login_username_entry = ttk.Entry(login_frame, style="RegisterPanel.TEntry")
        self.login_username_entry.pack(padx=5, pady=2, fill="x")

        ttk.Label(login_frame, text="Contraseña:", style="RegisterPanel.TLabel").pack(padx=5, pady=2, anchor="w")
        self.login_password_entry = ttk.Entry(login_frame, show="*", style="RegisterPanel.TEntry")
        self.login_password_entry.pack(padx=5, pady=2, fill="x")

        login_button = ttk.Button(login_frame, text="Iniciar Sesión", command=self.iniciar_sesion, style="Primary.TButton")
        login_button.pack(padx=5, pady=5, fill="x")

        # Botón para abrir la ventana de registro
        register_button = ttk.Button(login_frame, text="Registrarse", command=self.open_register_window, style="Secondary.TButton")
        register_button.pack(padx=5, pady=5, fill="x")

        # Separador
        ttk.Separator(self.user_panel).pack(fill="x", pady=5)

        # Sección de información del usuario
        self.user_info_frame = ttk.Frame(self.user_panel)
        self.user_info_frame.pack(fill="x")

        ttk.Label(self.user_info_frame, text="Información del Usuario", font=("Segoe UI", 12, "bold"), style="UserPanel.TLabel").pack(pady=5)
        self.user_info_labels = {
            "username": ttk.Label(self.user_info_frame, text=f"Usuario: {self.username.get()}", style="UserPanel.TLabel"),
            "credits": ttk.Label(self.user_info_frame, text=f"Créditos: {self.credits.get()}", style="UserPanel.TLabel"),
            "devices": ttk.Label(self.user_info_frame, text="Dispositivos:", style="UserPanel.TLabel"),
            "processes": ttk.Label(self.user_info_frame, text=f"Procesos: {self.device_processes.get()}", style="UserPanel.TLabel"),
            "credits_loaded": ttk.Label(self.user_info_frame, text="Créditos Cargados:", style="UserPanel.TLabel")
        }
        for label_key, label_widget in self.user_info_labels.items():
            label_widget.pack(anchor="w", padx=10, pady=2)

        # Espacio entre el panel de usuario y el área principal
        separator_main = ttk.Separator(self.root, orient="vertical")
        separator_main.pack(side="left", fill="y", padx=5)

        # Contenedor principal con pestañas (lado derecho)
        main_frame = ttk.Frame(self.root)
        main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Header con modo oscuro
        header = ttk.Frame(main_frame)
        header.pack(fill="x", pady=10)
        self.header_label = ttk.Label(header, text="iCosM8 TOOL v3.1", style="Header.TLabel")
        self.header_label.pack(side="left", padx=15)
        self.theme_btn = ttk.Button(header, text="☀️" if self.theme == "dark" else "🌙", command=self.toggle_theme)
        self.theme_btn.pack(side="right", padx=15)
        Tooltip(self.theme_btn, "Alternar tema oscuro/claro")

        # Pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, pady=10)

        # Pestaña de información del dispositivo
        self.device_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.device_tab, text="Información del Dispositivo")
        self.create_device_info_tab(self.device_tab)

        # Pestaña de herramientas
        self.tools_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.tools_tab, text="Herramientas")
        self.create_tools_tab(self.tools_tab)

        # Nueva pestaña para Jailbreaks
        self.jailbreak_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.jailbreak_tab, text="Jailbreaks")
        self.create_jailbreak_tab(self.jailbreak_tab)

    # Fin del método create_widgets
    # ==========================================================================

    def open_log_window_on_start(self):
        """Abre la ventana emergente para el registro de actividad al inicio."""
        self.log_window = tk.Toplevel(self.root)
        self.log_window.title("Cosm3No1de-Dev")
        self.log_window.geometry("600x200") # Tamaño inicial de la ventana
        self.log_window.configure(bg=COLORS["terminal_bg"])
        self.resultado_text = ScrolledText(self.log_window, height=10, wrap="word",
                                           bg=COLORS["terminal_bg"],
                                           fg=COLORS["terminal_fg"],
                                           insertbackground=COLORS["terminal_fg"],
                                           font=("Consolas", 10)) # Fuente estilo terminal
        self.resultado_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.resultado_text.config(state=tk.DISABLED)
        # Redirigir la función log a esta área de texto
        self._original_log = self.log
        self.log = self._log_to_window

    def _log_to_window(self, message, level="info"):
        """Muestra un mensaje en la ventana de registro de actividad."""
        if self.resultado_text:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            formatted_message = f"[{timestamp}] [{level.upper()}]: {message}\n"
            self.resultado_text.config(state=tk.NORMAL)
            if level == "error":
                self.resultado_text.insert(tk.END, formatted_message, "error")
                self.resultado_text.tag_config("error", foreground=COLORS["danger"])
            elif level == "warning":
                self.resultado_text.insert(tk.END, formatted_message, "warning")
                self.resultado_text.tag_config("warning", foreground=COLORS["warning"])
            elif level == "success":
                self.resultado_text.insert(tk.END, formatted_message, "success")
                self.resultado_text.tag_config("success", foreground=COLORS["secondary"])
            else:
                self.resultado_text.insert(tk.END, formatted_message)
            self.resultado_text.see(tk.END)
            self.resultado_text.config(state=tk.DISABLED)
        else:
            print(f"[LOG WINDOW NOT INITIALIZED]: {message}")

    def create_jailbreak_tab(self, parent):
        """Crea la pestaña de Jailbreaks."""
        # Frame para checkra1n
        checkra1n_frame = ttk.LabelFrame(parent, text="checkra1n")
        checkra1n_frame.pack(fill="x", padx=10, pady=10)
        self.create_checkra1n_section(checkra1n_frame)

        # Frame para palera1n
        palera1n_frame = ttk.LabelFrame(parent, text="palera1n")
        palera1n_frame.pack(fill="x", padx=10, pady=10)
        self.create_palera1n_section(palera1n_frame)

    def create_checkra1n_section(self, parent):
        """Crea la sección de checkra1n."""
        description = "checkra1n es un jailbreak semi-tethered basado en la vulnerabilidad checkm8, compatible con muchos dispositivos iOS desde iPhone 5s hasta iPhone X."
        img_path = "icons/checkra1n.png"
        try:
            img = Image.open(img_path).resize((100, 100))
            img_tk = ImageTk.PhotoImage(img)
            self._checkra1n_img_label = ttk.Label(parent, image=img_tk)
            self._checkra1n_img_label.image = img_tk # Keep a reference!
            self._checkra1n_img_label.pack(side="left", padx=10, pady=10)
        except FileNotFoundError:
            self.log(f"Imagen no encontrada: {img_path}", "warning")
            ttk.Label(parent, text="Imagen de checkra1n no encontrada").pack(side="left", padx=10, pady=10)

        desc_label = ttk.Label(parent, text=description, wraplength=400, justify="left")
        desc_label.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        run_button = ttk.Button(parent, text="Ejecutar checkra1n", command=self.run_checkra1n, style="Secondary.TButton")
        run_button.pack(side="bottom", padx=10, pady=10, fill="x")
        Tooltip(run_button, "Ejecuta la herramienta checkra1n (requiere tenerla instalada).")

    def create_palera1n_section(self, parent):
        """Crea la sección de palera1n."""
        description = "palera1n es un jailbreak semi-tethered basado en checkm8 y otros exploits, compatible con dispositivos A9-A11 en iOS 15 y superior."
        img_path = "icons/palera1n.png"
        try:
            img = Image.open(img_path).resize((100, 100))
            img_tk = ImageTk.PhotoImage(img)
            self._palera1n_img_label = ttk.Label(parent, image=img_tk)
            self._palera1n_img_label.image = img_tk # Keep a reference!
            self._palera1n_img_label.pack(side="left", padx=10, pady=10)
        except FileNotFoundError:
            self.log(f"Imagen no encontrada: {img_path}", "warning")
            ttk.Label(parent, text="Imagen de palera1n no encontrada").pack(side="left", padx=10, pady=10)

        desc_label = ttk.Label(parent, text=description, wraplength=400, justify="left")
        desc_label.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        run_button = ttk.Button(parent, text="Ejecutar palera1n", command=self.run_palera1n, style="Secondary.TButton")
        run_button.pack(side="bottom", padx=10, pady=10, fill="x")
        Tooltip(run_button, "Ejecuta la herramienta palera1n (requiere tenerla instalada).")

    def run_checkra1n(self):
        """Intenta ejecutar checkra1n."""
        self.log("Intentando ejecutar checkra1n...", "info")
        threading.Thread(target=self._run_checkra1n_thread).start()
        self._update_user_processes("Ejecutando checkra1n...")

    def _run_checkra1n_thread(self):
        """Ejecuta checkra1n en un hilo."""
        try:
            # Asegúrate de que 'checkra1n' esté en el PATH o proporciona la ruta completa
            process = subprocess.Popen(["sudo", "checkra1n", "-c"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.root.after(0, self.log, f"[checkra1n]: {output.strip()}")
            stderr_output = process.stderr.read()
            if stderr_output:
                self.root.after(0, self.log, f"[checkra1n Error]: {stderr_output.strip()}", "error")
            returncode = process.wait()
            if returncode == 0:
                self.root.after(0, self.log, "checkra1n finalizado.", "success")
            else:
                self.root.after(0, self.log, f"checkra1n finalizado con código: {returncode}", "warning")
        except FileNotFoundError:
            self.root.after(0, self.log, "Error: 'checkra1n' no se encontró. Asegúrese de que esté instalado y en el PATH.", "error")
        except Exception as e:
            self.root.after(0, self.log, f"Error al ejecutar checkra1n: {e}", "error")
        finally:
            self.root.after(0, self._update_user_processes, "Idle")

    def run_palera1n(self):
        """Intenta ejecutar palera1n."""
        self.log("Intentando ejecutar palera1n...", "info")
        threading.Thread(target=self._run_palera1n_thread).start()
        self._update_user_processes("Ejecutando palera1n...")

    def _run_palera1n_thread(self):
        """Ejecuta palera1n en un hilo."""
        try:
            # Asegúrate de que 'palera1n' esté en el PATH o proporciona la ruta completa
            process = subprocess.Popen(["sudo", "palera1n", "--tweaks"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.root.after(0, self.log, f"[palera1n]: {output.strip()}")
            stderr_output = process.stderr.read()
            if stderr_output:
                self.root.after(0, self.log, f"[palera1n Error]: {stderr_output.strip()}", "error")
            returncode = process.wait()
            if returncode == 0:
                self.root.after(0, self.log, "palera1n finalizado.", "success")
            else:
                self.root.after(0, self.log, f"palera1n finalizado con código: {returncode}", "warning")
        except FileNotFoundError:
            self.root.after(0, self.log, "Error: 'palera1n' no se encontró. Asegúrese de que esté instalado y en el PATH.", "error")
        except Exception as e:
            self.root.after(0, self.log, f"Error al ejecutar palera1n: {e}", "error")
        finally:
            self.root.after(0, self._update_user_processes, "Idle")

    def open_register_window(self):
        """Abre una nueva ventana para el registro de usuario."""
        self.register_window = tk.Toplevel(self.root)
        self.register_window.title("Registro de Usuario")
        register_frame = ttk.Frame(self.register_window)
        register_frame.pack(padx=10, pady=10)
        self.create_register_tools_panel(register_frame)

    def iniciar_sesion(self):
        """Simula el proceso de inicio de sesión."""
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()
        # Aquí iría la lógica real para verificar las credenciales
        self.log(f"Intentando iniciar sesión con usuario: {username}", "info")
        # Simulación de inicio de sesión exitoso
        if username and password:
            self.username.set(username)
            self.credits.set(10)  # Ejemplo de asignación de créditos
            self.user_info_labels["username"].config(text=f"Usuario: {username}")
            self.user_info_labels["credits"].config(text=f"Créditos: {self.credits.get()}")
            self.log("Inicio de sesión exitoso.", "success")
        else:
            self.log("Nombre de usuario o contraseña incorrectos.", "error")

    def create_register_tools_panel(self, parent):
        """Crea los widgets para el panel de registro de usuario."""
        ttk.Label(parent, text="Nombre de Usuario:", style="RegisterPanel.TLabel").pack(padx=5, pady=2, anchor="w")
        self.username_entry = ttk.Entry(parent, style="RegisterPanel.TEntry")
        self.username_entry.pack(padx=5, pady=2, fill="x")

        ttk.Label(parent, text="Contraseña:", style="RegisterPanel.TLabel").pack(padx=5, pady=2, anchor="w")
        self.password_entry = ttk.Entry(parent, show="*", style="RegisterPanel.TEntry")
        self.password_entry.pack(padx=5, pady=2, fill="x")

        ttk.Label(parent, text="Confirmar Contraseña:", style="RegisterPanel.TLabel").pack(padx=5, pady=2, anchor="w")
        self.confirm_password_entry = ttk.Entry(parent, show="*", style="RegisterPanel.TEntry")
        self.confirm_password_entry.pack(padx=5, pady=2, fill="x")

        register_button = ttk.Button(parent, text="Registrarse", command=self.registrar_usuario, style="Primary.TButton")
        register_button.pack(padx=5, pady=5, fill="x")

        self.registro_mensaje = ttk.Label(parent, text="", style="RegisterPanel.TLabel")
        self.registro_mensaje.pack(padx=5, pady=2)

    def create_device_info_tab(self, parent):
        """Crea la pestaña de información del dispositivo."""
        info_frame = ttk.LabelFrame(parent, text="Detalles del Dispositivo")
        info_frame.pack(fill="x", padx=10, pady=10)
        self.create_device_info_fields(info_frame)

        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(pady=10)
        self.detect_device_btn = ttk.Button(buttons_frame, text="Detectar Dispositivo", command=self.detect_device_info, style="Primary.TButton")
        self.detect_device_btn.pack(pady=5)
        Tooltip(self.detect_device_btn, "Intenta detectar un dispositivo iOS conectado.")

    def create_device_info_fields(self, parent):
        """Crea los campos de información del dispositivo."""
        info_fields = [
            ("Modelo:", self.device_model),
            ("ECID:", self.device_ecid),
            ("IMEI:", self.device_imei),
            ("iOS:", self.device_ios),
            ("Serial:", self.serial_number),
        ]
        for i, (label, var) in enumerate(info_fields):
            ttk.Label(parent, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ttk.Entry(parent, textvariable=var, width=30, state="readonly")
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
    # Fin del método create_device_info_tab
    # ==========================================================================

    def create_tools_tab(self, parent):
        """Crea la pestaña de herramientas."""
        # Botón iPwndfu en la parte superior
        self.ipwndfu_btn = ttk.Button(parent, text="Entrar en iPwndfu", command=self.enter_ipwndfu, style="Primary.TButton")
        self.ipwndfu_btn.pack(pady=10, fill="x", padx=10)
        Tooltip(self.ipwndfu_btn, "Intenta poner el dispositivo en modo iPwndfu.")

        # Separador
        ttk.Separator(parent).pack(fill="x", pady=5, padx=10)

        # Sección Ramdisk
        ramdisk_frame = ttk.LabelFrame(parent, text="Herramientas Ramdisk")
        ramdisk_frame.pack(fill="x", padx=10, pady=10)
        self.create_ramdisk_tools(ramdisk_frame)

        # Sección Bypass
        bypass_frame = ttk.LabelFrame(parent, text="Herramientas Bypass")
        bypass_frame.pack(fill="x", padx=10, pady=10)
        self.create_bypass_tools(bypass_frame)

        # Sección Restauración
        restore_frame = ttk.LabelFrame(parent, text="Herramientas de Restauración")
        restore_frame.pack(fill="x", padx=10, pady=10)
        self.create_restore_tools(restore_frame)
    # Fin del método create_tools_tab
    # ==========================================================================

    def enter_ipwndfu(self):
        """Intenta poner el dispositivo en modo iPwndfu."""
        self.log("Intentando entrar en modo iPwndfu...", "info")
        threading.Thread(target=self._enter_ipwndfu_thread).start()
        self._update_user_processes("Entrando en iPwndfu...")

    def _enter_ipwndfu_thread(self):
        """Ejecuta el proceso de entrar en iPwndfu en un hilo."""
        # Aquí iría la lógica real para ejecutar el comando iPwndfu
        self.log("Simulando proceso de iPwndfu...", "warning")
        time.sleep(5)  # Simulación
        self.log("Simulación de iPwndfu completada.", "success")
        self._update_user_processes("Idle")

    def registrar_usuario(self):
        """Realiza el proceso de registro del usuario."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not username or not password or not confirm_password:
            self.registro_mensaje.config(text="Por favor, complete todos los campos.", foreground=COLORS["danger"])
            return
        if password != confirm_password:
            self.registro_mensaje.config(text="Las contraseñas no coinciden.", foreground=COLORS["danger"])
            return

        backend_url = "http://localhost:5000/register"  # Ajusta la URL de tu backend
        data = {"username": username, "password": password}

        try:
            response = requests.post(backend_url, json=data)
            response.raise_for_status()
            response_data = response.json()
            if response_data.get("success"):
                self.registro_mensaje.config(text="Registro exitoso.", foreground=COLORS["secondary"])
                self.log(f"Usuario '{username}' registrado exitosamente.", "success")
                if hasattr(self, 'register_window'):
                    self.register_window.destroy() # Cerrar la ventana de registro tras éxito
                self.username.set(username) # Actualizar el nombre de usuario en el panel principal
                self.user_info_labels["username"].config(text=f"Usuario: {username}")
            else:
                error_message = response_data.get("error", "Error desconocido durante el registro.")
                self.registro_mensaje.config(text=f"Error al registrar: {error_message}", foreground=COLORS["danger"])
                self.log(f"Error al registrar usuario '{username}': {error_message}", "error")
        except requests.exceptions.ConnectionError:
            self.registro_mensaje.config(text="No se pudo conectar al servidor de registro.", foreground=COLORS["danger"])
            self.log("Error: No se pudo conectar al servidor de registro.", "error")
        except requests.exceptions.RequestException as e:
            self.registro_mensaje.config(text=f"Error de conexión o respuesta del servidor: {e}", foreground=COLORS["danger"])
            self.log(f"Error de conexión o respuesta del servidor: {e}", "error")
        except json.JSONDecodeError:
            self.registro_mensaje.config(text="Error al decodificar la respuesta del servidor.", foreground=COLORS["danger"])
            self.log("Error: Error al decodificar la respuesta JSON del servidor.", "error")
        except Exception as e:
            self.registro_mensaje.config(text=f"Error inesperado: {e}", foreground=COLORS["danger"])
            self.log(f"Error inesperado durante el registro: {e}", "error")
    # Fin del método registrar_usuario
    # ==========================================================================

    def create_ramdisk_tools(self, parent):
        """Crea las herramientas relacionadas con Ramdisk."""
        frame = ttk.Frame(parent)
        frame.pack(pady=5)

        ttk.Label(frame, text="Ruta del Ramdisk:").pack(side="left", padx=5)
        self.ramdisk_entry = ttk.Entry(frame, textvariable=self.ramdisk_path, width=60)
        self.ramdisk_entry.pack(side="left", padx=5, fill="x", expand=True)
        Tooltip(self.ramdisk_entry, "Ruta al archivo .dmg del Ramdisk.")

        browse_btn = ttk.Button(frame, text="...", command=self.browse_ramdisk, width=5)
        browse_btn.pack(side="left", padx=5)
        Tooltip(browse_btn, "Seleccionar archivo Ramdisk.")

        self.boot_ramdisk_btn = ttk.Button(parent, text="Bootear Ramdisk", command=self.boot_ramdisk, style="Secondary.TButton", state="disabled")
        self.boot_ramdisk_btn.pack(pady=5, fill="x", padx=10)
        Tooltip(self.boot_ramdisk_btn, "Intenta bootear el dispositivo con el Ramdisk seleccionado.")
    # Fin del método create_ramdisk_tools
    # ==========================================================================

    def create_bypass_tools(self, parent):
        """Crea las herramientas de bypass."""
        self.hello_bypass_btn = ttk.Button(parent, text="Bypass Hello", command=self.bypass_hello, style="Primary.TButton", state="disabled")
        self.hello_bypass_btn.pack(pady=5, fill="x", padx=10)
        Tooltip(self.hello_bypass_btn, "Intenta realizar el bypass de la pantalla Hello.")

        self.passcode_bypass_btn = ttk.Button(parent, text="Bypass Passcode (Tethered)", command=self.bypass_passcode, style="Primary.TButton", state="disabled")
        self.passcode_bypass_btn.pack(pady=5, fill="x", padx=10)
        Tooltip(self.passcode_bypass_btn, "Intenta realizar el bypass del passcode (requiere tethered boot).")
    # Fin del método create_bypass_tools
    # ==========================================================================

    def create_restore_tools(self, parent):
        """Crea las herramientas de restauración."""
        self.restore_btn = ttk.Button(parent, text="Restaurar Dispositivo (futurerestore)", command=self.restore_device, style="Danger.TButton", state="disabled")
        self.restore_btn.pack(pady=5, fill="x", padx=10)
        Tooltip(self.restore_btn, "Intenta restaurar el dispositivo usando futurerestore.")
    # Fin del método create_restore_tools
    # ==========================================================================

    def load_icons(self):
        """Carga los iconos para los botones."""
        try:
            self.detect_icon = ImageTk.PhotoImage(Image.open("icons/detect.png").resize((20, 20)))
            self.ramdisk_icon = ImageTk.PhotoImage(Image.open("icons/ramdisk.png").resize((20, 20)))
            self.bypass_icon = ImageTk.PhotoImage(Image.open("icons/bypass.png").resize((20, 20)))
            self.restore_icon = ImageTk.PhotoImage(Image.open("icons/restore.png").resize((20, 20)))
            if hasattr(self, 'detect_device_btn'):
                self.detect_device_btn.config(image=self.detect_icon, compound="left")
            if hasattr(self, 'boot_ramdisk_btn'):
                self.boot_ramdisk_btn.config(image=self.ramdisk_icon, compound="left")
            if hasattr(self, 'hello_bypass_btn'):
                self.hello_bypass_btn.config(image=self.bypass_icon, compound="left")
            if hasattr(self, 'passcode_bypass_btn'):
                self.passcode_bypass_btn.config(image=self.bypass_icon, compound="left")
            if hasattr(self, 'restore_btn'):
                self.restore_btn.config(image=self.restore_icon, compound="left")
            if hasattr(self, 'ipwndfu_btn'):
                # Puedes cargar un icono específico para iPwndfu si lo tienes
                pass
            # Cargar iconos para checkra1n y palera1n
            self.checkra1n_icon = ImageTk.PhotoImage(Image.open("icons/checkra1n.png").resize((80, 80))) if os.path.exists("icons/checkra1n.png") else None
            self.palera1n_icon = ImageTk.PhotoImage(Image.open("icons/palera1n.png").resize((80, 80))) if os.path.exists("icons/palera1n.png") else None
            if hasattr(self, '_checkra1n_img_label') and self.checkra1n_icon:
                self._checkra1n_img_label.config(image=self.checkra1n_icon)
                self._checkra1n_img_label.image = self.checkra1n_icon # Keep reference
            if hasattr(self, '_palera1n_img_label') and self.palera1n_icon:
                self._palera1n_img_label.config(image=self.palera1n_icon)
                self._palera1n_img_label.image = self.palera1n_icon # Keep reference
        except FileNotFoundError as e:
            self.log(f"Error al cargar iconos: {e}", "error")
    # Fin del método load_icons
    # ==========================================================================

    def log(self, message, level="info"):
        """Muestra un mensaje en el área de resultados (ventana emergente)."""
        if self.resultado_text:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            formatted_message = f"[{timestamp}] [{level.upper()}]: {message}\n"
            self.resultado_text.config(state=tk.NORMAL)
            if level == "error":
                self.resultado_text.insert(tk.END, formatted_message, "error")
                self.resultado_text.tag_config("error", foreground=COLORS["danger"])
            elif level == "warning":
                self.resultado_text.insert(tk.END, formatted_message, "warning")
                self.resultado_text.tag_config("warning", foreground=COLORS["warning"])
            elif level == "success":
                self.resultado_text.insert(tk.END, formatted_message, "success")
                self.resultado_text.tag_config("success", foreground=COLORS["secondary"])
            else:
                self.resultado_text.insert(tk.END, formatted_message)
            self.resultado_text.see(tk.END)
            self.resultado_text.config(state=tk.DISABLED)
        else:
            print(f"[LOG WINDOW NOT INITIALIZED]: {message}")

    def check_dependencies(self):
        """Verifica si las dependencias necesarias están instaladas."""
        dependencies = ["ideviceinfo", "futurerestore", "irecovery", "checkra1n", "palera1n"]
        missing = []
        for dep in dependencies:
            if not self.is_tool_installed(dep):
                missing.append(dep)
        if missing:
            self.log(f"Advertencia: Faltan las siguientes dependencias: {', '.join(missing)}", "warning")
            messagebox.showwarning("Advertencia", f"Faltan las siguientes dependencias:\n{', '.join(missing)}\nAlgunas funcionalidades podrían no funcionar correctamente.")
        else:
            self.log("Todas las dependencias necesarias parecen estar instaladas.", "success")
    # Fin del método check_dependencies
    # ==========================================================================

    def is_tool_installed(self, name):
        """Verifica si una herramienta está instalada en el sistema."""
        try:
            subprocess.run([name, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except FileNotFoundError:
            return False
    # Fin del método is_tool_installed
    # ==========================================================================

    def detect_device_info(self):
        """Detecta la información del dispositivo conectado."""
        self.log("Detectando información del dispositivo...")
        threading.Thread(target=self._detect_device_info_thread).start()

    def _detect_device_info_thread(self):
        """Ejecuta la detección de información del dispositivo en un hilo."""
        try:
            info = subprocess.check_output(["ideviceinfo"], text=True, timeout=10)
            device_data = {}
            for line in info.strip().split('\n'):
                if "=" in line:
                    key, value = line.split("=", 1)
                    device_data[key.strip()] = value.strip()

            self.root.after(0, self._update_device_info_ui, device_data)
        except subprocess.TimeoutExpired:
            self.root.after(0, self.log, "Error: Tiempo de espera agotado al obtener la información del dispositivo.", "error")
        except FileNotFoundError:
            self.root.after(0, self.log, "Error: 'ideviceinfo' no se encontró. Asegúrese de que esté instalado.", "error")
        except subprocess.CalledProcessError as e:
            self.root.after(0, self.log, f"Error al ejecutar 'ideviceinfo': {e}", "error")
        except Exception as e:
            self.root.after(0, self.log, f"Ocurrió un error inesperado: {e}", "error")

    def _update_device_info_ui(self, info):
        """Actualiza la interfaz de usuario con la información del dispositivo."""
        self.device_model.set(info.get("ProductType", "Desconocido"))
        self.device_ecid.set(info.get("UniqueChipID", "Desconocido"))
        self.device_imei.set(info.get("InternationalMobileEquipmentIdentity", "Desconocido"))
        self.device_ios.set(info.get("ProductVersion", "Desconocido"))
        self.serial_number.set(info.get("SerialNumber", "Desconocido"))
        self.log("Información del dispositivo detectada.", "success")
        self._update_user_device_info(info.get("ProductType", ""))
        self.enable_relevant_buttons(info.get("ProductType", ""))
    # Fin del método detect_device_info
    # ==========================================================================

    def _update_user_device_info(self, device_model):
        """Actualiza la información del dispositivo en el panel de usuario."""
        if hasattr(self, 'user_info_labels'):
            self.user_info_labels["devices"].config(text=f"Dispositivo: {device_model}")

    def enable_relevant_buttons(self, model):
        """Habilita los botones relevantes según el modelo del dispositivo (ejemplo)."""
        if "iPhone" in model or "iPad" in model:
            self.boot_ramdisk_btn.config(state=tk.NORMAL)
            self.hello_bypass_btn.config(state=tk.NORMAL)
            self.passcode_bypass_btn.config(state=tk.NORMAL)
            self.restore_btn.config(state=tk.NORMAL)
        else:
            self.log("Modelo de dispositivo no reconocido. Algunas funciones podrían estar deshabilitadas.", "warning")
            self.boot_ramdisk_btn.config(state=tk.DISABLED)
            self.hello_bypass_btn.config(state=tk.DISABLED)
            self.passcode_bypass_btn.config(state=tk.DISABLED)
            self.restore_btn.config(state=tk.DISABLED)
    # Fin del método enable_relevant_buttons
    # ==========================================================================

    def browse_ramdisk(self):
        """Abre un diálogo para seleccionar el archivo Ramdisk."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Ramdisk",
            filetypes=(("Archivos DMG", "*.dmg"), ("Todos los archivos", "*.*"))
        )
        if file_path:
            self.ramdisk_path.set(file_path)
            self.config["ramdisk_path"] = file_path
            self.save_config()
            self.log(f"Ruta del Ramdisk seleccionada: {file_path}")
    # Fin del método browse_ramdisk
    # ==========================================================================

    def boot_ramdisk(self):
        """Intenta bootear el dispositivo con el Ramdisk seleccionado."""
        ramdisk_file = self.ramdisk_path.get()
        if not ramdisk_file:
            self.log("Error: No se ha seleccionado ningún archivo Ramdisk.", "error")
            messagebox.showerror("Error", "Por favor, selecciona un archivo Ramdisk.")
            return
        if not os.path.exists(ramdisk_file):
            self.log(f"Error: El archivo Ramdisk no se encuentra en la ruta: {ramdisk_file}", "error")
            messagebox.showerror("Error", f"El archivo Ramdisk no se encuentra en la ruta:\n{ramdisk_file}")
            return
        self.log(f"Intentando bootear Ramdisk desde: {ramdisk_file}")
        threading.Thread(target=self._boot_ramdisk_thread, args=(ramdisk_file,)).start()

    def _boot_ramdisk_thread(self, ramdisk_file):
        """Ejecuta el proceso de bootear Ramdisk en un hilo."""
        # Aquí iría la lógica real para bootear el Ramdisk usando herramientas como irecovery, etc.
        self.log("Simulando proceso de boot de Ramdisk...", "warning")
        self._update_user_processes("Booting Ramdisk...")
        time.sleep(5)  # Simulación
        self.log("Simulación de boot de Ramdisk completada.", "success")
        self._update_user_processes("Idle")
    # Fin del método boot_ramdisk
    # ==========================================================================

    def bypass_hello(self):
        """Intenta realizar el bypassde la pantalla Hello."""
        self.log("Intentando bypass de la pantalla Hello...")
        threading.Thread(target=self._bypass_hello_thread).start()
        self._update_user_processes("Bypassing Hello...")

    def _bypass_hello_thread(self):
        """Ejecuta el proceso de bypass Hello en un hilo."""
        # Aquí iría la lógica real para el bypass Hello
        self.log("Simulando bypass de la pantalla Hello...", "warning")
        time.sleep(5)  # Simulación
        self.log("Simulación de bypass Hello completada.", "success")
        self._update_user_processes("Idle")
    # Fin del método bypass_hello
    # ==========================================================================

    def bypass_passcode(self):
        """Intenta realizar el bypass del passcode."""
        self.log("Intentando bypass del passcode (tethered)...")
        threading.Thread(target=self._bypass_passcode_thread).start()
        self._update_user_processes("Bypassing Passcode...")

    def _bypass_passcode_thread(self):
        """Ejecuta el proceso de bypass del passcode en un hilo."""
        # Aquí iría la lógica real para el bypass del passcode
        self.log("Simulando bypass del passcode (tethered)...", "warning")
        time.sleep(5)  # Simulación
        self.log("Simulación de bypass del passcode completada.", "success")
        self._update_user_processes("Idle")
    # Fin del método bypass_passcode
    # ==========================================================================

    def restore_device(self):
        """Intenta restaurar el dispositivo usando futurerestore."""
        self.log("Intentando restaurar el dispositivo usando futurerestore...")
        threading.Thread(target=self._restore_device_thread).start()
        self._update_user_processes("Restoring Device...")

    def _restore_device_thread(self):
        """Ejecuta el proceso de restauración en un hilo."""
        # Aquí iría la lógica real para la restauración con futurerestore
        self.log("Simulando proceso de restauración...", "warning")
        time.sleep(10)  # Simulación
        self.log("Simulación de restauración completada.", "success")
        self._update_user_processes("Idle")
    # Fin del método restore_device
    # ==========================================================================

    def _update_user_processes(self, process_info):
        """Actualiza la información de los procesos en el panel de usuario."""
        if hasattr(self, 'user_info_labels'):
            self.user_info_labels["processes"].config(text=f"Procesos: {process_info}")

# Fin de la clase iCosM8ToolGUI
# ==========================================================================

if __name__ == "__main__":
    if platform.system() != "Linux":
        messagebox.showerror("Error", "Esta herramienta está optimizada para Linux.")
        exit()
    root = tk.Tk()
    app = iCosM8ToolGUI(root)
    root.mainloop()
