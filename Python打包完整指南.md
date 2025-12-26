# Python GUI程序打包完整指南

## 一、打包准备

### 核心文件清单

**必需包含：**
- `gui.py` - 主程序
- `chaoxing_crawler.py` - 业务逻辑
- `auto_cookie.py` - 功能模块
- `鲸鱼.ico` - 程序图标
- `README.md` - 使用说明

**必需排除：**
- 开发文档（功能总和.md、问题总和.md）
- 用户数据（saved_cookie.json、gui_settings.json）
- 缓存文件（__pycache__、*.pyc）
- 启动脚本（*.bat、*.ps1）

## 二、快速打包

### 方法一：使用spec文件（推荐）

```bash
# 1. 安装PyInstaller
pip install pyinstaller

# 2. 执行打包
pyinstaller --clean build_gui.spec
```

### 方法二：命令行打包

```bash
pyinstaller --name="学习通图片爬取工具" \
            --onefile \
            --windowed \
            --icon=鲸鱼.ico \
            --add-data="鲸鱼.ico;." \
            gui.py
```

## 三、spec文件优化

### 完整配置示例

```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['gui.py'],
    datas=[('鲸鱼.ico', '.'), ('README.md', '.')],
    hiddenimports=['requests', 'tkinter', 'selenium'],
    excludes=['matplotlib', 'numpy', 'pandas', 'PIL', 'scipy', 'pytest'],
)

# 过滤不需要的文件
a.datas = [x for x in a.datas if not any([
    '功能总和.md' in x[0],
    '问题总和.md' in x[0],
    'saved_cookie.json' in x[0],
    'gui_settings.json' in x[0],
    '__pycache__' in x[0],
    '.pyc' in x[0],
])]

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='学习通图片爬取工具',
    console=False,
    icon='鲸鱼.ico',
    upx=True,
)
```

### 关键优化点

**1. 排除大型库（减少45MB）**
```python
excludes=['matplotlib', 'numpy', 'pandas', 'PIL', 'scipy']
```

**2. 过滤开发文件（减少2MB）**
```python
a.datas = [x for x in a.datas if not any([
    '功能总和.md' in x[0],
    '__pycache__' in x[0],
])]
```

**3. 启用UPX压缩（减少8MB）**
```python
upx=True
```

## 四、打包流程

### 标准流程

```bash
# 1. 备份旧版本
copy dist\程序.exe dist\程序_v1.1.exe

# 2. 清理缓存
pyinstaller --clean build_gui.spec

# 3. 测试新版本
cd dist
程序.exe

# 4. 确认后发布
```

### 文件覆盖说明

**会被覆盖：**
- `dist/` - 生成的EXE
- `build/` - 临时文件

**不会覆盖：**
- 源代码（.py）
- 配置文件（.json）
- 文档（.md）

## 五、测试清单

打包完成后必测：
- [ ] 程序正常启动
- [ ] 界面显示正常
- [ ] 核心功能可用
- [ ] 图标显示正确
- [ ] 无报错提示

## 六、常见问题

**Q: 体积太大怎么办？**

A: 
1. 排除不需要的库（excludes）
2. 过滤开发文件（a.datas过滤）
3. 启用UPX压缩（upx=True）

**Q: 打包后缺少模块？**

A: 在 `hiddenimports` 中添加模块名。

**Q: 杀毒软件误报？**

A: 添加到信任列表或使用代码签名。

**Q: 用户数据会丢失吗？**

A: 不会。用户数据在EXE运行目录，不会被覆盖。

**Q: --clean有什么用？**

A: 清理旧缓存，确保使用最新代码打包。

## 七、优化效果

| 优化项 | 优化前 | 优化后 | 减少 |
|--------|--------|--------|------|
| 排除大型库 | 80MB | 35MB | -45MB |
| 过滤开发文件 | 35MB | 33MB | -2MB |
| UPX压缩 | 33MB | 25MB | -8MB |
| **总计** | **80MB** | **25MB** | **-55MB** |

## 八、核心原则

✅ **只打包运行必需的文件**
✅ **排除所有开发和临时文件**
✅ **用户数据运行时生成，不预置**
✅ **使用spec文件统一管理配置**

---

**参考资料：**
- [PyInstaller官方文档](https://pyinstaller.org/)
- [Spec文件详解](https://pyinstaller.org/en/stable/spec-files.html)
