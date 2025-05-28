import flet as ft
import mysql.connector
from datetime import datetime
import re

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',  # Cambiar por tu usuario
                password='Santiago16_',  # Cambiar por tu contraseña
                database='farmacia_guadalajara'
            )
        except Exception as e:
            print(f"Error de conexión: {e}")
    
    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except Exception as e:
            print(f"Error en query: {e}")
            return None
    
    def fetch_all(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en fetch: {e}")
            return []


class FarmaciaApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = DatabaseManager()
        self.current_user = None
        self.user_role = None
        self.current_sale_items = []
        self.current_sale_total = 0.0
        
        self.page.title = "Sistema Farmacia Guadalajara"
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.theme_mode = ft.ThemeMode.LIGHT
        
        self.setup_login()
    
    def setup_login(self):
        self.page.clean()
        
        # Crear usuarios de prueba si no existen
        self.create_test_users()
        
        self.username_field = ft.TextField(
            label="Usuario",
            width=300,
            prefix_icon=ft.Icons.PERSON
        )
        
        self.password_field = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            width=300,
            prefix_icon=ft.Icons.LOCK
        )
        
        login_button = ft.ElevatedButton(
            "Iniciar Sesión",
            on_click=self.login,
            width=300,
            height=50,
            bgcolor=ft.Colors.BLUE,
            color=ft.Colors.WHITE
        )
        
        login_container = ft.Container(
            content=ft.Column([
                ft.Text("Sistema Farmacia Guadalajara", 
                        size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                ft.Divider(height=20),
                self.username_field,
                self.password_field,
                login_button,
                ft.Text("Admin: admin/admin | General: general/general | Cajero: cajero/cajero", 
                        size=12, color=ft.Colors.GREY_600)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
            padding=50,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.BLUE_GREY_300,
                offset=ft.Offset(0, 0),
            )
        )
        
        self.page.add(
            ft.Container(
                content=login_container,
                alignment=ft.alignment.center,
                expand=True,
                bgcolor=ft.Colors.BLUE_50
            )
        )
    
    def create_test_users(self):
        # Crear empleados de prueba
        users = [
            ("admin", "Administrador", "admin", "admin@farmacia.com", 1),
            ("general", "Empleado General", "general", "general@farmacia.com", 1),
            ("cajero", "Cajero", "cajero", "cajero@farmacia.com", 1)
        ]
        
        for user_id, nombre, puesto, correo, sucursal in users:
            self.db.execute_query(
                "INSERT IGNORE INTO empleados (idEmpleado, nombre, puesto, correo, idSucursal) VALUES (%s, %s, %s, %s, %s)",
                (user_id, nombre, puesto, correo, sucursal)
            )
    
    def login(self, e):
        username = self.username_field.value
        password = self.password_field.value
        
        # Verificar credenciales (simplificado - en producción usar hash)
        valid_users = {
            "admin": ("admin", "admin"),
            "general": ("general", "general"), 
            "cajero": ("cajero", "cajero")
        }
        
        if username in valid_users and valid_users[username][1] == password:
            self.current_user = username
            self.user_role = valid_users[username][0]
            self.setup_main_interface()
        else:
            self.show_message("Error", "Usuario o contraseña incorrectos")
    
    def setup_main_interface(self):
        self.page.clean()
        
        # Sidebar con navegación
        nav_items = []
        
        if self.user_role == "admin":
            nav_items = [
                ("Categorías", ft.Icons.CATEGORY, self.show_categorias),
                ("Unidades", ft.Icons.STRAIGHTEN, self.show_unidades),
                ("Proveedores", ft.Icons.BUSINESS, self.show_proveedores),
                ("Artículos", ft.Icons.INVENTORY, self.show_articulos),
                ("Sucursales", ft.Icons.STORE, self.show_sucursales),
                ("Empleados", ft.Icons.PEOPLE, self.show_empleados),
                ("Clientes", ft.Icons.PERSON, self.show_clientes),
                ("Ventas", ft.Icons.SHOPPING_CART, self.show_ventas),
                ("Pagos", ft.Icons.PAYMENT, self.show_pagos),
                ("Compras", ft.Icons.SHOPPING_BAG, self.show_compras),
            ]
        elif self.user_role == "general":
            nav_items = [
                ("Categorías", ft.Icons.CATEGORY, self.show_categorias),
                ("Unidades", ft.Icons.STRAIGHTEN, self.show_unidades),
                ("Proveedores", ft.Icons.BUSINESS, self.show_proveedores),
                ("Artículos", ft.Icons.INVENTORY, self.show_articulos),
                ("Sucursales", ft.Icons.STORE, self.show_sucursales),
                ("Clientes", ft.Icons.PERSON, self.show_clientes),
                ("Ventas", ft.Icons.SHOPPING_CART, self.show_ventas),
                ("Pagos", ft.Icons.PAYMENT, self.show_pagos),
                ("Compras", ft.Icons.SHOPPING_BAG, self.show_compras),
            ]
        else:  # cajero
            nav_items = [
                ("Clientes", ft.Icons.PERSON, self.show_clientes),
                ("Ventas", ft.Icons.SHOPPING_CART, self.show_ventas),
                ("Pagos", ft.Icons.PAYMENT, self.show_pagos),
            ]
        
        nav_buttons = []
        for name, icon, callback in nav_items:
            nav_buttons.append(
                ft.TextButton(
                    text=name,
                    icon=icon,
                    on_click=callback,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE_GREY_800
                    ),
                    width=200
                )
            )
        
        sidebar = ft.Container(
            content=ft.Column([
                ft.Text(f"Bienvenido, {self.current_user}", 
                        color=ft.Colors.WHITE, size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(color=ft.Colors.WHITE54),
                *nav_buttons,
                ft.Divider(color=ft.Colors.WHITE54),
                ft.TextButton(
                    "Cerrar Sesión",
                    icon=ft.Icons.LOGOUT,
                    on_click=self.logout,
                    style=ft.ButtonStyle(color=ft.Colors.RED_300)
                )
            ], spacing=5),
            width=220,
            bgcolor=ft.Colors.BLUE_GREY_900,
            padding=20
        )
        
        # Área de contenido principal
        self.content_area = ft.Container(
            content=ft.Text("Seleccione una opción del menú", size=20),
            expand=True,
            padding=20
        )
        
        # Layout principal
        main_row = ft.Row([
            sidebar,
            ft.VerticalDivider(width=1),
            self.content_area
        ], expand=True)
        
        self.page.add(main_row)
    
    def logout(self, e):
        self.current_user = None
        self.user_role = None
        self.setup_login()
    
    def show_message(self, title, message):
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=close_dialog)]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    # CRUD para Categorías
    def show_categorias(self, e):
        self.content_area.content = self.create_categorias_view()
        self.page.update()
    
    def create_categorias_view(self):
        # Campos del formulario
        self.cat_nombre = ft.TextField(label="Nombre", width=300)
        self.cat_descripcion = ft.TextField(label="Descripción", width=300, multiline=True)
        
        # Botones
        btn_agregar = ft.ElevatedButton("Agregar", on_click=self.add_categoria)
        btn_actualizar = ft.ElevatedButton("Actualizar", on_click=self.update_categoria)
        btn_eliminar = ft.ElevatedButton("Eliminar", on_click=self.delete_categoria, bgcolor=ft.Colors.RED)
        
        # Tabla de datos
        self.categorias_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Descripción")),
            ],
            rows=[]
        )
        
        self.load_categorias_data()
        
        return ft.Column([
            ft.Text("Gestión de Categorías", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    self.cat_nombre,
                    self.cat_descripcion,
                    ft.Row([btn_agregar, btn_actualizar, btn_eliminar])
                ]),
            ]),
            ft.Divider(),
            ft.Container(
                content=self.categorias_table,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                padding=10
            )
        ])
    
    def load_categorias_data(self):
        data = self.db.fetch_all("SELECT * FROM categorias")
        self.categorias_table.rows.clear()
        
        for row in data:
            self.categorias_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[0]))),
                        ft.DataCell(ft.Text(row[1] or "")),
                        ft.DataCell(ft.Text(row[2] or "")),
                    ],
                    on_select_changed=lambda e, data=row: self.select_categoria(data)
                )
            )
        self.page.update()
    
    def select_categoria(self, data):
        self.selected_categoria_id = data[0]
        self.cat_nombre.value = data[1]
        self.cat_descripcion.value = data[2]
        self.page.update()
    
    def add_categoria(self, e):
        if self.cat_nombre.value:
            self.db.execute_query(
                "INSERT INTO categorias (nombre, descripcion) VALUES (%s, %s)",
                (self.cat_nombre.value, self.cat_descripcion.value)
            )
            self.clear_categoria_form()
            self.load_categorias_data()
            self.show_message("Éxito", "Categoría agregada correctamente")
        else:
            self.show_message("Error", "El nombre de la categoría no puede estar vacío.")
    
    def update_categoria(self, e):
        if hasattr(self, 'selected_categoria_id') and self.cat_nombre.value:
            self.db.execute_query(
                "UPDATE categorias SET nombre=%s, descripcion=%s WHERE idCategoria=%s",
                (self.cat_nombre.value, self.cat_descripcion.value, self.selected_categoria_id)
            )
            self.clear_categoria_form()
            self.load_categorias_data()
            self.show_message("Éxito", "Categoría actualizada correctamente")
        else:
            self.show_message("Error", "Seleccione una categoría para actualizar o ingrese el nombre.")
    
    def delete_categoria(self, e):
        if hasattr(self, 'selected_categoria_id'):
            self.db.execute_query("DELETE FROM categorias WHERE idCategoria=%s", (self.selected_categoria_id,))
            self.clear_categoria_form()
            self.load_categorias_data()
            self.show_message("Éxito", "Categoría eliminada correctamente")
        else:
            self.show_message("Error", "Seleccione una categoría para eliminar.")
    
    def clear_categoria_form(self):
        self.cat_nombre.value = ""
        self.cat_descripcion.value = ""
        if hasattr(self, 'selected_categoria_id'):
            delattr(self, 'selected_categoria_id')
        self.page.update()
    
    # CRUD para Unidades
    def show_unidades(self, e):
        self.content_area.content = self.create_unidades_view()
        self.page.update()

    def create_unidades_view(self):
        self.uni_nombre = ft.TextField(label="Nombre de la Unidad", width=300)

        btn_agregar = ft.ElevatedButton("Agregar", on_click=self.add_unidad)
        btn_actualizar = ft.ElevatedButton("Actualizar", on_click=self.update_unidad)
        btn_eliminar = ft.ElevatedButton("Eliminar", on_click=self.delete_unidad, bgcolor=ft.Colors.RED)

        self.unidades_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
            ],
            rows=[]
        )
        self.load_unidades_data()

        return ft.Column([
            ft.Text("Gestión de Unidades", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    self.uni_nombre,
                    ft.Row([btn_agregar, btn_actualizar, btn_eliminar])
                ]),
            ]),
            ft.Divider(),
            ft.Container(
                content=self.unidades_table,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                padding=10
            )
        ])

    def load_unidades_data(self):
        data = self.db.fetch_all("SELECT * FROM unidades")
        self.unidades_table.rows.clear()
        for row in data:
            self.unidades_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[0]))),
                        ft.DataCell(ft.Text(row[1] or "")),
                    ],
                    on_select_changed=lambda e, data=row: self.select_unidad(data)
                )
            )
        self.page.update()

    def select_unidad(self, data):
        self.selected_unidad_id = data[0]
        self.uni_nombre.value = data[1]
        self.page.update()

    def add_unidad(self, e):
        if self.uni_nombre.value:
            self.db.execute_query(
                "INSERT INTO unidades (nombre) VALUES (%s)",
                (self.uni_nombre.value,)
            )
            self.clear_unidad_form()
            self.load_unidades_data()
            self.show_message("Éxito", "Unidad agregada correctamente")
        else:
            self.show_message("Error", "El nombre de la unidad no puede estar vacío.")

    def update_unidad(self, e):
        if hasattr(self, 'selected_unidad_id') and self.uni_nombre.value:
            self.db.execute_query(
                "UPDATE unidades SET nombre=%s WHERE idUnidad=%s",
                (self.uni_nombre.value, self.selected_unidad_id)
            )
            self.clear_unidad_form()
            self.load_unidades_data()
            self.show_message("Éxito", "Unidad actualizada correctamente")
        else:
            self.show_message("Error", "Seleccione una unidad para actualizar o ingrese el nombre.")

    def delete_unidad(self, e):
        if hasattr(self, 'selected_unidad_id'):
            self.db.execute_query("DELETE FROM unidades WHERE idUnidad=%s", (self.selected_unidad_id,))
            self.clear_unidad_form()
            self.load_unidades_data()
            self.show_message("Éxito", "Unidad eliminada correctamente")
        else:
            self.show_message("Error", "Seleccione una unidad para eliminar.")

    def clear_unidad_form(self):
        self.uni_nombre.value = ""
        if hasattr(self, 'selected_unidad_id'):
            delattr(self, 'selected_unidad_id')
        self.page.update()

    # CRUD para Proveedores
    def show_proveedores(self, e):
        self.content_area.content = self.create_proveedores_view()
        self.page.update()

    def create_proveedores_view(self):
        self.prov_nombre = ft.TextField(label="Nombre", width=300)
        self.prov_direccion = ft.TextField(label="Dirección", width=300)
        self.prov_correo = ft.TextField(label="Correo", width=300)
        self.prov_telefono = ft.TextField(label="Teléfono", width=300, input_filter=ft.InputFilter(allow=True, regex_string=r"^\d{0,10}$"))

        btn_agregar = ft.ElevatedButton("Agregar", on_click=self.add_proveedor)
        btn_actualizar = ft.ElevatedButton("Actualizar", on_click=self.update_proveedor)
        btn_eliminar = ft.ElevatedButton("Eliminar", on_click=self.delete_proveedor, bgcolor=ft.Colors.RED)

        self.proveedores_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Correo")),
                ft.DataColumn(ft.Text("Teléfono")),
            ],
            rows=[]
        )
        self.load_proveedores_data()

        return ft.Column([
            ft.Text("Gestión de Proveedores", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    self.prov_nombre,
                    self.prov_direccion,
                    self.prov_correo,
                    self.prov_telefono,
                    ft.Row([btn_agregar, btn_actualizar, btn_eliminar])
                ]),
            ]),
            ft.Divider(),
            ft.Container(
                content=self.proveedores_table,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                padding=10
            )
        ])

    def load_proveedores_data(self):
        data = self.db.fetch_all("SELECT * FROM proveedores")
        self.proveedores_table.rows.clear()
        for row in data:
            self.proveedores_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[0]))),
                        ft.DataCell(ft.Text(row[1] or "")),
                        ft.DataCell(ft.Text(row[2] or "")),
                        ft.DataCell(ft.Text(row[3] or "")),
                        ft.DataCell(ft.Text(row[4] or "")),
                    ],
                    on_select_changed=lambda e, data=row: self.select_proveedor(data)
                )
            )
        self.page.update()

    def select_proveedor(self, data):
        self.selected_proveedor_id = data[0]
        self.prov_nombre.value = data[1]
        self.prov_direccion.value = data[2]
        self.prov_correo.value = data[3]
        self.prov_telefono.value = data[4]
        self.page.update()

    def add_proveedor(self, e):
        if self.prov_nombre.value and self.prov_telefono.value and re.fullmatch(r'\d{10}', self.prov_telefono.value):
            self.db.execute_query(
                "INSERT INTO proveedores (nombre, direccion, correo, telefono) VALUES (%s, %s, %s, %s)",
                (self.prov_nombre.value, self.prov_direccion.value, self.prov_correo.value, self.prov_telefono.value)
            )
            self.clear_proveedor_form()
            self.load_proveedores_data()
            self.show_message("Éxito", "Proveedor agregado correctamente")
        else:
            self.show_message("Error", "Asegúrese de que el nombre no esté vacío y el teléfono tenga 10 dígitos numéricos.")

    def update_proveedor(self, e):
        if hasattr(self, 'selected_proveedor_id') and self.prov_nombre.value and self.prov_telefono.value and re.fullmatch(r'\d{10}', self.prov_telefono.value):
            self.db.execute_query(
                "UPDATE proveedores SET nombre=%s, direccion=%s, correo=%s, telefono=%s WHERE idProveedor=%s",
                (self.prov_nombre.value, self.prov_direccion.value, self.prov_correo.value, self.prov_telefono.value, self.selected_proveedor_id)
            )
            self.clear_proveedor_form()
            self.load_proveedores_data()
            self.show_message("Éxito", "Proveedor actualizado correctamente")
        else:
            self.show_message("Error", "Seleccione un proveedor para actualizar y asegúrese de que el nombre no esté vacío y el teléfono tenga 10 dígitos numéricos.")

    def delete_proveedor(self, e):
        if hasattr(self, 'selected_proveedor_id'):
            self.db.execute_query("DELETE FROM proveedores WHERE idProveedor=%s", (self.selected_proveedor_id,))
            self.clear_proveedor_form()
            self.load_proveedores_data()
            self.show_message("Éxito", "Proveedor eliminado correctamente")
        else:
            self.show_message("Error", "Seleccione un proveedor para eliminar.")

    def clear_proveedor_form(self):
        self.prov_nombre.value = ""
        self.prov_direccion.value = ""
        self.prov_correo.value = ""
        self.prov_telefono.value = ""
        if hasattr(self, 'selected_proveedor_id'):
            delattr(self, 'selected_proveedor_id')
        self.page.update()

    # CRUD para Artículos
    def show_articulos(self, e):
        self.content_area.content = self.create_articulos_view()
        self.page.update()

    def create_articulos_view(self):
        self.art_idArticulo = ft.TextField(label="Código de Artículo (13 caracteres)", width=300, input_filter=ft.InputFilter(allow=True, regex_string=r"^\d{0,13}$"))
        self.art_nombre = ft.TextField(label="Nombre", width=300)
        self.art_descripcion = ft.TextField(label="Descripción", width=300, multiline=True)
        self.art_precio = ft.TextField(label="Precio", width=150, input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$"))
        self.art_costo = ft.TextField(label="Costo", width=150, input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$"))
        self.art_stock = ft.TextField(label="Stock", width=150, input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*$"))
        
        self.art_categoria_dropdown = ft.Dropdown(label="Categoría", width=200)
        self.load_dropdown_options("categorias", self.art_categoria_dropdown)
        
        self.art_unidad_dropdown = ft.Dropdown(label="Unidad", width=200)
        self.load_dropdown_options("unidades", self.art_unidad_dropdown)

        self.art_proveedor_dropdown = ft.Dropdown(label="Proveedor", width=200)
        self.load_dropdown_options("proveedores", self.art_proveedor_dropdown)

        btn_agregar = ft.ElevatedButton("Agregar", on_click=self.add_articulo)
        btn_actualizar = ft.ElevatedButton("Actualizar", on_click=self.update_articulo)
        btn_eliminar = ft.ElevatedButton("Eliminar", on_click=self.delete_articulo, bgcolor=ft.Colors.RED)
        
        self.articulos_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Costo")),
                ft.DataColumn(ft.Text("Stock")),
                ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Unidad")),
                ft.DataColumn(ft.Text("Proveedor")),
            ],
            rows=[]
        )
        self.load_articulos_data()

        return ft.Column([
            ft.Text("Gestión de Artículos", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Row([self.art_idArticulo, self.art_nombre]),
                    self.art_descripcion,
                    ft.Row([self.art_precio, self.art_costo, self.art_stock]),
                    ft.Row([self.art_categoria_dropdown, self.art_unidad_dropdown, self.art_proveedor_dropdown]),
                    ft.Row([btn_agregar, btn_actualizar, btn_eliminar])
                ]),
            ]),
            ft.Divider(),
            ft.Container(
                content=self.articulos_table,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                padding=10
            )
        ])

    def load_dropdown_options(self, table_name, dropdown_control):
         if table_name == "categorias":
            data = self.db.fetch_all("SELECT idCategoria, nombre FROM categorias")
         elif table_name == "unidades":
            data = self.db.fetch_all("SELECT idUnidad, nombre FROM unidades")
         elif table_name == "proveedores":
            data = self.db.fetch_all("SELECT idProveedor, nombre FROM proveedores")
         elif table_name == "sucursales":  # ← ESTA LÍNEA ES CLAVE
             data = self.db.fetch_all("SELECT idSucursal, nombre FROM sucursales")
         elif table_name == "articulos":
             data = self.db.fetch_all("SELECT idArticulo, nombre FROM articulos")
         else:
             data = []
    
         dropdown_control.options = [
            ft.dropdown.Option(key=str(row[0]), text=row[1]) for row in data
    ]
         self.page.update()


    def load_articulos_data(self):
        query = """
            SELECT a.idArticulo, a.nombre, a.precio, a.costo, a.stock, 
                   c.nombre, u.nombre, p.nombre
            FROM articulos a
            LEFT JOIN categorias c ON a.idCategoria = c.idCategoria
            LEFT JOIN unidades u ON a.idUnidad = u.idUnidad
            LEFT JOIN proveedores p ON a.idProveedor = p.idProveedor
        """
        data = self.db.fetch_all(query)
        self.articulos_table.rows.clear()
        for row in data:
            self.articulos_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(row[0] or "")),
                        ft.DataCell(ft.Text(row[1] or "")),
                        ft.DataCell(ft.Text(f"${row[2]:.2f}" if row[2] is not None else "$0.00")),
                        ft.DataCell(ft.Text(f"${row[3]:.2f}" if row[3] is not None else "$0.00")),
                        ft.DataCell(ft.Text(str(row[4]) if row[4] is not None else "0")),
                        ft.DataCell(ft.Text(row[5] or "")),
                        ft.DataCell(ft.Text(row[6] or "")),
                        ft.DataCell(ft.Text(row[7] or "")),
                    ],
                    on_select_changed=lambda e, data=row: self.select_articulo(data)
                )
            )
        self.page.update()

    def select_articulo(self, data):
        self.selected_articulo_id = data[0]
        self.art_idArticulo.value = data[0]
        self.art_nombre.value = data[1]
        self.art_descripcion.value = self.db.fetch_all("SELECT descripcion FROM articulos WHERE idArticulo = %s", (data[0],))[0][0] # Fetch full description
        self.art_precio.value = str(data[2])
        self.art_costo.value = str(data[3])
        self.art_stock.value = str(data[4])
        
        # Set dropdown values by finding the corresponding ID
        id_categoria = self.db.fetch_all("SELECT idCategoria FROM categorias WHERE nombre = %s", (data[5],))
        self.art_categoria_dropdown.value = str(id_categoria[0][0]) if id_categoria else None

        id_unidad = self.db.fetch_all("SELECT idUnidad FROM unidades WHERE nombre = %s", (data[6],))
        self.art_unidad_dropdown.value = str(id_unidad[0][0]) if id_unidad else None

        id_proveedor = self.db.fetch_all("SELECT idProveedor FROM proveedores WHERE nombre = %s", (data[7],))
        self.art_proveedor_dropdown.value = str(id_proveedor[0][0]) if id_proveedor else None
        
        self.art_idArticulo.read_only = True # Prevent changing ID on update
        self.page.update()

    def add_articulo(self, e):
        if (self.art_idArticulo.value and self.art_nombre.value and self.art_precio.value and 
            self.art_costo.value and self.art_stock.value and self.art_categoria_dropdown.value and 
            self.art_unidad_dropdown.value and self.art_proveedor_dropdown.value and
            re.fullmatch(r'\d{13}', self.art_idArticulo.value)):
            
            try:
                precio = float(self.art_precio.value)
                costo = float(self.art_costo.value)
                stock = int(self.art_stock.value)

                self.db.execute_query(
                    "INSERT INTO articulos (idArticulo, nombre, descripcion, precio, costo, stock, idCategoria, idUnidad, idProveedor) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (self.art_idArticulo.value, self.art_nombre.value, self.art_descripcion.value, 
                     precio, costo, stock, self.art_categoria_dropdown.value, 
                     self.art_unidad_dropdown.value, self.art_proveedor_dropdown.value)
                )
                self.clear_articulo_form()
                self.load_articulos_data()
                self.show_message("Éxito", "Artículo agregado correctamente")
            except ValueError:
                self.show_message("Error", "Precio, costo y stock deben ser números válidos.")
        else:
            self.show_message("Error", "Complete todos los campos y asegúrese de que el código de artículo tenga 13 dígitos.")

    def update_articulo(self, e):
        if (hasattr(self, 'selected_articulo_id') and self.art_nombre.value and self.art_precio.value and 
            self.art_costo.value and self.art_stock.value and self.art_categoria_dropdown.value and 
            self.art_unidad_dropdown.value and self.art_proveedor_dropdown.value):
            try:
                precio = float(self.art_precio.value)
                costo = float(self.art_costo.value)
                stock = int(self.art_stock.value)

                self.db.execute_query(
                    "UPDATE articulos SET nombre=%s, descripcion=%s, precio=%s, costo=%s, stock=%s, idCategoria=%s, idUnidad=%s, idProveedor=%s WHERE idArticulo=%s",
                    (self.art_nombre.value, self.art_descripcion.value, precio, costo, stock, 
                     self.art_categoria_dropdown.value, self.art_unidad_dropdown.value, 
                     self.art_proveedor_dropdown.value, self.selected_articulo_id)
                )
                self.clear_articulo_form()
                self.load_articulos_data()
                self.show_message("Éxito", "Artículo actualizado correctamente")
            except ValueError:
                self.show_message("Error", "Precio, costo y stock deben ser números válidos.")
        else:
            self.show_message("Error", "Seleccione un artículo para actualizar y complete todos los campos.")

    def delete_articulo(self, e):
        if hasattr(self, 'selected_articulo_id'):
            self.db.execute_query("DELETE FROM articulos WHERE idArticulo=%s", (self.selected_articulo_id,))
            self.clear_articulo_form()
            self.load_articulos_data()
            self.show_message("Éxito", "Artículo eliminado correctamente")
        else:
            self.show_message("Error", "Seleccione un artículo para eliminar.")

    def clear_articulo_form(self):
        self.art_idArticulo.value = ""
        self.art_nombre.value = ""
        self.art_descripcion.value = ""
        self.art_precio.value = ""
        self.art_costo.value = ""
        self.art_stock.value = ""
        self.art_categoria_dropdown.value = None
        self.art_unidad_dropdown.value = None
        self.art_proveedor_dropdown.value = None
        self.art_idArticulo.read_only = False
        if hasattr(self, 'selected_articulo_id'):
            delattr(self, 'selected_articulo_id')
        self.page.update()

    # CRUD para Sucursales
    def show_sucursales(self, e):
        self.content_area.content = self.create_sucursales_view()
        self.page.update()

    def create_sucursales_view(self):
        self.suc_nombre = ft.TextField(label="Nombre", width=300)
        self.suc_direccion = ft.TextField(label="Dirección", width=300)
        self.suc_telefono = ft.TextField(label="Teléfono", width=300, input_filter=ft.InputFilter(allow=True, regex_string=r"^\d{0,10}$"))
        self.suc_correo = ft.TextField(label="Correo", width=300)

        btn_agregar = ft.ElevatedButton("Agregar", on_click=self.add_sucursal)
        btn_actualizar = ft.ElevatedButton("Actualizar", on_click=self.update_sucursal)
        btn_eliminar = ft.ElevatedButton("Eliminar", on_click=self.delete_sucursal, bgcolor=ft.Colors.RED)

        self.sucursales_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Correo")),
            ],
            rows=[]
        )
        self.load_sucursales_data()

        return ft.Column([
            ft.Text("Gestión de Sucursales", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    self.suc_nombre,
                    self.suc_direccion,
                    self.suc_telefono,
                    self.suc_correo,
                    ft.Row([btn_agregar, btn_actualizar, btn_eliminar])
                ]),
            ]),
            ft.Divider(),
            ft.Container(
                content=self.sucursales_table,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                padding=10
            )
        ])

    def load_sucursales_data(self):
        data = self.db.fetch_all("SELECT * FROM sucursales")
        self.sucursales_table.rows.clear()
        for row in data:
            self.sucursales_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[0]))),
                        ft.DataCell(ft.Text(row[1] or "")),
                        ft.DataCell(ft.Text(row[2] or "")),
                        ft.DataCell(ft.Text(row[3] or "")),
                        ft.DataCell(ft.Text(row[4] or "")),
                    ],
                    on_select_changed=lambda e, data=row: self.select_sucursal(data)
                )
            )
        self.page.update()

    def select_sucursal(self, data):
        self.selected_sucursal_id = data[0]
        self.suc_nombre.value = data[1]
        self.suc_direccion.value = data[2]
        self.suc_telefono.value = data[3]
        self.suc_correo.value = data[4]
        self.page.update()

    def add_sucursal(self, e):
        if self.suc_nombre.value and self.suc_telefono.value and re.fullmatch(r'\d{10}', self.suc_telefono.value):
            self.db.execute_query(
                "INSERT INTO sucursales (nombre, direccion, telefono, correo) VALUES (%s, %s, %s, %s)",
                (self.suc_nombre.value, self.suc_direccion.value, self.suc_telefono.value, self.suc_correo.value)
            )
            self.clear_sucursal_form()
            self.load_sucursales_data()
            self.show_message("Éxito", "Sucursal agregada correctamente")
        else:
            self.show_message("Error", "Asegúrese de que el nombre no esté vacío y el teléfono tenga 10 dígitos numéricos.")

    def update_sucursal(self, e):
        if hasattr(self, 'selected_sucursal_id') and self.suc_nombre.value and self.suc_telefono.value and re.fullmatch(r'\d{10}', self.suc_telefono.value):
            self.db.execute_query(
                "UPDATE sucursales SET nombre=%s, direccion=%s, telefono=%s, correo=%s WHERE idSucursal=%s",
                (self.suc_nombre.value, self.suc_direccion.value, self.suc_telefono.value, self.suc_correo.value, self.selected_sucursal_id)
            )
            self.clear_sucursal_form()
            self.load_sucursales_data()
            self.show_message("Éxito", "Sucursal actualizada correctamente")
        else:
            self.show_message("Error", "Seleccione una sucursal para actualizar y asegúrese de que el nombre no esté vacío y el teléfono tenga 10 dígitos numéricos.")

    def delete_sucursal(self, e):
        if hasattr(self, 'selected_sucursal_id'):
            self.db.execute_query("DELETE FROM sucursales WHERE idSucursal=%s", (self.selected_sucursal_id,))
            self.clear_sucursal_form()
            self.load_sucursales_data()
            self.show_message("Éxito", "Sucursal eliminada correctamente")
        else:
            self.show_message("Error", "Seleccione una sucursal para eliminar.")

    def clear_sucursal_form(self):
        self.suc_nombre.value = ""
        self.suc_direccion.value = ""
        self.suc_telefono.value = ""
        self.suc_correo.value = ""
        if hasattr(self, 'selected_sucursal_id'):
            delattr(self, 'selected_sucursal_id')
        self.page.update()

    # CRUD para Empleados
    def show_empleados(self, e):
        self.content_area.content = self.create_empleados_view()
        self.page.update()

    def create_empleados_view(self):
        self.emp_idEmpleado = ft.TextField(label="ID Empleado (10 caracteres)", width=300, input_filter=ft.InputFilter(allow=True, regex_string=r"^[a-zA-Z0-9]{0,10}$"))
        self.emp_nombre = ft.TextField(label="Nombre", width=300)
        self.emp_puesto = ft.Dropdown(
            label="Puesto",
            width=200,
            options=[
                ft.dropdown.Option("admin"),
                ft.dropdown.Option("general"),
                ft.dropdown.Option("cajero"),
            ]
        )
        self.emp_correo = ft.TextField(label="Correo", width=300)
        
        self.emp_sucursal_dropdown = ft.Dropdown(label="Sucursal", width=200)
        self.load_dropdown_options("sucursales", self.emp_sucursal_dropdown)

        btn_agregar = ft.ElevatedButton("Agregar", on_click=self.add_empleado)
        btn_actualizar = ft.ElevatedButton("Actualizar", on_click=self.update_empleado)
        btn_eliminar = ft.ElevatedButton("Eliminar", on_click=self.delete_empleado, bgcolor=ft.Colors.RED)

        self.empleados_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Puesto")),
                ft.DataColumn(ft.Text("Correo")),
                ft.DataColumn(ft.Text("Sucursal")),
                ft.DataColumn(ft.Text("Ventas Realizadas")),
            ],
            rows=[]
        )
        self.load_empleados_data()

        return ft.Column([
            ft.Text("Gestión de Empleados", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Row([self.emp_idEmpleado, self.emp_nombre]),
                    ft.Row([self.emp_puesto, self.emp_correo]),
                    self.emp_sucursal_dropdown,
                    ft.Row([btn_agregar, btn_actualizar, btn_eliminar])
                ]),
            ]),
            ft.Divider(),
            ft.Container(
                content=self.empleados_table,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                padding=10
            )
        ])

    def load_empleados_data(self):
        query = """
            SELECT e.idEmpleado, e.nombre, e.puesto, e.correo, s.nombre, e.ventasRealizadas
            FROM empleados e
            LEFT JOIN sucursales s ON e.idSucursal = s.idSucursal
        """
        data = self.db.fetch_all(query)
        self.empleados_table.rows.clear()
        for row in data:
            self.empleados_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(row[0] or "")),
                        ft.DataCell(ft.Text(row[1] or "")),
                        ft.DataCell(ft.Text(row[2] or "")),
                        ft.DataCell(ft.Text(row[3] or "")),
                        ft.DataCell(ft.Text(row[4] or "")),
                        ft.DataCell(ft.Text(str(row[5]) if row[5] is not None else "0")),
                    ],
                    on_select_changed=lambda e, data=row: self.select_empleado(data)
                )
            )
        self.page.update()

    def select_empleado(self, data):
        self.selected_empleado_id = data[0]
        self.emp_idEmpleado.value = data[0]
        self.emp_nombre.value = data[1]
        self.emp_puesto.value = data[2]
        self.emp_correo.value = data[3]
        
        id_sucursal = self.db.fetch_all("SELECT idSucursal FROM sucursales WHERE nombre = %s", (data[4],))
        self.emp_sucursal_dropdown.value = str(id_sucursal[0][0]) if id_sucursal else None

        self.emp_idEmpleado.read_only = True
        self.page.update()

    def add_empleado(self, e):
        if (self.emp_idEmpleado.value and self.emp_nombre.value and self.emp_puesto.value and 
            self.emp_correo.value and self.emp_sucursal_dropdown.value and
            re.fullmatch(r'[a-zA-Z0-9]{1,10}', self.emp_idEmpleado.value)):
            self.db.execute_query(
                "INSERT INTO empleados (idEmpleado, nombre, puesto, correo, idSucursal) VALUES (%s, %s, %s, %s, %s)",
                (self.emp_idEmpleado.value, self.emp_nombre.value, self.emp_puesto.value, self.emp_correo.value, self.emp_sucursal_dropdown.value)
            )
            self.clear_empleado_form()
            self.load_empleados_data()
            self.show_message("Éxito", "Empleado agregado correctamente")
        else:
            self.show_message("Error", "Complete todos los campos y asegúrese de que el ID de empleado tenga hasta 10 caracteres alfanuméricos.")

    def update_empleado(self, e):
        if (hasattr(self, 'selected_empleado_id') and self.emp_nombre.value and self.emp_puesto.value and 
            self.emp_correo.value and self.emp_sucursal_dropdown.value):
            self.db.execute_query(
                "UPDATE empleados SET nombre=%s, puesto=%s, correo=%s, idSucursal=%s WHERE idEmpleado=%s",
                (self.emp_nombre.value, self.emp_puesto.value, self.emp_correo.value, self.emp_sucursal_dropdown.value, self.selected_empleado_id)
            )
            self.clear_empleado_form()
            self.load_empleados_data()
            self.show_message("Éxito", "Empleado actualizado correctamente")
        else:
            self.show_message("Error", "Seleccione un empleado para actualizar y complete todos los campos.")

    def delete_empleado(self, e):
        if hasattr(self, 'selected_empleado_id'):
            self.db.execute_query("DELETE FROM empleados WHERE idEmpleado=%s", (self.selected_empleado_id,))
            self.clear_empleado_form()
            self.load_empleados_data()
            self.show_message("Éxito", "Empleado eliminado correctamente")
        else:
            self.show_message("Error", "Seleccione un empleado para eliminar.")

    def clear_empleado_form(self):
        self.emp_idEmpleado.value = ""
        self.emp_nombre.value = ""
        self.emp_puesto.value = None
        self.emp_correo.value = ""
        self.emp_sucursal_dropdown.value = None
        self.emp_idEmpleado.read_only = False
        if hasattr(self, 'selected_empleado_id'):
            delattr(self, 'selected_empleado_id')
        self.page.update()

    # CRUD para Clientes
    def show_clientes(self, e):
        self.content_area.content = self.create_clientes_view()
        self.page.update()

    def create_clientes_view(self):
        self.cli_idCliente = ft.TextField(label="ID Cliente (10 caracteres)", width=300, input_filter=ft.InputFilter(allow=True, regex_string=r"^[a-zA-Z0-9]{0,10}$"))
        self.cli_nombre = ft.TextField(label="Nombre", width=300)
        self.cli_direccion = ft.TextField(label="Dirección", width=300)
        self.cli_correo = ft.TextField(label="Correo", width=300)

        btn_agregar = ft.ElevatedButton("Agregar", on_click=self.add_cliente)
        btn_actualizar = ft.ElevatedButton("Actualizar", on_click=self.update_cliente)
        btn_eliminar = ft.ElevatedButton("Eliminar", on_click=self.delete_cliente, bgcolor=ft.Colors.RED)

        self.clientes_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Correo")),
                ft.DataColumn(ft.Text("Compras Totales")),
            ],
            rows=[]
        )
        self.load_clientes_data()

        return ft.Column([
            ft.Text("Gestión de Clientes", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Row([self.cli_idCliente, self.cli_nombre]),
                    self.cli_direccion,
                    self.cli_correo,
                    ft.Row([btn_agregar, btn_actualizar, btn_eliminar])
                ]),
            ]),
            ft.Divider(),
            ft.Container(
                content=self.clientes_table,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                padding=10
            )
        ])

    def load_clientes_data(self):
        data = self.db.fetch_all("SELECT * FROM clientes")
        self.clientes_table.rows.clear()
        for row in data:
            self.clientes_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(row[0] or "")),
                        ft.DataCell(ft.Text(row[1] or "")),
                        ft.DataCell(ft.Text(row[2] or "")),
                        ft.DataCell(ft.Text(row[3] or "")),
                        ft.DataCell(ft.Text(str(row[4]) if row[4] is not None else "0")),
                    ],
                    on_select_changed=lambda e, data=row: self.select_cliente(data)
                )
            )
        self.page.update()

    def select_cliente(self, data):
        self.selected_cliente_id = data[0]
        self.cli_idCliente.value = data[0]
        self.cli_nombre.value = data[1]
        self.cli_direccion.value = data[2]
        self.cli_correo.value = data[3]
        self.cli_idCliente.read_only = True
        self.page.update()

    def add_cliente(self, e):
        if (self.cli_idCliente.value and self.cli_nombre.value and 
            re.fullmatch(r'[a-zA-Z0-9]{1,10}', self.cli_idCliente.value)):
            self.db.execute_query(
                "INSERT INTO clientes (idCliente, nombre, direccion, correo) VALUES (%s, %s, %s, %s)",
                (self.cli_idCliente.value, self.cli_nombre.value, self.cli_direccion.value, self.cli_correo.value)
            )
            self.clear_cliente_form()
            self.load_clientes_data()
            self.show_message("Éxito", "Cliente agregado correctamente")
        else:
            self.show_message("Error", "Complete los campos obligatorios y asegúrese de que el ID de cliente tenga hasta 10 caracteres alfanuméricos.")

    def update_cliente(self, e):
        if (hasattr(self, 'selected_cliente_id') and self.cli_nombre.value):
            self.db.execute_query(
                "UPDATE clientes SET nombre=%s, direccion=%s, correo=%s WHERE idCliente=%s",
                (self.cli_nombre.value, self.cli_direccion.value, self.cli_correo.value, self.selected_cliente_id)
            )
            self.clear_cliente_form()
            self.load_clientes_data()
            self.show_message("Éxito", "Cliente actualizado correctamente")
        else:
            self.show_message("Error", "Seleccione un cliente para actualizar y complete los campos obligatorios.")

    def delete_cliente(self, e):
        if hasattr(self, 'selected_cliente_id'):
            self.db.execute_query("DELETE FROM clientes WHERE idCliente=%s", (self.selected_cliente_id,))
            self.clear_cliente_form()
            self.load_clientes_data()
            self.show_message("Éxito", "Cliente eliminado correctamente")
        else:
            self.show_message("Error", "Seleccione un cliente para eliminar.")

    def clear_cliente_form(self):
        self.cli_idCliente.value = ""
        self.cli_nombre.value = ""
        self.cli_direccion.value = ""
        self.cli_correo.value = ""
        self.cli_idCliente.read_only = False
        if hasattr(self, 'selected_cliente_id'):
            delattr(self, 'selected_cliente_id')
        self.page.update()

    # CRUD para Ventas (con scanner de código de barras)
    def show_ventas(self, e):
        self.content_area.content = self.create_ventas_view()
        self.page.update()
    
    def create_ventas_view(self):
        # Campos para nueva venta
        self.venta_cliente = ft.Dropdown(label="Cliente", width=300)
        self.load_clientes_dropdown()
        # Campo para ingresar manualmente el ID del producto
        self.codigo_manual_input = ft.TextField(
             label="Código del Producto",
             width=300,
             on_submit=self.on_codigo_ingresado
        )
        btn_agregar_producto = ft.ElevatedButton(
        "Añadir a Venta",
         icon=ft.Icons.ADD,
         on_click=self.on_codigo_ingresado
        )

        
        # Área de productos escaneados  
        self.items_venta_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Cantidad")),
                ft.DataColumn(ft.Text("Subtotal")),
                ft.DataColumn(ft.Text("Acciones")), # New column for actions
            ],
            rows=[]
        )
        
        # Total de la venta
        self.total_venta_text = ft.Text("Total: $0.00", size=20, weight=ft.FontWeight.BOLD)
        
        # Botones de venta
        btn_procesar_venta = ft.ElevatedButton(
            "Procesar Venta",
            on_click=self.procesar_venta,
            bgcolor=ft.Colors.BLUE
        )
        
        btn_cancelar_venta = ft.ElevatedButton(
            "Cancelar Venta",
            on_click=self.cancelar_venta,
            bgcolor=ft.Colors.RED
        )
        
        # Tabla de ventas realizadas
        self.ventas_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Empleado")),
                ft.DataColumn(ft.Text("Total")),
                ft.DataColumn(ft.Text("Detalles")),
            ],
            rows=[]
        )
        
        self.load_ventas_data()
        
        return ft.Column([
            ft.Text("Gestión de Ventas", size=24, weight=ft.FontWeight.BOLD),
            
            # Sección nueva venta
            ft.Container(
                content=ft.Column([
                    ft.Text("Nueva Venta", size=18, weight=ft.FontWeight.BOLD),
                    ft.Row([self.venta_cliente, self.codigo_manual_input,btn_agregar_producto]),
                    ft.Container(
                        content=self.items_venta_table,
                        border=ft.border.all(1, ft.Colors.GREY_400),
                        border_radius=5,
                        padding=10,
                        height=200,
                        expand=True
                    ),
                    ft.Row([
                        self.total_venta_text,
                        ft.Container(expand=True), # Spacer
                        btn_procesar_venta,
                        btn_cancelar_venta
                    ], alignment=ft.MainAxisAlignment.END)
                ]),
                bgcolor=ft.Colors.BLUE_50,
                padding=20,
                border_radius=10
            ),
            
            ft.Divider(),
            
            # Historial de ventas
            ft.Text("Historial de Ventas", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=self.ventas_table,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                padding=10,
                expand=True
            )
        ], expand=True)
    
    def load_clientes_dropdown(self):
        clientes = self.db.fetch_all("SELECT idCliente, nombre FROM clientes")
        self.venta_cliente.options = [
            ft.dropdown.Option(key=str(cliente[0]), text=cliente[1])
            for cliente in clientes
        ]
        self.page.update()
    def on_codigo_ingresado(self, e):
         codigo = self.codigo_manual_input.value.strip()
         if not codigo:
            self.show_message("Código vacío", "Por favor ingresa un código de producto.")
            return

         articulo = self.db.fetch_all(
            "SELECT idArticulo, nombre, precio, stock FROM articulos WHERE idArticulo = %s",
            (codigo,)
        )

         if articulo:
            if articulo[0][3] > 0:  # Stock disponible
                  self.add_item_to_sale(articulo[0])
            else:
                  self.page.run_async(self.show_message, "Sin Stock", f"El artículo '{articulo[0][1]}' no tiene stock.")
         else:
             self.page.run_async(self.show_message, "Artículo no encontrado", f"No se encontró el artículo con el código: {codigo}")

    def add_item_to_sale(self, articulo_data):
        codigo, nombre, precio, stock_disponible = articulo_data
        
        # Verificar si el artículo ya está en la venta
        found = False
        for i, item in enumerate(self.current_sale_items):
            if item['codigo'] == codigo:
                if item['cantidad'] < stock_disponible:
                    self.current_sale_items[i]['cantidad'] += 1
                    self.current_sale_items[i]['subtotal'] = self.current_sale_items[i]['cantidad'] * precio
                    found = True
                else:
                    self.show_message("Stock Insuficiente", f"No hay suficiente stock de '{nombre}' (disponible: {stock_disponible}).")
                break
        
        if not found:
            if stock_disponible > 0:
                # Agregar nuevo artículo
                self.current_sale_items.append({
                    'codigo': codigo,
                    'nombre': nombre,
                    'precio': precio,
                    'cantidad': 1,
                    'subtotal': precio
                })
            else:
                self.show_message("Sin Stock", f"El artículo '{nombre}' no tiene stock disponible.")
        
        self.update_sale_display()

    def remove_item_from_sale(self, item_codigo):
        self.current_sale_items = [item for item in self.current_sale_items if item['codigo'] != item_codigo]
        self.update_sale_display()
    
    def update_sale_display(self):
        # Actualizar tabla de items
        self.items_venta_table.rows.clear()
        self.current_sale_total = 0
        
        for item in self.current_sale_items:
            self.items_venta_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item['codigo'])),
                    ft.DataCell(ft.Text(item['nombre'])),
                    ft.DataCell(ft.Text(f"${item['precio']:.2f}")),
                    ft.DataCell(ft.Text(str(item['cantidad']))),
                    ft.DataCell(ft.Text(f"${item['subtotal']:.2f}")),
                    ft.DataCell(ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,
                        on_click=lambda e, code=item['codigo']: self.remove_item_from_sale(code)
                    ))
                ])
            )
            self.current_sale_total += item['subtotal']
        
        self.total_venta_text.value = f"Total: ${self.current_sale_total:.2f}"
        self.page.update()
    
    def procesar_venta(self, e):
        if not self.current_sale_items or not self.venta_cliente.value:
            self.show_message("Error", "Seleccione un cliente y agregue productos a la venta.")
            return
        
        try:
            # Insertar venta
            cursor = self.db.execute_query(
                "INSERT INTO ventas (idCliente, idEmpleado, total) VALUES (%s, %s, %s)",
                (self.venta_cliente.value, self.current_user, self.current_sale_total)
            )
            
            id_venta = cursor.lastrowid
            
            # Insertar detalles de venta y actualizar stock
            for item in self.current_sale_items:
                self.db.execute_query(
                    "INSERT INTO detalleventa (idVenta, idArticulo, cantidad, precioUnitario, subtotal) VALUES (%s, %s, %s, %s, %s)",
                    (id_venta, item['codigo'], item['cantidad'], item['precio'], item['subtotal'])
                )
                
                # Actualizar stock
                self.db.execute_query(
                    "UPDATE articulos SET stock = stock - %s WHERE idArticulo = %s",
                    (item['cantidad'], item['codigo'])
                )
            
            # Limpiar venta actual
            self.current_sale_items = []
            self.current_sale_total = 0
            self.update_sale_display()
            self.load_ventas_data() # Reload sales history
            
            self.show_message("Éxito", f"Venta procesada correctamente. ID de Venta: {id_venta}")
            
        except Exception as ex:
            self.show_message("Error", f"Error al procesar venta: {str(ex)}")
    
    def cancelar_venta(self, e):
        self.current_sale_items = []
        self.current_sale_total = 0
        self.update_sale_display()
        self.show_message("Venta Cancelada", "La venta actual ha sido cancelada.")
    
    def load_ventas_data(self):
        data = self.db.fetch_all("""
            SELECT v.idVenta, v.fechaVenta, c.nombre, e.nombre, v.total 
            FROM ventas v 
            LEFT JOIN clientes c ON v.idCliente = c.idCliente 
            LEFT JOIN empleados e ON v.idEmpleado = e.idEmpleado
            ORDER BY v.fechaVenta DESC
        """)
        
        self.ventas_table.rows.clear()
        for row in data:
            self.ventas_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(row[0]))),
                    ft.DataCell(ft.Text(str(row[1]))),
                    ft.DataCell(ft.Text(row[2] or "")),
                    ft.DataCell(ft.Text(row[3] or "")),
                    ft.DataCell(ft.Text(f"${row[4]:.2f}" if row[4] else "$0.00")),
                    ft.DataCell(ft.IconButton(
                        icon=ft.Icons.INFO,
                        tooltip="Ver Detalles",
                        on_click=lambda e, id_venta=row[0]: self.show_detalle_venta(id_venta)
                    ))
                ])
            )
        self.page.update()

    def show_detalle_venta(self, id_venta):
        detalle_data = self.db.fetch_all("""
            SELECT a.nombre, dv.cantidad, dv.precioUnitario, dv.subtotal
            FROM detalleventa dv
            JOIN articulos a ON dv.idArticulo = a.idArticulo
            WHERE dv.idVenta = %s
        """, (id_venta,))

        if not detalle_data:
            self.show_message("Detalle de Venta", f"No se encontraron detalles para la venta ID: {id_venta}")
            return

        detalle_rows = []
        for item in detalle_data:
            detalle_rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item[0])),
                    ft.DataCell(ft.Text(str(item[1]))),
                    ft.DataCell(ft.Text(f"${item[2]:.2f}")),
                    ft.DataCell(ft.Text(f"${item[3]:.2f}")),
                ])
            )

        detalle_table = ft.DataTable(
            columns=[
                  ft.DataColumn(ft.Text("Producto")),
                 ft.DataColumn(ft.Text("Cantidad")),
                 ft.DataColumn(ft.Text("Precio Unitario")),
                 ft.DataColumn(ft.Text("Subtotal")),
            ],
             rows=detalle_rows,
             border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=5
        )


        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Detalle de Venta #{id_venta}"),
            content=ft.Container(
                content=ft.Column([
                    detalle_table
                ], scroll=ft.ScrollMode.ADAPTIVE, height=300),
                width=500
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self.close_dialog_and_update(dlg))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def close_dialog_and_update(self, dialog_control):
        dialog_control.open = False
        self.page.update()

    # CRUD para Pagos
    def show_pagos(self, e):
        self.content_area.content = self.create_pagos_view()
        self.page.update()

    def create_pagos_view(self):
        self.pago_idVenta = ft.TextField(label="ID Venta", width=200, input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*$"))
        self.pago_metodo = ft.Dropdown(
            label="Método de Pago",
            width=200,
            options=[
                ft.dropdown.Option("Efectivo"),
                ft.dropdown.Option("Tarjeta"),
                ft.dropdown.Option("Transferencia"),
                ft.dropdown.Option("Crédito"),
            ]
        )
        self.pago_monto = ft.TextField(label="Monto", width=150, input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$"))

        btn_agregar = ft.ElevatedButton("Registrar Pago", on_click=self.add_pago)
        
        self.pagos_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID Pago")),
                ft.DataColumn(ft.Text("ID Venta")),
                ft.DataColumn(ft.Text("Método de Pago")),
                ft.DataColumn(ft.Text("Monto")),
                ft.DataColumn(ft.Text("Fecha de Pago")),
            ],
            rows=[]
        )
        self.load_pagos_data()

        return ft.Column([
            ft.Text("Gestión de Pagos", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Row([self.pago_idVenta, self.pago_metodo, self.pago_monto]),
                    btn_agregar
                ]),
            ]),
            ft.Divider(),
            ft.Container(
                content=self.pagos_table,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                padding=10
            )
        ])

    def load_pagos_data(self):
        data = self.db.fetch_all("SELECT * FROM pagos ORDER BY fechaPago DESC")
        self.pagos_table.rows.clear()
        for row in data:
            self.pagos_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[0]))),
                        ft.DataCell(ft.Text(str(row[1]))),
                        ft.DataCell(ft.Text(row[2] or "")),
                        ft.DataCell(ft.Text(f"${row[3]:.2f}" if row[3] is not None else "$0.00")),
                        ft.DataCell(ft.Text(str(row[4]) or "")),
                    ]
                )
            )
        self.page.update()

    def add_pago(self, e):
        if self.pago_idVenta.value and self.pago_metodo.value and self.pago_monto.value:
            try:
                id_venta = int(self.pago_idVenta.value)
                monto = float(self.pago_monto.value)

                # Optional: Validate if idVenta exists
                venta_exists = self.db.fetch_all("SELECT idVenta FROM ventas WHERE idVenta = %s", (id_venta,))
                if not venta_exists:
                    self.show_message("Error", "El ID de Venta no existe.")
                    return

                self.db.execute_query(
                    "INSERT INTO pagos (idVenta, metodoPago, monto) VALUES (%s, %s, %s)",
                    (id_venta, self.pago_metodo.value, monto)
                )
                self.pago_idVenta.value = ""
                self.pago_metodo.value = None
                self.pago_monto.value = ""
                self.load_pagos_data()
                self.show_message("Éxito", "Pago registrado correctamente")
            except ValueError:
                self.show_message("Error", "Monto debe ser un número válido.")
        else:
            self.show_message("Error", "Complete todos los campos de pago.")

    # CRUD para Compras a Proveedores
    def show_compras(self, e):
        self.content_area.content = self.create_compras_view()
        self.page.update()

    def create_compras_view(self):
        self.compra_proveedor_dropdown = ft.Dropdown(label="Proveedor", width=300)
        self.load_dropdown_options("proveedores", self.compra_proveedor_dropdown)

        self.compra_articulo_dropdown = ft.Dropdown(label="Artículo", width=300)
        self.load_dropdown_options("articulos", self.compra_articulo_dropdown) # Assuming idArticulo and nombre are the options
        self.compra_cantidad = ft.TextField(label="Cantidad", width=150, input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*$"))
        self.compra_precio_unitario = ft.TextField(label="Precio Unitario", width=150, input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$"))

        self.current_purchase_items = []
        self.current_purchase_total = 0.0

        self.items_compra_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Artículo")),
                ft.DataColumn(ft.Text("Cantidad")),
                ft.DataColumn(ft.Text("Precio Unitario")),
                ft.DataColumn(ft.Text("Total")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )

        self.total_compra_text = ft.Text("Total Compra: $0.00", size=20, weight=ft.FontWeight.BOLD)

        btn_add_item = ft.ElevatedButton("Añadir Artículo a Compra", on_click=self.add_item_to_purchase)
        btn_procesar_compra = ft.ElevatedButton("Procesar Compra", on_click=self.procesar_compra, bgcolor=ft.Colors.BLUE)
        btn_cancelar_compra = ft.ElevatedButton("Cancelar Compra", on_click=self.cancelar_compra, bgcolor=ft.Colors.RED)

        self.compras_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID Compra")),
                ft.DataColumn(ft.Text("Proveedor")),
                ft.DataColumn(ft.Text("Fecha Compra")),
            ],
            rows=[]
        )
        self.load_compras_data()

        return ft.Column([
            ft.Text("Gestión de Compras a Proveedores", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column([
                    ft.Text("Nueva Compra", size=18, weight=ft.FontWeight.BOLD),
                    self.compra_proveedor_dropdown,
                    ft.Row([self.compra_articulo_dropdown, self.compra_cantidad, self.compra_precio_unitario]),
                    btn_add_item,
                    ft.Container(
                        content=self.items_compra_table,
                        border=ft.border.all(1, ft.Colors.GREY_400),
                        border_radius=5,
                        padding=10,
                        height=200,
                        expand=True
                    ),
                    ft.Row([
                        self.total_compra_text,
                        ft.Container(expand=True),
                        btn_procesar_compra,
                        btn_cancelar_compra
                    ], alignment=ft.MainAxisAlignment.END)
                ]),
                bgcolor=ft.Colors.BLUE_50,
                padding=20,
                border_radius=10
            ),
            ft.Divider(),
            ft.Text("Historial de Compras", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=self.compras_table,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                padding=10,
                expand=True
            )
        ], expand=True)

    def add_item_to_purchase(self, e):
        if (self.compra_articulo_dropdown.value and self.compra_cantidad.value and 
            self.compra_precio_unitario.value):
            try:
                articulo_id = self.compra_articulo_dropdown.value
                cantidad = int(self.compra_cantidad.value)
                precio_unitario = float(self.compra_precio_unitario.value)
                
                if cantidad <= 0 or precio_unitario <= 0:
                    self.show_message("Error de Entrada", "Cantidad y Precio Unitario deben ser mayores que cero.")
                    return

                articulo_nombre = self.db.fetch_all("SELECT nombre FROM articulos WHERE idArticulo = %s", (articulo_id,))
                articulo_nombre = articulo_nombre[0][0] if articulo_nombre else "Artículo Desconocido"

                total_item = cantidad * precio_unitario

                # Check if item already in current purchase
                found = False
                for item in self.current_purchase_items:
                    if item['idArticulo'] == articulo_id:
                        item['cantidad'] += cantidad
                        item['total'] += total_item
                        found = True
                        break
                
                if not found:
                    self.current_purchase_items.append({
                        'idArticulo': articulo_id,
                        'nombre': articulo_nombre,
                        'cantidad': cantidad,
                        'precioUnitario': precio_unitario,
                        'total': total_item
                    })
                
                self.update_purchase_display()
                self.compra_articulo_dropdown.value = None
                self.compra_cantidad.value = ""
                self.compra_precio_unitario.value = ""
                self.page.update()

            except ValueError:
                self.show_message("Error de Entrada", "Cantidad y Precio Unitario deben ser números válidos.")
        else:
            self.show_message("Error", "Seleccione un artículo y complete la cantidad y el precio unitario.")

    def remove_item_from_purchase(self, item_idArticulo):
        self.current_purchase_items = [item for item in self.current_purchase_items if item['idArticulo'] != item_idArticulo]
        self.update_purchase_display()

    def update_purchase_display(self):
        self.items_compra_table.rows.clear()
        self.current_purchase_total = 0

        for item in self.current_purchase_items:
            self.items_compra_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item['nombre'])),
                    ft.DataCell(ft.Text(str(item['cantidad']))),
                    ft.DataCell(ft.Text(f"${item['precioUnitario']:.2f}")),
                    ft.DataCell(ft.Text(f"${item['total']:.2f}")),
                    ft.DataCell(ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,
                        on_click=lambda e, code=item['idArticulo']: self.remove_item_from_purchase(code)
                    ))
                ])
            )
            self.current_purchase_total += item['total']

        self.total_compra_text.value = f"Total Compra: ${self.current_purchase_total:.2f}"
        self.page.update()

    def procesar_compra(self, e):
        if not self.compra_proveedor_dropdown.value or not self.current_purchase_items:
            self.show_message("Error", "Seleccione un proveedor y añada artículos a la compra.")
            return

        try:
            cursor = self.db.execute_query(
                "INSERT INTO compras (idProveedor, fechaCompra) VALUES (%s, %s)",
                (self.compra_proveedor_dropdown.value, datetime.now())
            )
            id_compra = cursor.lastrowid

            for item in self.current_purchase_items:
                self.db.execute_query(
                    "INSERT INTO detallecompra (idCompra, idArticulo, cantidad, precioUnitario, total) VALUES (%s, %s, %s, %s, %s)",
                    (id_compra, item['idArticulo'], item['cantidad'], item['precioUnitario'], item['total'])
                )
                # Update stock of articles
                self.db.execute_query(
                    "UPDATE articulos SET stock = stock + %s WHERE idArticulo = %s",
                    (item['cantidad'], item['idArticulo'])
                )
            
            self.current_purchase_items = []
            self.current_purchase_total = 0.0
            self.update_purchase_display()
            self.load_compras_data()
            self.show_message("Éxito", f"Compra registrada correctamente. ID: {id_compra}")

        except Exception as ex:
            self.show_message("Error", f"Error al procesar la compra: {str(ex)}")

    def cancelar_compra(self, e):
        self.current_purchase_items = []
        self.current_purchase_total = 0.0
        self.update_purchase_display()
        self.show_message("Compra Cancelada", "La compra actual ha sido cancelada.")

    def load_compras_data(self):
        query = """
            SELECT c.idCompra, p.nombre, c.fechaCompra
            FROM compras c
            JOIN proveedores p ON c.idProveedor = p.idProveedor
            ORDER BY c.fechaCompra DESC
        """
        data = self.db.fetch_all(query)
        self.compras_table.rows.clear()
        for row in data:
            self.compras_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(row[0]))),
                    ft.DataCell(ft.Text(row[1] or "")),
                    ft.DataCell(ft.Text(str(row[2]) or "")),
                ])
            )
        self.page.update()

def main(page: ft.Page):
    app = FarmaciaApp(page)

if __name__ == "__main__":
    ft.app(target=main)