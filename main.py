# -*- coding: utf-8 -*-
import flet as ft
from loguru import logger

from src.change_name_description_photo import handle_change_name_description_photo
from src.commentator import TelegramCommentator
from src.config_handler import (
    program_version,
    program_last_modified_date,
    program_name,
    app_log,
    errors_log,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)
from src.core.handle_connect_accounts import handle_connect_accounts
from src.core.handlers import (
    handle_documentation,
    handle_creating_list_of_channels,
    handle_settings,
)
from src.core.views import PRIMARY_COLOR, TITLE_FONT_WEIGHT
from src.getting_list_channels import handle_getting_list_channels
from src.logging_in import loging
from src.settings import SettingPage
from src.subscribe import handle_channel_subscription

logger.add(f"{app_log}", rotation="500 KB", compression="zip", level="INFO")
logger.add(f"{errors_log}", rotation="500 KB", compression="zip", level="ERROR")

SPACING = 5
RADIUS = 5
LINE_COLOR = ft.Colors.GREY
BUTTON_HEIGHT = 40
LINE_WIDTH = 1
PADDING = 10
BUTTON_WIDTH = 300
PROGRAM_MENU_WIDTH = BUTTON_WIDTH + PADDING


def create_title(text: str, font_size) -> ft.Text:
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


def create_button(page: ft.Page, text: str, route: str) -> ft.OutlinedButton:
    return ft.OutlinedButton(
        content=ft.Text(text),
        on_click=lambda _: page.go(route),
        width=BUTTON_WIDTH,
        height=BUTTON_HEIGHT,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=RADIUS)),
    )


def build_menu(page: ft.Page) -> ft.Column:
    title = create_title(text=program_name, font_size=16)
    version = create_title(text=f"Версия программы: {program_version}", font_size=13)
    date_program_change = create_title(
        text=f"Дата изменения: {program_last_modified_date}", font_size=13
    )
    buttons = [
        create_button(page, "📋 Получение списка каналов", "/getting_list_channels"),
        create_button(page, "💬 Отправка комментариев", "/submitting_comments"),
        create_button(
            page, "🖼️ Смена имени, описания", "/change_name_description_photo"
        ),
        create_button(page, "🔗 Подписка на каналы", "/channel_subscription"),
        create_button(
            page, "📂 Формирование списка каналов", "/creating_list_of_channels"
        ),
        create_button(page, "📖 Документация", "/documentation"),
        create_button(page, "🔗 Подключение аккаунтов", "/connect_accounts"),
        create_button(page, "⚙️ Настройки программы", "/settings"),
    ]
    return ft.Column(
        [title, version, date_program_change, *buttons],
        alignment=ft.MainAxisAlignment.START,
        spacing=SPACING,
    )


async def actions_with_the_program_window(page: ft.Page):
    page.title = (
        f"Версия {program_version}. Дата изменения {program_last_modified_date}"
    )
    page.window.width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT
    page.window.resizable = False
    page.window.min_width = WINDOW_WIDTH
    page.window.max_width = WINDOW_WIDTH
    page.window.min_height = WINDOW_HEIGHT
    page.window.max_height = WINDOW_HEIGHT


def add_startup_message(info_list: ft.ListView):
    info_list.controls.append(
        ft.Text(
            "TelegramMaster-GPT-Comments 🚀\n\nTelegramMaster-GPT-Comments - это программа для автоматического "
            "написания комментариев в каналах Telegram, а также для работы с аккаунтами. 💬\n\n"
            "📂 Проект доступен на GitHub: https://github.com/pyadrus/TelegramMaster_Commentator \n"
            "📲 Контакт с разработчиком в Telegram: https://t.me/PyAdminRU\n"
            "📡 Информация на канале: https://t.me/master_tg_d"
        )
    )


async def setup(page: ft.Page, info_list: ft.ListView):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.on_route_change = lambda e: route_change(page, info_list)
    await actions_with_the_program_window(page)
    add_startup_message(info_list)
    await route_change(page, info_list)


async def route_change(page: ft.Page, info_list: ft.ListView):
    page.views.clear()

    menu = build_menu(page)

    layout = ft.Row(
        [
            ft.Container(menu, width=PROGRAM_MENU_WIDTH, padding=PADDING),
            ft.VerticalDivider(width=1),
            ft.Container(info_list, expand=True, padding=PADDING),
        ],
        spacing=0,
        expand=True,
    )

    page.views.append(ft.View("/", [layout]))
    page.update()

    route_handlers = {
        "/getting_list_channels": lambda: handle_getting_list_channels(page),
        "/submitting_comments": lambda: TelegramCommentator(
            page
        ).handle_submitting_comments(),
        "/change_name_description_photo": lambda: handle_change_name_description_photo(
            page
        ),
        "/channel_subscription": lambda: handle_channel_subscription(page),
        "/creating_list_of_channels": lambda: handle_creating_list_of_channels(page),
        "/documentation": lambda: handle_documentation(page),
        "/connect_accounts": lambda: handle_connect_accounts(page),
        "/settings": lambda: handle_settings(page),
        "/settings_proxy": lambda: SettingPage(
            page
        ).creating_the_main_window_for_proxy_data_entry(),
        "/record_id_hash": lambda: SettingPage(page).writing_api_id_api_hash(),
        "/recording_message": lambda: SettingPage(
            page
        ).recording_text_for_sending_messages(
            "Введите сообщение, которое будет отправляться в канал",
            "data/message/message",
        ),
        "/choosing_an_ai_model": lambda: SettingPage(page).choosing_an_ai_model(),
        "/record_time": lambda: SettingPage(page).record_setting(
            limit_type="time_config", label="Введите время в секундах, в цифрах"
        ),
    }

    route = page.route if page.route else "/"
    handler = route_handlers.get(route)
    if handler:
        await handler()
    page.update()


async def setup(page: ft.Page, info_list: ft.ListView):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.on_route_change = lambda e: route_change(page, info_list)
    await actions_with_the_program_window(page)
    add_startup_message(info_list)
    await route_change(page, info_list)


async def route_change(page: ft.Page, info_list: ft.ListView):
    page.views.clear()

    menu = build_menu(page)

    layout = ft.Row(
        [
            ft.Container(menu, width=PROGRAM_MENU_WIDTH, padding=PADDING),
            ft.VerticalDivider(width=1),
            ft.Container(info_list, expand=True, padding=PADDING),
        ],
        spacing=0,
        expand=True,
    )

    page.views.append(ft.View("/", [layout]))
    page.update()

    route_handlers = {
        "/getting_list_channels": lambda: handle_getting_list_channels(page),
        "/submitting_comments": lambda: TelegramCommentator(
            page
        ).handle_submitting_comments(),
        "/change_name_description_photo": lambda: handle_change_name_description_photo(
            page
        ),
        "/channel_subscription": lambda: handle_channel_subscription(page),
        "/creating_list_of_channels": lambda: handle_creating_list_of_channels(page),
        "/documentation": lambda: handle_documentation(page),
        "/connect_accounts": lambda: handle_connect_accounts(page),
        "/settings": lambda: handle_settings(page),
        "/settings_proxy": lambda: SettingPage(
            page
        ).creating_the_main_window_for_proxy_data_entry(),
        "/record_id_hash": lambda: SettingPage(page).writing_api_id_api_hash(),
        "/recording_message": lambda: SettingPage(
            page
        ).recording_text_for_sending_messages(
            "Введите сообщение, которое будет отправляться в канал",
            "data/message/message",
        ),
        "/choosing_an_ai_model": lambda: SettingPage(page).choosing_an_ai_model(),
        "/record_time": lambda: SettingPage(page).record_setting(
            limit_type="time_config", label="Введите время в секундах, в цифрах"
        ),
    }

    route = page.route if page.route else "/"
    handler = route_handlers.get(route)
    if handler:
        await handler()
    page.update()


async def main(page: ft.Page):
    await actions_with_the_program_window(page)
    page.theme_mode = ft.ThemeMode.LIGHT

    def show_main_menu():
        """Показывает главное меню"""
        page.clean()
        info_list = ft.ListView(
            expand=True, spacing=10, padding=PADDING, auto_scroll=True
        )
        add_startup_message(info_list)
        menu = build_menu(page)

        layout = ft.Row(
            [
                ft.Container(menu, width=PROGRAM_MENU_WIDTH, padding=PADDING),
                ft.VerticalDivider(width=1),
                ft.Container(info_list, expand=True, padding=PADDING),
            ],
            spacing=0,
            expand=True,
        )
        page.add(layout)
        page.update()

    async def route_change(e):
        logger.info(f"Route change to: {page.route}")

        if page.route == "/" or not page.route:
            show_main_menu()
        else:
            page.views.clear()
            route_handlers = {
                "/getting_list_channels": lambda: handle_getting_list_channels(page),
                "/submitting_comments": lambda: TelegramCommentator(
                    page
                ).handle_submitting_comments(),
                "/change_name_description_photo": lambda: (
                    handle_change_name_description_photo(page)
                ),
                "/channel_subscription": lambda: handle_channel_subscription(page),
                "/creating_list_of_channels": lambda: handle_creating_list_of_channels(
                    page
                ),
                "/documentation": lambda: handle_documentation(page),
                "/connect_accounts": lambda: handle_connect_accounts(page),
                "/settings": lambda: handle_settings(page),
                "/settings_proxy": lambda: SettingPage(
                    page
                ).creating_the_main_window_for_proxy_data_entry(),
                "/record_id_hash": lambda: SettingPage(page).writing_api_id_api_hash(),
                "/recording_message": lambda: SettingPage(
                    page
                ).recording_text_for_sending_messages(
                    "Введите сообщение, которое будет отправляться в канал",
                    "data/message/message",
                ),
                "/choosing_an_ai_model": lambda: SettingPage(
                    page
                ).choosing_an_ai_model(),
                "/record_time": lambda: SettingPage(page).record_setting(
                    limit_type="time_config", label="Введите время в секундах, в цифрах"
                ),
            }

            handler = route_handlers.get(page.route)
            if handler:
                await handler()
            page.update()

    page.on_route_change = route_change
    logger.info("Starting app")
    show_main_menu()
    await loging()


ft.run(main)
