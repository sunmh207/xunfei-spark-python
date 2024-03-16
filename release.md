## 发布流程

1. 修改setup.py文件中版本号

```
VERSION = '0.0.5'
```

2. 打包

```commandline
python setup.py sdist bdist_wheel
```

3. 上传

```commandline
twine upload dist/*
```

4.安装测试
在新项目中安装xunfei-spark-python,并参照main.py中示例测试

```
pip install xunfei-spark-python=0.05
```





