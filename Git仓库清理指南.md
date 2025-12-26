# 清理Git仓库中不需要的文件

## 问题
`.gitignore` 只对新文件生效，已追踪的文件需要手动删除。

## 解决方案

### 1. 删除已追踪的开发文档

```bash
# 从Git中删除（保留本地文件）
git rm --cached "功能总和.md"
git rm --cached "问题总和.md"
git rm --cached "技术问题记录.md"
git rm --cached "打包说明.md"
git rm --cached "PyInstaller打包优化指南.md"
git rm --cached "Python打包完整指南.md"
git rm --cached "EXE启动速度优化指南.md"

# 提交删除
git commit -m "Remove development documentation from repository"

# 推送到远程
git push
```

### 2. 一键清理脚本（推荐）

```bash
# 删除所有已追踪但在.gitignore中的文件
git rm -r --cached .
git add .
git commit -m "Clean up repository: remove ignored files"
git push
```

### 3. 验证清理结果

```bash
# 查看将要提交的文件
git status

# 查看远程仓库文件列表
git ls-files
```

## 应该保留的文件

**核心代码：**
- gui.py
- chaoxing_crawler.py
- auto_cookie.py

**配置文件：**
- build_gui.spec
- .gitignore

**资源文件：**
- 鲸鱼.ico
- README.md

**可执行文件：**
- dist/学习通图片爬取工具.exe

## 不应该提交的文件

**开发文档：**
- 功能总和.md
- 问题总和.md
- 技术问题记录.md
- Python打包完整指南.md
- EXE启动速度优化指南.md

**用户数据：**
- saved_cookie.json
- gui_settings.json
- images/

**构建产物：**
- build/
- __pycache__/
- *.pyc

## 注意事项

⚠️ 使用 `git rm --cached` 只会从Git中删除，本地文件不会丢失。

⚠️ 推送后，其他人拉取代码时这些文件会被删除（如果他们没有本地修改）。

⚠️ 建议在清理前先备份重要文件。
