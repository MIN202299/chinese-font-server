> 中文字体服务器

## 约束
1. 所有需要分割的字体都放在 `font/split` 文件夹下
2. 所有不需要分割的字体都放在 `font/normal` 文件夹下 
3. 每一个 `font/split` 文件夹下, 第一级目录的每一个文件夹为同一个字体家族, 不同字重的字体可以放在同一个字体家族
4. 只支持 ttf 和 otf 格式的字体
5. 同一个字体,多个相同的字重可能会被覆盖,建议将相同字体的不同字体风格分为两个不同字体

## 用法

1. 安装python依赖
```bash
pip install -r requirements.txt
```

2. 将需要分割的字体放在 /font/split 目录下
3. 运行
```bash
# linux
nohup python ./src/run.py &
# win
python ./src/run.py 
```
4. 使用
```html
<!-- 所有支持的字体及字重可以在 `FONT_DETAIL.json` 查看 -->
<!-- 默认引入所有字重 -->
<link rel="stylesheet" href="http://{host}:{port}/css?family={font_family}"/>
<!-- 引入字重[400] -->
<link rel="stylesheet" href="http://{host}:{port}/css?family={font_family}:wght@400"/>
<!-- 引入[100-700] -->
<link rel="stylesheet" href="http://{host}:{port}/css?family={font_family}:wght@100..700"/>
```

## 配置
可以将分割后的字体`/dist/transform`文件夹上传自己的OSS服务器或者通过Nginx代理,然后将`/src/run.py`中的变量`CSS_HOST_URI`改为自己的OSS路径前缀或者Nginx路径前缀即可


## TODO
- 同一个字体,多个相同的字重可能会被覆盖,建议将相同字体的不同字体风格分为两个不同字体
