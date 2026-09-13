# 脑叶公司 Wiki
非官方中文静态资料站。黑金收容档案风格，支持中文/英文/编号检索、危险等级组合筛选、词条详情和浏览器前进后退。

## 当前范围
12 个精选异想体基础档案、主管入门、工作与伤害速查。不是全量 Wiki；无在线编辑或账号系统。精确数值、工作概率及特殊条件尚未完整收录与逐项核验。各词条附英文 Wiki 入口。

## 本地预览
直接用浏览器打开 dist/index.html，或运行：
python3 -m http.server 8000 --directory dist

## GitHub Pages
1. 在自己的 GitHub 下新建公开仓库 lobotomy-wiki，默认分支使用 main。
2. 将本项目的内容上传到仓库根目录，保留 dist 和 .github/workflows/pages.yml 的目录结构。
3. 打开仓库 Settings → Pages → Build and deployment，将 Source 选择为 GitHub Actions。
4. 打开 Actions，运行 Deploy Wiki to GitHub Pages；也可通过向 main 推送提交触发。
5. 等待部署成功后，从工作流的 github-pages 环境入口打开站点。

官方说明：https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

## 更新内容
编辑 dist/app.js 中的 data 数组可补充异想体，字段为编号、中文名、英文名、等级、主题、概览、阅读建议。编辑 dist/style.css 调整样式。全站不依赖外部字体、图片或 JavaScript 库。

## 验证与限制
JavaScript 语法与渲染/过滤逻辑已检查。当前远程浏览器拒绝访问本地预览地址，尚未完成浏览器视觉验证。
部署采用仓库内的 GitHub Actions 工作流。首次发布需要在 Settings → Pages 中选择 GitHub Actions；以工作流成功状态及实际站点响应为发布依据。

## 版权
游戏及相关名称、角色和世界观归 Project Moon 及相应权利人所有；本站与官方无隶属关系。
