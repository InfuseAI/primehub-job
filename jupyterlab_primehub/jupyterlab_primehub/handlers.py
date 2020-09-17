import json

from notebook.base.handlers import APIHandler
from notebook.utils import url_path_join
from primehub_job.utils import get_group_info
import tornado

class RouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post, 
    # patch, put, delete, options) to ensure only authorized user can request the 
    # Jupyter server
    @tornado.web.authenticated
    def get(self, group_id):
        self.finish(json.dumps(get_group_info(group_id)))


def setup_handlers(web_app):
    host_pattern = ".*$"
    
    base_url = web_app.settings["base_url"]
    route_pattern = url_path_join(base_url, "jupyterlab-primehub", "get_group_info", "([^/]+)")
    handlers = [(route_pattern, RouteHandler)]
    web_app.add_handlers(host_pattern, handlers)
