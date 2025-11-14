from datetime import datetime, timezone
from typing import Dict, List, Optional

from bson import ObjectId

from apps.investors.models import InvestorProfile
from apps.startups.models import StartupProfile
from apps.users.models import User

# from pymongo import MongoClient


# Connection to Mongo DB


def get_mongo_db():
    # mongo_client = MongoClient(settings.MONGODB_SETTINGS['host'])
    # return mongo_client[settings.MONGODB_SETTINGS['db']]
    pass


def get_messages_collection():
    return get_mongo_db()['messages']


def get_conversations_collection():
    return get_mongo_db()['conversations']


# helpers
def _is_investor(user_id: str) -> bool:
    try:
        user = User.objects.get(id=user_id)
        return InvestorProfile.objects.filter(user=user).exists()
    except User.DoesNotExist:
        return False


def _is_startup(user_id: str) -> bool:
    try:
        user = User.objects.get(id=user_id)
        return StartupProfile.objects.filter(user=user).exists()
    except User.DoesNotExist:
        return False


def _validate_participant(conversation_id: str, user_id: str) -> Dict:
    conversations = get_conversations_collection()
    conversation = conversations.find.one(
        {'_id': ObjectId(conversation_id), 'participants': str(user_id)}
    )

    if not conversation:
        raise PermissionError(
            f"User {user_id} is not a participant of the conversation {conversation_id}"
        )
    return conversation


# create_message(conversation_id, sender_id, body, attachments, meta) -> message_doc
# get_conversation(conversation_id, page, page_size)
# list_conversations_for_user(user_id, page, page_size)
# mark_messages_read(conversation_id, user_id)


def create_conversation(
    investor_id: str, startup_id: str, initial_message: Optional[str] = None
) -> Dict:
    if not _is_investor(investor_id):
        raise PermissionError("Only investors can initiate conversations. ")
    if not _is_startup(startup_id):
        raise ValueError("Conversations can only be initiated with startups. ")
    conversations = get_conversations_collection()

    existing = conversations.find_one(
        {'participants': {'$all': [str(investor_id), str(startup_id)]}}
    )
    if existing:
        return existing

    conversation_doc = {
        'participants': [str(investor_id), str(startup_id)],
        'created_at': datetime.now(timezone.utc),
        'created_by': str(investor_id),
        'last_message_at': None,
        'last_message_preview': None,
        'meta': {
            'investor_id': str(investor_id),
            'startup_id': str(startup_id),
        },
    }
    result = conversations.insert_one(conversation_doc)
    conversation_doc['_id'] = result.inserted_id

    if initial_message:
        create_message(
            conversation_id=str(conversation_doc['_id']),
            sender_id=investor_id,
            body=initial_message,
        )
    return conversation_doc


def create_message(
    conversation_id: str,
    sender_id: str,
    body: str,
    attachments: Optional[List[Dict]] = None,
    meta: Optional[Dict] = None,
) -> Dict:
    _validate_participant(conversation_id, sender_id)
    messages = get_messages_collection()
    conversations = get_conversations_collection()

    message_doc = {
        'conversation_id': ObjectId(conversation_id),
        'sender_id': str(sender_id),
        'body': body,
        'attachments': attachments or [],
        'meta': meta or {},
        'created_at': datetime.now(timezone.utc),
        'read_by': [str(sender_id)],
    }
    result = messages.insert_one(message_doc)
    message_doc['_id'] = result.inserted_id

    conversations.update_one(
        {'_id': ObjectId(conversation_id)},
        {
            '$set': {
                'last_message_at': datetime.now(timezone.utc),
                'last_message_preview': body[:100],
            }
        },
    )

    return message_doc


def get_conversation(
    conversation_id: str, user_id: str, page: int = 1, page_size: int = 50
) -> Dict:
    _validate_participant(conversation_id, user_id)

    messages = get_messages_collection()

    skip = (page - 1) * page_size

    messages_list = list(
        messages.find({'conversation_id': ObjectId(conversation_id)})
        .sort('created_at', -1)
        .skip(skip)
        .limit(page_size)
    )

    total = messages.count_documents({'conversation_id': ObjectId(conversation_id)})

    return {
        'messages': messages_list,
        'total': total,
        'page': page,
        'page_size': page_size,
    }


def list_conversation_for_user(
    user_id: str, page: int = 1, page_size: int = 20
) -> Dict:
    conversations = get_conversations_collection()
    skip = (page - 1) * page_size
    conversations_list = list(
        conversations.find({'participants': str(user_id)})
        .sort('last_messages_at', -1)
        .skip(skip)
        .limit(page_size)
    )

    total = conversations.count_documents({'participants': str(user_id)})
    return {
        'conversations': conversations_list,
        'total': total,
        'page': page,
    }


def mark_messages_read(conversation_id: str, user_id: str) -> int:
    _validate_participant(conversation_id, user_id)
    messages = get_messages_collection()

    result = messages.update_many(
        {
            'conversation_id': ObjectId(conversation_id),
            'read_by': {'$ne': str(user_id)},
        },
        {'$addToSet': {'read_by': str(user_id)}},
    )
    return result.modified_count
