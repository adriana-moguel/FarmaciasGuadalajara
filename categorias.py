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

# Funciones CRUD para Categorias
def crear_categoria(id_categoria, nombre):
    try:
        cursor.execute("INSERT INTO categorias (idCategorias, nombre) VALUES (%s, %s)", (id_categoria, nombre))
        db.commit()
        return cursor.lastrowid
    except mysql.connector.Error as err:
        print(f"Error al crear categoría: {err}")
        db.rollback()
        return None

def existe_id(id_categoria):
    cursor.execute("SELECT COUNT(*) FROM categorias WHERE idCategorias=%s", (id_categoria,))
    return cursor.fetchone()[0] > 0

def obtener_categorias():
    try:
        cursor.execute("SELECT idCategorias, nombre FROM categorias ORDER BY nombre")
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error al obtener categorías: {err}")
        return []

def actualizar_categoria(id_categoria, nombre):
    try:
        cursor.execute(
            "UPDATE categorias SET nombre=%s WHERE idCategorias=%s",
            (nombre, id_categoria)
        )
        db.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error al actualizar categoría: {err}")
        db.rollback()
        return False

def eliminar_categoria(id_categoria):
    try:
       
        cursor.execute("DELETE FROM categorias WHERE idCategorias=%s", (id_categoria,))
        db.commit()
        return True, "Categoría eliminada"
    except mysql.connector.Error as err:
        print(f"Error al eliminar categoría: {err}")
        db.rollback()
        return False, f"Error: {err}"

# Interfaz principal
def main(page: ft.Page):
    page.title = "Gestión de Categorías"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F5F1E9"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # Controles
    id_input = ft.TextField(
        label="ID Categoría",
        width=100,
        input_filter=ft.NumbersOnlyInputFilter(),
        error_text=None,
    )
    nombre_input = ft.TextField(label="Nombre Categoría", width=300)
    
    categorias_list = ft.ListView(expand=True, spacing=10)
    
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
            boton_guardar.disabled = False
            boton_crear.disabled = True
        else:
            if existe_id(numero):
                id_input.error_text = "ID ya existente, usa otro."
                boton_crear.disabled = True
                boton_guardar.disabled = True
            else:
                id_input.error_text = None
                boton_crear.disabled = False
                boton_guardar.disabled = True
        page.update()

    def cargar_categorias():
        categorias_list.controls.clear()
        for categoria in obtener_categorias():
            id_cat, nombre_cat = categoria
            
            categorias_list.controls.append(
                ft.Card(
                    ft.Container(
                        ft.Column([
                            ft.Text(nombre_cat, weight="bold"),
                            ft.Text(f"ID: {id_cat}", size=12),
                            ft.Row([
                                ft.IconButton(
                                    ft.Icons.EDIT,
                                    on_click=lambda e, id=id_cat: cargar_para_editar(id),
                                    tooltip="Editar"
                                ),
                                ft.IconButton(
                                    ft.Icons.DELETE,
                                    on_click=lambda e, id=id_cat: eliminar_categoria_click(id),
                                    tooltip="Eliminar"
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

    def cargar_para_editar(id_categoria):
        nonlocal editando
        cursor.execute("SELECT * FROM categorias WHERE idCategorias=%s", (id_categoria,))
        categoria = cursor.fetchone()
        if categoria:
            id_input.value = str(categoria[0])
            id_input.error_text = None
            id_input.read_only = True
            nombre_input.value = categoria[1]
            editando = True
            boton_guardar.disabled = False
            boton_crear.disabled = True
            page.update()

    def guardar_categoria(e):
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
            if actualizar_categoria(id_num, nombre_input.value):
                mostrar_mensaje("Categoría actualizada", False)
                id_input.read_only = False
                limpiar_formulario()
                cargar_categorias()
                page.update()
        else:
            if existe_id(id_num):
                id_input.error_text = "ID ya existente, usa otro."
                page.update()
                return
            if crear_categoria(id_num, nombre_input.value):
                mostrar_mensaje("Categoría creada", False)
                limpiar_formulario()
                cargar_categorias()
                page.update()

    def eliminar_categoria_click(id_categoria):
        success, msg = eliminar_categoria(id_categoria)
        mostrar_mensaje(msg, not success)
        if success:
            limpiar_formulario()
            cargar_categorias()
            page.update()

    id_input.on_change = validar_id_y_activar_botones

    boton_crear = ft.ElevatedButton("Crear", on_click=guardar_categoria, bgcolor="#795548", color="white", width=150, height=40, disabled=True)
    boton_guardar = ft.ElevatedButton("Guardar", on_click=guardar_categoria, bgcolor="#2196F3", color="white", width=150, height=40, disabled=True)

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
            ft.Text("Gestión de Categorías", size=24, weight="bold", color="#795548"),
            ft.Divider(),
            form,
            ft.Divider(),
            ft.Text("Listado de Categorías", size=18, color="#0066CC"),
            ft.Container(
                content=categorias_list,
                height=400,
                border=ft.border.all(1, "#E0E0E0"),
                padding=10,
                bgcolor="#F5F5F5",
                border_radius=10,
                clip_behavior=ft.ClipBehavior.HARD_EDGE
            )
        ], spacing=15)
    )

    cargar_categorias()

ft.app(target=main)
