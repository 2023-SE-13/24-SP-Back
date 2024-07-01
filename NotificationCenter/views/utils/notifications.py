import json
import uuid
from django.utils import timezone

from CompanyManagement.models import Company
from NotificationCenter.models import Notification
from PositionManagement.models import Position, Offer
from TweetManagement.models import Tweet
from UserManagement.models import User, Message


def create_notification(json_str):
    try:
        notification_id = generate_notification_id()
        data = json.loads(json_str)
        username = data.get('username')
        user = User.objects.get(username=username)
        notification_type = data.get('notification_type')
        content = data.get('content')
        notification = None
        if notification_type == "subscribe":
            tweet_id = data.get('tweet_id', None)
            if tweet_id:
                tweet = Tweet.objects.get(tweet_id=tweet_id)
                notification = Notification.objects.create(
                    notification_id=notification_id,
                    user=user,
                    notification_type=notification_type,
                    content=content,
                    tweet=tweet,
                    created_at=timezone.now()
                )
            position_id = data.get('position_id', None)
            if position_id:
                position = Position.objects.get(position_id=position_id)
                notification = Notification.objects.create(
                    notification_id=notification_id,
                    user=user,
                    notification_type=notification_type,
                    content=content,
                    position=position,
                    created_at=timezone.now()
                )
        elif notification_type == "message":
            message_id = data.get('message_id')
            message = Message.objects.get(message_id=message_id)
            notification = Notification.objects.create(
                notification_id=notification_id,
                user=user,
                notification_type=notification_type,
                content=content,
                message=message,
                created_at=timezone.now()
            )
        elif notification_type == "system":
            company_id = data.get('company_id', None)
            company = Company.objects.filter(company_id=company_id).first()
            position_id = data.get('position_id', None)
            position = Position.objects.filter(position_id=position_id).first()
            offer_id =  data.get('offer_id', None)
            offer = Offer.objects.filter(offer_id=offer_id).first()
            notification = Notification.objects.create(
                notification_id=notification_id,
                user=user,
                notification_type=notification_type,
                content=content,
                company=company,
                position=position,
                offer=offer,
                created_at=timezone.now()
            )

        return notification

    except Exception as e:
        print(e)
        return f'An error occurred: {e}'


def generate_notification_id():
    return str(uuid.uuid4())