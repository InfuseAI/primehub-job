import json

from notebook.base.handlers import APIHandler
from notebook.utils import url_path_join
from primehub_job.utils import get_group_info
import tornado
from tornado import httpclient

NAMESPACE = "jupyterlab-primehub"


class RouteHandler(APIHandler):

    @tornado.web.authenticated
    def get(self, group_id):
        self.finish(json.dumps(get_group_info(group_id)))


class InstanceHandler(APIHandler):

    @tornado.web.authenticated
    def post(self):
        print(self.get_json_body())
        self.finish(json.dumps({
            "data": "instances !!!"
        }))


def url_pattern(web_app, endpoint, *pieces):
    base_url = web_app.settings["base_url"]
    return url_path_join(base_url, NAMESPACE, endpoint, *pieces)


def setup_handlers(web_app):
    host_pattern = ".*$"

    handlers = [(url_pattern(web_app, "get_group_info", "([^/]+)"), RouteHandler),
                (url_pattern(web_app, 'instances'), InstanceHandler)]

    web_app.add_handlers(host_pattern, handlers)

    for h in handlers:
        print(h)
