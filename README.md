# 凌特杯赛道三计算工具

## 使用前须知/免责声明
>本项目仅仅用于交流学习，代码编写学习使用；如果用于商用，作弊等行为，后果自负，与作者无关。
## 目录结构一览
|  文件   | 解释  |
|  ----  | ----  |
| pycache  | python缓存文件夹 |
| build | 构建exe的文件 |
| dist | 构建后的exe存在这里 |
| source | 储存算法脚本 |
| main.py | 主程序 |
## 打包exe
pyinstaller -w -F -i favicon.ico main.py

pip install pyinstaller