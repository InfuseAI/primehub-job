# pypi: primehub-job
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*

# npm: jupyterlab-primehub
cd jupyterlab_primehub
yarn publish --access public

# pypi: jupyterlab-primehub
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*