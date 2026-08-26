import uuid
from unittest.mock import Mock, MagicMock

import pytest

from src.models.chat import Conversation, Message
from src.services.conversation import ConversationService, ConversationNotFoundError, ConversationOwnershipError
from src.services.message import MessageService, MessageOwnershipError, MessageConversationNotFoundError


def test_list_conversations():
    # Setup mocks
    mock_repo = Mock()
    mock_db = Mock()
    user_id = uuid.uuid4()
    
    # Mock return values
    mock_repo.get_by_user_id.return_value = [Conversation(id=uuid.uuid4())]
    mock_repo.count_by_user_id.return_value = 1
    
    service = ConversationService(repository=mock_repo)
    conversations, total = service.list_conversations(mock_db, user_id, 1, 10)
    
    assert total == 1
    assert len(conversations) == 1
    mock_repo.get_by_user_id.assert_called_once_with(mock_db, user_id, 0, 10, None)
    mock_repo.count_by_user_id.assert_called_once_with(mock_db, user_id, None)


def test_delete_message_success():
    mock_msg_repo = Mock()
    mock_conv_repo = Mock()
    mock_db = Mock()
    
    user_id = uuid.uuid4()
    other_user_id = uuid.uuid4()
    conversation_id = uuid.uuid4()
    message_id = uuid.uuid4()
    
    # The message belongs to user_id
    mock_message = Message(
        id=message_id,
        conversation_id=conversation_id,
        sender_user_id=user_id,
        content="Hello",
    )
    mock_msg_repo.get.return_value = mock_message
    
    # The conversation is valid and owned by user_id
    mock_conv = Conversation(
        id=conversation_id,
        user_a_id=user_id,
        user_b_id=other_user_id,
    )
    mock_conv_repo.get.return_value = mock_conv
    
    service = MessageService(repository=mock_msg_repo, conversation_repository=mock_conv_repo)
    result = service.delete_message(mock_db, user_id, message_id)
    
    assert result.deleted_at is not None
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_message)


def test_delete_message_ownership_error():
    mock_msg_repo = Mock()
    mock_conv_repo = Mock()
    mock_db = Mock()
    
    user_id = uuid.uuid4()
    other_user_id = uuid.uuid4()
    conversation_id = uuid.uuid4()
    message_id = uuid.uuid4()
    
    # The message was sent by other_user_id
    mock_message = Message(
        id=message_id,
        conversation_id=conversation_id,
        sender_user_id=other_user_id,
        content="Hello",
    )
    mock_msg_repo.get.return_value = mock_message
    
    mock_conv = Conversation(
        id=conversation_id,
        user_a_id=user_id,
        user_b_id=other_user_id,
    )
    mock_conv_repo.get.return_value = mock_conv
    
    service = MessageService(repository=mock_msg_repo, conversation_repository=mock_conv_repo)
    
    with pytest.raises(MessageOwnershipError, match="Only the sender can recall this message"):
        service.delete_message(mock_db, user_id, message_id)
