import requests
import json

class FBUtils:

    VERIFY_TOKEN = "hpou_0i219nas90u21_rsmnsh"

    ACCESS_TOKEN = "EAAIZCp9fYIDMBAAJU7jlZBQeg1ZAjWQmZCx7pUqVQaXVNW31MTIDm6ASyZC72XGsTJnnRiSQkaKtzezEbkypA71ZC1VtCNP8eXZB0JIcA8NtslcyL6PZCnSzzs4uKlDe7ZBlG2z2OEMJulEBpVh1G3E2AC9qzr2sOapiHBAWMO8rIZBAZDZD"
    FB_POST_URL = "https://graph.facebook.com/v2.6/me/messages?access_token="
    FB_GRAPH_URL = "https://graph.facebook.com/v2.6/"

    @staticmethod
    def send_text_message(receiver_id, msg):
        post_message_url = FBUtils.FB_POST_URL + FBUtils.ACCESS_TOKEN
        response_msg = json.dumps({"recipient": {"id":receiver_id}, "message": {"text": msg}})
        status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
        return status.json()

    @staticmethod
    def get_user_details(userid):
        # these are page scoped IDs - https://chatbotsmagazine.com/fb-messenger-bot-how-to-identify-a-user-via-page-app-scoped-user-ids-f95b807b7e46
        # http://stackoverflow.com/questions/40404524/fb-messenger-get-email-address-from-fbid
        fb_user_url = FBUtils.FB_GRAPH_URL + userid + "?access_token=" + FBUtils.ACCESS_TOKEN
        # print "User Details URL:", fb_user_url
        resp = requests.get(fb_user_url)
        if resp:
            return resp.json()
        else:
            return None

    @staticmethod
    def send_media_message(receiver_id, message_type, media_url):
        # https://developers.facebook.com/docs/messenger-platform/send-api-reference/image-attachment
        post_message_url = FBUtils.FB_POST_URL + FBUtils.ACCESS_TOKEN
        response_msg = json.dumps({"recipient": {"id": receiver_id}, "message": {"attachment": {"type": message_type,
                                                                                    "payload": {"url": media_url}}}})
        #print "-----> Sending:", response_msg
        status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
        return status.json()
