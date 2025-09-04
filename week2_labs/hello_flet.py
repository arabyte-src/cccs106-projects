# hello_flet.py
# CCCS 106 - Week 2 Lab Exercise
# First Flet GUI Application
# Student: [Arabella Bayta]

import flet as ft
from datetime import datetime

def main(page: ft.Page):
        # Dark mode toggle
    def toggle_theme(e):
        if theme_switch.value:
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
        page.update()

    theme_switch = ft.Switch(
        label="DARK MODE",
        value=False,     # start in Light Mode (unchecked)
        scale=0.7,
        on_change=toggle_theme
    )

    # Page configuration
    page.title = "CCCS 106 - Hello Flet"
    page.window.width = 450
    page.window.height = 650
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT   # start in Light Mode

    
    # Title with styling
    title = ft.Text(
        "CCCS 106: Hello Flet Application".upper(),
        size=24,
        font_family= 'Roboto Condensed Black',
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
        color=ft.Colors.BLUE_700
    )
    
    # Student information (update with your details)
    student_info = ft.Column([
        ft.Text("Student Information", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700, font_family= 'Roboto Condensed Medium'),
        ft.Text("Name: Arabella Bayta", size=12),
        ft.Text("Student ID: 231004406", size=12),
        ft.Text("Program: BSCS", size=12),
        ft.Text(f"Date: {datetime.now().strftime('%B %d, %Y')}", size=12),
    ])
    
    # Interactive name input
    name_input = ft.TextField(
        label= "Enter your name",
        text_size=15,
        width=300,
        height=50,
        border_color=ft.Colors.BLUE_300,
        text_align=ft.TextAlign.CENTER,
        border_radius=10
    )
    
    # Output text for greetings
    greeting_text = ft.Text(
        "",
        size=15,
        text_align=ft.TextAlign.CENTER,
        color=ft.Colors.BLUE_800
    )
    
    # Button functions
    def say_hello(e):
        if name_input.value:
            greeting_text.value = f"Hello, {name_input.value}! Welcome to Flet GUI development!"
        else:
            greeting_text.value = "Please enter your name first!"
        page.update()
    
    def clear_all(e):
        name_input.value = ""
        greeting_text.value = ""
        page.update()
    
    def show_info(e):
        info_text = (
            "This is a Flet 0.28.3 application built for CCCS 106.\n"
            "Flet allows you to create beautiful GUI applications using Python!\n"
            f"Current time: {datetime.now().strftime('%I:%M:%S %p')}"
        )
        
        # Create dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Application Information"),
            content=ft.Text(info_text),
            actions=[
                ft.TextButton("Close", on_click=lambda e: close_dialog(dialog))
            ]
        )
        page.open(dialog)
        
        def close_dialog(dialog):
            dialog.open = False
            page.update()
    
    # Buttons with styling
    hello_button = ft.ElevatedButton(
        "Say Hello",
        on_click=say_hello,
        width=93,
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=8))
    )
    
    clear_button = ft.ElevatedButton(
        "Clear",
        on_click=clear_all,
        width=93,
        bgcolor=ft.Colors.RED_600,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=8))
    )
    
    info_button = ft.ElevatedButton(
        "App Info",
        on_click=show_info,
        width=93,
        bgcolor=ft.Colors.GREEN_600,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=8))
    )
    
    # Layout using containers and columns
    page.add(
        ft.Container(
            content=ft.Column([
                # Row for switch (right aligned)
                ft.Row(
                    [theme_switch],
                    alignment=ft.MainAxisAlignment.END
                ),
                title,
                ft.Divider(height=10),
                student_info,
                ft.Divider(height=10),
                ft.Text(
                    "Interactive Section", 
                    size=16, 
                    weight=ft.FontWeight.BOLD, 
                    color=ft.Colors.BLUE_700, 
                    font_family='Roboto Condensed Medium'
                ),
                name_input,
                ft.Row(
                    [hello_button, clear_button, info_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                ),
                ft.Divider(height=10),
                greeting_text,
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20),
            padding=40
        )
    )


# Run the application
if __name__ == "__main__":
    ft.app(target=main)