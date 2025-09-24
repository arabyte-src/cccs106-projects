# main.py
import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact

def main(page: ft.Page):
    page.title = "Contact Book"
    page.window_width = 400
    page.window_height = 600
    page.scroll = "adaptive"
    page.padding=0
    
    # default color to use for text, icons, and borders
    primary_color = "#58835A"
    
    # define light and dark themes using the same primary color
    light_theme = ft.Theme(color_scheme_seed=primary_color, use_material3=True)
    dark_theme = ft.Theme(color_scheme_seed=primary_color, use_material3=True)

    page.theme = light_theme
    page.theme_mode = ft.ThemeMode.LIGHT

    db_conn = init_db()

    

    name_input = ft.TextField(
        label="Name",
        prefix_icon=ft.Icon(ft.Icons.PERSON_OUTLINE, color=primary_color),
        width=350,
        border_color=primary_color,
        focused_border_color=primary_color,
        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=14, color=primary_color),
        label_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=13, color=primary_color)
    )

    phone_input = ft.TextField(
        label="Phone",
        prefix_icon=ft.Icon(ft.Icons.PHONE_OUTLINED, color=primary_color),
        width=350,
        border_color=primary_color,
        focused_border_color=primary_color,
        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=14, color=primary_color),
        label_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=13, color=primary_color)
    )

    email_input = ft.TextField(
        label="Email",
        prefix_icon=ft.Icon(ft.Icons.EMAIL_OUTLINED, color=primary_color),
        width=350,
        border_color=primary_color,
        focused_border_color=primary_color,
        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=14, color=primary_color),
        label_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=13, color=primary_color)
    )

    inputs = (name_input, phone_input, email_input)

    contacts_list_view = ft.ListView(expand=1, spacing=10, auto_scroll=True, padding=10)


    search_field = ft.Container(
    content=ft.TextField(
        label="Search by name",
        expand=True,
        prefix_icon=ft.Icon(ft.Icons.SEARCH, color=primary_color),
        border_color=primary_color,
        focused_border_color=primary_color,
        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=14, color=primary_color),
        label_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=13, color=primary_color),
        on_change=lambda e: display_contacts(page, contacts_list_view, db_conn, e.control.value),
    ),
    padding=10
    )


    add_button = ft.ElevatedButton(
        text="Add Contact",
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn),
        style=ft.ButtonStyle(
            bgcolor=primary_color,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=10),
            text_style=ft.TextStyle(size=15)
        )
    )

    theme_button = ft.IconButton(
        icon=ft.Icons.DARK_MODE_OUTLINED,
    )

    
    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            theme_button.icon = ft.Icons.WB_SUNNY_OUTLINED  
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_button.icon = ft.Icons.DARK_MODE_OUTLINED  


        new_primary = page.theme.color_scheme.primary if page.theme.color_scheme else primary_color
        theme_button.icon.color = new_primary
        name_input.prefix_icon.color = new_primary
        name_input.text_style.color = new_primary
        name_input.label_style.color = new_primary
        phone_input.prefix_icon.color = new_primary
        phone_input.text_style.color = new_primary
        phone_input.label_style.color = new_primary
        email_input.prefix_icon.color = new_primary
        email_input.text_style.color = new_primary
        email_input.label_style.color = new_primary
        search_field.content.prefix_icon.color = new_primary
        search_field.content.text_style.color = new_primary
        search_field.content.label_style.color = new_primary
        add_button.style.bgcolor = new_primary

        page.update()

    theme_button.on_click = toggle_theme
    
    header_row = ft.Container(
        content=ft.Row(
            [
                ft.Text("CONTACT BOOK", weight=ft.FontWeight.BOLD, size=30, color=ft.Colors.WHITE),
                theme_button,
            ],
            alignment="spaceBetween",
            expand=True
        ),
        bgcolor=primary_color,
        padding=12,
        border_radius=ft.border_radius.all(0)
    )

    page.add(
        ft.Column(
            [
                header_row,
                ft.Container(height=20),
                ft.Column(
                    [
                        ft.Container(height=20),
                        ft.Text("Enter Contact Details", size=20, weight=ft.FontWeight.BOLD, color=primary_color),
                        name_input,
                        phone_input,
                        email_input,
                        add_button,
                        ft.Divider(),
                        ft.Text("Contacts", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=primary_color),
                        search_field,
                    ],
                    horizontal_alignment="center",
                    spacing=5,
                ),
                contacts_list_view
            ],
            spacing=10,
        )
    )

    display_contacts(page, contacts_list_view, db_conn)

if __name__ == "__main__":
    ft.app(target=main)
