import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import os, json, sys, webbrowser
from PIL import Image, ImageTk
from tkinterdnd2 import TkinterDnD, DND_FILES
import time



# ---------- Tema ----------
TEMA_CLARO = {
    "bg": (240, 240, 245),
    "fg": (0,0,0),
    "btn": (225, 229, 237),       
    "btn_fg": (20, 20, 20),       
    "scroll": (180, 180, 200),    
    "btn_hover": (217, 222, 222),
    "menu_bg": (240,240,240),
    "menu_fg": (20,20,20),
    "menu_hover": (217,217,217)

}

TEMA_OSCURO = {
    "bg": (30,30,30),
    "fg": (255,255,255),
    "btn": (50,50,50),
    "btn_fg": (255,255,255),
    "scroll": (80,80,80),
    "btn_hover": (100, 100, 100),
    "menu_bg": (30,30,30),
    "menu_fg": (255,255,255),
    "menu_hover": (100,100,100)
}


tema_actual = "claro"

def aplicar_tema_valores(tema):
    color_bg = rgb_to_hex(tema["bg"])
    color_btn = rgb_to_hex(tema["btn"])
    color_btn_fg = rgb_to_hex(tema["btn_fg"])
    color_hover = rgb_to_hex(tema["btn_hover"])
    color_scroll = rgb_to_hex(tema["scroll"])

    root.configure(bg=color_bg)
    canvas.configure(bg=color_bg, highlightthickness=0)
    grid_frame.configure(bg=color_bg)
    frame_cfg.configure(bg=color_bg)

    # Scrollbar completo
    scroll.configure(
        bg=color_scroll,
        troughcolor=color_bg,
        activebackground=color_hover,
        highlightbackground=color_bg,
        relief="flat"
    )

    # Botones del grid
    for w in grid_frame.winfo_children():
        if isinstance(w, tk.Button):
            w.configure(
                bg=color_btn,
                fg=color_btn_fg,
                activebackground=color_hover,
                activeforeground=color_btn_fg,
                bd=1,
                relief="flat",
                highlightthickness=0
            )
            aplicar_hover(w)


    # Botones inferiores (+ - añadir etc)
    for w in frame_cfg.winfo_children():
        if isinstance(w, tk.Button):
            w.configure(
                bg=color_btn,
                fg=color_btn_fg,
                activebackground=color_hover,
                activeforeground=color_btn_fg,
                bd=0,
                relief="flat",
                highlightthickness=0
            )

    # Botón pin (solo si NO está fijado)
    if not ventana_fija and "btn_pin" in globals():
        btn_pin.configure(
            bg=color_btn,
            fg=color_btn_fg,
            activebackground=color_hover
        )

    actualizar_boton_pin()

            
def aplicar_hover(w):
    w.bind("<Enter>", lambda e: w.configure(bg=rgb_to_hex(TEMA_OSCURO["btn_hover"] if config["tema"]=="oscuro" else TEMA_CLARO["btn_hover"])))
    w.bind("<Leave>", lambda e: w.configure(bg=rgb_to_hex(TEMA_OSCURO["btn"] if config["tema"]=="oscuro" else TEMA_CLARO["btn"])))

def aplicar_tema():
    tema = TEMA_OSCURO if config["tema"] == "oscuro" else TEMA_CLARO
    aplicar_tema_valores(tema)
            
def toggle_tema():
    if animando:
        return

    inicio = TEMA_OSCURO if config["tema"]=="oscuro" else TEMA_CLARO
    config["tema"] = "claro" if config["tema"]=="oscuro" else "oscuro"
    fin = TEMA_OSCURO if config["tema"]=="oscuro" else TEMA_CLARO

    guardar_config()
    animar_tema(inicio, fin)


def rgb_to_hex(c):
    return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"

def lerp(a,b,t):
    return int(a + (b-a)*t)



def animar_tema(tema_inicio, tema_fin, paso=0):
    global animando
    animando = True

    t = paso / 12
    if t > 1:
        t = 1

    tema = {}
    for k in tema_inicio:
        tema[k] = (
            lerp(tema_inicio[k][0], tema_fin[k][0], t),
            lerp(tema_inicio[k][1], tema_fin[k][1], t),
            lerp(tema_inicio[k][2], tema_fin[k][2], t)
        )

    aplicar_tema_valores(tema)

    if t < 1:
        root.after(15, lambda: animar_tema(tema_inicio, tema_fin, paso+1))
    else:
        animando = False

# ---------- COUNTDOWN ----------
def abrir_countdown():
    win = tk.Toplevel(root)
    win.title("Countdown")
    # ---------- POSICIÓN (izquierda y más arriba) ----------
    root.update_idletasks()

    x = root.winfo_x()
    y = root.winfo_y()
    ancho = 250
    alto = 180

    offset_y = 50  # ← ajusta esto si quieres más separación

    win.geometry(f"{ancho}x{alto}+{x - ancho - 10}+{y + offset_y}")

    tiempo_total = tk.IntVar(value=60)
    corriendo = {"estado": False}

    lbl = tk.Label(win, text="00:01:00", font=("Segoe UI", 24))
    lbl.pack(pady=10)

    entry = tk.Entry(win, justify="center")
    entry.insert(0, "00:01:00")
    entry.pack()

    def actualizar_label(seg):
        h = seg // 3600
        m = (seg % 3600) // 60
        s = seg % 60
        lbl.config(text=f"{h:02}:{m:02}:{s:02}")

    def tick():
        if corriendo["estado"] and tiempo_total.get() > 0:
            tiempo_total.set(tiempo_total.get() - 1)
            actualizar_label(tiempo_total.get())
            win.after(1000, tick)

        elif tiempo_total.get() <= 0:
            corriendo["estado"] = False
            lbl.config(fg="red")
            win.attributes("-topmost", True)
            
    def parse_tiempo(txt):
        try:
            partes = txt.split(":")
            partes = [int(p) for p in partes]

            if len(partes) == 3:  # hh:mm:ss
                return partes[0]*3600 + partes[1]*60 + partes[2]
            elif len(partes) == 2:  # mm:ss
                return partes[0]*60 + partes[1]
            elif len(partes) == 1:  # ss
                return partes[0]
        except:
            return 0
        return 0
    
    def play():
        tiempo = parse_tiempo(entry.get())
        if tiempo <= 0:
            return

        tiempo_total.set(tiempo)
        lbl.config(fg=rgb_to_hex((255,255,255) if config["tema"]=="oscuro" else (0,0,0)))  # 👈 reset color
        win.attributes("-topmost", False)

        corriendo["estado"] = True
        tick()

    def pause():
        corriendo["estado"] = False

    def reset():
        corriendo["estado"] = False
        tiempo_total.set(0)
        actualizar_label(0)

        lbl.config(fg=rgb_to_hex((255,255,255) if config["tema"]=="oscuro" else (0,0,0)))  # 👈 color normal
        win.attributes("-topmost", False)

    frame = tk.Frame(win)
    frame.pack(pady=10)

    tk.Button(frame, text="▶", command=play).pack(side="left", padx=5)
    tk.Button(frame, text="⏸", command=pause).pack(side="left", padx=5)
    tk.Button(frame, text="⟲", command=reset).pack(side="left", padx=5)

    aplicar_tema_ventana(win)

# ---------- NOTAS ----------

def abrir_notas():
    global ventana_notas

    if ventana_notas is not None and ventana_notas.winfo_exists():
        ventana_notas.deiconify()
        ventana_notas.lift()
        ventana_notas.focus_force()
        return
    
    ventana_notas = tk.Toplevel(root)
    win = ventana_notas

    # ---------- POSICIÓN ----------
    root.update_idletasks()
    x = root.winfo_x()
    y = root.winfo_y()
    ancho = 300
    alto = root.winfo_height()
    win.geometry(f"{ancho}x{alto}+{x - ancho - 10}+{y}")

    # ---------- TOOLBAR ----------
    toolbar = tk.Frame(win)
    toolbar.pack(fill="x", side="top")

    # ---------- TEXT ----------
    text = tk.Text(win, wrap="word")
    text.pack(fill="both", expand=True)

    # ---------- ESTILOS ----------
    text.tag_configure("bold", font=("Segoe UI", 10, "bold"))
    text.tag_configure("italic", font=("Segoe UI", 10, "italic"))
    text.tag_configure("underline", font=("Segoe UI", 10, "underline"))

    # ---------- CARGAR ----------
    notas_data = config.get("notas", {})
    contenido = notas_data.get("texto", "")
    formatos = notas_data.get("formatos", [])

    text.insert("1.0", contenido)

    # Restaurar formatos
    for f in formatos:
        try:
            text.tag_add(f["tag"], f["start"], f["end"])
        except:
            pass

    # ---------- GUARDAR ----------
    def guardar():
        contenido = text.get("1.0", "end-1c")

        formatos = []
        for tag in ["bold", "italic", "underline"]:
            ranges = text.tag_ranges(tag)
            for i in range(0, len(ranges), 2):
                formatos.append({
                    "tag": tag,
                    "start": str(ranges[i]),
                    "end": str(ranges[i+1])
                })

        config["notas"] = {
            "texto": contenido,
            "formatos": formatos
        }

        guardar_config()

    def guardar_delay(event=None):
        if hasattr(guardar_delay, "job"):
            win.after_cancel(guardar_delay.job)
        guardar_delay.job = win.after(500, guardar)

    text.bind("<KeyRelease>", guardar_delay)

    def al_cerrar():
        global ventana_notas
        guardar()
        ventana_notas.destroy()
        ventana_notas = None
        
    win.protocol("WM_DELETE_WINDOW", al_cerrar)
    # ---------- FUNCIONES ----------
    def toggle_tag(tag):
        try:
            start = text.index("sel.first")
            end = text.index("sel.last")
        except:
            return

        if tag in text.tag_names("sel.first"):
            text.tag_remove(tag, start, end)
        else:
            text.tag_add(tag, start, end)

        guardar_delay()
        
    def insertar_bullet():
        # Inserta bullet real alineado
        line_start = text.index("insert linestart")
        text.insert(line_start, "• ")

    def toggle_lista():
        # Añade o quita bullet en líneas seleccionadas
        try:
            start = text.index("sel.first linestart")
            end = text.index("sel.last lineend")
        except:
            start = text.index("insert linestart")
            end = text.index("insert lineend")

        line = start
        while text.compare(line, "<=", end):
            contenido = text.get(line, f"{line} lineend")

            if contenido.startswith("• "):
                text.delete(line, f"{line}+2c")
            else:
                text.insert(line, "• ")

            line = text.index(f"{line}+1line")
        guardar_delay()
        
    # ---------- BOTONES ----------
    tk.Button(toolbar, text="•", width=3, command=toggle_lista).pack(side="left", padx=2, pady=2)

    tk.Button(toolbar, text="B", width=3,
              font=("Segoe UI", 10, "bold"),
              command=lambda: toggle_tag("bold")).pack(side="left", padx=2)

    tk.Button(toolbar, text="I", width=3,
              font=("Segoe UI", 10, "italic"),
              command=lambda: toggle_tag("italic")).pack(side="left", padx=2)

    tk.Button(toolbar, text="U", width=3,
              font=("Segoe UI", 10, "underline"),
              command=lambda: toggle_tag("underline")).pack(side="left", padx=2)

    aplicar_tema_ventana(win)
# ---------- TEMA PARA VENTANAS SECUNDARIAS ----------
def aplicar_tema_ventana(win):
    tema = TEMA_OSCURO if config.get("tema") == "oscuro" else TEMA_CLARO

    bg = rgb_to_hex(tema["bg"])
    fg = rgb_to_hex(tema["fg"])

    win.configure(bg=bg)

    for w in win.winfo_children():
        try:
            w.configure(bg=bg, fg=fg)
        except:
            pass
# ---------- Función PIN ----------
def actualizar_boton_pin():
    tema = config.get("tema", "claro")
    
    if ventana_fija:
        fg_color = (227, 140, 35)   # dorado si está fijo
        text = "📌"
        
    else:
        fg_color = TEMA_OSCURO["btn_fg"] if tema == "oscuro" else TEMA_CLARO["btn_fg"]
        text = "📌"
        

    btn_pin.configure(
        text=text,
        fg=rgb_to_hex(fg_color)
        
    )
def toggle_on_top():
    global ventana_fija
    ventana_fija = not ventana_fija

    root.attributes("-topmost", ventana_fija)
    actualizar_boton_pin()



# ---------- Función para rutas de recursos ----------
def resource_path(relative_path):
    """Devuelve la ruta absoluta del recurso, funciona dentro del exe o script"""
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def emoji_image(emoji, size=32):
    from PIL import ImageDraw, ImageFont

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("seguiemj.ttf", int(size * 0.8))
    except:
        font = ImageFont.load_default()

    w, h = draw.textbbox((0, 0), emoji, font=font)[2:]
    draw.text(
        ((size - w) // 2, (size - h) // 2),
        emoji,
        font=font,
        fill=(255, 255, 255, 255)
    )

    return ImageTk.PhotoImage(img)

# ---------- Configuración ----------
ICON_PATH = resource_path("icon.png")
DEFAULT_ICON = resource_path("icon_default.png")
# Guardar siempre junto al exe/script
CONFIG_FILE = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), "config.json")

BTN_W = 120
BTN_H = 60
ICON_SIZE = 64
BTN_PAD = 8

image_cache = {}  # cache de imágenes Pillow
escala_btn = 1.0  # factor de escala
ventana_notas: tk.Toplevel | None = None

# ---------- Sistema ----------
def abrir_ruta(ruta):
    """Abre carpeta o URL según el tipo"""
    if not ruta:
        return
    if ruta.startswith(("http://", "https://")):
        webbrowser.open(ruta)
    elif os.path.exists(ruta):
        try:
            os.startfile(ruta)  # abre cualquier ruta mapeada correctamente
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la ruta:\n{ruta}\n{e}")
    else:
        messagebox.showerror("Error", f"La ruta no existe:\n{ruta}")

def cargar_config():
    base = {"botones": [], "columnas": 2, "tema": "claro"}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data.get("botones"), dict):
                nuevos = [{"nombre": k, "ruta": v, "icono": ""} for k, v in data["botones"].items()]
                data["botones"] = nuevos
            if "columnas" not in data:
                data["columnas"] = 2
            if "tema" not in data:
                data["tema"] = "claro"
            return data
        except:
            return base
    return base

def guardar_config():
    # Guardar tamaño del canvas
    config["canvas_width"] = canvas.winfo_width()
    config["canvas_height"] = canvas.winfo_height()

    limpio = {
        "columnas": config["columnas"],
        "tema": config.get("tema", "claro"),
        "botones": [],
        "canvas_width": config.get("canvas_width", 400),
        "canvas_height": config.get("canvas_height", 300),
        "escala_btn": config.get("escala_btn", 1.0),
        "notas": config.get("notas", {})
    }
    for b in config["botones"]:
        limpio["botones"].append({
            "nombre": b["nombre"],
            "ruta": b["ruta"],
            "icono": b.get("icono", "")
        })
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(limpio, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar config.json:\n{e}")


# ---------- Ventana principal ----------
root = TkinterDnD.Tk()
root.title("Flash Menu")
root.resizable(True, True)

# Icono de la ventana
icon = ImageTk.PhotoImage(file=ICON_PATH)
root.iconphoto(True, icon)

# ---------- FUENTE ----------
import tkinter.font as tkfont

FONT_BTN = tkfont.Font(family="Segoe UI", size=13)
FONT_BTN_accesos = tkfont.Font(family="Segoe UI", size=10)
FONT_BTN2 = tkfont.Font(family="Segoe UI", size=10)
FONT_MENU = tkfont.Font(family="Segoe UI", size=10)
FONT_MENU_TITLE = tkfont.Font(family="Segoe UI", size=11)

# ---------- Ajustar ventana ----------
def ajustar_ventana():
    cols = config["columnas"]
    ancho = int(cols * (BTN_W * escala_btn + BTN_PAD*2) + 3)
    alto = root.winfo_height()
    if alto < 200:
        alto = 200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    MARGIN = 10
    OFFSET_Y = 75
    x = screen_width - ancho - MARGIN
    y = screen_height - alto - MARGIN - OFFSET_Y
    root.geometry(f"{ancho}x{alto}+{x}+{y}")
    
# ---------- Drag & Drop desde el Explorador de Windows ----------
def recibir_drop(event):
    rutas = root.tk.splitlist(event.data)

    for ruta in rutas:
        ruta = ruta.replace("{", "").replace("}", "")
        ruta = os.path.normpath(ruta)

        if not os.path.isdir(ruta):
            continue

        nombre_sugerido = os.path.basename(ruta)
        nombre = simpledialog.askstring("Nuevo botón", "Nombre del botón:", initialvalue=nombre_sugerido)
        if not nombre:
            continue

        # Evitar duplicados
        ya = any(b["ruta"] == ruta for b in config["botones"])
        if ya:
            messagebox.showinfo("Ya existe", "Ese acceso ya existe.")
            continue
        
        ruta = os.path.normpath(ruta)
        config["botones"].append({
            "nombre": nombre,
            "ruta": ruta,
            "icono": ""
        })

    guardar_config()
    refrescar_botones()


# Registrar la ventana como zona de drop
root.drop_target_register(DND_FILES)
root.dnd_bind("<<Drop>>", recibir_drop)

# ---------- Funciones de botón ----------
def editar_boton(idx):
    b = config["botones"][idx]
    nombre = simpledialog.askstring("Editar nombre", "Nombre del botón:", initialvalue=b["nombre"])
    if not nombre:
        return

    tipo = messagebox.askyesno("Tipo de ruta", "¿Es una carpeta local?\nSí: carpeta, No: URL WEB")
    if tipo:
        initial_dir = b["ruta"] if os.path.exists(b["ruta"]) else os.path.expanduser("~")
        ruta = filedialog.askdirectory(title="Editar carpeta", initialdir=initial_dir) or b["ruta"]
    else:
        ruta = simpledialog.askstring("Editar URL", "URL:", initialvalue=b["ruta"]) or b["ruta"]

    icono = filedialog.askopenfilename(
        title="Editar icono (opcional)",
        filetypes=[("Imágenes", "*.png *.jpg *.ico")]
    ) or b.get("icono", "")
    ruta = os.path.normpath(ruta)
    b.update({"nombre": nombre, "ruta": ruta, "icono": icono})
    guardar_config()
    refrescar_botones()

def borrar_boton(idx):
    b = config["botones"][idx]
    if messagebox.askyesno("Confirmar", f"¿Borrar {b['nombre']}?"):
        config["botones"].pop(idx)
        guardar_config()
        refrescar_botones()

# ---------- UI grid ----------
# Lista global para guardar widgets de botones
botones_widgets = []

def refrescar_botones():
    global botones_widgets
    columnas = config["columnas"]
    tema = TEMA_OSCURO if config.get("tema") == "oscuro" else TEMA_CLARO

    # Asegurar que la lista de widgets tenga la misma longitud que config["botones"]
    while len(botones_widgets) < len(config["botones"]):
        btn = tk.Button(grid_frame, compound="top", bd=0, highlightthickness=0)
        
        # Hover efecto
        def on_enter(e, btn=btn):
            btn.configure(bg=rgb_to_hex(tema.get("btn_hover", tema["btn"])))
        def on_leave(e, btn=btn):
            btn.configure(bg=rgb_to_hex(tema["btn"]))
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        # Drag & drop
        idx = len(botones_widgets)
        btn.bind("<Button-1>", lambda e, idx=idx: iniciar_drag(idx))
        btn.bind("<B1-Motion>", mover_drag)
        btn.bind("<ButtonRelease-1>", soltar_drag)

        # Menú contextual
        def mostrar_menu(event, idx=idx):
            menu = tk.Menu(root, tearoff=0)
            menu.add_command(label="Editar", command=lambda idx=idx: editar_boton(idx))
            menu.add_command(label="Borrar", command=lambda idx=idx: borrar_boton(idx))
            menu.tk_popup(event.x_root, event.y_root)
        btn.bind("<Button-3>", mostrar_menu)

        btn.grid(row=0, column=0)  # posición inicial temporal
        botones_widgets.append(btn)

    # Si hay más widgets que botones, ocultarlos
    for i in range(len(botones_widgets)):
        if i >= len(config["botones"]):
            botones_widgets[i].grid_forget()
        else:
            b = config["botones"][i]

            # Imagen
            # Imagen o emoji
            img = None
            texto = b["nombre"]

            if b.get("icono") and os.path.exists(b["icono"]):
                ruta_icono = b["icono"]

            elif os.path.exists(DEFAULT_ICON):
                ruta_icono = DEFAULT_ICON

            else:
                ruta_icono = None


            if ruta_icono:
                if ruta_icono in image_cache:
                    img = image_cache[ruta_icono]
                else:
                    pil_img = Image.open(ruta_icono)
                    new_size = (
                        max(1, int(pil_img.width * escala_btn)),
                        max(1, int(pil_img.height * escala_btn))
                    )
                    resized = pil_img.resize(new_size, Image.Resampling.LANCZOS)
                    img = ImageTk.PhotoImage(resized)
                    image_cache[ruta_icono] = img
            else:
                img = emoji_image("📂", size=32)
                image_cache[i] = img
                texto = b["nombre"]

            # Configurar botón
            btn = botones_widgets[i]
            btn.configure(
                text=texto,
                image=img,
                compound="top" if img else "center",
                width=int(BTN_W * escala_btn),
                height=int(BTN_H * escala_btn * 1.5),
                wraplength=int(100 * escala_btn),
                bg=rgb_to_hex(tema["btn"]),
                fg=rgb_to_hex(tema["btn_fg"]),
                font=FONT_BTN_accesos
            )

            btn.config(command=lambda r=b["ruta"]: abrir_ruta(r))

            # Reubicar en grid
            fila = i // columnas
            col = i % columnas
            btn.grid(row=fila, column=col, padx=3, pady=3)

    grid_frame.update_idletasks()

    # Ajuste automático para que los botones no queden detrás del frame inferior
    canvas.configure(scrollregion=(
        0,  # x0
        0,  # y0
        grid_frame.winfo_width(),  # x1
        grid_frame.winfo_height() + frame_cfg.winfo_height() + 15  # y1, margen extra abajo
    ))

    ajustar_ventana()

    
    
# ---------- SCROLL ----------

def habilitar_scroll_mouse(canvas):
    # Scroll con rueda del ratón
    def on_mousewheel(event):
        # Windows / MacOS
        canvas.yview_scroll(-1 * int(event.delta / 120), "units")
    
    # Linux (event.delta no existe)
    def on_mousewheel_linux(event):
        if event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")

    # Al entrar con el ratón, bind a la rueda
    def on_enter(event):
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Button-4>", on_mousewheel_linux)
        canvas.bind_all("<Button-5>", on_mousewheel_linux)

    # Al salir, desbindear
    def on_leave(event):
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")

    canvas.bind("<Enter>", on_enter)
    canvas.bind("<Leave>", on_leave)


# ---------- Añadir / Columnas / Escala ----------
def añadir_boton():
    nombre = simpledialog.askstring("Nombre", "Nombre del botón:")
    if not nombre:
        return
    tipo = messagebox.askyesno("Tipo de ruta", "¿Es una carpeta local?\nSí: carpeta, No: URL")
    if tipo:
        initial_dir = os.path.expanduser("~")
        ruta = filedialog.askdirectory(title="Carpeta", initialdir=initial_dir)
        if not ruta:
            return
        
        ruta = os.path.normpath(ruta)

    else:
        ruta = simpledialog.askstring("URL", "URL:")
        if not ruta:
            return
    icono = filedialog.askopenfilename(
        title="Icono (opcional)",
        filetypes=[("Imágenes", "*.png *.jpg *.ico")]
    )
    config["botones"].append({"nombre": nombre, "ruta": ruta, "icono": icono})
    guardar_config()
    refrescar_botones()

def cambiar_columnas():
    n = simpledialog.askinteger("Columnas", "Número de columnas:", minvalue=1, maxvalue=8)
    if n:
        config["columnas"] = n
        guardar_config()
        refrescar_botones()
        ajustar_ventana()

def aumentar_escala():
    global escala_btn
    if escala_btn < 2.0:
        escala_btn += 0.1
        config["escala_btn"] = escala_btn
        guardar_config()
        refrescar_botones()

def disminuir_escala():
    global escala_btn
    if escala_btn > 0.5:
        escala_btn -= 0.1
        config["escala_btn"] = escala_btn
        guardar_config()
        refrescar_botones()


# ---------- Drag & Drop ----------
# ---------- Drag & Drop ----------
drag_index = None

def iniciar_drag(idx):
    """Inicia el arrastre de un botón"""
    global drag_index
    drag_index = idx

def mover_drag(event):
    """Mueve el botón arrastrado y actualiza la posición en la lista"""
    global drag_index
    if drag_index is None:
        return

    # Posición relativa al grid
    x = canvas.winfo_pointerx() - grid_frame.winfo_rootx()
    y = canvas.winfo_pointery() - grid_frame.winfo_rooty()

    # Calcular fila y columna donde caerá
    col = int(x // (BTN_W * escala_btn + BTN_PAD*2))
    fila = int(y // (BTN_H * escala_btn + BTN_PAD*2))

    destino = max(0, min(len(config["botones"])-1, fila * config["columnas"] + col))

    # Limitar destino dentro de los índices válidos
    if 0 <= destino < len(config["botones"]) and destino != drag_index:
        # Intercambiar posiciones
        config["botones"][drag_index], config["botones"][destino] = \
            config["botones"][destino], config["botones"][drag_index]
        drag_index = destino
        refrescar_botones()

def soltar_drag(event):
    """Guarda la configuración al soltar el botón"""
    global drag_index
    drag_index = None
    guardar_config()


# ---------- Inicialización ----------
config = cargar_config()
escala_btn = config.get("escala_btn", 1.0)
animando = False
ventana_fija = False
canvas = tk.Canvas(root)
scroll = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scroll.set)

# Recuperar tamaño guardado en config
canvas_width = config.get("canvas_width", 400)
canvas_height = config.get("canvas_height", 300)
canvas.config(width=canvas_width, height=canvas_height)

scroll.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

habilitar_scroll_mouse(canvas)


def guardar_tamano_canvas(event):
    config["canvas_width"] = event.width
    config["canvas_height"] = event.height
    
    if hasattr(guardar_tamano_canvas, "job"):
        root.after_cancel(guardar_tamano_canvas.job)

    guardar_tamano_canvas.job = root.after(400, guardar_config)
canvas.bind("<Configure>", guardar_tamano_canvas)

# Frame dentro del canvas
grid_frame = tk.Frame(canvas)
canvas.create_window((0,0), window=grid_frame, anchor="nw")

# BOTONES de control alineados abajo a la derecha
frame_cfg = tk.Frame(root)
frame_cfg.place(relx=1, rely=1, anchor="se", x=-25, y=-10)


# Botón desplegable “☰” a la derecha
def mostrar_menu(event):
    tema = TEMA_OSCURO if config.get("tema") == "oscuro" else TEMA_CLARO

    menu = tk.Menu(
        root,
        tearoff=0,
        bg=rgb_to_hex(tema["menu_bg"]),
        fg=rgb_to_hex(tema["menu_fg"]),
        activebackground=rgb_to_hex(tema["menu_hover"]),
        activeforeground=rgb_to_hex(tema["menu_fg"]),
        bd=0,
        font=FONT_MENU,

    )
    menu.configure(borderwidth=0)
    
    menu.add_command(label="📝 Notas", command= abrir_notas)
    menu.add_command(label="⏱ Temporizador", command=abrir_countdown)    
    menu.add_command(label="⧉ Color Picker", command=lambda: os.startfile(
        os.path.join(
            os.path.dirname(sys.executable),
            "apps",
            "Color_picker.exe"
        )
    ))
    menu.add_command(label="+ Añadir botón", command= añadir_boton)
    menu.add_command(label="🏛 Columnas", command=cambiar_columnas)

    menu.tk_popup(event.x_root, event.y_root)

btn_pin = tk.Button(
    frame_cfg,
    text="📌",
    width=3,
    font=FONT_BTN,
    command=toggle_on_top
)
btn_pin.pack(side="right", padx=3)


btn_menu = tk.Button(frame_cfg, text="⋮", width=3, font=FONT_BTN,)
btn_menu.pack(side="right", padx=3)
btn_menu.bind("<Button-1>", mostrar_menu)

# Botones normales
tk.Button(frame_cfg, text="-🔍", width=3, font=FONT_BTN, command=disminuir_escala).pack(side="right", padx=3)
tk.Button(frame_cfg, text="+🔍", width=3, font=FONT_BTN, command=aumentar_escala).pack(side="right", padx=3)
tk.Button(frame_cfg, text="◑", width=3, font=FONT_BTN, command=toggle_tema).pack(side="right", padx=3)

# btn_timer = tk.Button(frame_cfg, text="⏱", width=3, font=FONT_BTN, command=abrir_countdown)
# btn_timer.pack(side="right", padx=3)

# btn_notas = tk.Button(frame_cfg, text="📝", width=3, font=FONT_BTN, command=abrir_notas)
# btn_notas.pack(side="right", padx=3)

# Botón Info
icon_info_tk = ImageTk.PhotoImage(Image.open(ICON_PATH).resize((20,20), Image.Resampling.LANCZOS))
btn_info = tk.Button(frame_cfg, image=icon_info_tk, width=30, height=30, command=lambda: mostrar_info())
btn_info.image = icon_info_tk  # evitar que se elimine la imagen
btn_info.pack(side="right", padx=3)

# Función del popup (puede ir en cualquier parte arriba)
def mostrar_info():
    popup = tk.Toplevel(root)
    popup.title("Información")
    popup.geometry("600x350+1500+700")
    info_text = r"""
       ___ _           _                             
      / __\ | __ _ ___| |__   /\/\   ___ _ __  _   _ 
     / _\ | |/ _` / __| '_ \ /    \ / _ \ '_ \| | | |
    / /   | | (_| \__ \ | | / /\/\ \  __/ | | | |_| |
    \/    |_|\__,_|___/_| |_\/    \/\___|_| |_|\__,_|

    Flash Menu v2.0
    Desarrollado por Álvaro_A
    © 2026

    • Drag & Drop desde el explorador para crear accesos.
    • Drag & Drop para ordenar botones.
    • Botón derecho para editar o eliminar.
    • Botón ⋮ > Añadir: Crear manualmente accesos a carpetas y web.
    • Botón ⋮ > Columnas:  Cambiar el número de columnas.
    • Botón 📌 fija el menu siempre al frente.
    • Botón ◑ Modo claro/oscuro.
    • Botones +🔍 y -🔍 ajustan el tamaño de los botones.
    • Iconos para personalizar accesos en la carpeta Icons.
    • Toda la info se guarda automáticamente en un archivo de configuración.

    """

    label_info = tk.Label(
        popup,
        text=info_text,
        font=("Consolas", 9),
        justify="left",
        anchor="nw"
    )
    label_info.pack(fill="both", expand=True, padx=15, pady=15)




# Refrescar botones inicial
refrescar_botones()
aplicar_tema()
root.mainloop()

