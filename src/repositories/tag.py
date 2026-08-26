from src.models.contact import Tag
from src.repositories.base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    pass

tag_repo = TagRepository(Tag)
