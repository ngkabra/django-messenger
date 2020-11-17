from __future__ import division

from django.db import models
from django.contrib.auth.models import User

from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
import json
from datetime import datetime
import requests
from .utils.filedownloader import DownloadThread
from .utils.msgr_utils import FBUtils
from . import settings as st

# Create your models here.
'''
            What Needs To Be Done

            (1) Create Sender & Message models to store data from FB messages
            (2) Capture FB ID (rather messanger ID), name, email & phone of the sender
            (3) Message should get text, image/audio/video/file (field - FileType) and timestamp as well as raw JSON in the table
            (4) For each type of message, the configurable reply could be either text or callable function (which gets called by raw message JSON)
            (5) Create MessageManager model which can take text/media and send messages
            (6) The media file uploads must be stored in the configurable directory
            (7) Create app that can be used anywhere else

'''


class MessengerUser(models.Model):
    #types
    FB = "FB"
    TYPE_CHOICES = (
        (FB, 'Facebook'),
    )
    type = models.CharField(max_length=3,
                            choices=TYPE_CHOICES,
                            default='FB')
    sm_id = models.CharField(max_length=255,null=False)
    fname = models.CharField(max_length=100, null=True)
    lname = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=16, null=True)
    django_user = models.ForeignKey(User, null=True,
                                    on_delete=models.CASCADE)

    def link_user(self, d_user):
        if d_user:
            self.django_user = d_user
            self.save()


    # old link_user() when thie app itself linked it with auth_user of django, now the django user must be sent explicitly
    '''
    EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    USERID_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+$)")

    def link_user(self, username_email):
        user = None
        error = None
        try:
            user = User.objects.get(username=username_email)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username_email)
            except User.MultipleObjectsReturned:
                error = "Multiple accounts exist for this email '{}', please send your username instead".format(username_email)
            except User.DoesNotExist:
                error = "This username OR email '{}' does not exist in our system, please send registered email or username".format(username_email)

        # link user if found
        if user and not error:
            self.django_user = user
            self.save()

        #print "Error:", error
        return error
    '''

    def send_text(self, txt, save_message=True):
        if self.FB == self.type:
            status = FBUtils.send_text_message(self.sm_id, txt)
            if save_message and status and status['message_id']:
                #print "Reply MID:", status['message_id']
                store_message(self, Message.TXT, "SENT", txt, reply_mid=status['message_id'])
        else:
            raise TypeError("Sending message not supported for:", self.type)

    def expect_email_or_username(self, success_text=None, error_text=None, only_username=False):
        # https://developers.facebook.com/docs/messenger-platform/product-overview/conversation
        # https://developers.facebook.com/docs/messenger-platform/webhook-reference/postback

        if not success_text:
            success_text = "Received your email/user ID."
        if not error_text:
            error_text = "Only send your ReliScore user-id (preferred) OR email-id, do not add anything else."

        #self.send_text("Please send your ReliScore user-id (preferred) OR email-id:")
        # get the last reply by user
        msg = self._get_latest_user_message_from_db()
        uid_email = msg.text_message
        regex_matched = False

        if only_username and self.USERID_REGEX.match(uid_email):
            regex_matched = True
        elif not only_username:
            if self.USERID_REGEX.match(uid_email) or self.EMAIL_REGEX.match(uid_email):
                regex_matched = True

        if not regex_matched: #while???
            self.send_text(error_text)
        else:
            # ask Navin about storage of the message exchanges
            self.send_text(success_text)
            #print uid_email
            return uid_email

    def _get_latest_user_message_from_db(self, media_type=None):
        user_messages = None
        if media_type:
            user_messages = Message.objects.filter(sender=self).filter(inout=Message.RCVD).filter(mtype=media_type).order_by("-timestamp")
        else:
            user_messages = Message.objects.filter(sender=self).filter(inout=Message.RCVD).order_by("-timestamp")
        if user_messages and len(user_messages) > 0:
            return user_messages[0]
        else:
            return None

    def expect_username(self, success_text=None, error_text=None):
        if not success_text:
            success_text = "Received your ReliScore User ID."
        if not error_text:
            error_text = "Only send your ReliScore user-id, do not add anything else."
        return self.expect_email_or_username(success_text=success_text, error_text=error_text, only_username=True)

    def expect_media(self, success_text, error_text, media_type=None):
        msg = self._get_latest_user_message_from_db(media_type=media_type)
        # more later....

'''
    {u"profile_pic": u"https://scontent.xx.fbcdn.net/v/t1.0-1/12974378_10153525197907742_5935357303322933357_n.jpg?oh=183ca6f72aa7e73dd2573b2cef708934&oe=59B915B6",
     u"first_name": u"Manish", u"last_name": u"Kumar", u"locale": u"en_US", u"gender": u"male", u"timezone": 5.5}
'''


def get_or_create_fb_user(user_id, user_data):
    user, created = MessengerUser.objects.get_or_create(sm_id=user_id)
    if created:
        user.type = "FB"
        user.fname = user_data["first_name"]
        user.lname = user_data["last_name"]
        user.save()
    #return the user
    return user, created


class MessageManager(models.Manager):

    def download_missing_media(self):
        messages = Message.objects.filter(media_url__isnull=False).filter(media='')
        total_downloads = len(messages)
        successful_downloads = 0
        for msg in messages:
            status = msg.download_media()
            if status:
                successful_downloads += 1
        return successful_downloads, total_downloads



class Message(models.Model):
    # types
    TXT = "TXT"
    IMG = "IMG"
    VID = "VID"
    AUD = "AUD"
    FIL = "FIL"

    # sent/received
    RCVD = "RCVD"
    SENT = "SENT"

    TYPE_CHOICES = (
        (TXT, 'Text'),
        (IMG, 'Image'),
        (VID, 'Video'),
        (AUD, 'Audio'),
        (FIL, 'File'),
    )

    MSG_INOUT_CHOICES = (
        (RCVD, "Received"),
        (SENT, "Sent")
    )
    sender = models.ForeignKey(MessengerUser, on_delete=models.CASCADE)
    mid = models.CharField(max_length=255, null=True, unique=True)
    mtype = models.CharField(max_length=3,choices=TYPE_CHOICES, default=TXT)
    inout = models.CharField(max_length=4,choices=MSG_INOUT_CHOICES, default=RCVD)
    text_message = models.CharField(max_length=255,null=True, blank=True)
    media_url = models.URLField(null=True, blank=True)
    media = models.FileField(upload_to=st.MEDIA_UPLOAD_DIR, null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    raw_message = models.TextField(null=True, blank=True)

    # objects = MessageManager()
    def download_media(self):
        temp_media = NamedTemporaryFile(delete=True)
        res = requests.get(self.media_url)
        if res.status_code == requests.codes.ok:
            for block in res.iter_content(16 * 1024):
                if not block:
                    break
                temp_media.write(block)

            #save this to message now
            start = self.media_url.rfind("/") + 1
            end = self.media_url.find("?", start)
            filename = self.media_url[start:end]

            self.media.save(filename, File(temp_media), save=True)
            #print "Downloaded and saved successfully:", filename
            return True  # success

        else: #maybe we should do something about it
            #print "Failed to download media:", self.media_url
            return False # failure




def store_message(user, mtype, inout, message, reply_mid=None):
    # msg = Message.objects.create_message(user)
    msg = None
    is_new = True
    if isinstance(message, dict) and message['message']['mid']:
        try:
            msg = Message.objects.get(mid=message['message']['mid'])
            #print "Message exists, ignoring duplicate:", msg.mid
            if msg:
                is_new = False
        except Message.DoesNotExist:
            msg = _create_new_message(user, mtype, inout, message, reply_mid)
    else:
        msg = _create_new_message(user, mtype, inout, message, reply_mid)

    return msg, is_new


def _create_new_message(user, mtype, inout, message, reply_mid=None):
    msg = Message()

    msg.sender = user
    msg.mtype = mtype
    msg.inout = inout

    if isinstance(message, dict) and message['message']['mid']:
        msg.mid = message['message']['mid']
    elif reply_mid:
        msg.mid = reply_mid

    if isinstance(message, dict) and message['timestamp']:
        msg.timestamp = datetime.fromtimestamp(int(message['timestamp']//1000))
    else:  # for sent messages
        msg.timestamp = datetime.now()


    if isinstance(message, dict):
        msg.raw_message = json.dumps(message)
    else:
        msg.raw_message = message

    if Message.TXT == mtype:
        if isinstance(message, dict):
            #print "Message Text:",  message["message"]['text']
            msg.text_message = message['message']['text']
        else:
            msg.text_message = message

        msg.save() #save
    else:  # media - process asynchronously
        media_url = message['message']['attachments'][0]['payload']['url']
        msg.media_url = media_url
        msg.save()

        #print "Getting media:", media_url

        if st.DEFERRED_DOWNLOADER and callable(st.DEFERRED_DOWNLOADER):  # if custom downloader exists, call it
            st.DEFERRED_DOWNLOADER(msg)
        else: # the default downloader thread
            downloader = DownloadThread(msg)
            downloader.start()
            #pass  # testing no download

    return msg


