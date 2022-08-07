from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading
import time
import os
import textwrap
import datetime
import requests
import json
from html2image import Html2Image
hti = Html2Image()
hti.temp_path = "./temp"

def load_template(name):
    html = ""
    css = ""
    path = "templates/" + name
    with open(path + "/index.html", "r") as f:
        html = f.read()

    with open("templates/template.css", "r") as f:
        css = f.read()

    with open(path + "/main.css", "r") as f:
        css += f.read()

    return {"html": html, "path": path, "css": css}


def render_template(html, css, usetemplate=True):
    timestamp = time.time()
    path = "temp_" + str(timestamp) + ".png"
    hti.screenshot(html_str=html, css_str=css, save_as=path, size=(1280, 720))
    return path


def repl_var(html, vars):
    for var in vars:
        html = html.replace("{" + var[0] + "}", str(var[1]))
    return html


class Handler(BaseHTTPRequestHandler):
    def respond(path, self):
        with open(path, 'rb') as file:
            self.wfile.write(file.read())
        os.remove(path)

    def template_medals(self, template, path):
        name = template["name"]
        medal = path[2]

        url = 'https://osekai.net/medals/api/public/get_medal.php?medal=' + medal
        resp = requests.get(url)
        medalinfo = json.loads(resp.text)

        template = load_template(name)
        vars = [
            ["medal_icon", medalinfo['Link'].replace(".png", "@2x.png")],
            ["medal_name", medalinfo['Name']],
            ["medal_description", medalinfo['Description']],
            ["medal_hint", medalinfo['Instructions']],
            ["medal_solution", medalinfo['Solution']],
            ["accent", "255, 102, 170"]
        ]
        template["html"] = repl_var(template['html'], vars)

        if(medalinfo['Instructions'] == "NULL"):
            template["html"] += "<style>.medalinfo_top_texts h3 { display: none; }</style>"

        rendered = render_template(template["html"], template["css"])
        Handler.respond(rendered, self)

    templates = [{"name": "medals", "def": template_medals}]

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
                    template["def"](self, template, path)
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
