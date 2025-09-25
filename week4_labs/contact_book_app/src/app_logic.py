# app_logic.py
import flet as ft
from database import update_contact_db, delete_contact_db, add_contact_db, get_all_contacts_db
import re


primary_color = "#58835A"
light_theme = ft.Theme(color_scheme_seed=primary_color, use_material3=True)
dark_theme = ft.Theme(color_scheme_seed=primary_color, use_material3=True)

def display_contacts(page, contacts_list_view, db_conn, search_text=""):
    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(conn=db_conn, search_term=search_text)

    for contact in contacts:
        contact_id, name, phone, email = contact

        contact_card = ft.Card(
            color="#E7FFE9",
            content=ft.Container(
                padding=10,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(name.upper(), size=18, weight="bold", color=primary_color),
                                        ft.Row([
                                            ft.Icon(ft.Icons.PHONE_OUTLINED, size=16, color=primary_color),
                                            ft.Text(phone, color=primary_color),
                                        ]),
                                        ft.Row([
                                            ft.Icon(ft.Icons.EMAIL_OUTLINED, size=16, color=primary_color),
                                            ft.Text(email, color=primary_color),
                                        ])
                                    ],
                                    expand=True
                                ),
                                ft.PopupMenuButton(
                                    icon=ft.Icons.MORE_VERT,
                                    items=[
                                        ft.PopupMenuItem(
                                            text="Edit",
                                            icon=ft.Icons.EDIT,
                                            on_click=lambda _, c=contact: open_edit_dialog(page, c, db_conn, contacts_list_view)
                                        ),
                                        ft.PopupMenuItem(),
                                        ft.PopupMenuItem(
                                            text="Delete",
                                            icon=ft.Icons.DELETE,
                                            on_click=lambda _, cid=contact_id: delete_contact(page, cid, db_conn, contacts_list_view)
                                        ),
                                    ],
                                ),
                            ]
                        )
                    ]
                )
            ),
            elevation=3,
            shape=ft.RoundedRectangleBorder(radius=8)
        )

        contacts_list_view.controls.append(contact_card)

    page.update()


def add_contact(page, inputs, contacts_list_view, db_conn):
    name_input, phone_input, email_input = inputs
    
    '''
    Email Pattern, uses regex to make sure there's something before @, 
    something after @, and a dot with at least 2 letters (like .com)
    '''
    EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

    has_error = False
    # name validation
    if not name_input.value.strip():
        name_input.error_text = "Name cannot be empty"
        has_error = True
    else:
        name_input.error_text = None
        
    # Phone validation

    if not phone_input.value.strip():
        phone_input.error_text = "Phone must be a valid number"
        has_error = True
    else:
        if not phone_input.value.isdigit(): 
            phone_input.error_text = "Invalid phone number"
            has_error = True
        else:
            phone_input.error_text = None
            

    if not email_input.value.strip():
        email_input.error_text = "Email cannot be empty"
        has_error = True
    else:
        if not EMAIL_PATTERN.match(email_input.value):
            email_input.error_text = "Invalid email address"
            has_error = True
        else:
            email_input.error_text = None
            
    if has_error:
        page.update()
        return

    add_contact_db(db_conn, name_input.value, phone_input.value, email_input.value)

    for field in inputs:
        field.value = ""

    display_contacts(page, contacts_list_view, db_conn)
    page.update()

def delete_contact(page, contact_id, db_conn, contacts_list_view):
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirm Delete", weight=ft.FontWeight.BOLD),
        content=ft.Text("Are you sure you want to delete this contact?"),
        actions=[
            ft.TextButton(
                "No",
                on_click=lambda e: setattr(dialog, "open", False) or page.update()
            ),
            ft.TextButton(
                "Yes",
                on_click=lambda e: confirm_delete(page, contact_id, db_conn, contacts_list_view, dialog)
            ),
        ],
    )
    page.open(dialog)

def confirm_delete(page, contact_id, db_conn, contacts_list_view, dialog):
    delete_contact_db(db_conn, contact_id)
    dialog.open = False
    page.update()
    display_contacts(page, contacts_list_view, db_conn)
    
    
def open_edit_dialog(page, contact, db_conn, contacts_list_view):
    contact_id, name, phone, email = contact

    edit_name = ft.TextField(
        label="Name",
        value=name,
        border_color=primary_color,
        focused_border_color=primary_color
    )
    edit_phone = ft.TextField(
        label="Phone",
        value=phone,
        border_color=primary_color,
        focused_border_color=primary_color
    )
    edit_email = ft.TextField(
        label="Email",
        value=email,
        border_color=primary_color,
        focused_border_color=primary_color
    )

    def save_and_close(e):
        update_contact_db(db_conn, contact_id, edit_name.value, edit_phone.value, edit_email.value)
        dialog.open = False
        page.update()
        display_contacts(page, contacts_list_view, db_conn)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Contact", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([edit_name, edit_phone, edit_email]),
            width=400,
            height=200
            
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
            ft.TextButton("Save", on_click=save_and_close),
        ],
    )
    page.open(dialog)
