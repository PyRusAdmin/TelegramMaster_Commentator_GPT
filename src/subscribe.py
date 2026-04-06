# -*- coding: utf-8 -*-
import asyncio
import datetime
import time

import flet as ft
from loguru import logger
from telethon.errors import FloodWaitError, ChannelPrivateError, UsernameInvalidError
from telethon.tl.functions.channels import JoinChannelRequest

from src.config_handler import time_config
from src.core.buttons import create_buttons
from src.core.views import program_title, view_with_elements
from src.db_handler import (
    read_channel_list_from_database,
    delete_username_from_database,
)
from src.telegram_client import connect_telegram_account


async def handle_channel_subscription(page: ft.Page):
    """Создает страницу Подписка на каналы"""
    logger.info("Пользователь перешел на страницу Подписка на каналы")
    page.views.clear()
    lv = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)

    lv.controls.append(
        ft.Text(
            "🔗 Перед началом работы сформируйте список каналов для подписки\n\n"
            "🔄 В процессе работы программа будет подписываться на каналы и отображать важную информацию для пользователя.\n\n"
        )
    )

    async def action_1(_):
        lv.controls.append(
            ft.Text("Подписка на каналы / группы")
        )  # отображаем сообщение в ListView
        page.update()  # Обновляем страницу
        client = await connect_telegram_account()

        channel_name = await read_channel_list_from_database()
        lv.controls.append(
            ft.Text(f"Группы и каналы из базы данных {channel_name}")
        )  # отображаем сообщение в ListView
        page.update()  # Обновляем страницу
        for channel in channel_name:
            lv.controls.append(
                ft.Text(f"Подписка на: {channel[0]}")
            )  # отображаем сообщение в ListView
            page.update()  # Обновляем страницу
            await SUBSCRIBE(page).subscribe_to_channel(client, channel[0], lv)
        lv.controls.append(
            ft.Text(f"Подписка завершена")
        )  # отображаем сообщение в ListView
        page.update()  # Обновляем страницу

    await view_with_elements(
        page=page,
        title=await program_title(title="Подписка на каналы"),
        buttons=[
            await create_buttons(text="Подписка", on_click=action_1),
            await create_buttons(text="Назад", on_click=lambda _: page.go("/")),
        ],
        route_page="channel_subscription",
        lv=lv,
    )
    page.update()  # Обновляем страницу


class SUBSCRIBE:
    """Класс подписки на группы и каналы Telegram"""

    def __init__(self, page: ft.Page):
        self.page = page

    async def subscribe_to_channel(self, client, channel_name, lv: ft.ListView) -> None:
        """
        Подписывается на Telegram-канал.
        :param channel_name: Имя канала Telegram.
        :param client: TelegramClient объект.
        :param lv: ListView.
        :return: None.
        """
        if not channel_name or channel_name.isdigit():
            lv.controls.append(
                ft.Text(
                    f"Неверный username канала: {channel_name}", color=ft.Colors.RED
                )
            )
            self.page.update()
            return
        try:
            await client(JoinChannelRequest(channel_name))
            lv.controls.append(
                ft.Text(f"Успешная подписка на {channel_name}", color=ft.Colors.RED)
            )
            self.page.update()
            await asyncio.sleep(int(time_config))
        except ChannelPrivateError:
            lv.controls.append(
                ft.Text(f"Канал {channel_name} закрыт", color=ft.Colors.RED)
            )  # отображаем сообщение в ListView
            self.page.update()  # Обновляем страницу
        except FloodWaitError as e:
            lv.controls.append(
                ft.Text(
                    f"Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}",
                    color=ft.Colors.RED,
                )
            )  # отображаем сообщение в ListView
            self.page.update()  # Обновляем страницу
            time.sleep(e.seconds)
        except UsernameInvalidError:
            logger.error(
                f"Ошибка при подписке на канал. Не верный username канала: {channel_name}"
            )
            delete_username_from_database(channel_name)
        except ValueError:
            logger.error(
                f"Ошибка при подписке на канал. Не верный username канала: {channel_name}"
            )
            delete_username_from_database(channel_name)
