from pushserver.applications.apple import *
from pushserver.applications.firebase import *
from pushserver.resources.utils import callid_to_uuid


__all__ = ['AppleSylkHeaders', 'AppleSylkPayload',
           'FirebaseSylkHeaders', 'FirebaseSylkPayload']


class AppleSylkHeaders(AppleHeaders):
    """
    An Apple headers structure for a push notification
    """

    def create_push_type(self) -> str:
        """
        logic to define apns_push_type value using request parameters
        apns_push_type reflect the contents of the notification’s payload,
        it can be:
        'alert', 'background', 'voip',
        'complication', 'fileprovider' or 'mdm'.
        """
        push_type = 'voip' if self.event in ('incoming_session', 'incoming_conference_request') else 'background'

        return push_type

    def create_expiration(self) -> int:
        """
        logic to define apns_expiration value using request parameters
        apns_expiration is the date at which the notification expires,
        (UNIX epoch expressed in seconds UTC).
        """
        return '120'

    def create_topic(self) -> str:
        """
        logic to define apns_topic value using request parameters
        apns_topic is in general is the app’s bundle ID and may have
        a suffix based on the notification’s type.
        """
        apns_topic = self.app_id

        if self.app_id.endswith('.dev') or self.app_id.endswith('.prod'):
            apns_topic = '.'.join(self.app_id.split('.')[:-1])

        if self.event in ('incoming_session', 'incoming_conference_request'):
            apns_topic = f"{apns_topic}.voip"

        return apns_topic

    def create_priority(self) -> int:
        """
        logic to define apns_priority value using request parameters
        Notification priority,
        apns_prioriy 10 o send the notification immediately,
        5 to send the notification based on power considerations
        on the user’s device.
        """
        apns_priority = '10' if self.event in ('incoming_session', 'incoming_conference_request') else '5'

        return apns_priority


class FirebaseSylkHeaders(FirebaseHeaders):
    """
    Firebase headers for a push notification
    """


class AppleSylkPayload(ApplePayload):
    """
    A payload for a Apple Sylk push notification
    """

    @property 
    def payload(self) -> str:
        """
        Generate an AppleSylk notification payload
        """

        if self.event == 'cancel':
            payload = {
                'event': self.event,
                'call-id': self.call_id,
                'session-id': callid_to_uuid(self.call_id),
            }
        else:
            payload = {
                'event': self.event,
                'call-id': self.call_id,
                'session-id': callid_to_uuid(self.call_id),
                'media-type': self.media_type,
                'from_uri': self.sip_from,
                'from_display_name': self.from_display_name,
                'to_uri': self.sip_to
            }

        return payload


class FirebaseSylkPayload(FirebasePayload):
    """
    A payload for a Firebase Sylk push notification
    """

    @property
    def payload(self) -> str:
        """
        Generate a Sylk payload and extra Firebase parameters
        """

        if not self.from_display_name:
            from_display_name = self.sip_from
        else:
            from_display_name = self.from_display_name

        if self.event == 'cancel':
            data = {
                'event': self.event,
                'call-id': self.call_id,
                'session-id': callid_to_uuid(self.call_id),
            }
        else:
            data = {
                'event': self.event,
                'call-id': self.call_id,
                'session-id': callid_to_uuid(self.call_id),
                'media-type': self.media_type,
                'from_uri': self.sip_from,
                'from_display_name': from_display_name,
                'to_uri': self.sip_to
            }

        payload = {
            'message': {
                'token': self.token,
                'data': data,
                'android': {
                             'priority': 'high',
                             'ttl': '60s'
                            }
                       }
                   }

        return payload

