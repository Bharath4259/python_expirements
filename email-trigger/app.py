

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from SendGmail import SendEmail
from SendMSmail import SendEmail


PORT = 8888

class JobStatus(tornado.web.RequestHandler):
    def get(self):
        subject = self.get_argument("subject", default="unknown", strip=True)
        message = self.get_argument("message", default="unknown", strip=True)
        notify = SendEmail()
        notify.send_email(subject, message)
        self.write("Notified !!")

if __name__ == "__main__":
    app = tornado.web.Application(handlers=[(r"/notification", JobStatus)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(PORT)
    print("Starting server")
    tornado.ioloop.IOLoop.instance().start()
