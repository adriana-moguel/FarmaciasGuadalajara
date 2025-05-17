import flet as ft
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Santiago16_",
    database="farmaciasguadalajara"
)
cursor = db.cursor()

def crear_sucursal(id_sucursal, nombre, direccion, telefono, correo):
    cursor.execute(
        "INSERT INTO sucursales VALUES (%s, %s, %s, %s, %s)",
        (id_sucursal, nombre, direccion, telefono, correo)
    )
    db.commit()

def mostrar_sucursales():
    cursor.execute("SELECT * FROM sucursales ORDER BY nombreSucursal")
    return cursor.fetchall()

def editar_sucursal(id_sucursal, nombre, direccion, telefono, correo):
    cursor.execute(
        "UPDATE sucursales SET nombreSucursal=%s, direccion=%s, telefono=%s, correoElectronico=%s WHERE idSucursales=%s",
        (nombre, direccion, telefono, correo, id_sucursal)
    )
    db.commit()

def eliminar_sucursal(id_sucursal):
    cursor.execute("DELETE FROM sucursales WHERE idSucursales=%s", (id_sucursal,))
    db.commit()

def main(page: ft.Page):
    page.title = "Farmacias Guadalajara - Gestión de Sucursales"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F5F1E9"
    page.padding = 20
    page.expand = True
    page.scroll = ft.ScrollMode.AUTO
    
    titulo = ft.Text(
        "Gestión de Sucursales",
        size=28,
        weight="bold",
        color="#795548",
        text_align=ft.TextAlign.CENTER
    )
    
    header = ft.Container(
        ft.Row([titulo], alignment=ft.MainAxisAlignment.CENTER),
        padding=10,
        bgcolor="#F5F1E9",
        border_radius=10
    )
    
  
    id_input = ft.TextField(
        label="ID Sucursal", 
        border_color="#0066CC", 
        width=400,
        input_filter=ft.NumbersOnlyInputFilter(),
        disabled=False 
    )
    nombre_input = ft.TextField(label="Nombre Sucursal", border_color="#0066CC", width=400)
    direccion_input = ft.TextField(label="Dirección", border_color="#0066CC", width=400)
    telefono_input = ft.TextField(
        label="Teléfono", 
        border_color="#0066CC", 
        width=400,
        input_filter=ft.NumbersOnlyInputFilter(),
        max_length=10,
        hint_text="Sólo 10 dígitos"
    )
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
        direccion_input,
        telefono_input,
        correo_input
    ], spacing=10)
    
    sucursales_grid = ft.Column(scroll="auto", spacing=10, expand=True)
    
    editando = False  
    def limpiar_inputs():
        nonlocal editando
        for control in [id_input, nombre_input, direccion_input, telefono_input, correo_input]:
            control.value = ""
            control.error_text = None
        id_input.disabled = False
        boton_crear.disabled = False
        boton_guardar.disabled = True
        editando = False
        page.update()
    
    def validar_campos():
        if not id_input.value.isdigit():
            return "El ID debe ser un número"
        if not telefono_input.value.isdigit() or len(telefono_input.value) != 10:
            return "El teléfono debe tener exactamente 10 dígitos numéricos"
        if correo_input.value and ("@" not in correo_input.value or "." not in correo_input.value):
            return "Ingrese un correo electrónico válido"
        return None
    
    def existe_id(id_sucursal):
        cursor.execute("SELECT COUNT(*) FROM sucursales WHERE idSucursales=%s", (id_sucursal,))
        return cursor.fetchone()[0] > 0
    
    def crear_sucursal_action(e):
        nonlocal editando
        if editando:
            return
        
        error = validar_campos()
        if error:
            snackbar.content.value = error
            snackbar.bgcolor = ft.Colors.RED_400
            snackbar.open = True
            page.update()
            return
        
        if existe_id(int(id_input.value)):
            snackbar.content.value = f"El ID {id_input.value} ya existe, usa otro."
            snackbar.bgcolor = ft.Colors.RED_400
            snackbar.open = True
            page.update()
            return
        
        crear_sucursal(
            int(id_input.value),
            nombre_input.value,
            direccion_input.value,
            telefono_input.value,
            correo_input.value
        )
        limpiar_inputs()
        mostrar_sucursales_action()
        snackbar.content.value = "Sucursal creada exitosamente"
        snackbar.bgcolor = ft.Colors.GREEN_400
        snackbar.open = True
        page.update()
    
    def mostrar_sucursales_action(e=None):
        sucursales_grid.controls.clear()
        sucursales = mostrar_sucursales()
        if not sucursales:
            sucursales_grid.controls.append(
                ft.Text("No hay sucursales registradas", italic=True, color="grey")
            )
            sucursales_grid.update()
            page.update()
            return
        rows = []
        current_row = None
        for i, suc in enumerate(sucursales):
            if i % 3 == 0:
                current_row = ft.Row(spacing=10, wrap=True)
                rows.append(current_row)
            card = ft.Card(
                ft.Container(
                    ft.Column([
                        ft.Text(f"🏬 {suc[1]}", size=18, weight="bold"),
                        ft.Text(f"🆔 ID: {suc[0]}"),
                        ft.Text(f"📍 {suc[2]}"),
                        ft.Text(f"📞 {suc[3]}"),
                        ft.Text(f"✉️ {suc[4]}"),
                        ft.Row([
                            ft.IconButton(
                                ft.Icons.EDIT,
                                on_click=lambda e, idp=suc[0]: cargar_para_editar(e, idp),
                                icon_color=ft.Colors.BLUE_600,
                                tooltip="Editar"
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE,
                                on_click=lambda e, idp=suc[0]: eliminar_sucursal_action(e, idp),
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
            sucursales_grid.controls.append(row)
        sucursales_grid.update()
        page.update()
    
    def cargar_para_editar(e, id_sucursal):
        nonlocal editando
        cursor.execute("SELECT * FROM sucursales WHERE idSucursales=%s", (id_sucursal,))
        suc = cursor.fetchone()
        if suc:
            id_input.value = str(suc[0])
            nombre_input.value = suc[1]
            direccion_input.value = suc[2]
            telefono_input.value = suc[3]
            correo_input.value = suc[4]
            id_input.disabled = True  # no permitir cambiar el ID al editar
            boton_crear.disabled = True
            boton_guardar.disabled = False
            editando = True
            page.update()
    
    def editar_sucursal_action(e):
        nonlocal editando
        if not id_input.value:
            snackbar.content.value = "Seleccione una sucursal para editar"
            snackbar.bgcolor = ft.Colors.RED_400
            snackbar.open = True
            page.update()
            return
            
        error = validar_campos()
        if error:
            snackbar.content.value = error
            snackbar.bgcolor = ft.Colors.RED_400
            snackbar.open = True
            page.update()
            return
            
        editar_sucursal(
            int(id_input.value),
            nombre_input.value,
            direccion_input.value,
            telefono_input.value,
            correo_input.value
        )
        limpiar_inputs()
        mostrar_sucursales_action()
        snackbar.content.value = "Sucursal actualizada exitosamente"
        snackbar.bgcolor = ft.Colors.GREEN_400
        snackbar.open = True
        page.update()
        editando = False
    
    def eliminar_sucursal_action(e, id_sucursal):
        nonlocal editando
        eliminar_sucursal(id_sucursal)
        mostrar_sucursales_action()
        snackbar.content.value = "Sucursal eliminada exitosamente"
        snackbar.bgcolor = ft.Colors.GREEN_400
        snackbar.open = True
        page.update()
        limpiar_inputs()
        editando = False
    
    boton_crear = ft.ElevatedButton("Crear", on_click=crear_sucursal_action, bgcolor="#795548", color="white", width=150, height=40)
    boton_guardar = ft.ElevatedButton("Guardar", on_click=editar_sucursal_action, bgcolor="#2196F3", color="white", width=150, height=40, disabled=True)

    buttons = ft.Row([boton_crear, boton_guardar], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

    sucursales_container = ft.Container(
        ft.Column([
            header,
            ft.Container(inputs, padding=20, alignment=ft.alignment.center),
            buttons,
            ft.Divider(height=20, color="transparent"),
            ft.Text("Sucursales Registradas", size=18, weight="bold", color="#0066CC"),
            ft.Container(
                sucursales_grid,
                padding=10,
                border_radius=10,
                bgcolor="#F5F5F5",
                expand=True,
            )
        ]),
        padding=10,
        expand=True,
    )

    page.add(
        ft.Column([
            sucursales_container
        ], scroll=ft.ScrollMode.AUTO, spacing=20, expand=True)
    )

    mostrar_sucursales_action()

ft.app(target=main)
