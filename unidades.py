import flet as ft
import mysql.connector

def conectar_db():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Santiago16_",
            database="farmaciasguadalajara"
        )
        return db
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        return None

db = conectar_db()
cursor = db.cursor()

cursor.execute("SHOW COLUMNS FROM articulos LIKE '%unidad%'")
columna_unidad = cursor.fetchone()
COLUMNA_UNIDADES = columna_unidad[0] if columna_unidad else "idUnidades"

def crear_unidad(id_unidad, nombre):
    try:
        cursor.execute("INSERT INTO unidades (idUnidades, nombreUnidad) VALUES (%s, %s)", (id_unidad, nombre))
        db.commit()
        return cursor.lastrowid
    except mysql.connector.Error as err:
        print(f"Error al crear unidad: {err}")
        db.rollback()
        return None

def existe_id(id_unidad):
    cursor.execute("SELECT COUNT(*) FROM unidades WHERE idUnidades=%s", (id_unidad,))
    return cursor.fetchone()[0] > 0

def obtener_unidades():
    try:
        cursor.execute(f"""
            SELECT u.idUnidades, u.nombreUnidad, COUNT(a.idArticulos) as en_uso 
            FROM unidades u
            LEFT JOIN articulos a ON u.idUnidades = a.{COLUMNA_UNIDADES}
            GROUP BY u.idUnidades
            ORDER BY u.nombreUnidad
        """)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error al obtener unidades: {err}")
        return []

def actualizar_unidad(id_unidad, nombre):
    try:
        cursor.execute(
            "UPDATE unidades SET nombreUnidad=%s WHERE idUnidades=%s",
            (nombre, id_unidad)
        )
        db.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error al actualizar unidad: {err}")
        db.rollback()
        return False

def eliminar_unidad(id_unidad):
    try:
        cursor.execute(f"SELECT COUNT(*) FROM articulos WHERE {COLUMNA_UNIDADES}=%s", (id_unidad,))
        if cursor.fetchone()[0] > 0:
            return False, "Unidad en uso por artículos"
        
        cursor.execute("DELETE FROM unidades WHERE idUnidades=%s", (id_unidad,))
        db.commit()
        return True, "Unidad eliminada"
    except mysql.connector.Error as err:
        print(f"Error al eliminar unidad: {err}")
        db.rollback()
        return False, f"Error: {err}"

def main(page: ft.Page):
    page.title = "Gestión de Unidades"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F5F1E9"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    id_input = ft.TextField(
        label="ID",
        width=100,
        input_filter=ft.NumbersOnlyInputFilter(),
        error_text=None,
    )
    nombre_input = ft.TextField(label="Nombre", width=300)
    
    unidades_list = ft.ListView(expand=True, spacing=10)
    
    mensaje = ft.SnackBar(
        ft.Text(), 
        bgcolor=ft.Colors.RED_400,
        duration=2000
    )
    page.snack_bar = mensaje

    editando = False

    def mostrar_mensaje(texto, error=True):
        mensaje.content.value = texto
        mensaje.bgcolor = ft.Colors.RED_400 if error else ft.Colors.GREEN_400
        mensaje.open = True
        page.update()

    def limpiar_formulario(e=None):
        nonlocal editando
        id_input.value = ""
        id_input.error_text = None
        id_input.read_only = False
        nombre_input.value = ""
        editando = False
        boton_guardar.disabled = True
        boton_crear.disabled = True
        page.update()

    def validar_id_y_activar_botones(e=None):
        nonlocal editando
        valor = id_input.value.strip()
        if valor == "" or not valor.isdigit() or int(valor) <= 0:
            id_input.error_text = "Ingrese un número entero positivo"
            boton_crear.disabled = True
            boton_guardar.disabled = True
            page.update()
            return
        numero = int(valor)
        if editando:
            id_input.error_text = None
            # En edición, solo activamos Guardar si hay texto en nombre
            boton_guardar.disabled = nombre_input.value.strip() == ""
            boton_crear.disabled = True
        else:
            if existe_id(numero):
                id_input.error_text = "ID ya existente, usa otro."
                boton_crear.disabled = True
                boton_guardar.disabled = True
            else:
                id_input.error_text = None
                boton_crear.disabled = nombre_input.value.strip() == ""
                boton_guardar.disabled = True
        page.update()

    def validar_nombre_y_activar_botones(e=None):
        nonlocal editando
        nombre_val = nombre_input.value.strip()
        if editando:
            boton_guardar.disabled = nombre_val == ""
        else:
            boton_crear.disabled = nombre_val == "" or id_input.error_text is not None
        page.update()

    def cargar_unidades():
        unidades_list.controls.clear()
        for unidad in obtener_unidades():
            id_u, nombre, en_uso = unidad
            
            unidades_list.controls.append(
                ft.Card(
                    ft.Container(
                        ft.Column([
                            ft.Text(nombre, weight="bold"),
                            ft.Text(f"ID: {id_u} | Artículos: {en_uso}", size=12),
                            ft.Row([
                                ft.IconButton(
                                    ft.Icons.EDIT,
                                    on_click=lambda e, id=id_u: cargar_para_editar(id),
                                    tooltip="Editar"
                                ),
                                ft.IconButton(
                                    ft.Icons.DELETE,
                                    on_click=lambda e, id=id_u: eliminar_unidad_click(id),
                                    tooltip="Eliminar",
                                    disabled=en_uso > 0
                                )
                            ], alignment=ft.MainAxisAlignment.END)
                        ], spacing=5),
                        padding=15,
                        width=400
                    ),
                    color=ft.Colors.BLUE_50
                )
            )
        page.update()

    def cargar_para_editar(id_unidad):
        nonlocal editando
        cursor.execute("SELECT * FROM unidades WHERE idUnidades=%s", (id_unidad,))
        unidad = cursor.fetchone()
        if unidad:
            id_input.value = str(unidad[0])
            id_input.error_text = None
            id_input.read_only = True  # bloquear ID en edición
            nombre_input.value = unidad[1]
            editando = True
            boton_guardar.disabled = False
            boton_crear.disabled = True
            page.update()

    def guardar_unidad(e):
        nonlocal editando
        if not nombre_input.value.strip():
            mostrar_mensaje("Nombre es requerido")
            return
        
        if not id_input.value.strip() or not id_input.value.isdigit() or int(id_input.value) <= 0:
            id_input.error_text = "Ingrese un ID válido"
            page.update()
            return
        
        id_num = int(id_input.value)
        
        if editando:
            if actualizar_unidad(id_num, nombre_input.value):
                mostrar_mensaje("Unidad actualizada", False)
                id_input.read_only = False
                limpiar_formulario()
                cargar_unidades()
        else:
            if existe_id(id_num):
                id_input.error_text = "ID ya existente, usa otro."
                page.update()
                return
            if crear_unidad(id_num, nombre_input.value):
                mostrar_mensaje("Unidad creada", False)
                limpiar_formulario()
                cargar_unidades()

    def eliminar_unidad_click(id_unidad):
        success, msg = eliminar_unidad(id_unidad)
        mostrar_mensaje(msg, not success)
        if success:
            limpiar_formulario()
            cargar_unidades()

    id_input.on_change = validar_id_y_activar_botones
    nombre_input.on_change = validar_nombre_y_activar_botones

    boton_crear = ft.ElevatedButton("Crear", on_click=guardar_unidad, bgcolor="#795548", color="white", width=150, height=40, disabled=True)
    boton_guardar = ft.ElevatedButton("Guardar", on_click=guardar_unidad, bgcolor="#2196F3", color="white", width=150, height=40, disabled=True)

    form = ft.Row(
        controls=[
            id_input,
            nombre_input,
            boton_crear,
            boton_guardar
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
    )

    page.add(
        ft.Column([
            ft.Text("Gestión de Unidades", size=24, weight="bold", color="#795548"),
            ft.Divider(),
            form,
            ft.Divider(),
            ft.Text("Listado de Unidades", size=18, color="#0066CC"),
            ft.Container(
                content=unidades_list,
                height=400,
                border=ft.border.all(1, "#E0E0E0"),
                padding=10,
                bgcolor="#F5F5F5",
                border_radius=10,
                clip_behavior=ft.ClipBehavior.HARD_EDGE
            )
        ], spacing=15)
    )

    cargar_unidades()

ft.app(target=main)
