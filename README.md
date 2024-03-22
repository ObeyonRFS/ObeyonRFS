# Robotic Framework System

RFS (Robotic Framework System) is a python package that mimic ROS(Robotic Operating System) in term of communication ex. TCP, DDS but also supports for

This python package aim to be ROS-like that mainly focus on working on Windows.

However working across OS is likely easy right now. As python are riches in modules to make many tasks possible.

ROS2 utilize FastDDS and QT

This package will utilize socket, wxPython similarly in ROS1

However this package might utilize FastDDS in the future.

Quick command for dev/test

```
poetry build
pip install .\dist\rfs-0.0.10-py3-none-any.whl --force-reinstall --no-deps
```

since `pip install -e .` doesn't properly work with poetry

https://readthedocs.org/ might be the best here
