import json
from pathlib import Path
from typing import Dict, Any
from fastapi import HTTPException


class QuestLoader:
    _cache: Dict[str, dict] = {}
    _quests_dir = Path("content/quests")

    @classmethod
    def get_quest(cls, quest_id: str) -> dict:
        """Загружает квест из кэша или с диска"""
        if quest_id in cls._cache:
            return cls._cache[quest_id]

        file_path = cls._quests_dir / f"{quest_id}.json"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Квест не найден")

        with open(file_path, "r", encoding="utf-8") as f:
            quest_data = json.load(f)
            cls._cache[quest_id] = quest_data
            return quest_data

    @classmethod
    def get_scene(cls, quest_id: str, scene_id: str) -> dict:
        """Получает конкретную сцену из квеста"""
        quest = cls.get_quest(quest_id)
        scene = quest.get("scenes", {}).get(scene_id)
        if not scene:
            raise HTTPException(status_code=404, detail="Сцена не найдена")
        return scene
    
    @classmethod
    def get_all_quests(cls) -> list[dict]:
        """Возвращает информацию о всех доступных квестах"""
        quests = []
        if not cls._quests_dir.exists():
            return quests
        for file_path in cls._quests_dir.glob("*.json"):
            quest_id = file_path.stem
            try:
                quest_data = cls.get_quest(quest_id)
                quests.append({
                    "id": quest_id,
                    "title": quest_data.get("title", "Без названия"),
                    "description": quest_data.get("description", "Без описания")
                })
            except Exception:
                continue
        return quests
