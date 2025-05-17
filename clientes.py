import flet as ft
import mysql.connector

db = mysql.connector.connect(
    host="localhost", 
    user="root",        
    password="Santiago16_", 
    database="farmaciasguadalajara"  
)

def crear_cliente(telefono, nombre, correo):
    cursor = db.cursor()
    cursor.execute("INSERT INTO clientes VALUES (%s, %s, %s)", (telefono, nombre, correo))
    db.commit()
    cursor.close()

def mostrar_clientes():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM clientes")
    resultados = cursor.fetchall()
    cursor.close()
    return resultados

def editar_cliente(telefono, nombre, correo):
    cursor = db.cursor()
    cursor.execute("UPDATE clientes SET nombre=%s, correo=%s WHERE telefono=%s", (nombre, correo, telefono))
    db.commit()
    cursor.close()

def eliminar_cliente(telefono):
    cursor = db.cursor()
    cursor.execute("DELETE FROM clientes WHERE telefono=%s", (telefono,))
    db.commit()
    cursor.close()

def telefono_existe(telefono):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM clientes WHERE telefono=%s", (telefono,))
    existe = cursor.fetchone()[0] > 0
    cursor.close()
    return existe

def main(page: ft.Page):
    page.title = "Farmacias Guadalajara - Clientes"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F5F1E9"
    page.padding = 20
    page.expand = True

    titulo = ft.Text(
        "Gestión de Clientes", 
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
    correo_input = ft.TextField(label="Correo", border_color="#0066CC", width=400)
    

    snackbar = ft.SnackBar(
        content=ft.Text("", color=ft.Colors.WHITE), 
        bgcolor=ft.Colors.RED_400,
        duration=2000
    )
    page.snack_bar = snackbar
    
    inputs = ft.Column([telefono_input, nombre_input, correo_input], spacing=10)
    clientes_list = ft.ListView(expand=True, spacing=10)

    editando = False

    def limpiar_inputs():
        nonlocal editando
        telefono_input.value = ""
        telefono_input.error_text = None
        nombre_input.value = ""
        correo_input.value = ""
        editando = False
        boton_crear.disabled = False
        boton_guardar.disabled = True
        page.update()
    
    def validar_telefono(telefono):
        return telefono.isdigit() and len(telefono) == 10

    def validar_campos():
        if not nombre_input.value.strip():
            snackbar.content.value = "El nombre es obligatorio"
            snackbar.bgcolor = ft.Colors.RED_400
            snackbar.open = True
            page.update()
            return False
        if not correo_input.value.strip():
            snackbar.content.value = "El correo es obligatorio"
            snackbar.bgcolor = ft.Colors.RED_400
            snackbar.open = True
            page.update()
            return False
        return True
    
    def crear_cliente_action(e):
        nonlocal editando
        telefono_input.error_text = None  # Limpiar error previo
        
        if not validar_telefono(telefono_input.value):
            telefono_input.error_text = "El teléfono debe tener 10 dígitos numéricos"
            page.update()
            return
        
        if telefono_existe(telefono_input.value):
            telefono_input.error_text = "Cliente ya existente"
            page.update()
            return
        
        if not validar_campos():
            return
        
        crear_cliente(telefono_input.value, nombre_input.value, correo_input.value)
        limpiar_inputs()
        mostrar_clientes_action()
        snackbar.content.value = "Cliente creado exitosamente"
        snackbar.bgcolor = ft.Colors.GREEN_400
        snackbar.open = True
        page.update()
    
    def mostrar_clientes_action(e=None):
        clientes_list.controls.clear()
        for cliente in mostrar_clientes():
            clientes_list.controls.append(
                ft.Card(
                    ft.Container(
                        ft.Column([ 
                            ft.Text(f"📱 {cliente[0]}", weight="bold"),
                            ft.Text(f"👤 {cliente[1]}"),
                            ft.Text(f"✉️ {cliente[2]}"),
                            ft.Row([ 
                                crear_boton_editar(cliente[0]),
                                crear_boton_eliminar(cliente[0])
                            ], alignment=ft.MainAxisAlignment.END)
                        ], spacing=5),
                        padding=15,
                        width=400
                    ),
                    color=ft.Colors.BLUE_50
                )
            )
        page.update()

    def crear_boton_editar(telefono):
        return ft.IconButton(
            ft.Icons.EDIT, 
            on_click=lambda e: cargar_para_editar(telefono),
            tooltip="Editar",
            icon_color=ft.Colors.BLUE_600
        )
    
    def crear_boton_eliminar(telefono):
        return ft.IconButton(
            ft.Icons.DELETE, 
            on_click=lambda e: eliminar_cliente_action(telefono),
            tooltip="Eliminar",
            icon_color=ft.Colors.RED_600
        )
    
    def cargar_para_editar(telefono):
        nonlocal editando
        cursor = db.cursor()
        cursor.execute("SELECT * FROM clientes WHERE telefono=%s", (telefono,))
        cliente = cursor.fetchone()
        cursor.close()
        if cliente:
            telefono_input.value = cliente[0]
            telefono_input.error_text = None
            nombre_input.value = cliente[1]
            correo_input.value = cliente[2]
            editando = True
            boton_crear.disabled = True
            boton_guardar.disabled = False
            page.update()
    
    def editar_cliente_action(e):
        nonlocal editando
        telefono_input.error_text = None  
        
        if not validar_telefono(telefono_input.value):
            telefono_input.error_text = "El teléfono debe tener 10 dígitos numéricos"
            page.update()
            return
        
        if not validar_campos():
            return
        
        editar_cliente(telefono_input.value, nombre_input.value, correo_input.value)
        limpiar_inputs()
        mostrar_clientes_action()
        snackbar.content.value = "Cliente actualizado exitosamente"
        snackbar.bgcolor = ft.Colors.GREEN_400
        snackbar.open = True
        page.update()
        editando = False
    
    def eliminar_cliente_action(telefono):
        eliminar_cliente(telefono)
        mostrar_clientes_action()
        snackbar.content.value = "Cliente eliminado exitosamente"
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
    
    boton_crear = create_button("Crear", crear_cliente_action, "#795548", disabled=False)
    boton_guardar = create_button("Guardar", editar_cliente_action, "#2196F3", disabled=True)

    buttons = ft.Row([
        boton_crear,
        boton_guardar
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    
    page.add(
        ft.Column([
            header,
            ft.Container(inputs, padding=20, alignment=ft.alignment.center),
            buttons,
            ft.Divider(height=20, color="transparent"),
            ft.Text("Clientes Registrados", size=18, weight="bold", color="#0066CC"),
            ft.Container(
                clientes_list,
                padding=10,
                border_radius=10,
                bgcolor="#F5F5F5",
                height=600,
                expand=True,
            )
        ], spacing=20, expand=True)
    )
    
    mostrar_clientes_action()

ft.app(target=main)
