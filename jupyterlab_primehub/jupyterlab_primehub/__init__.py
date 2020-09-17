from ._version import __version__
from .handlers import setup_handlers
from jupyterlab.labapp import LabApp


def _jupyter_server_extension_paths():
    return [{
        "module": "jupyterlab_primehub"
    }]


def load_jupyter_server_extension(lab_app: LabApp):
    """Registers the API handler to receive HTTP requests from the frontend extension.

    Parameters
    ----------
    lab_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    setup_handlers(lab_app)
    lab_app.log.info("Registered HelloWorld extension at URL path /jupyterlab-primehub")
