# -*- coding: utf-8 -*-
import flet as ft
from faker import Faker
from loguru import logger
from telethon import functions

from src.core.buttons import create_buttons
from src.core.views import program_title, view_with_elements_input_field
from src.telegram_client import connect_telegram_account


async def handle_change_name_description_photo(page: ft.Page):
    """Создает страницу 🖼️ Смена имени, описания"""

    page.views.clear()
    lv = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)

    lv.controls.append(
        ft.Text(
            "🖼️ Смена имени и описания\n\n"
            "🔹 Здесь вы можете изменить имя профиля и описание.\n"
            "🔹 Имя будет автоматически сгенерировано на русском языке с помощью Faker.\n"
            "🔹 Введите новое описание профиля в поле ниже и нажмите кнопку 'Смена имени, описания'.\n\n"
            "📌 Что будет изменено?\n"
            "✅ Имя (будет сгенерировано случайное)\n"
            "✅ Описание профиля (то, что вы введете)\n\n"
            "⚠️ Обратите внимание: Telegram может ограничивать частоту смены имени и описания."
        )
    )

    about_field = ft.TextField(
        label="Введите описание профиля", multiline=True, max_lines=19
    )

    async def action_1(_):
        try:
            lv.controls.append(
                ft.Text("🖼️ Смена имени, описания")
            )  # отображаем сообщение в ListView
            page.update()  # Обновляем страницу
            await change_profile_descriptions(
                await connect_telegram_account(), lv, about_field.value
            )
            page.update()  # Обновляем страницу
        except Exception as e:
            logger.error(e)
            lv.controls.append(
                ft.Text(f"Ошибка: {str(e)}")
            )  # отображаем ошибку в ListView
            page.update()  # Обновляем страницу

    await view_with_elements_input_field(
        page=page,
        title=await program_title(title="🖼️ Смена имени, описания"),
        buttons=[
            await create_buttons(text="🖼️ Смена имени, описания", on_click=action_1),
            await create_buttons(text="Назад", on_click=lambda _: page.go("/")),
        ],
        route_page="change_name_description_photo",
        lv=lv,
        text_field=about_field,  # Создаем TextField поле ввода
    )
    page.update()  # Обновляем страницу


async def change_profile_descriptions(client, lv: ft.ListView, about) -> None:
    """
    Обновляет описание профиля Telegram и имя со случайными данными с помощью библиотеки Faker.

    :param client: TelegramClient объект.
    :param lv: ListView объект.
    :param about: Описание профиля.
    :return: None
    """
    fake = Faker("ru_RU")  # Устанавливаем локаль для генерации русских имен
    fake_name = fake.first_name_female()  # Генерируем женское имя
    lv.controls.append(
        ft.Text(f"🎭 Сгенерированное имя: {fake_name}")
    )  # отображаем сообщение в ListView

    # Вводим данные для телеги
    async with client:  # Используем асинхронный контекстный менеджер
        # Обновляем имя и описание профиля
        result = await client(
            functions.account.UpdateProfileRequest(
                first_name=fake_name,  # Устанавливаем новое имя
                about=about,  # Устанавливаем новое описание
            )
        )
        # Форматируем результат для пользователя
        user_info = (
            f"🆔 ID: {result.id}\n"
            f"👤 Имя: {result.first_name}\n"
            f"👥 Фамилия: {result.last_name}\n"
            f"📛 Username: {result.username}\n"
            f"📞 Телефон: {result.phone}\n"
            f"📝 Описание профиля обновлено: {about}"
        )
        # Добавляем отформатированные данные в ListView
        lv.controls.append(ft.Text(user_info))
        lv.controls.append(
            ft.Text("✅ Профиль успешно обновлен!")
        )  # отображаем сообщение в ListView
