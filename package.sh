SO_DIR=count_sketch/build/

mkdir -p $SO_DIR
cp build/count_sketch.so $SO_DIR

python setup.py bdist_wheel
