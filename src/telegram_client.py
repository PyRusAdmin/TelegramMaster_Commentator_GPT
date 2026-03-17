# -*- coding: utf-8 -*-
import os

from loguru import logger
from telethon import TelegramClient
from telethon.sessions import StringSession

from src.config_handler import api_id, api_hash
from src.connect import reading_proxy_data_from_the_database


def find_files(directory_path: str, extension: str) -> list:
    """
    Поиск файлов с определенным расширением в директории. Расширение файла должно быть указано без точки.

    :param directory_path: Путь к директории
    :param extension: Расширение файла (указанное без точки)
    :return list: Список имен найденных файлов
    """
    entities = []  # Список для хранения имен найденных файлов
    try:
        for file_name in os.listdir(directory_path):
            if file_name.endswith(
                    f".{extension}"
            ):  # Проверяем, заканчивается ли имя файла на заданное расширение
                file_path = os.path.join(
                    directory_path, file_name
                )  # Полный путь к файлу
                entities.append(file_path)  # Добавляем путь к файлу в список

        logger.info(f"🔍 Найденные файлы: {entities}")  # Выводим имена найденных файлов
        return entities  # Возвращаем список путей к файлам
    except FileNotFoundError:
        logger.error(f"❌ Ошибка! Директория {directory_path} не найдена!")
        return []  # Возвращаем пустой список, если директория не найдена


async def connect_client(session_path: str) -> TelegramClient | None:
    """
    Подключение к Telegram через session-файл.
    Возвращает клиент, если удалось подключиться и авторизация успешна.
    """
    try:
        async with TelegramClient(
                session=session_path,
                api_id=api_id,
                api_hash=api_hash,
                system_version="4.16.30-vxCUSTOM",
        ) as tmp_client:
            # Сохраняем как StringSession (удобно для прокси)
            session_string = StringSession.save(tmp_client.session)

        # Создаём клиент с прокси и StringSession
        client = TelegramClient(
            StringSession(session_string),
            api_id=api_id,
            api_hash=api_hash,
            system_version="4.16.30-vxCUSTOM",
            proxy=await reading_proxy_data_from_the_database(),
        )

        logger.info(f"🔌 Попытка подключения к {session_path}")
        await client.connect()

        if await client.is_user_authorized():
            logger.success(f"✅ Успешное подключение к {session_path}")
            return client
        else:
            logger.warning(f"❌ Аккаунт {session_path} не авторизован. Удаляю файл...")
            await client.disconnect()
            try:
                os.remove(session_path)
            except OSError as e:
                logger.error(f"Ошибка при удалении {session_path}: {e}")
            return None

    except Exception as e:
        logger.error(f"❌ Ошибка при подключении к {session_path}: {e}")
        return None


async def connect_telegram_account() -> TelegramClient:
    """
    Подключается к первому рабочему Telegram аккаунту.
    :return: TelegramClient (подключенный аккаунт).
    :raises: Exception, если подключение не удалось.
    """
    session_files = find_files("data/accounts/", extension="session")
    if not session_files:
        raise Exception(
            "❌ Не найдено ни одного файла сессии в директории data/accounts/."
        )

    for session_file in session_files:
        client = await connect_client(session_file)
        if client:
            return client

    raise Exception("❌ Не удалось подключиться ни к одному аккаунту.")
