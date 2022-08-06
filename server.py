from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading
import time
import os
import textwrap
import datetime
import imgkit


def load_template(name):
    html = ""
    css = ""
    path = "templates/" + name
    with open(path + "/index.html", "r") as f:
        html = f.read()

    return {"html": html, "path": path}


def render_template(html, css, usetemplate=True):
    timestamp = time.time()
    path = "temp/temp_" + str(timestamp) + ".png"
    csstouse = [css, "templates/template.css"]
    if(usetemplate == False):
        csstouse = [css]
    imgkit.from_string(html, path, css=csstouse)
    return path


class Handler(BaseHTTPRequestHandler):
    def respond(path, self):
        with open(path, 'rb') as file:
            self.wfile.write(file.read())
        os.remove(path)

    def template_test(self, template):
        name = template["name"]
        template = load_template(name)
        # <TEXT>
        # TODO: clean this up in a more flexible way
        tim = time.localtime()
        current_time = time.strftime("%H:%M:%S", tim)
        template["html"] = template["html"].replace(
            "{TIME}", str(current_time))
        # </>
        rendered = render_template(
            template["html"], template["path"] + "/main.css", False)
        Handler.respond(rendered, self)
    templates = [{"name": "test", "def": template_test}]

    def do_GET(self):
        path = list(filter(None, self.path.split("/")))
        notFound = True
        if(path[0] == "template"):
            if(len(path) > 1):
                exists = False
                template = None
                for templ in Handler.templates:
                    print(templ)
                    if(templ['name'] == path[1]):
                        print("that's the one")
                        exists = True
                        template = templ
                        break
                if(template is not None):
                    notFound = False
                    self.send_response(200)
                    self.send_header("Content-Type", "image/png")
                    self.end_headers()
                    template["def"](self, template)
        if(notFound == True):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(str("not found").encode())


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass


def run():
    server = ThreadingSimpleServer(('0.0.0.0', 23419), Handler)
    server.serve_forever()


if __name__ == '__main__':
    run()
