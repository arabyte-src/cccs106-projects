import flet as ft
import mysql.connector
from db_connection import connect_db

def main(page: ft.Page):
    page.window.center()
    page.window.frameless = True
    page.window.title_bar_hidden = True
    page.window.title_bar_buttons_hidden = True
    page.title = "User Login"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.height = 350
    page.window.width = 400
    page.bgcolor = ft.Colors.AMBER_ACCENT
    page.window.always_on_top = True
    
    login_title = ft.Text(
        "User Login",
        text_align=ft.TextAlign.CENTER,
        size=20,
        weight=ft.FontWeight.BOLD,
        font_family="Arial"
    )

    username_field = ft.TextField(
        label="Username",
        hint_text="Enter your username",
        helper_text="This is your unique identifier",
        width=300,
        autofocus=True,
        icon=ft.Icons.PERSON,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT
    )

    password_field = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        helper_text="This is your secret key",
        width=300,
        password=True,
        can_reveal_password=True,
        icon=ft.Icons.PASSWORD,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT
    )

    def login_click(e):
        username = username_field.value
        password = password_field.value

        success_dialog = ft.AlertDialog(
            title=ft.Text("Login Successful", text_align="center"),
            content=ft.Text(f"Welcome, {username}!", text_align="center"),
            actions=[
                ft.TextButton(
                    "OK",
                    on_click=lambda ev: close_dialog(success_dialog)
                )
            ],
            icon=ft.Icon(ft.Icons.CHECK_CIRCLE, color="green"),
        )

        failure_dialog = ft.AlertDialog(
            title=ft.Text("Login Failed", text_align="center"),
            content=ft.Text("Invalid username or password", text_align="center"),
            actions=[
                ft.TextButton(
                    "OK",
                    on_click=lambda ev: close_dialog(failure_dialog)
                )
            ],
            icon=ft.Icon(ft.Icons.ERROR, color="red"),
        )

        invalid_input_dialog = ft.AlertDialog(
            title=ft.Text("Input Error", text_align="center"),
            content=ft.Text("Please enter username and password", text_align="center"),
            actions=[
                ft.TextButton(
                    "OK",
                    on_click=lambda ev: close_dialog(invalid_input_dialog)
                )
            ],
            icon=ft.Icon(ft.Icons.INFO, color="blue"),
        )

        database_error_dialog = ft.AlertDialog(
            title=ft.Text("Database Error", text_align="center"),
            content=ft.Text(
                "An error occurred while connecting to the database",
                text_align="center",
            ),
            actions=[
                ft.TextButton(
                    "OK",
                    on_click=lambda ev: close_dialog(database_error_dialog)
                )
            ],
            icon=ft.Icon(ft.Icons.ERROR, color="red"),
        )

        if not username or not password:
            page.open(invalid_input_dialog)
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username, password),
            )
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                page.open(success_dialog)
            else:
                page.open(failure_dialog)

        except mysql.connector.Error:
            page.open(database_error_dialog)


    def close_dialog(dlg: ft.AlertDialog):
        dlg.open = False
        page.update()



    login_button = ft.ElevatedButton(
        text="Login",
        on_click=login_click,
        width=100,
        icon=ft.Icons.LOGIN,
    )

    
    page.add(
        login_title,
        ft.Container(
            content=ft.Column([username_field, password_field], spacing=20),
            alignment=ft.alignment.center,
        ),
        ft.Container(
            content=login_button,
            alignment=ft.alignment.top_right,
            margin=ft.Margin(0, 20, 40, 0),
        ),
    )

ft.app(target=main)
