from __future__ import print_function
from __future__ import absolute_import
import json

from django.http import HttpResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .utils.msgr_utils import FBUtils
from . import models as md
from . import settings as st


class FBMessengerProcessor(View):

    mtypes_map = {
        "text": md.Message.TXT,
        "image": md.Message.IMG,
        "audio": md.Message.AUD,
        "video": md.Message.VID,
        "file": md.Message.FIL,
    }

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(FBMessengerProcessor, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        resp = None
        if request.GET.get('hub.challenge'):
            challenge = request.GET.get('hub.challenge')
            hub_verify_token = request.GET.get('hub.verify_token')
            if hub_verify_token == FBUtils.VERIFY_TOKEN:
                resp = challenge
            else:
                resp = "Error, wrong validation token"

        return HttpResponse(resp)

    def post(self, request):
        json_data = json.loads(request.body.decode('utf-8'))
        #print "Raw JSON:", json_data

        reply_msg = "ACK"
        for entry in json_data['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    #print(message)
                    sender = message['sender']['id']
                    user_details = FBUtils.get_user_details(sender)
                    #print user_details

                    user, is_new_user = md.get_or_create_fb_user(sender, user_details)
                    #print "---> Is New User:", is_new_user, user.fname

                    message_type = None
                    if 'attachments' in message['message']:  # see if it is a media message
                        message_type = message['message']["attachments"][0]["type"].lower()
                    else:  # text message
                        message_type = "text"
                        #print "message----->", message['message']["text"]

                    mtype = self.mtypes_map.get(message_type)
                    msg, is_new_msg = md.store_message(user, mtype, "RCVD", message)  # save incoming message

                    if is_new_user or user.django_user is None:
                        if message['message']["text"]:
                            user_identification = message['message']["text"]
                            #as discussed with Navin on 26 June 2017, the including code must take care of handling user
                            new_user_handler = st.MESSAGE_HANDLERS.get("new_user_handler")
                            if new_user_handler:
                                django_user, new_user_msg = new_user_handler(msg) #get user from callable and link it
                                if django_user is None: #error
                                    user.send_text(new_user_msg, save_message=False)
                                else:
                                    user.link_user(django_user)
                                    user.send_text(new_user_msg)
                            else:
                                raise RuntimeError("The handler 'new_user_handler' is not configured")

                    else:  # regular message, user is known and linked
                        if is_new_msg:  # handle the message via callable or send text reply
                            msg_handler = st.MESSAGE_HANDLERS.get(message_type)
                            #print msg_handler
                            if msg_handler and not callable(msg_handler):
                                reply_msg = msg_handler
                            else:  # call the handler with (user, message)
                                reply_msg = msg_handler(user, msg)
                            user.send_text(reply_msg)
                        else:
                            print("Duplicate message (not replying):", msg.mid)

                else:
                    print("Ignoring non-message/delivery:", json_data)

        # just return blank response
        return HttpResponse()



#sending multimedia messages
#status = FBUtils.send_media_message(sender, "image", "https://i1.wp.com/myzenpath.com/wp-content/uploads/2015/11/MyZenPath.png")
#status = FBUtils.send_media_message(sender, "video", "http://www.sample-videos.com/video/mp4/720/big_buck_bunny_720p_1mb.mp4")
#status = FBUtils.send_media_message(sender, "video", "https://www.quirksmode.org/html5/videos/big_buck_bunny.webm")
