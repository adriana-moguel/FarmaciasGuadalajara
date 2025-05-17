import flet as ft
import mysql.connector
from datetime import datetime

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

# Cargar opciones para dropdowns
def obtener_categorias():
    cursor.execute("SELECT idCategorias, nombre FROM categorias ORDER BY nombre")
    return cursor.fetchall()

def obtener_proveedores():
    cursor.execute("SELECT idProveedores, nombre FROM proveedores ORDER BY nombre")
    return cursor.fetchall()

def obtener_unidades():
    cursor.execute("SELECT idUnidades, nombreUnidad FROM unidades ORDER BY nombreUnidad")
    return cursor.fetchall()

# CRUD articulos
def crear_articulo(id_art, nombre, descripcion, precio, stock, fecha_ven, costo, cat_id, prov_id, uni_id):
    try:
        cursor.execute("""
            INSERT INTO articulos (
                idArticulos, nombre, descripcion, precioUnitario, stock, fechaVencimiento, costo, fk_idCategorias, fk_idProveedores, fk_idUnidades
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (id_art, nombre, descripcion, precio, stock, fecha_ven, costo, cat_id, prov_id, uni_id))
        db.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error al crear artículo: {err}")
        db.rollback()
        return False

def existe_id_articulo(id_art):
    cursor.execute("SELECT COUNT(*) FROM articulos WHERE idArticulos=%s", (id_art,))
    return cursor.fetchone()[0] > 0

def obtener_articulos():
    cursor.execute("""
        SELECT a.idArticulos, a.nombre, a.descripcion, a.precioUnitario, a.stock, a.fechaVencimiento, a.costo,
               c.nombre, p.nombre, u.nombreUnidad
        FROM articulos a
        LEFT JOIN categorias c ON a.fk_idCategorias = c.idCategorias
        LEFT JOIN proveedores p ON a.fk_idProveedores = p.idProveedores
        LEFT JOIN unidades u ON a.fk_idUnidades = u.idUnidades
        ORDER BY a.nombre
    """)
    return cursor.fetchall()

def actualizar_articulo(id_art, nombre, descripcion, precio, stock, fecha_ven, costo, cat_id, prov_id, uni_id):
    try:
        cursor.execute("""
            UPDATE articulos SET 
                nombre=%s, descripcion=%s, precioUnitario=%s, stock=%s, fechaVencimiento=%s, costo=%s,
                fk_idCategorias=%s, fk_idProveedores=%s, fk_idUnidades=%s
            WHERE idArticulos=%s
        """, (nombre, descripcion, precio, stock, fecha_ven, costo, cat_id, prov_id, uni_id, id_art))
        db.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error al actualizar artículo: {err}")
        db.rollback()
        return False

def eliminar_articulo(id_art):
    try:
        cursor.execute("DELETE FROM articulos WHERE idArticulos=%s", (id_art,))
        db.commit()
        return True, "Artículo eliminado"
    except mysql.connector.Error as err:
        print(f"Error al eliminar artículo: {err}")
        db.rollback()
        return False, f"Error: {err}"

# UI
def main(page: ft.Page):
    page.title = "Gestión de Artículos"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F5F1E9"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    id_input = ft.TextField(
        label="ID Artículo (máx 13 chars)",
        width=250,
        max_length=13,
        error_text=None,
    )
    nombre_input = ft.TextField(label="Nombre", width=400)
    descripcion_input = ft.TextField(label="Descripción", width=500, multiline=True, max_lines=3)
    precio_input = ft.TextField(label="Precio Unitario", width=150)  # Sin input_filter para permitir decimales
    stock_input = ft.TextField(label="Stock", width=100, input_filter=ft.NumbersOnlyInputFilter())
    fecha_ven_input = ft.TextField(label="Fecha de Vencimiento (YYYY-MM-DD)", width=200, hint_text="Ej: 2025-12-31")
    costo_input = ft.TextField(label="Costo", width=150)  # Sin input_filter para permitir decimales

    categorias = obtener_categorias()
    categoria_dropdown = ft.Dropdown(
        label="Categoría",
        width=300,
        options=[ft.dropdown.Option(str(c[0]), c[1]) for c in categorias]
    )

    proveedores = obtener_proveedores()
    proveedor_dropdown = ft.Dropdown(
        label="Proveedor",
        width=300,
        options=[ft.dropdown.Option(str(p[0]), p[1]) for p in proveedores]
    )

    unidades = obtener_unidades()
    unidad_dropdown = ft.Dropdown(
        label="Unidad",
        width=300,
        options=[ft.dropdown.Option(str(u[0]), u[1]) for u in unidades]
    )

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
        descripcion_input.value = ""
        precio_input.value = ""
        stock_input.value = ""
        fecha_ven_input.value = ""
        costo_input.value = ""
        categoria_dropdown.value = None
        proveedor_dropdown.value = None
        unidad_dropdown.value = None
        editando = False
        boton_guardar.disabled = True
        boton_crear.disabled = True
        page.update()

    def validar_campos():
        if not id_input.value.strip() or len(id_input.value.strip()) > 13:
            id_input.error_text = "ID requerido y max 13 caracteres"
            return False
        else:
            id_input.error_text = None

        if not nombre_input.value.strip():
            mostrar_mensaje("Nombre es requerido")
            return False

        # Validar fecha si no esta vacia
        if fecha_ven_input.value.strip():
            try:
                datetime.strptime(fecha_ven_input.value.strip(), "%Y-%m-%d")
            except ValueError:
                mostrar_mensaje("Formato de fecha inválido (YYYY-MM-DD)")
                return False

        # Validar numeros decimales
        try:
            if precio_input.value.strip() != "":
                float(precio_input.value.strip())
        except ValueError:
            mostrar_mensaje("Precio inválido")
            return False

        try:
            if costo_input.value.strip() != "":
                float(costo_input.value.strip())
        except ValueError:
            mostrar_mensaje("Costo inválido")
            return False

        if stock_input.value.strip() and (not stock_input.value.strip().isdigit()):
            mostrar_mensaje("Stock debe ser un número entero")
            return False

        if not categoria_dropdown.value:
            mostrar_mensaje("Seleccione una categoría")
            return False

        if not proveedor_dropdown.value:
            mostrar_mensaje("Seleccione un proveedor")
            return False

        if not unidad_dropdown.value:
            mostrar_mensaje("Seleccione una unidad")
            return False

        return True

    def validar_id_y_activar_botones(e=None):
        nonlocal editando
        valor = id_input.value.strip()
        if valor == "" or len(valor) > 13:
            id_input.error_text = "ID requerido y max 13 caracteres"
            boton_crear.disabled = True
            boton_guardar.disabled = True
            page.update()
            return
        if editando:
            id_input.error_text = None
            boton_guardar.disabled = False
            boton_crear.disabled = True
        else:
            if existe_id_articulo(valor):
                id_input.error_text = "ID ya existente, usa otro."
                boton_crear.disabled = True
                boton_guardar.disabled = True
            else:
                id_input.error_text = None
                boton_crear.disabled = False
                boton_guardar.disabled = True
        page.update()

    def cargar_articulos():
        articulos_list.controls.clear()
        for art in obtener_articulos():
            (id_art, nombre, desc, precio, stock, fecha_ven, costo, cat_nom, prov_nom, uni_nom) = art

            articulos_list.controls.append(
                ft.Card(
                    ft.Container(
                        ft.Column([
                            ft.Text(nombre, weight="bold"),
                            ft.Text(f"ID: {id_art}", size=12),
                            ft.Text(f"Descripción: {desc or 'N/A'}"),
                            ft.Text(f"Precio Unitario: ${precio:,.2f}" if precio is not None else "Precio Unitario: N/A"),
                            ft.Text(f"Costo: ${costo:,.2f}" if costo is not None else "Costo: N/A"),
                            ft.Text(f"Stock: {stock}" if stock is not None else "Stock: N/A"),
                            ft.Text(f"Vence: {fecha_ven.strftime('%Y-%m-%d') if fecha_ven else 'N/A'}"),
                            ft.Text(f"Categoría: {cat_nom or 'N/A'}"),
                            ft.Text(f"Proveedor: {prov_nom or 'N/A'}"),
                            ft.Text(f"Unidad: {uni_nom or 'N/A'}"),
                            ft.Row([
                                ft.IconButton(
                                    ft.Icons.EDIT,
                                    on_click=lambda e, id=id_art: cargar_para_editar(id),
                                    tooltip="Editar"
                                ),
                                ft.IconButton(
                                    ft.Icons.DELETE,
                                    on_click=lambda e, id=id_art: eliminar_articulo_click(id),
                                    tooltip="Eliminar"
                                )
                            ], alignment=ft.MainAxisAlignment.END)
                        ], spacing=5),
                        padding=15,
                        width=500
                    ),
                    color=ft.Colors.BLUE_50
                )
            )
        page.update()

    def cargar_para_editar(id_art):
        nonlocal editando
        cursor.execute("SELECT * FROM articulos WHERE idArticulos=%s", (id_art,))
        art = cursor.fetchone()
        if art:
            id_input.value = art[0]
            id_input.error_text = None
            id_input.read_only = True
            nombre_input.value = art[1] or ""
            descripcion_input.value = art[2] or ""
            precio_input.value = str(art[3]) if art[3] is not None else ""
            stock_input.value = str(art[4]) if art[4] is not None else ""
            fecha_ven_input.value = art[5].strftime("%Y-%m-%d") if art[5] else ""
            costo_input.value = str(art[6]) if art[6] is not None else ""
            categoria_dropdown.value = str(art[7]) if art[7] is not None else None
            proveedor_dropdown.value = str(art[8]) if art[8] is not None else None
            unidad_dropdown.value = str(art[9]) if art[9] is not None else None

            editando = True
            boton_guardar.disabled = False
            boton_crear.disabled = True
            page.update()

    def guardar_articulo(e):
        nonlocal editando
        if not validar_campos():
            return
        
        id_art = id_input.value.strip()
        nombre = nombre_input.value.strip()
        descripcion = descripcion_input.value.strip()
        precio = float(precio_input.value.strip()) if precio_input.value.strip() else None
        stock = int(stock_input.value.strip()) if stock_input.value.strip() else None
        fecha_ven = fecha_ven_input.value.strip() or None
        costo = float(costo_input.value.strip()) if costo_input.value.strip() else None
        cat_id = int(categoria_dropdown.value)
        prov_id = int(proveedor_dropdown.value)
        uni_id = int(unidad_dropdown.value)

        # Validar fecha formato correcto si existe
        if fecha_ven:
            try:
                datetime.strptime(fecha_ven, "%Y-%m-%d")
            except ValueError:
                mostrar_mensaje("Fecha de vencimiento inválida (YYYY-MM-DD)")
                return
        
        if editando:
            if actualizar_articulo(id_art, nombre, descripcion, precio, stock, fecha_ven, costo, cat_id, prov_id, uni_id):
                mostrar_mensaje("Artículo actualizado", False)
                id_input.read_only = False
                limpiar_formulario()
                cargar_articulos()
                page.update()
        else:
            if existe_id_articulo(id_art):
                id_input.error_text = "ID ya existente, usa otro."
                page.update()
                return
            if crear_articulo(id_art, nombre, descripcion, precio, stock, fecha_ven, costo, cat_id, prov_id, uni_id):
                mostrar_mensaje("Artículo creado", False)
                limpiar_formulario()
                cargar_articulos()
                page.update()

    def eliminar_articulo_click(id_art):
        success, msg = eliminar_articulo(id_art)
        mostrar_mensaje(msg, not success)
        if success:
            limpiar_formulario()
            cargar_articulos()
            page.update()

    id_input.on_change = validar_id_y_activar_botones = lambda e=None: (
        (lambda val=id_input.value.strip(): (
            setattr(id_input, "error_text", None) if (val and len(val) <= 13) else setattr(id_input, "error_text", "ID requerido, max 13 chars"),
            setattr(boton_crear, "disabled", False if (val and len(val) <= 13 and (not existe_id_articulo(val) or editando)) else True),
            setattr(boton_guardar, "disabled", True if not editando else False),
            page.update()
        ))()
    )

    boton_crear = ft.ElevatedButton("Crear", on_click=guardar_articulo, bgcolor="#795548", color="white", width=150, height=40, disabled=True)
    boton_guardar = ft.ElevatedButton("Guardar", on_click=guardar_articulo, bgcolor="#2196F3", color="white", width=150, height=40, disabled=True)

    form = ft.Column([
        ft.Row([
            id_input,
            nombre_input,
        ], spacing=10),
        descripcion_input,
        ft.Row([
            precio_input,
            stock_input,
            fecha_ven_input,
        ], spacing=10),
        costo_input,
        ft.Row([
            categoria_dropdown,
            proveedor_dropdown,
            unidad_dropdown
        ], spacing=10),
        ft.Row([
            boton_crear,
            boton_guardar
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    ], spacing=15)

    articulos_list = ft.ListView(expand=True, spacing=10)

    page.add(
        ft.Column([
            ft.Text("Gestión de Artículos", size=24, weight="bold", color="#795548"),
            ft.Divider(),
            form,
            ft.Divider(),
            ft.Text("Listado de Artículos", size=18, color="#0066CC"),
            ft.Container(
                articulos_list,
                height=500,
                border=ft.border.all(1, "#E0E0E0"),
                padding=10,
                bgcolor="#F5F5F5",
                border_radius=10,
                clip_behavior=ft.ClipBehavior.HARD_EDGE
            )
        ], spacing=15)
    )

    cargar_articulos()

ft.app(target=main)
