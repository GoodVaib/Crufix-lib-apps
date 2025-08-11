import os
import requests
import json
import tempfile
import webbrowser
import customtkinter as ctk
from PIL import Image, ImageOps
from io import BytesIO

# Настройки внешнего вида
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Конфигурация
DRIVE_BASE_URL = "https://drive.google.com/uc?export=download&id="
APPS_CONFIG_URL = "https://drive.google.com/uc?export=download&id=YOUR_CONFIG_FILE_ID"

class AppStore:
    def __init__(self):
        self.apps = []
        self.current_app = None
        self.image_cache = {}
        
        self.root = ctk.CTk()
        self.root.title("Crufix Library Apps")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        self.create_widgets()
        self.load_apps_data()
        
    def create_widgets(self):
        # Основная рамка
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Список приложений слева
        self.apps_frame = ctk.CTkScrollableFrame(
            self.main_frame, 
            width=250,
            label_text="Доступные приложения"
        )
        self.apps_frame.pack(side="left", fill="y", padx=(0, 10), pady=10)
        
        # Детали приложения справа
        self.details_frame = ctk.CTkFrame(self.main_frame)
        self.details_frame.pack(side="right", fill="both", expand=True, pady=10)
        
        # Элементы деталей
        self.app_icon = ctk.CTkLabel(self.details_frame, text="", width=200, height=200)
        self.app_icon.pack(pady=20)
        
        self.app_name = ctk.CTkLabel(
            self.details_frame, 
            text="Выберите приложение",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.app_name.pack(pady=5)
        
        self.app_version = ctk.CTkLabel(
            self.details_frame, 
            text="",
            text_color="gray70"
        )
        self.app_version.pack(pady=2)
        
        self.app_description = ctk.CTkTextbox(
            self.details_frame,
            height=150,
            wrap="word",
            font=ctk.CTkFont(size=14)
        )
        self.app_description.pack(fill="x", padx=20, pady=10)
        self.app_description.configure(state="disabled")
        
        # Скриншоты
        self.screenshots_label = ctk.CTkLabel(
            self.details_frame, 
            text="Скриншоты:",
            anchor="w",
            font=ctk.CTkFont(weight="bold")
        )
        self.screenshots_label.pack(fill="x", padx=20, pady=(10, 5))
        
        self.screenshots_frame = ctk.CTkScrollableFrame(
            self.details_frame,
            orientation="horizontal",
            height=150
        )
        self.screenshots_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        # Кнопка скачивания
        self.download_btn = ctk.CTkButton(
            self.details_frame,
            text="Скачать APK",
            command=self.download_app,
            height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#2aa244",
            hover_color="#1f8134"
        )
        self.download_btn.pack(fill="x", padx=50, pady=10)
        self.download_btn.configure(state="disabled")

    def load_apps_data(self):
        """Загрузка данных о приложениях"""
        try:
            response = requests.get(APPS_CONFIG_URL)
            response.raise_for_status()
            self.apps = json.loads(response.text)["apps"]
            self.display_apps_list()
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.apps_frame,
                text=f"Ошибка загрузки данных: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=20)

    def display_apps_list(self):
        """Отображение списка приложений"""
        for app in self.apps:
            # Создание рамки для приложения
            app_frame = ctk.CTkFrame(self.apps_frame, height=70)
            app_frame.pack(fill="x", pady=5, padx=5)
            app_frame.bind("<Button-1>", lambda e, a=app: self.show_app_details(a))
            
            # Загрузка иконки
            icon_url = f"{DRIVE_BASE_URL}{app['icon_id']}"
            try:
                if icon_url not in self.image_cache:
                    response = requests.get(icon_url)
                    img = Image.open(BytesIO(response.content))
                    img = ImageOps.fit(img, (50, 50), Image.LANCZOS)
                    self.image_cache[icon_url] = ctk.CTkImage(light_image=img, size=(50, 50))
                
                icon_label = ctk.CTkLabel(app_frame, image=self.image_cache[icon_url], text="")
                icon_label.pack(side="left", padx=10)
                icon_label.bind("<Button-1>", lambda e, a=app: self.show_app_details(a))
            except:
                icon_label = ctk.CTkLabel(app_frame, text="❌", width=50)
                icon_label.pack(side="left", padx=10)
            
            # Информация о приложении
            text_frame = ctk.CTkFrame(app_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
            text_frame.bind("<Button-1>", lambda e, a=app: self.show_app_details(a))
            
            name_label = ctk.CTkLabel(
                text_frame, 
                text=app["name"],
                anchor="w",
                font=ctk.CTkFont(weight="bold")
            )
            name_label.pack(fill="x", pady=(5, 0))
            
            version_label = ctk.CTkLabel(
                text_frame, 
                text=f"Версия: {app['version']}",
                anchor="w",
                text_color="gray70"
            )
            version_label.pack(fill="x")

    def show_app_details(self, app):
        """Отображение деталей приложения"""
        self.current_app = app
        
        # Обновление основной информации
        self.app_name.configure(text=app["name"])
        self.app_version.configure(text=f"Версия: {app['version']}")
        
        # Описание
        self.app_description.configure(state="normal")
        self.app_description.delete("1.0", "end")
        self.app_description.insert("1.0", app["description"])
        self.app_description.configure(state="disabled")
        
        # Загрузка иконки
        icon_url = f"{DRIVE_BASE_URL}{app['icon_id']}"
        try:
            if icon_url not in self.image_cache:
                response = requests.get(icon_url)
                img = Image.open(BytesIO(response.content))
                img = ImageOps.fit(img, (200, 200), Image.LANCZOS)
                self.image_cache[icon_url] = ctk.CTkImage(light_image=img, size=(200, 200))
            
            self.app_icon.configure(image=self.image_cache[icon_url])
        except:
            self.app_icon.configure(image=None, text="❌ Иконка недоступна")
        
        # Очистка скриншотов
        for widget in self.screenshots_frame.winfo_children():
            widget.destroy()
        
        # Загрузка скриншотов
        for screenshot_id in app["screenshot_ids"]:
            screenshot_url = f"{DRIVE_BASE_URL}{screenshot_id}"
            try:
                # Асинхронная загрузка для производительности
                self.root.after(0, lambda url=screenshot_url: self.load_screenshot(url))
            except Exception as e:
                print(f"Ошибка загрузки скриншота: {e}")
        
        # Активация кнопки скачивания
        self.download_btn.configure(state="normal")

    def load_screenshot(self, url):
        """Загрузка и отображение скриншота"""
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            img = ImageOps.fit(img, (200, 350), Image.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img, size=(200, 350))
            
            screenshot_label = ctk.CTkLabel(
                self.screenshots_frame, 
                image=ctk_img, 
                text=""
            )
            screenshot_label.pack(side="left", padx=5)
        except:
            screenshot_label = ctk.CTkLabel(
                self.screenshots_frame, 
                text="❌\nСкриншот\nне загружен",
                width=100,
                height=150,
                justify="center"
            )
            screenshot_label.pack(side="left", padx=5)

    def download_app(self):
        """Скачивание приложения"""
        if not self.current_app:
            return
        
        apk_url = f"{DRIVE_BASE_URL}{self.current_app['apk_id']}"
        try:
            webbrowser.open(apk_url)
        except Exception as e:
            error_dialog = ctk.CTkToplevel(self.root)
            error_dialog.title("Ошибка")
            error_dialog.geometry("300x150")
            
            ctk.CTkLabel(
                error_dialog, 
                text=f"Не удалось открыть ссылку для скачивания:\n{str(e)}",
                justify="center",
                wraplength=280
            ).pack(pady=20, padx=10)
            
            ctk.CTkButton(
                error_dialog, 
                text="OK", 
                command=error_dialog.destroy
            ).pack(pady=10)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app_store = AppStore()
    app_store.run()