import flet as ft
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Santiago16_",
    database="farmaciasguadalajara"
)
cursor = db.cursor()

def crear_proveedor(id_proveedor, nombre, telefono, direccion, correo):
    cursor.execute(
        "INSERT INTO proveedores VALUES (%s, %s, %s, %s, %s)",
        (id_proveedor, nombre, telefono, direccion, correo)
    )
    db.commit()

def mostrar_proveedores():
    cursor.execute("SELECT * FROM proveedores")
    return cursor.fetchall()

def editar_proveedor(id_proveedor, nombre, telefono, direccion, correo):
    cursor.execute(
        "UPDATE proveedores SET nombre=%s, telefono=%s, direccion=%s, correoElectronico=%s WHERE idProveedores=%s",
        (nombre, telefono, direccion, correo, id_proveedor)
    )
    db.commit()

def eliminar_proveedor(id_proveedor):
    cursor.execute("DELETE FROM proveedores WHERE idProveedores=%s", (id_proveedor,))
    db.commit()


def main(page: ft.Page):
    page.title = "Farmacias Guadalajara - Proveedores"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F5F1E9"
    page.padding = 20
    page.expand = True
    page.scroll = ft.ScrollMode.AUTO
    
    # Título
    titulo = ft.Text("Gestión de Proveedores", 
                   size=28, 
                   weight="bold", 
                   color="#795548",
                   text_align=ft.TextAlign.CENTER)
    
    header = ft.Container(
        ft.Row([titulo], alignment=ft.MainAxisAlignment.CENTER),
        padding=10,
        bgcolor="#F5F1E9",
        border_radius=10
    )
    
 
    id_input = ft.TextField(
        label="ID Proveedor", 
        border_color="#0066CC", 
        width=400,
        input_filter=ft.NumbersOnlyInputFilter()
    )
    nombre_input = ft.TextField(label="Nombre", border_color="#0066CC", width=400)
    telefono_input = ft.TextField(
        label="Teléfono", 
        border_color="#0066CC", 
        width=400,
        input_filter=ft.NumbersOnlyInputFilter(),
        max_length=10
    )
    direccion_input = ft.TextField(label="Dirección", border_color="#0066CC", width=400)
    correo_input = ft.TextField(label="Correo Electrónico", border_color="#0066CC", width=400)
    
    snackbar = ft.SnackBar(
        content=ft.Text("", color=ft.Colors.WHITE),
        bgcolor=ft.Colors.RED_400,
        duration=2000
    )
    page.snack_bar = snackbar
    
    inputs = ft.Column([
        id_input,
        nombre_input,
        telefono_input,
        direccion_input,
        correo_input
    ], spacing=10)
    
    proveedores_grid = ft.Column(scroll="auto", spacing=10, expand=True)
   
    def limpiar_inputs():
        for control in [id_input, nombre_input, telefono_input, direccion_input, correo_input]:
            control.value = ""
            control.error_text = None
        page.update()
    
    def validar_campos():
        if not id_input.value.isdigit():
            return "El ID debe ser un número"
        if not telefono_input.value.isdigit() or len(telefono_input.value) != 10:
            return "El teléfono debe tener 10 dígitos numéricos"
        if "@" not in correo_input.value or "." not in correo_input.value:
            return "Ingrese un correo electrónico válido"
        return None
    
    def crear_proveedor_action(e):
        error = validar_campos()
        if error:
            snackbar.content.value = error
            snackbar.bgcolor = ft.Colors.RED_400
            snackbar.open = True
            page.update()
            return
        
        crear_proveedor(
            int(id_input.value),
            nombre_input.value,
            telefono_input.value,
            direccion_input.value,
            correo_input.value
        )
        limpiar_inputs()
        mostrar_proveedores_action()
        snackbar.content.value = "Proveedor creado exitosamente"
        snackbar.bgcolor = ft.Colors.GREEN_400
        snackbar.open = True
        page.update()
    
    def mostrar_proveedores_action(e=None):
        proveedores_grid.controls.clear()
        proveedores = mostrar_proveedores()
        if not proveedores:
            proveedores_grid.controls.append(
                ft.Text("No hay proveedores registrados", italic=True, color="grey")
            )
            proveedores_grid.update()
            page.update()
            return
        rows = []
        current_row = None
        for i, prov in enumerate(proveedores):
            if i % 3 == 0:
                current_row = ft.Row(spacing=10, wrap=True)
                rows.append(current_row)
            card = ft.Card(
                ft.Container(
                    ft.Column([
                        ft.Text(f"🆔 ID: {prov[0]}", weight="bold"),
                        ft.Text(f"🏢 {prov[1]}"),
                        ft.Text(f"📱 {prov[2]}"),
                        ft.Text(f"📍 {prov[3]}"),
                        ft.Text(f"✉️ {prov[4]}"),
                        ft.Row([
                            ft.IconButton(
                                ft.Icons.EDIT, 
                                on_click=lambda e, idp=prov[0]: cargar_para_editar(e, idp),
                                icon_color=ft.Colors.BLUE_600,
                                tooltip="Editar"
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE, 
                                on_click=lambda e, idp=prov[0]: eliminar_proveedor_action(e, idp),
                                icon_color=ft.Colors.RED_600,
                                tooltip="Eliminar"
                            )
                        ], alignment=ft.MainAxisAlignment.END)
                    ], spacing=5),
                    padding=15,
                    width=400
                ),
                color=ft.Colors.BLUE_50
            )
            current_row.controls.append(card)
        for row in rows:
            proveedores_grid.controls.append(row)
        proveedores_grid.update()
        page.update()
    
    def cargar_para_editar(e, id_proveedor):
        cursor.execute("SELECT * FROM proveedores WHERE idProveedores=%s", (id_proveedor,))
        prov = cursor.fetchone()
        if prov:
            id_input.value = str(prov[0])
            nombre_input.value = prov[1]
            telefono_input.value = prov[2]
            direccion_input.value = prov[3]
            correo_input.value = prov[4]
            page.update()
    
    def editar_proveedor_action(e):
        error = validar_campos()
        if error:
            snackbar.content.value = error
            snackbar.bgcolor = ft.Colors.RED_400
            snackbar.open = True
            page.update()
            return
            
        editar_proveedor(
            int(id_input.value),
            nombre_input.value,
            telefono_input.value,
            direccion_input.value,
            correo_input.value
        )
        limpiar_inputs()
        mostrar_proveedores_action()
        snackbar.content.value = "Proveedor actualizado exitosamente"
        snackbar.bgcolor = ft.Colors.GREEN_400
        snackbar.open = True
        page.update()
    
    def eliminar_proveedor_action(e, id_proveedor):
        eliminar_proveedor(id_proveedor)
        mostrar_proveedores_action()
        snackbar.content.value = "Proveedor eliminado exitosamente"
        snackbar.bgcolor = ft.Colors.GREEN_400
        snackbar.open = True
        page.update()
        limpiar_inputs()
    
    def create_button(text, action, color):
        return ft.ElevatedButton(
            text,
            on_click=action,
            bgcolor=color,
            color="white",
            height=40,
            width=150
        )
    
    buttons = ft.Row([
        create_button("Crear", crear_proveedor_action, "#795548"),
        create_button("Guardar", editar_proveedor_action, "#2196F3"),
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    
    page.add(
        ft.Column([
            header,
            ft.Container(inputs, padding=20, alignment=ft.alignment.center),
            buttons,
            ft.Divider(height=20, color="transparent"),
            ft.Text("Proveedores Registrados", size=18, weight="bold", color="#0066CC"),
            ft.Container(
                proveedores_grid,
                padding=10,
                border_radius=10,
                bgcolor="#F5F5F5",
                expand=True,
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO, expand=True)
    )
    
    mostrar_proveedores_action()

ft.app(target=main)
