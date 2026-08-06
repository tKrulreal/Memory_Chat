import uuid

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class ContactBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        validation_alias=AliasChoices("name", "display_name"),
        description="Tên liên hệ không được rỗng",
    )
    avatar_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("avatar_url", "avatar"),
    )
    relationship_score: int | None = Field(0, description="Điểm mối quan hệ")

    model_config = ConfigDict(str_strip_whitespace=True)


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)
    avatar_url: str | None = None
    relationship_score: int | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class ContactResponse(ContactBase):
    id: uuid.UUID
    user_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
