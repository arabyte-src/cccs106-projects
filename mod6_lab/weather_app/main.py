# main.py
"""Weather Application using Flet v0.28.3 with search history, unit toggle, and persistent watchlist."""

import flet as ft
from weather_service import WeatherService
from config import Config
import asyncio
import json
import os

WATCHLIST_FILE = "watchlist.json"


class WeatherApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.search_history = []
        self.watchlist = self.load_watchlist()
        self.current_unit = "metric"
        self.current_temp = 0
        self.current_city = None

        self.setup_page()
        self.build_ui()
        self.refresh_watchlist_panel()

    def setup_page(self):
        self.page.title = Config.APP_TITLE

        # SINGLE THEME (system default)
        self.page.theme = ft.Theme(use_material3=True)
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.padding = 20
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False
        self.page.window.center()

    def build_ui(self):
        # Title
        self.title = ft.Text("⛅ Weather App", size=32, weight=ft.FontWeight.BOLD)
        self.theme_button = ft.IconButton(icon=ft.Icons.DARK_MODE, tooltip="Toggle theme", on_click=self.toggle_theme)
        title_row = ft.Row([self.title, self.theme_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # City input
        self.city_input = ft.TextField(
            hint_text="e.g., London, Tokyo, New York",
            prefix_icon=ft.Icons.LOCATION_CITY_OUTLINED,
            autofocus=True,
            expand=True,
            on_submit=self.on_search,
            on_focus=self.show_history_dropdown,
            on_blur=self.hide_history_dropdown,
            border_color="#054181",          # normal border color
            focused_border_color="#054181"   # border color when focused
        )

        self.search_button = ft.IconButton(icon=ft.Icons.SEARCH_OUTLINED, on_click=self.on_search)
        self.unit_button = ft.TextButton(f"°C", on_click=self.toggle_units)

        self.input_row = ft.Row([self.city_input, self.search_button, self.unit_button],
                                spacing=10, alignment=ft.MainAxisAlignment.CENTER, expand=True)

        # Search history
        self.history_container = ft.Container(content=ft.Column([], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.START),
                                             visible=False, border_radius=5, padding=5)
        self.clear_history_button = ft.TextButton("Clear History", on_click=self.clear_history, visible=False)
        self.input_column = ft.Column([self.input_row, self.history_container, self.clear_history_button],
                                      spacing=5, horizontal_alignment=ft.CrossAxisAlignment.START)

        # Weather container
        self.weather_container = ft.Container(
            visible=False,
            bgcolor="#eef1ff",
            border_radius=7,
            padding=30,
            width=800,
            height=450
        )

        # Add button
        self.add_to_watchlist_button = ft.ElevatedButton(
            "Add city to watchlist",
            on_click=self.add_current_city_to_watchlist,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),  # radius
                color={"default": ft.Colors.BLACK, "hovered": ft.Colors.BLACK},  # font color
                bgcolor={"default": ft.Colors.WHITE, "hovered": "#054181"}  # background color
            )
            
        )



        # Watchlist
        self.watchlist_column = ft.Column(spacing=10)
        self.watchlist_panel = ft.Container(
            content=ft.Column([
                ft.Text("City Comparison", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                self.watchlist_column
            ], spacing=8),
            width=350,
            padding=12,
            bgcolor="#eef1ff",
            border_radius=10
        )

        # Error & loading
        self.error_message = ft.Text("", visible=False)
        self.loading = ft.ProgressRing(visible=False)

        # Row with weather and watchlist panel
        weather_watchlist_row = ft.Row(
            [self.weather_container, ft.Container(width=20), self.watchlist_panel],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True
        )

        # Main layout
        main_row = ft.Row([
            ft.Column([
                title_row,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                self.input_column,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.loading,
                self.error_message,
                weather_watchlist_row,
                ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6, expand=True)
        ])

        self.page.controls.clear()
        self.page.add(main_row)
        self.page.update()

    # ------------------ Theme ------------------
    def toggle_theme(self, e):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
        self.page.update()

    # ------------------ Search ------------------
    def on_search(self, e):
        city = self.city_input.value.strip()
        if not city:
            self.show_error("Please enter a city name")
            return
        if city not in self.search_history:
            self.search_history.insert(0, city)
        self.update_history_dropdown()
        self.page.run_task(self.get_weather)

    async def get_weather(self):
        city = self.city_input.value.strip()
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.add_to_watchlist_button.visible = False
        self.page.update()
        try:
            data = await self.weather_service.get_weather(city, unit=self.current_unit)
            await self.display_weather(data)
        except Exception as e:
            self.show_error(str(e))
        finally:
            self.loading.visible = False
            self.page.update()

    async def display_weather(self, data: dict):
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = data.get("main", {}).get("temp", 0)
        self.current_temp = temp
        self.current_city = city_name
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        pressure = data.get("main", {}).get("pressure", 0)
        clouds = data.get("clouds", {}).get("all", 0)

        self.temp_text = ft.Text(f"{temp:.1f}°{'C' if self.current_unit=='metric' else 'F'}", size=48, weight=ft.FontWeight.BOLD, color="#054181")
        
        left_column = ft.Column(
            [
                ft.Text(f"{city_name}, {country}", size=24, weight=ft.FontWeight.BOLD, color="#054181"),
                ft.Image(src=f"https://openweathermap.org/img/wn/{icon_code}@4x.png", width=120, height=120),
                self.temp_text,
                ft.Text(description, size=18, italic=True, color="#054181")
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )


        right_column = ft.Column([
            self.create_info_card("Humidity", f"{humidity}%", ft.Icons.WATER_DROP),
            self.create_info_card("Wind", f"{wind_speed} m/s", ft.Icons.AIR),
            self.create_info_card("Pressure", f"{pressure} hPa", ft.Icons.SPEED),
            self.create_info_card("Clouds", f"{clouds}%", ft.Icons.CLOUD)
        ], spacing=10)

        self.weather_container.content = ft.Column([
            ft.Row([left_column, ft.Container(width=30), right_column], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            self.add_to_watchlist_button
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.add_to_watchlist_button.visible = True
        self.weather_container.visible = True
        self.page.update()

    def create_info_card(self, label, value, icon):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=20),
                ft.Container(width=8),
                ft.Column([
                    ft.Text(label, size=12, color=ft.Colors.BLACK),
                    ft.Text(value, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)
                ], spacing=2)
            ], spacing=5),
            border_radius=10,
            padding=10,
            width=160
        )

    def show_error(self, message: str):
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.add_to_watchlist_button.visible = False
        self.page.update()

    # ------------------ Search History ------------------
    def update_history_dropdown(self):
        self.history_container.content.controls.clear()
        for city in self.search_history:
            self.history_container.content.controls.append(
                ft.TextButton(text=city, on_click=lambda e, c=city: self.select_history(c))
            )
        self.page.update()

    def select_history(self, city):
        self.city_input.value = city
        self.hide_history_dropdown(None)
        self.page.update()
        self.on_search(None)

    def show_history_dropdown(self, e):
        if self.search_history:
            self.history_container.visible = True
            self.clear_history_button.visible = True
            self.page.update()

    def hide_history_dropdown(self, e):
        self.history_container.visible = False
        self.clear_history_button.visible = False
        self.page.update()

    def clear_history(self, e):
        self.search_history.clear()
        self.hide_history_dropdown(None)
        self.page.update()

    # ------------------ Unit Toggle ------------------
    def toggle_units(self, e):
        if self.current_unit == "metric":
            self.current_unit = "imperial"
            self.current_temp = (self.current_temp * 9 / 5) + 32
            self.unit_button.text = "°F"
        else:
            self.current_unit = "metric"
            self.current_temp = (self.current_temp - 32) * 5 / 9
            self.unit_button.text = "°C"
        self.refresh_watchlist_panel()
        self.update_display()

    def update_display(self):
        if hasattr(self, "temp_text"):
            self.temp_text.value = f"{self.current_temp:.1f}°{'C' if self.current_unit=='metric' else 'F'}"
            self.page.update()


    # ------------------ Watchlist ------------------
    def add_current_city_to_watchlist(self, e):
        if not self.current_city or self.current_city in self.watchlist:
            return
        self.watchlist.append(self.current_city)
        self.save_watchlist()
        self.refresh_watchlist_panel()

    def load_watchlist(self):
        if os.path.exists(WATCHLIST_FILE):
            try:
                with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_watchlist(self):
        with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(self.watchlist, f, ensure_ascii=False, indent=2)

    def refresh_watchlist_panel(self):
        self.watchlist_column.controls.clear()
        if not self.watchlist:
            self.watchlist_column.controls.append(ft.Text("No cities in watchlist.", italic=True, color=ft.Colors.BLACK))
            self.page.update()
            return

        for city in self.watchlist:
            placeholder = ft.Container(content=ft.Row([ft.Text(city, color=ft.Colors.BLACK), ft.ProgressRing()],
                                                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                       padding=8, border_radius=8)
            self.watchlist_column.controls.append(placeholder)

            async def _fetch(c=city, container=placeholder):
                try:
                    data = await self.weather_service.get_weather(c, unit=self.current_unit)
                    name = data.get("name", c)
                    country = data.get("sys", {}).get("country", "")
                    temp = data.get("main", {}).get("temp", 0)
                    icon = data.get("weather", [{}])[0].get("icon", "01d")
                    desc = data.get("weather", [{}])[0].get("description", "").title()

                    card = ft.Container(content=ft.Row([
                        ft.Column([
                            ft.Text(f"{name}, {country}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                            ft.Row([
                                ft.Image(src=f"https://openweathermap.org/img/wn/{icon}.png", width=44, height=44),
                                ft.Column([
                                    ft.Text(f"{temp:.1f}°{'C' if self.current_unit=='metric' else 'F'}", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                                    ft.Text(desc, size=12, italic=True, color=ft.Colors.BLACK)
                                ])
                            ])
                        ], spacing=6),
                        ft.Column([ft.IconButton(icon=ft.Icons.REMOVE_CIRCLE_OUTLINE, tooltip="Remove",
                                                 on_click=lambda e, c=city: self.remove_from_watchlist(c))],
                                  alignment=ft.MainAxisAlignment.CENTER, spacing=6)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), padding=8, border_radius=10)

                    idx = self.watchlist_column.controls.index(container)
                    self.watchlist_column.controls[idx] = card
                    self.page.update()
                except Exception:
                    err_card = ft.Container(content=ft.Row([ft.Text(city), ft.Text(" — error")]),
                                            padding=8, border_radius=8)
                    try:
                        idx2 = self.watchlist_column.controls.index(container)
                        self.watchlist_column.controls[idx2] = err_card
                    except ValueError:
                        self.watchlist_column.controls.append(err_card)
                    self.page.update()

            self.page.run_task(_fetch)

    def remove_from_watchlist(self, city):
        if city in self.watchlist:
            self.watchlist.remove(city)
            self.save_watchlist()
            self.refresh_watchlist_panel()


# ------------------ Main ------------------
def main(page: ft.Page):
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)
