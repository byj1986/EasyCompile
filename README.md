# compile_package — C# 项目编译打包工具

`pack.py` 在 **当前工作目录** 下自动查找解决方案与可执行项目，使用 `dotnet build` 以 Release 输出到 `build/<版本>/`，删除 `.pdb` 后可选地将输出目录打成 zip。

## 环境要求

- **Python 3.x**（运行 `pack.py`；脚本仅使用标准库，无需 `pip install` 依赖）
- **.NET SDK**（需能在命令行执行 `dotnet build`）

## 项目需满足的条件

1. 当前目录下存在 **一个** `.sln` 解决方案文件。
2. 存在标记为 **WinExe** 的 `.csproj`（多个时取**修改时间最新**的一个）。
3. 该 `.csproj` 中必须包含 **`<Version>`**；若还有 **`<FileVersion>`**，zip 命名会使用 `版本-FileVersion` 形式。

输出目录会先清空整个 **`build`** 文件夹再重新创建，请注意不要在该目录存放需要保留的文件。

## 使用方法

在 **C# 解决方案所在目录** 打开终端，执行：

```bash
python /path/to/pack.py
```

若已将本工具所在目录加入 PATH，并在该目录下放置下文中的 **`pack.cmd`**（与 `pack.py` 同级），可在任意解决方案目录下执行：

```bash
pack.cmd
```

否则请使用 `python` 加脚本的**完整路径**，或在解决方案目录使用相对路径指向 `pack.py`。

### 命令行参数

| 参数 | 说明 |
|------|------|
| `-c` | **仅编译**，不生成 zip；输出仍在 `build/<版本>/`，仍会清理并重建 `build`。 |

示例：

```bash
python pack.py        # 编译并打包 zip
python pack.py -c     # 只编译，不打包
```

### 运行结果

- 编译输出：`build/<Version>[-<FileVersion>]/`
- 打包文件（未使用 `-c` 时）：`build/<应用名>.<Version>[-<FileVersion>].zip`（应用名为输出目录中**最新修改**的 `.exe` 的主文件名）

---

## 将工具加入 PATH（Windows）

把 **包含 `pack.py` 的文件夹** 加入系统或用户 PATH 后，可在任意目录用 `python pack.py` 调用（需写清脚本全路径或从该目录复制/软链脚本）。更常见的做法是：

1. 按 **Win + R**，输入 `sysdm.cpl` 回车，打开「系统属性」。
2. 打开 **「高级」** 选项卡 → **「环境变量」**。
3. 在 **「用户变量」** 或 **「系统变量」** 中选中 **Path** → **「编辑」**。
4. **「新建」**，填入本仓库所在目录的完整路径，例如：
   - `C:\Users\你的用户名\Codes\swhysc\compile_package`
5. 依次 **确定** 保存所有对话框。
6. **重新打开** 终端（或 Cursor/VS Code 内置终端），使 PATH 生效。

之后在解决方案目录执行（将路径换成你的实际路径）：

```bash
python C:\Users\你的用户名\Codes\swhysc\compile_package\pack.py
```

若希望只输入短命令（如 `pack.cmd`），在本工具目录下新建 **`pack.cmd`**（与 `pack.py` 同级），内容如下；再把**该目录**加入 PATH 即可在任意解决方案目录调用：

```bat
@echo off
python "%~dp0pack.py" %*
```

用法示例：`pack.cmd`、`pack.cmd -c`。

---

## 将 `pack.py` 打成独立 exe（可选）

本仓库提供 PyInstaller 配置说明，详见 `create_exe.txt`。安装构建依赖后可在本目录执行：

```bash
pip install pyinstaller
pyinstaller -F -n pack pack.py --distpath dist
```

生成的 `dist\pack.exe` 可复制到 PATH 中的目录，在解决方案文件夹内直接运行 `pack.exe` 即可（仍需本机已安装 .NET SDK）。

---

## 常见问题

- **「未找到 .sln 文件」**：请在包含 `.sln` 的目录下执行脚本，不要在上级目录执行。
- **「编译失败」**：确认已安装 .NET SDK，且 `dotnet --version` 正常；在项目目录手动执行 `dotnet build` 排查工程问题。
- **PATH 改完无效**：关闭并重新打开所有终端/IDE 窗口后再试。
