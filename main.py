# -*- coding: utf-8 -*-
import flet as ft
from loguru import logger

from src.change_name_description_photo import handle_change_name_description_photo
from src.commentator import TelegramCommentator
from src.config_handler import (
    program_version, program_last_modified_date, program_name, app_log, errors_log, WINDOW_WIDTH, WINDOW_HEIGHT,
)
from src.core.handle_connect_accounts import handle_connect_accounts
from src.core.handlers import (
    handle_documentation, handle_creating_list_of_channels, handle_settings,
)
from src.core.views import PRIMARY_COLOR, TITLE_FONT_WEIGHT
from src.getting_list_channels import handle_getting_list_channels
from src.logging_in import loging
from src.settings import SettingPage
from src.subscribe import handle_channel_subscription

# Настройка логирования
logger.add(f"{app_log}", rotation="500 KB", compression="zip", level="INFO")
logger.add(f"{errors_log}", rotation="500 KB", compression="zip", level="ERROR")


class Application:
    """Класс для управления приложением."""

    def __init__(self):
        self.page = None
        self.info_list = None
        self.SPACING = 5
        self.RADIUS = 5
        self.LINE_COLOR = ft.Colors.GREY
        self.BUTTON_HEIGHT = 40
        self.LINE_WIDTH = 1
        self.PADDING = 10
        self.BUTTON_WIDTH = 300
        self.PROGRAM_MENU_WIDTH = self.BUTTON_WIDTH + self.PADDING

    async def actions_with_the_program_window(self, page: ft.Page):
        """Изменение на изменение главного окна программы."""
        page.title = (
            f"Версия {program_version}. Дата изменения {program_last_modified_date}"
        )
        page.window.width = WINDOW_WIDTH  # Устанавливаем ширину окна
        page.window.height = WINDOW_HEIGHT  # Устанавливаем высоту окна
        page.window.resizable = False
        page.window.min_width = WINDOW_WIDTH  # Устанавливаем минимальную ширину окна
        page.window.max_width = WINDOW_WIDTH  # Устанавливаем максимальную ширину окна
        page.window.min_height = WINDOW_HEIGHT  # Устанавливаем минимальную высоту окна
        page.window.max_height = WINDOW_HEIGHT  # Устанавливаем максимальную высоту окна

    def create_title(self, text: str, font_size) -> ft.Text:
        """
        Создает заголовок с градиентом.

        :param text: Текст заголовка.
        :param font_size: Размер шрифта.
        """
        return ft.Text(
            spans=[
                ft.TextSpan(
                    text,
                    ft.TextStyle(
                        size=font_size,
                        weight=TITLE_FONT_WEIGHT,
                        foreground=ft.Paint(
                            gradient=ft.PaintLinearGradient(
                                (0, 20), (150, 20), [PRIMARY_COLOR, PRIMARY_COLOR]
                            )
                        ),
                    ),
                ),
            ],
        )

    def create_button(self, text: str, route: str) -> ft.OutlinedButton:
        """Создает кнопку меню."""
        return ft.OutlinedButton(
            text=text,
            on_click=lambda _: self.page.go(route),
            width=self.BUTTON_WIDTH,
            height=self.BUTTON_HEIGHT,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=self.RADIUS)),
        )

    def build_menu(self) -> ft.Column:
        """Создает колонку с заголовками и кнопками для главного меню программы"""
        title = self.create_title(text=program_name, font_size=16)
        version = self.create_title(
            text=f"Версия программы: {program_version}", font_size=13
        )
        date_program_change = self.create_title(
            text=f"Дата изменения: {program_last_modified_date}", font_size=13
        )
        buttons = [
            self.create_button("📋 Получение списка каналов", "/getting_list_channels"),
            self.create_button("💬 Отправка комментариев", "/submitting_comments"),
            self.create_button(
                "🖼️ Смена имени, описания", "/change_name_description_photo"
            ),
            self.create_button("🔗 Подписка на каналы", "/channel_subscription"),
            self.create_button(
                "📂 Формирование списка каналов", "/creating_list_of_channels"
            ),
            self.create_button("📖 Документация", "/documentation"),
            self.create_button("🔗 Подключение аккаунтов", "/connect_accounts"),
            self.create_button("⚙️ Настройки программы", "/settings"),
        ]
        return ft.Column(
            [title, version, date_program_change, *buttons],
            alignment=ft.MainAxisAlignment.START,
            spacing=self.SPACING,
        )

    async def setup(self):
        """Настраивает страницу."""
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.on_route_change = self.route_change
        await self.actions_with_the_program_window(self.page)
        self._add_startup_message()
        await self.route_change(None)

    def _add_startup_message(self):
        """Добавляет стартовое сообщение в ListView."""
        self.info_list.controls.append(
            ft.Text(
                "TelegramMaster-GPT-Comments 🚀\n\nTelegramMaster-GPT-Comments - это программа для автоматического "
                "написания комментариев в каналах Telegram, а также для работы с аккаунтами. 💬\n\n"
                "📂 Проект доступен на GitHub: https://github.com/pyadrus/TelegramMaster_Commentator \n"
                "📲 Контакт с разработчиком в Telegram: https://t.me/PyAdminRU\n"
                f"📡 Информация на канале: https://t.me/master_tg_d"
            )
        )

    async def route_change(self, route):
        """Обработчик изменения маршрута."""
        self.page.views.clear()
        layout = ft.Row(
            [
                ft.Container(
                    self.build_menu(),
                    width=self.PROGRAM_MENU_WIDTH,
                    padding=self.PADDING,
                ),
                ft.Container(width=self.LINE_WIDTH, bgcolor=self.LINE_COLOR),
                ft.Container(self.info_list, expand=True, padding=self.PADDING),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=0,
            expand=True,
        )
        self.page.views.append(ft.View("/", [layout]))
        route_handlers = {
            "/getting_list_channels": self._handle_getting_list_channels,
            "/submitting_comments": self._handle_submitting_comments,
            "/change_name_description_photo": self._handle_change_name_description_photo,
            "/channel_subscription": self._handle_channel_subscription,
            "/creating_list_of_channels": self._handle_creating_list_of_channels,
            "/documentation": self._handle_documentation,
            "/connect_accounts": self._handle_connect_accounts,
            "/settings": self._handle_settings,
            "/settings_proxy": self._handle_settings_proxy,
            "/record_id_hash": self._handle_record_id_hash,
            "/recording_message": self._recording_message,
            "/choosing_an_ai_model": self._handle_choosing_an_ai_model,
            "/record_time": self._handle_record_time,
        }
        handler = route_handlers.get(self.page.route)
        if handler:
            await handler()
        self.page.update()

    async def _handle_choosing_an_ai_model(self):
        """Страница Выбор модели AI"""
        logger.info("Пользователь перешел на выбор модели AI")
        await SettingPage(self.page).choosing_an_ai_model()

    async def _handle_record_time(self):
        """Страница Запись времени"""
        await SettingPage(self.page).record_setting(
            limit_type="time_config",
            label="Введите время в секундах, в цифрах",  # Подпись в поле ввода
        )

    async def _recording_message(self):
        """Страница Запись сообщения"""
        await SettingPage(self.page).recording_text_for_sending_messages(
            "Введите сообщение, которое будет отправляться в канал",
            "data/message/message",
        )

    async def _handle_record_id_hash(self):
        """Страница Запись id и hash"""
        await SettingPage(self.page).writing_api_id_api_hash()

    async def _handle_settings_proxy(self):
        """Страница ⚙️ Настройки прокси"""
        await SettingPage(self.page).creating_the_main_window_for_proxy_data_entry()

    async def _handle_connect_accounts(self):
        """Страница 🔗 Подключение аккаунтов"""
        await handle_connect_accounts(self.page)

    async def _handle_settings(self):
        """Страница ⚙️ Настройки программы"""
        await handle_settings(self.page)

    async def _handle_getting_list_channels(self):
        """Страница 📋 Получение списка каналов"""
        await handle_getting_list_channels(self.page)

    async def _handle_submitting_comments(self):
        """Страница 💬 Отправка комментариев"""
        await TelegramCommentator(self.page).handle_submitting_comments()

    async def _handle_change_name_description_photo(self):
        """Страница 🖼️ Смена имени, описания"""
        await handle_change_name_description_photo(self.page)

    async def _handle_channel_subscription(self):
        """Страница 🔗 Подписка на каналы"""
        await handle_channel_subscription(self.page)

    async def _handle_creating_list_of_channels(self):
        """Страница 📂 Формирование списка каналов"""
        await handle_creating_list_of_channels(self.page)

    async def _handle_documentation(self):
        """Страница 📖 Документация"""
        await handle_documentation(self.page)

    async def main(self, page: ft.Page):
        """Точка входа в приложение."""
        self.page = page
        self.info_list = ft.ListView(
            expand=True, spacing=10, padding=self.PADDING, auto_scroll=True
        )

        await self.setup()
        await loging()


if __name__ == "__main__":
    ft.app(target=Application().main)
