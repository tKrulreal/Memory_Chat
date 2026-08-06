from src.repositories.base import BaseRepository
from src.models.contact import Tag

class TagRepository(BaseRepository[Tag]):
    pass

tag_repo = TagRepository(Tag)
