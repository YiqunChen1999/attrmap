source ~/.bashrc

min_ver=6
max_ver=10

# executing unit tests
for ((ver=$min_ver; ver <= $max_ver; ver++))
do
    echo "executing unit tests under python version $ver"
    conda activate py3.$ver
    python3 -m pip install --user -e .
    pytest tests
    conda deactivate 
    conda remove -n py3.$ver --all -y
done