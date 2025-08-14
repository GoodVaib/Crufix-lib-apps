import os
import json
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.uix.list import MDList, OneLineAvatarListItem, ImageLeftWidget

# Конфигурация
REPO_URL = "https://raw.githubusercontent.com/ваш-аккаунт/ваш-репозиторий/ветка"
INDEX_FILE = f"{REPO_URL}/apps.json"

class AppListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.scroll = ScrollView()
        self.list_view = MDList()
        
        self.load_data()
        self.scroll.add_widget(self.list_view)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

    def load_data(self):
        try:
            response = requests.get(INDEX_FILE)
            apps = json.loads(response.text)["apps"]
            
            for app in apps:
                item = OneLineAvatarListItem(
                    text=f"{app['name']} v{app['version']}",
                    on_release=lambda x, a=app: self.show_app_detail(a)
                )
                icon = ImageLeftWidget(
                    source=f"{REPO_URL}/{app['folder']}/{app['icon']}"
                )
                item.add_widget(icon)
                self.list_view.add_widget(item)
                
        except Exception as e:
            self.layout.add_widget(Label(text=f"Ошибка: {str(e)}"))

    def show_app_detail(self, app):
        app_manager.current = 'detail'
        app_manager.current_screen.load_app(app)

class AppDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter('height'))
        
        self.back_btn = Button(text="Назад", size_hint_y=None, height=50)
        self.back_btn.bind(on_release=self.go_back)
        
        self.layout.add_widget(self.back_btn)
        self.scroll.add_widget(self.content)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)
    
    def load_app(self, app):
        self.content.clear_widgets()
        
        # Иконка
        self.content.add_widget(
            AsyncImage(source=f"{REPO_URL}/{app['folder']}/{app['icon']}", size_hint=(1, None), height=100)
        )
        
        # Информация
        info = f"""
        [b]{app['name']}[/b] v{app['version']}
        Автор: {app.get('author', 'Неизвестен')}
        
        {app['description']}
        """
        self.content.add_widget(Label(text=info, markup=True))
        
        # Скриншоты
        self.content.add_widget(Label(text="Скриншоты:"))
        screenshot_grid = GridLayout(cols=2, size_hint_y=None)
        screenshot_grid.bind(minimum_height=screenshot_grid.setter('height'))
        
        for shot in app['screenshots']:
            screenshot_grid.add_widget(
                AsyncImage(
                    source=f"{REPO_URL}/{app['folder']}/screenshots/{shot}",
                    size_hint=(None, None),
                    width=Window.width/2.2,
                    height=200
                )
            )
        self.content.add_widget(screenshot_grid)
        
        # Кнопка установки
        install_btn = Button(text="Установить", size_hint_y=None, height=60)
        install_btn.bind(
            on_release=lambda x: self.install_app(
                f"{REPO_URL}/{app['folder']}/{app['apk_file']}",
                app['name']
            )
        )
        self.content.add_widget(install_btn)

    def install_app(self, url, name):
        from android.permissions import request_permissions, Permission
        from android.storage import app_storage_path
        
        request_permissions([Permission.WRITE_EXTERNAL_STORAGE])
        
        try:
            apk_path = os.path.join(app_storage_path(), f"{name.replace(' ', '_')}.apk")
            
            # Скачивание APK
            response = requests.get(url)
            with open(apk_path, 'wb') as f:
                f.write(response.content)
            
            # Установка
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            File = autoclass('java.io.File')
            
            intent = Intent(Intent.ACTION_VIEW)
            intent.setDataAndType(
                Uri.fromFile(File(apk_path)),
                "application/vnd.android.package-archive"
            )
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            PythonActivity.mActivity.startActivity(intent)
            
        except Exception as e:
            print(f"Ошибка установки: {str(e)}")

    def go_back(self, instance):
        app_manager.current = 'list'

class AppStoreApp(App):
    def build(self):
        global app_manager
        app_manager = ScreenManager()
        app_manager.add_widget(AppListScreen(name='list'))
        app_manager.add_widget(AppDetailScreen(name='detail'))
        return app_manager

if __name__ == '__main__':
    AppStoreApp().run()