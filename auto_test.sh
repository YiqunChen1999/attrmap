
min_ver=6
max_ver=10

# create conda environment.
for ((ver=$min_ver; ver <= $max_ver; ver++))
do 
    echo "creating conda environment with python version $ver"
    conda create -n py3.$ver python=3.$ver -y
    conda activate py3.$ver
    python3 -m pip install --user -e .
    conda install pytest -y
    pytest tests
    conda deactivate
done

source ~/.bashrc

# # executing unit tests
# for ((ver=$min_ver; ver <= $max_ver; ver++))
# do
#     echo "executing unit tests under python version $ver"
#     # conda init bash
#     conda activate py3.$ver
#     conda deactivate 
# done

for ((ver=$min_ver; ver <= $max_ver; ver++))
do
    echo "removing python environment of version $ver"
    conda remove -n py3.$ver --all -y
done