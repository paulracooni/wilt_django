#%%
from firebase_admin import messaging
# See firebase_admin.messaging documentation
# [https://firebase.google.com/docs/reference/admin/python/firebase_admin.messaging]


def send_message(title, msg, token, data_object=None, dry_run=False, app=None):
    # Send a message to the single device
    response = messaging.send(
        message=messaging.Message(
            notification=messaging.Notification(
                title=title, body=msg
            ),#Notification
            data=data_object,
            token=token,
        ),#Message
        dry_run=dry_run, 
        app=firebase_app
    )#send


def send_multicast(title, msg, tokens, data_object=None, dry_run=False, app=None):
    # Send a message to the device corresponding to the provided
    response = messaging.send_multicast(
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title, body=msg
            ),#Notification
            data=data_object,
            tokens=tokens,
        ),#MulticastMessage
        dry_run=dry_run, 
        app=firebase_app
    )#send_multicast
# %%
