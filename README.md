# 脑叶公司 Wiki（无广告镜像）

面向游玩查阅的中文静态 Wiki。版式和条目尽量贴近 [Fandom 脑叶公司 Wiki](https://lobotomycorp.fandom.com/zh/)，去掉广告、账号墙和追踪脚本。

当前收录 **345** 篇正文和 **181** 条重定向，覆盖异想体档案、部门、职员、考验、抑制核心、E.G.O、剧情和机制。图片仍从原站图床加载。

## 在线地址

GitHub Pages 开启后访问：

https://ji415.github.io/lobotomy-wiki/

仓库：https://github.com/ji415/lobotomy-wiki

## 本地预览

```bash
python3 -m http.server 8000 --directory dist
```

打开 http://127.0.0.1:8000/

## 重新导出

正文来自 Fandom MediaWiki API 的渲染结果（CC BY-SA）。若原 Wiki 有更新：

```bash
python3 scripts/dump_wiki.py
python3 scripts/build_site.py
```

依赖：Python 3.10+、`lxml`。

## 版权

- 词条文本来自社区 Wiki，按 CC BY-SA 使用，并保留指向原站的署名。
- 《脑叶公司》及名称、立绘、设定归 Project Moon 所有。
- 本站为粉丝资料镜像，与官方和 Fandom 均无隶属关系。
