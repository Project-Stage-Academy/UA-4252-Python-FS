import uuid

from apps.conversations.documents import Conversation, Message


def test_create_conversation():
    """Test MongoDB accepts Conversation document"""

    conv = Conversation.objects.create(
        conversation_id=uuid.uuid4(),
        participants=[uuid.uuid4(), uuid.uuid4()],
        project_id=uuid.uuid4(),
    )

    assert Conversation.objects.count() == 1
    assert conv.conversation_id is not None


def test_create_message():
    """Test MongoDB accepts Message document"""

    message = Message.objects.create(
        conversation_id=uuid.uuid4(),
        sender_id=uuid.uuid4(),
        body="Test message",
    )

    assert Message.objects.count() == 1
    assert message.conversation_id is not None
    assert message.body == "Test message"


def test_create_conversation_and_message():
    """Test MongoDB accepts Conversation and Message document"""

    conv = Conversation.objects.create(
        conversation_id=uuid.uuid4(),
        participants=[uuid.uuid4(), uuid.uuid4()],
        project_id=uuid.uuid4(),
    )

    Message.objects.create(
        conversation_id=conv.conversation_id,
        sender_id=conv.participants[0],
        body="Hello from pytest",
    )

    messages = Message.objects.filter(conversation_id=conv.conversation_id)
    assert messages.count() == 1
