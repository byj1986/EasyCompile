# EasyCompile — C# 项目编译打包工具（pack）

自动在指定目录下查找含 **WinExe** 输出的 `.csproj`（多个时取**修改时间最新**的一个），使用 `dotnet build` 以 **Debug** 模式编译（`-p:WarningLevel=0`），输出到 `build/<版本标签>/`，删除 `.pdb` 后可选地将输出目录打成压缩包。默认生成 **`.zip`**；使用 **`-f 7z`** 时若 PATH 中能找到 **`7z` / `7z.exe`** 则生成 **`.7z`**，否则打印提示并改用 **zip**。

## 环境要求

- **.NET SDK**（需能在命令行执行 `dotnet build`）
- **（可选）7-Zip**：仅在使用 **`-f 7z`** 时需要；本机 PATH 中须有 `7z` / `7z.exe` 才会产出 `.7z`，找不到时自动退回 zip。默认 **zip** 打包不依赖 7-Zip。

## C# 项目需满足的条件

1. 存在标记为 **WinExe** 的 `.csproj`（多个时取**修改时间最新**的一个）。
2. 若 `.csproj` 中包含 **`<Version>`**，输出子目录名为版本相关标签；若还有 **`<FileVersion>`**，标签为 `Version-FileVersion`（`FileVersion` 中的半角空格会去掉）。缺少 `<Version>` 时，标签为 **csproj 文件名**（不含扩展名）。压缩包默认为 **`.zip`**；**`-f 7z`** 且 PATH 中有 `7z` 时为 **`.7z`**，否则为 **`.zip`**。

> [!WARNING]
> 每次运行会先**清空整个 `build` 文件夹**再重新创建，请勿在该目录存放需要保留的文件。

---

## 一、使用 pack.exe（推荐）

### 1. 将 pack.exe 加入 PATH

在 PowerShell 中运行本仓库提供的 `AddToUserPath.ps1` 脚本，将 `pack.exe` 所在目录添加至用户 Path：

```powershell
.\AddToUserPath.ps1 "D:\Tools"
```

脚本会自动去重，并在**当前终端会话中立即生效**，无需重新打开终端。

> 首次运行前若遇到执行策略限制，先执行：
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

### 2. 在 Visual Studio 的 PowerShell 终端中运行

Visual Studio 内置的 PowerShell 终端启动后，工作目录（`pwd`）已自动切换到工程所在目录，因此直接执行即可，无需指定路径参数：

```powershell
pack.exe              # 编译并打包为 zip（默认）
pack.exe -f 7z        # 使用 7-Zip 压缩（无 7z 则退回 zip）
pack.exe -c           # 仅编译，不打包
```

### 3. 运行结果

- 编译输出：`build/<版本标签>/`，其中版本标签为 `<Version>`、`<Version>-<FileVersion>`（`FileVersion` 会去掉半角空格以便作路径名），或缺少 `<Version>` 时为 **csproj 文件名**（不含扩展名）。
- 打包文件（未使用 `-c` 时）：`build/<应用名>-V<版本标签>.zip`（默认）；**`-f 7z`** 且 PATH 中有 `7z` 时为 **`.7z`**，否则为 **`.zip`**。
- **Windows**：打包成功后会尝试用资源管理器打开 `build` 所在目录，便于直接取用压缩包。

---

## 二、通过 Python 运行 pack.py

适用于未打包 exe、或在非 Visual Studio 环境下调用的场景。此时终端的工作目录不一定是解决方案目录，**通常需要通过 `-d` 明确指定**。

### 环境要求

- **Python 3.x**（脚本仅使用标准库，**pip 无需安装额外包**；默认 zip，使用 `-f 7z` 且本机无 `7z` 时会自动退回 zip。）

## 参数说明

| 参数 | 说明 |
|------|------|
| `-c` | **仅编译**，不生成压缩包；输出仍在 `build/<版本标签>/`，仍会清理并重建 `build`。 |
| `-f zip`，`-f 7z`，`--format` | **zip**（默认）；**7z** 使用 7-Zip 压缩，若 PATH 中有 `7z` 则用 7z，否则 zip 并打印提示。 |
| `-d <路径>`，`--solution-dir <路径>` | 指定解决方案目录路径；默认使用当前工作目录。 |


### 示例

```bash
python pack.py -d C:\path\to\project           # 指定目录，默认 zip
python pack.py -d C:\path\to\project -f 7z     # 使用 7-Zip 压缩
python pack.py -d C:\path\to\project -c        # 指定目录，仅编译
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

- **「编译失败」**：确认已安装 .NET SDK，且 `dotnet --version` 正常；在项目目录手动执行 `dotnet build` 排查工程问题。
- **「7z 打包失败」**：`7z` 已找到但压缩命令失败时退出；若希望避免走 7z，不要加 **`-f 7z`**（默认即为 zip）。**指定 `-f 7z` 却得到 zip**：说明 PATH 中未找到 `7z`，脚本已自动退回 zip，可按提示安装 7-Zip 并配置 PATH。
- **打包后未自动打开文件夹**：仅 Windows 且打包成功时尝试打开；非 Windows 或打开失败时脚本会打印提示，可手动进入解决方案下的 `build` 目录。
