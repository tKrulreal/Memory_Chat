import pytest
from pydantic import ValidationError
from src.schemas.contact import ContactCreate
from src.schemas.message import MessageCreate
from src.schemas.enums import MessageRole

def test_contact_validation():
    # Valid
    c = ContactCreate(name="Nguyễn Văn A")
    assert c.name == "Nguyễn Văn A"
    
    # Invalid (empty name)
    with pytest.raises(ValidationError):
        ContactCreate(name="")

def test_message_validation():
    # Valid
    m = MessageCreate(content="Hello", role=MessageRole.USER)
    assert m.content == "Hello"
    
    # Invalid (empty content)
    with pytest.raises(ValidationError):
        MessageCreate(content="", role=MessageRole.USER)
