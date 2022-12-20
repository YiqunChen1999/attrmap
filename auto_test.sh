
min_ver=6
max_ver=10

# create conda environment.
for ((ver=$min_ver; ver <= $max_ver; ver++))
do 
    echo "creating conda environment with python version 3.$ver"
    conda create -n py3.$ver python=3.$ver -y
    conda activate py3.$ver
    conda install pytest -y
    python3 -m pip install -e .
    # pip install -U attrmap
    pytest tests
    conda deactivate
done

for ((ver=$min_ver; ver <= $max_ver; ver++))
do
    echo "removing python environment of version 3.$ver"
    conda remove -n py3.$ver --all -y
done
