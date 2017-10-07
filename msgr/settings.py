from django.conf import settings

# override defaults to customize the app

MEDIA_UPLOAD_DIR = getattr(settings, 'MEDIA_UPLOAD_DIR', "media_files/%Y/%m/%d")
DEFERRED_DOWNLOADER = getattr(settings, 'DEFERRED_DOWNLOADER', None)   # If this is a callable, then this is called with Message object
MESSAGE_HISTORY_DURATION = getattr(settings, 'MESSAGE_HISTORY_DURATION', 7)  # 0 - don't save, negative forever, positive = no of DAYS

MESSAGE_HANDLERS = getattr(settings, 'MESSAGE_HANDLERS',
                           dict(new_user_handler=None,
                           text="Received your text message. We will get back to you soon!",
                           image="Received your image. We will get back to you soon!",
                           audio="Received your audio. We will get back to you soon!",
                           video="Received your video. We will get back to you soon!",
                           file="Received your file. We will get back to you soon!"))



