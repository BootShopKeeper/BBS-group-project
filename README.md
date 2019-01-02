# 有名BBS
> 有名BBS是一个美丽的功能完善的校园轻论坛，基于SQLite数据库和Flask框架，支持多层次的用户视图以及便捷的帖子管理。
## 安装及快速开始
该项目使用`Python 2.7`和`SQLlite3`，需提前安装并配置。首先将其`git clone`到本地
```
    $ cd BBS
    $ pip install -r requirements.txt
    $ python create_db.py
    $ python migrate_db.py
    $ python run.py
```
系统会自动创建新数据库`app.db`，默认端口为`127.0.0.0:5000`。虽然此时数据库内是空的，但是你可以自己在网页或直接在`pycharm`的终端处用`sqlite3`的语句进行操作。

## 目录
```
    ├─app
    │  ├─static
    │  │  ├─css
    │  │  ├─fonts
    │  │  ├─images
    │  │  ├─js
    │  │  └─vendor
    │  └─templates
    ├─db_repository
```
其中，页面模板在/app/templates文件夹下，前端依赖项主要在/app/static/vendor下。后端文件/app/下。其中，views.py定义路由及数据库查询细节， models.py定义数据库模式，forms.py定义表单格式。

## BBS功能简介
分为用户、版主、管理员三种角色（每种角色的usr_role需要在终端用`sqlite3`进行操作，详见`models.py`）。
* 都有的操作为登录注册、发帖回帖、点赞、浏览版面、查询等，查询用户可以显示该用户基本信息以及发帖回帖的`xml`格式输出。
* 版主可以修改版面名（**但是这里有bug，因为最初创建数据库的时候不知道版面名可以改，于是将版面名设为了主码，但是后来懒得改了，可以将主码改为b_id，再自行修改代码内相关部分**），删除版面内的帖子及回复。
* 管理员可以管理全部帖子与用户（增删）。
* 有几个查询，比如显示十大与热帖，`compete`界面是查询出在A版面发帖比B版面多的用户。
* 有个触发器设置，若一个用户在10分钟内连续发帖超过10个，则判定为水帖用户，不能继续发帖，要缓10分钟。

## 备注

本项目由BootShopKeeper与shellywhen共同创建，是北京大学2018秋数据库概论大作业项目。
