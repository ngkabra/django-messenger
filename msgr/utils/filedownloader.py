import threading


class DownloadThread(threading.Thread):
    def __init__(self, msg):
        super(DownloadThread, self).__init__()
        self.message = msg
        self.daemon = True

    def run(self):
        try:
            status = self.message.download_media()
            if not status:
                print "Failed to download media:", self.message.media_url
        except Exception, e:
            print "   Error: %s"%e

