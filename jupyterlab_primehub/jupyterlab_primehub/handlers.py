import json

from jupyterlab.labapp import LabApp
from notebook.base.handlers import APIHandler
from notebook.utils import url_path_join
import tornado
from .api import group_info, submit_job, get_env
from .utils import get_group_volume_path
import os.path
from shutil import copyfile
from datetime import datetime

ENV_API_ENDPOINT = 'JUPYTERLAB_DEV_API_ENDPOINT'

NAMESPACE = "jupyterlab-primehub"
api_endpoint = 'http://primehub-graphql.hub.svc.cluster.local/api/graphql'

NOTEBOOK_DIR = None


class ResourceHandler(APIHandler):

    @tornado.web.authenticated
    def post(self):
        params = self.get_json_body()
        api_token = params.get('api_token', None)
        group_id = os.environ.get('GROUP_ID')
        self.log.info('group_info with group_id: {}'.format(group_id))
        self.finish(json.dumps(group_info(api_endpoint, api_token, group_id)))


class SubmitJobHandler(APIHandler):

    @tornado.web.authenticated
    def post(self):
        params = self.get_json_body()
        api_token = params.get('api_token', None)
        name = params.get('name', 'notebook_job')
        group_id = os.environ.get('GROUP_ID')
        instance_type = params.get('instance_type', None)
        image = params.get('image', os.environ.get('IMAGE_NAME'))
        path = params.get('path', None)
        self.log.info('group_info with group_id: {}'.format(group_id))

        fullpath = os.path.join(NOTEBOOK_DIR, path)
        self.log.info("notebook path: " + fullpath)
        # copy the file
        group_name = params.get('group_name', os.environ.get('GROUP_NAME'))
        time_string = datetime.now().strftime("%Y%m%d%H%M%S%f")
        copy_file_name = path.replace('.ipynb', '') + '-' + time_string + '.ipynb'
        copy_file_path = os.path.join(get_group_volume_path(group_name), '.' + copy_file_name)
        output_file_path = os.path.join(get_group_volume_path(group_name), copy_file_name.replace('.ipynb', '-output'))
        copyfile(fullpath, copy_file_path)
        command_str = 'jupyter nbconvert --execute {} --output {} --to html --ExecutePreprocessor.timeout=10000 && rm {}'.format(copy_file_path, output_file_path, copy_file_path)
                
        self.finish(json.dumps(submit_job(api_endpoint, api_token, name, group_id, instance_type, image, command_str)))


class EnvironmentHandler(APIHandler):

    @tornado.web.authenticated
    def post(self):
        self.finish(json.dumps(get_env()))


def url_pattern(web_app, endpoint, *pieces):
    base_url = web_app.settings["base_url"]
    return url_path_join(base_url, NAMESPACE, endpoint, *pieces)


def setup_handlers(lab_app: LabApp):
    setup_globals(lab_app)
    web_app, logger = lab_app.web_app, lab_app.log
    apply_api_endpoint_override(logger)

    host_pattern = ".*$"

    handlers = [(url_pattern(web_app, 'resources'), ResourceHandler),
                (url_pattern(web_app, 'submit-job'), SubmitJobHandler),
                (url_pattern(web_app, 'get-env'), EnvironmentHandler)]

    web_app.add_handlers(host_pattern, handlers)
    for h in handlers:
        logger.info('handler => {}'.format(h))


def setup_globals(lab_app):
    global NOTEBOOK_DIR
    NOTEBOOK_DIR = lab_app.notebook_dir

    lab_app.log.info('setup globals')
    lab_app.log.info('\tNOTEBOOK_DIR: ' + NOTEBOOK_DIR)


def apply_api_endpoint_override(logger):
    global api_endpoint
    override = os.environ.get(ENV_API_ENDPOINT, None)
    if not override:
        logger.info('use api-endpoint: {}'.format(api_endpoint))
        logger.info('it could be override from ENV with the key {}'.format(ENV_API_ENDPOINT))
        return
    logger.info('update api-endpoint from ENV: {}'.format(override))
    api_endpoint = override
