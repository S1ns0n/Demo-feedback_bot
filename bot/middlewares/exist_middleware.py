from aiogram import BaseMiddleware
from aiogram.types import Update
from typing import Callable, Dict, Any, Awaitable
import json
import os
from bot.config import USERS_DIR

class ExistMiddleware(BaseMiddleware):
    def __init__(self, whitelist_file: str = "whitelist.json"):
        # Создаем директорию если не существует
        os.makedirs(USERS_DIR, exist_ok=True)
        self.whitelist_file = f"{USERS_DIR}/{whitelist_file}"
        self._ensure_whitelist_file()
        print(f"Middleware инициализирован. Файл белого списка: {self.whitelist_file}")

    def _ensure_whitelist_file(self):
        """Создает файл с белым списком, если он не существует"""
        if not os.path.exists(self.whitelist_file):
            with open(self.whitelist_file, 'w', encoding='utf-8') as f:
                json.dump({"whitelist": [], "admin_ids": []}, f, ensure_ascii=False, indent=2)
            print(f"Создан файл белого списка: {self.whitelist_file}")

    def _load_whitelist(self) -> dict:
        """Загружает белый список из JSON файла"""
        try:
            with open(self.whitelist_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Ошибка загрузки белого списка: {e}")
            return {"whitelist": [], "admin_ids": []}

    def _save_whitelist(self, data: dict):
        """Сохраняет белый список в JSON файл"""
        with open(self.whitelist_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_whitelist(self) -> set[int]:
        """Возвращает множество ID пользователей из белого списка"""
        data = self._load_whitelist()
        return set(data.get("whitelist", []))

    def get_admin_ids(self) -> set[int]:
        """Возвращает множество ID администраторов"""
        data = self._load_whitelist()
        return set(data.get("admin_ids", []))

    def add_to_whitelist(self, user_id: int):
        """Добавляет пользователя в белый список"""
        data = self._load_whitelist()
        whitelist = data.get("whitelist", [])

        if user_id not in whitelist:
            whitelist.append(user_id)
            data["whitelist"] = whitelist
            self._save_whitelist(data)
            print(f"Пользователь {user_id} добавлен в белый список")

    def remove_from_whitelist(self, user_id: int):
        """Удаляет пользователя из белого списка"""
        data = self._load_whitelist()
        whitelist = data.get("whitelist", [])

        if user_id in whitelist:
            whitelist.remove(user_id)
            data["whitelist"] = whitelist
            self._save_whitelist(data)
            print(f"Пользователь {user_id} удален из белого списка")

    def add_admin(self, user_id: int):
        """Добавляет администратора"""
        data = self._load_whitelist()
        admin_ids = data.get("admin_ids", [])

        if user_id not in admin_ids:
            admin_ids.append(user_id)
            data["admin_ids"] = admin_ids
            self._save_whitelist(data)
            print(f"Пользователь {user_id} добавлен как администратор")

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:

        user_id = await self._extract_user_id(event)

        if user_id is None:
            return await handler(event, data)

        # Получаем актуальный белый список
        whitelist = self.get_whitelist()
        admin_ids = self.get_admin_ids()


        # Проверяем доступ (админы всегда имеют доступ)
        if user_id in whitelist or user_id in admin_ids:
            return await handler(event, data)
        else:
            await self._notify_no_access(event)
            return

    async def _extract_user_id(self, event: Update) -> int | None:
        """Извлекает ID пользователя из события"""
        if event.message:
            return event.message.from_user.id
        elif event.callback_query:
            return event.callback_query.from_user.id
        elif event.edited_message:
            return event.edited_message.from_user.id
        return None

    async def _notify_no_access(self, event: Update):
        """Уведомляет пользователя об отсутствии доступа"""
        if event.message:
            await event.message.answer("🚫 У вас нет доступа к этому боту")
        elif event.callback_query:
            await event.callback_query.answer(
                "🚫 Доступ к боту запрещен",
                show_alert=True
            )