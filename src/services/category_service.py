from typing import List, Optional
from src.database import CategoryRepository
from src.models import Category


class CategoryService:
    def __init__(self, cat_repo: CategoryRepository):
        self._cat_repo = cat_repo

    def get_all(self) -> List[Category]:
        return self._cat_repo.get_all()

    def get_by_name(self, name: str) -> Optional[Category]:
        return self._cat_repo.get_by_name(name)

    def add(self, name: str, icon: str = "", color: str = "", budget: float = 0) -> Category:
        cid = self._cat_repo.add(name, icon, color, budget)
        return Category(id=cid, name=name, icon=icon, color=color, budget=budget)

    def update(self, cat_id: int, **kwargs):
        self._cat_repo.update(cat_id, **kwargs)

    def delete(self, cat_id: int) -> bool:
        return self._cat_repo.delete(cat_id)

    def get_category_names(self) -> List[str]:
        return [c.name for c in self._cat_repo.get_all()]
