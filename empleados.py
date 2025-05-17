import flet as ft
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Santiago16_",
    database="farmaciasguadalajara"
)

def crear_empleado(telefono, nombre, puesto, usuario, salario, sucursal, contra):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO empleados VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (telefono, nombre, puesto, usuario, salario, sucursal, contra)
    )
    db.commit()
    cursor.close()

def mostrar_empleados():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM empleados")
    resultados = cursor.fetchall()
    cursor.close()
    return resultados

def editar_empleado(telefono, nombre, puesto, usuario, salario, sucursal, contra):
    cursor = db.cursor()
    cursor.execute(
        "UPDATE empleados SET nombre=%s, puesto=%s, usuario=%s, salario=%s, sucursales=%s, contra=%s WHERE telefono=%s",
        (nombre, puesto, usuario, salario, sucursal, contra, telefono)
    )
    db.commit()
    cursor.close()

def eliminar_empleado(telefono):
    cursor = db.cursor()
    cursor.execute("DELETE FROM empleados WHERE telefono=%s", (telefono,))
    db.commit()
    cursor.close()

def telefono_existe(telefono):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM empleados WHERE telefono=%s", (telefono,))
    existe = cursor.fetchone()[0] > 0
    cursor.close()
    return existe

def main(page: ft.Page):
    page.title = "Farmacias Guadalajara - Empleados"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F5F1E9"
    page.padding = 20
    page.expand = True
    page.scroll = "auto"  

    titulo = ft.Text(
        "Gestión de Empleados",
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

    telefono_input = ft.TextField(
        label="Teléfono",
        border_color="#0066CC",
        width=400,
        input_filter=ft.NumbersOnlyInputFilter(),
        max_length=10
    )
    nombre_input = ft.TextField(label="Nombre", border_color="#0066CC", width=400)
    puesto_input = ft.TextField(label="Puesto", border_color="#0066CC", width=400)
    usuario_input = ft.TextField(label="Usuario", border_color="#0066CC", width=400)
    salario_input = ft.TextField(
        label="Salario (solo números positivos)",
        border_color="#0066CC",
        width=400,
        hint_text="Ingrese un valor mayor a 0"
    )
    sucursal_input = ft.TextField(
        label="Sucursal (ID)",
        border_color="#0066CC",
        width=400,
        input_filter=ft.NumbersOnlyInputFilter()
    )
    contra_input = ft.TextField(
        label="Contraseña",
        border_color="#0066CC",
        width=400,
        password=True,
        can_reveal_password=True
    )

    snackbar = ft.SnackBar(
        content=ft.Text("", color=ft.Colors.WHITE),
        bgcolor=ft.Colors.RED_400,
        duration=2000
    )
    page.snack_bar = snackbar

    inputs = ft.Column([
        telefono_input,
        nombre_input,
        puesto_input,
        usuario_input,
        salario_input,
        sucursal_input,
        contra_input
    ], spacing=10)

    
    empleados_grid = ft.Column(scroll="auto", spacing=10, expand=True)

    editando = False

    def limpiar_inputs():
        nonlocal editando
        for campo in [telefono_input, nombre_input, puesto_input, usuario_input,
                      salario_input, sucursal_input, contra_input]:
            campo.value = ""
            campo.error_text = None
        editando = False
        boton_crear.disabled = False
        boton_guardar.disabled = True
        page.update()

    def validar_telefono(telefono):
        return telefono.isdigit() and len(telefono) == 10

    def validar_campos():
        if not validar_telefono(telefono_input.value):
            telefono_input.error_text = "El teléfono debe tener 10 dígitos numéricos"
            return False
        else:
            telefono_input.error_text = None

        try:
            salario = float(salario_input.value)
            if salario <= 0:
                salario_input.error_text = "El salario debe ser un número positivo"
                return False
            salario_input.error_text = None
        except:
            salario_input.error_text = "Salario debe ser número válido"
            return False

        if not sucursal_input.value.isdigit():
            sucursal_input.error_text = "Sucursal debe ser un ID numérico"
            return False
        else:
            sucursal_input.error_text = None

        return True

    def crear_empleado_action(e):
        nonlocal editando
        if editando:
            return

        if telefono_existe(telefono_input.value):
            telefono_input.error_text = "Empleado ya existente"
            page.update()
            return

        if not validar_campos():
            page.update()
            return

        crear_empleado(
            telefono_input.value,
            nombre_input.value,
            puesto_input.value,
            usuario_input.value,
            float(salario_input.value),
            int(sucursal_input.value),
            contra_input.value
        )
        limpiar_inputs()
        mostrar_empleados_action()
        snackbar.content.value = "Empleado creado exitosamente"
        snackbar.bgcolor = ft.Colors.GREEN_400
        snackbar.open = True
        page.update()

    def mostrar_empleados_action(e=None):
        empleados_grid.controls.clear()
        empleados = mostrar_empleados()
        
       
        if not empleados:
            empleados_grid.controls.append(
                ft.Text("No hay empleados registrados", italic=True, color="grey")
            )
            page.update()
            return
        
        
        rows = []
        current_row = None
        
        for i, emp in enumerate(empleados):
            if i % 3 == 0:
                current_row = ft.Row(spacing=10, wrap=True)
                rows.append(current_row)
            
            card = ft.Card(
                ft.Container(
                    ft.Column([
                        ft.Text(f"📱 {emp[0]}", weight="bold"),
                        ft.Text(f"👤 {emp[1]}"),
                        ft.Text(f"💼 {emp[2]}"),
                        ft.Text(f"👤 Usuario: {emp[3]}"),
                        ft.Text(f"💰 Salario: ${float(emp[4]):,.2f}"),
                        ft.Text(f"🏬 Sucursal ID: {emp[5]}"),
                        ft.Row([
                            ft.IconButton(
                                ft.Icons.EDIT,
                                on_click=lambda e, tel=emp[0]: cargar_para_editar(tel),
                                icon_color=ft.Colors.BLUE_600,
                                tooltip="Editar"
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE,
                                on_click=lambda e, tel=emp[0]: eliminar_empleado_action(tel),
                                icon_color=ft.Colors.RED_600,
                                tooltip="Eliminar"
                            )
                        ], alignment=ft.MainAxisAlignment.END)
                    ], spacing=5),
                    padding=15,
                    width=350,
                ),
                color=ft.Colors.BLUE_50
            )
            current_row.controls.append(card)
        
        for row in rows:
            empleados_grid.controls.append(row)
   
        empleados_grid.controls.append(
            ft.Text(f"Total de empleados: {len(empleados)}", weight="bold", color="#0066CC")
        )
        
        page.update()

    def cargar_para_editar(telefono):
        nonlocal editando
        cursor = db.cursor()
        cursor.execute("SELECT * FROM empleados WHERE telefono=%s", (telefono,))
        emp = cursor.fetchone()
        cursor.close()
        if emp:
            telefono_input.value = emp[0]
            telefono_input.error_text = None
            nombre_input.value = emp[1]
            puesto_input.value = emp[2]
            usuario_input.value = emp[3]
            salario_input.value = str(emp[4])
            sucursal_input.value = str(emp[5])
            contra_input.value = emp[6]
            editando = True
            boton_crear.disabled = True
            boton_guardar.disabled = False
            page.update()

    def editar_empleado_action(e):
        nonlocal editando
        if not validar_campos():
            page.update()
            return

        editar_empleado(
            telefono_input.value,
            nombre_input.value,
            puesto_input.value,
            usuario_input.value,
            float(salario_input.value),
            int(sucursal_input.value),
            contra_input.value
        )
        limpiar_inputs()
        mostrar_empleados_action()
        snackbar.content.value = "Empleado actualizado exitosamente"
        snackbar.bgcolor = ft.Colors.GREEN_400
        snackbar.open = True
        page.update()
        editando = False

    def eliminar_empleado_action(telefono):
        eliminar_empleado(telefono)
        mostrar_empleados_action()
        snackbar.content.value = "Empleado eliminado exitosamente"
        snackbar.bgcolor = ft.Colors.GREEN_400
        snackbar.open = True
        page.update()
        limpiar_inputs()

    def create_button(text, action, color, disabled=False):
        return ft.ElevatedButton(
            text,
            on_click=action,
            bgcolor=color,
            color="white",
            height=40,
            width=150,
            disabled=disabled
        )

    boton_crear = create_button("Crear", crear_empleado_action, "#795548", disabled=False)
    boton_guardar = create_button("Guardar", editar_empleado_action, "#2196F3", disabled=True)

    buttons = ft.Row([
        boton_crear,
        boton_guardar
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

    empleados_container = ft.Container(
        ft.Column([
            ft.Text("Empleados Registrados", size=18, weight="bold", color="#0066CC"),
            ft.Container(
                empleados_grid,
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
            header,
            ft.Container(inputs, padding=20, alignment=ft.alignment.center),
            buttons,
            ft.Divider(height=20, color="transparent"),
            empleados_container
        ], scroll="auto", spacing=20, expand=True)
    )

    mostrar_empleados_action()

ft.app(target=main)