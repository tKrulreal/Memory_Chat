from src.repositories.contact import ContactRepository
from src.repositories.conversation import ConversationRepository
from src.repositories.message import MessageRepository
from src.services.contact import ContactService
from src.services.message import MessageService


def test_contact_service_can_be_constructed():
    assert ContactService(ContactRepository()) is not None


def test_message_service_can_be_constructed():
    assert MessageService(MessageRepository(), ConversationRepository()) is not None
