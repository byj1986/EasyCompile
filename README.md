# EasyPack — C# 项目编译打包工具

自动查找解决方案与可执行项目，使用 `dotnet build` 以 Release 模式编译，输出到 `build/<版本>/`，删除 `.pdb` 后可选地将输出目录打成 zip。

## 环境要求

- **.NET SDK**（需能在命令行执行 `dotnet build`）

## C# 项目需满足的条件

1. 解决方案目录下存在 **一个** `.sln` 解决方案文件。
2. 存在标记为 **WinExe** 的 `.csproj`（多个时取**修改时间最新**的一个）。
3. 该 `.csproj` 中必须包含 **`<Version>`**；若还有 **`<FileVersion>`**，zip 命名会使用 `版本-FileVersion` 形式。

> [!WARNING]
> 每次运行会先**清空整个 `build` 文件夹**再重新创建，请勿在该目录存放需要保留的文件。

---

## 一、使用 pack.exe（推荐）

### 1. 将 pack.exe 加入 PATH

1. 按 **Win + R**，输入 `sysdm.cpl` 回车，打开「系统属性」。
2. 打开 **「高级」** 选项卡 → **「环境变量」**。
3. 在 **「用户变量」** 或 **「系统变量」** 中选中 **Path** → **「编辑」**。
4. **「新建」**，填入 `pack.exe` 所在目录的完整路径，例如：`D:\Tools`
5. 依次 **确定** 保存所有对话框，然后**重新打开**终端使 PATH 生效。

### 2. 在 Visual Studio 的 PowerShell 终端中运行

Visual Studio 内置的 PowerShell 终端启动后，工作目录（`pwd`）已自动切换到 `.sln` 所在目录，因此直接执行即可，无需指定路径参数：

```powershell
pack.exe        # 编译并打包成 zip
pack.exe -c     # 仅编译，不打包
```

### 3. 运行结果

- 编译输出：`build/<Version>[-<FileVersion>]/`
- 打包文件（未使用 `-c` 时）：`build/<应用名>.<Version>[-<FileVersion>].zip`

---

## 二、通过 Python 运行 pack.py

适用于未打包 exe、或在非 Visual Studio 环境下调用的场景。此时终端的工作目录不一定是解决方案目录，**通常需要通过 `-d` 明确指定**。

### 环境要求

- **Python 3.x**（脚本仅使用标准库，无需额外安装依赖）

## 参数说明

| 参数 | 说明 |
|------|------|
| `-c` | **仅编译**，不生成 zip；输出仍在 `build/<版本>/`，仍会清理并重建 `build`。 |
| `-d <路径>`，`--solution-dir <路径>` | 指定解决方案目录路径；默认使用当前工作目录。 |


### 示例

```bash
python pack.py -d C:\path\to\project       # 指定目录并打包
python pack.py -d C:\path\to\project -c    # 指定目录，仅编译
```

---

## 三、修改编译打包逻辑后重新生成 exe

若需要修改 `pack.py` 的编译或打包逻辑，修改完成后需用 PyInstaller 重新生成 `pack.exe`：

```bash
pip install pyinstaller
pyinstaller -F -n pack pack.py --distpath dist
```

生成的 `dist\pack.exe` 替换到 PATH 中的对应目录即可生效。

---

## 常见问题

- **「未找到 .sln 文件」**：确认当前目录或 `-d` 指定的目录中存在 `.sln` 文件。
- **「编译失败」**：确认已安装 .NET SDK，且 `dotnet --version` 正常；在项目目录手动执行 `dotnet build` 排查工程问题。
- **PATH 改完无效**：关闭并重新打开所有终端/IDE 窗口后再试。
