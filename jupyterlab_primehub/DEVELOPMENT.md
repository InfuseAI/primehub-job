
# Prepare your development environment

We follow [Extension Tutorial](https://jupyterlab.readthedocs.io/en/stable/developer/extension_tutorial.html#extension-tutorial) to create the development environment.

## jupyterlab-ext env

Create and activate `jupyterlab-ext` env

```
conda create -n jupyterlab-ext --override-channels --strict-channel-priority -c conda-forge -c anaconda jupyterlab cookiecutter nodejs git
```

```
conda activate jupyterlab-ext
```

Install jupyterlab, the version `2.2.5` is same with dependencies set in the `package.json`

```
conda install -c conda-forge jupyterlab=2.2.5
```

## Developing

### Install modules

Run the command at `jupyterlab_primehub` directory, if you haven't install dependencies.

```
yarn install
```

### Install extension

For the first time to launch our extension, you have to build and do `labextension install`

```
jlpm run build
jupyter labextension install .
```

### Install serverextension

Install 

```
pip install .
```

Enable serverextension

```
jupyter serverextension enable jupyterlab_primehub
```

### Update and run

Open another terminal and watch changes same directorty

```
jupyter lab --watch
```

If you want to use serverextension to query graphql

```
JUPYTERLAB_DEV_API_ENDPOINT=http://hub.xxx.aws.primehub.io \
GROUP_ID=xxxxx \
jupyter lab --watch
```

In the originial terminal, rebuild and wait for updated

```
jlpm run build
```

After updatd, refresh browser and see the changes.

### Publish

```
yarn login
yarn publish --access public
```
