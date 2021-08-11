# jupyterlab-primehub

Jupyterlab extension for PrimeHub

## Requirements

* JupyterLab >= 2.2.5

## Install

```bash
jupyter labextension install @infuseai/jupyterlab-primehub
pip install jupyterlab_primehub
jupyter serverextension enable jupyterlab_primehub
```

## Uninstall

```bash
jupyter labextension uninstall @infuseai/jupyterlab-primehub
jupyter serverextension disable jupyterlab_primehub
pip uninstall jupyterlab_primehub
```

## Build the Docker Image

Example docker file:
```dockerfile
FROM jupyter/base-notebook
ARG PRIMEHUB_EXTENSION_VERSION="0.1.4"
USER $NB_UID
RUN pip install --no-cache-dir jupyterlab_primehub~=$PRIMEHUB_EXTENSION_VERSION && \
    jupyter serverextension enable jupyterlab_primehub && \
    jupyter labextension install @infuseai/jupyterlab-primehub@~v$PRIMEHUB_EXTENSION_VERSION && \
    jupyter-lab build
```

## Troubleshooting

- If the JupyterLab < 2.2.5, you may see this error:
    ```
    ValueError: No version of @infuseai/jupyterlab-primehub could be found that is compatible with the current version of JupyterLab. However, it seems to support a new version of JupyterLab. Consider upgrading JupyterLab.

    Conflicting Dependencies:
    JupyterLab              Extension      Package
    >=2.1.2 <2.2.0          >=2.2.5 <3.0.0 @jupyterlab/application
    >=2.1.1 <2.2.0          >=2.2.5 <3.0.0 @jupyterlab/apputils
    >=2.1.2 <2.2.0          >=2.2.5 <3.0.0 @jupyterlab/notebook
    >=5.1.0 <5.2.0          >=5.2.4 <6.0.0 @jupyterlab/services
    ```

- If the `jupyter-client` version is too old, you may see this error:
    ```python
    from jupyter_client import AsyncKernelManager
    ImportError: cannot import name ‘AsyncKernelManager’
    ```

- If the `ipykernel` version is too old, you may see this error:
    ```python
    AttributeError: 'AsyncKernelManager' object has no attribute ‘cleanup_resources'
    ```

## Contributing

Please check [DEVELOPMENT](DEVELOPMENT.md).