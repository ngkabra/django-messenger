from __future__ import print_function
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
                print("Failed to download media:", self.message.media_url)
        except Exception as e:
            print("   Error: %s"%e)

