python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*

cd jupyterlab_primehub
source /Users/jackpan/miniconda3/etc/profile.d/conda.sh
conda activate jupyterlab-ext

yarn publish --access public

python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*

conda deactivate