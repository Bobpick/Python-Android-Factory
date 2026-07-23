"""
Option 2 Example: Write the WHOLE app in Python -> APK

Install:
pip install kivy buildozer flet

This file shows 2 libraries:

1. KIVY - most mature
2. FLET - newest & easiest (Recommended for beginners in 2024-2026)

Pick one.
"""

# === FLET VERSION (Recommended) ===
# pip install flet
# Run on desktop: python OPTION_2_kivy_example.py
# Build for Android: pip install flet && flet pack your_app.py -i icon.png --distpath ./dist --android

import flet as ft

def main(page: ft.Page):
    page.title = "My Python Android App"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    def button_clicked(e):
        page.add(ft.Text(f"You typed: {name_input.value}"))
        page.snack_bar = ft.SnackBar(ft.Text(f"Hello {name_input.value}! Built with Python!"))
        page.snack_bar.open = True
        page.update()
    
    name_input = ft.TextField(label="Your Name", width=300)
    greet_btn = ft.ElevatedButton("Greet Me", on_click=button_clicked)
    
    page.add(
        ft.Column([
            ft.Text("Hello from Python to Android!", size=24, weight="bold"),
            name_input,
            greet_btn,
            ft.Text("This entire app is Python. No Kotlin/Java needed.")
        ], alignment="center")
    )

# Uncomment to run Flet app:
# ft.app(target=main)

# === KIVY VERSION ===
# from kivy.app import App
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.button import Button
# from kivy.uix.label import Label
# from kivy.uix.textinput import TextInput
#
# class MyApp(App):
#     def build(self):
#         layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
#         self.label = Label(text="Hello from Python!", font_size=24)
#         self.input = TextInput(hint_text="Enter your name", multiline=False)
#         btn = Button(text="Click Me", size_hint_y=None, height=60)
#         btn.bind(on_press=self.greet)
#         layout.add_widget(self.label)
#         layout.add_widget(self.input)
#         layout.add_widget(btn)
#         return layout
#
#     def greet(self, instance):
#         self.label.text = f"Hello {self.input.text}!"
#
# if __name__ == '__main__':
#     MyApp().run()
