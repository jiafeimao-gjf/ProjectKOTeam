# 说明与扩展

## 运行示例
```
# 读取文件
$ python toolset.py read README.md
# 文件内容会直接输出到终端

# 写入文件
$ python toolset.py write ./tmp/hello.txt "Hello, world!"
[成功] 已写入 /absolute/path/tmp/hello.txt
```
## 如何添加新工具
### 定义类
```
class MyTool(BaseTool):
    def run(self, args):
        # 你的实现
        return 0
```
### 注册工具
```
ToolRegistry.register("mytool", MyTool)
```
### 添加命令行子解析器
```
my_parser = subparsers.add_parser("mytool", help="自定义工具说明")
my_parser.add_argument(... )   # 根据需要添加参数
my_parser.set_defaults(func=MyTool().run)
```
这样，只要重启脚本即可使用 mytool 命令。