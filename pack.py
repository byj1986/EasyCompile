import argparse
import glob
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile


def find_7z():
    for name in ("7z", "7z.exe"):
        path = shutil.which(name)
        if path:
            return path
    return None


def find_exe_csproj(solution_dir):
    """查找含 <OutputType>Exe</OutputType> 的 .csproj 文件，有多个时取修改时间最新的"""
    candidates = []
    for root, _, files in os.walk(solution_dir):
        # 跳过 build 目录
        if os.path.basename(root).lower() == "build":
            continue
        for f in files:
            if f.endswith(".csproj"):
                path = os.path.join(root, f)
                try:
                    tree = ET.parse(path)
                    root_el = tree.getroot()
                    # 兼容有命名空间和无命名空间两种格式
                    for output_type in root_el.iter():
                        if output_type.tag in (
                            "OutputType",
                            "{http://schemas.microsoft.com/developer/msbuild/2003}OutputType",
                        ):
                            if (
                                output_type.text
                                and output_type.text.strip().lower() in ("winexe")
                            ):
                                candidates.append(path)
                                break
                except ET.ParseError:
                    continue
    if not candidates:
        print("[错误] 未找到 .csproj 文件")
        sys.exit(1)
    return max(candidates, key=os.path.getmtime)


def read_versions(csproj_path):
    """读取 .csproj 中的 <Version> 和 <FileVersion>，返回 (version, file_version)。
    FileVersion 会先 strip，再去掉半角空格（如 'Patch 1' -> 'Patch1'），便于文件名等场景。"""
    version = None
    file_version = None
    try:
        tree = ET.parse(csproj_path)
        root_el = tree.getroot()
        for el in root_el.iter():
            tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
            if tag == "Version" and el.text and el.text.strip():
                version = el.text.strip()
            elif tag == "FileVersion" and el.text and el.text.strip():
                file_version = el.text.strip().replace(" ", "")
    except ET.ParseError:
        pass
    return version, file_version


def prepare_build_dir(build_dir):
    if os.path.exists(build_dir):
        print(f"[清理] {build_dir}")
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    print(f"[创建] {build_dir}")


def run_build(csproj_file, output_dir):
    cmd = [
        "dotnet",
        "build",
        csproj_file,
        "-p:WarningLevel=0",
        "-c",
        "Debug",
        "-o",
        output_dir,
    ]
    print(f"[编译] {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("[错误] 编译失败")
        sys.exit(result.returncode)


def delete_pdb(output_dir):
    pdbs = glob.glob(os.path.join(output_dir, "*.pdb"))
    for pdb in pdbs:
        os.remove(pdb)


def find_latest_exe(output_dir):
    exes = glob.glob(os.path.join(output_dir, "*.exe"))
    if not exes:
        print("[错误] 未找到 .exe 文件，无法打包")
        sys.exit(1)
    return max(exes, key=os.path.getmtime)


def create_archive(output_dir, app_name, version_tag, build_dir, archive_format):
    """archive_format: 'zip' 或 '7z'。仅当为 7z 且 PATH 中存在 7z 时使用 7z，否则一律 zip。"""
    seven_z = find_7z() if archive_format == "7z" else None
    if archive_format == "7z" and seven_z:
        archive_name = f"{app_name}-V{version_tag}.7z"
        archive_path = os.path.abspath(os.path.join(build_dir, archive_name))
        print(f"[打包] {archive_path} (7z)")
        # 在 output_dir 下执行，使包内路径与 zip 一致（相对输出目录的根）
        cmd = [seven_z, "a", "-t7z", "-y", "-r", archive_path, "*"]
        result = subprocess.run(cmd, cwd=output_dir)
        if result.returncode != 0:
            print("[错误] 7z 打包失败")
            sys.exit(result.returncode)
    else:
        if archive_format == "7z" and not seven_z:
            print(
                "[提示] 已指定 -f 7z，但未在 PATH 中找到 7z / 7z.exe，改用 zip 打包。"
            )
        zip_name = f"{app_name}-V{version_tag}.zip"
        zip_path = os.path.join(build_dir, zip_name)
        print(f"[打包] {zip_path} (zip)")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in glob.glob(os.path.join(output_dir, "**"), recursive=True):
                if os.path.isfile(file_path):
                    arcname = os.path.relpath(file_path, output_dir)
                    zf.write(file_path, arcname)
    print("[打包完成]")
    if sys.platform == "win32" and hasattr(os, "startfile"):
        folder = os.path.abspath(build_dir)
        try:
            os.startfile(folder)
            print(f"[打开] 资源管理器: {folder}")
        except OSError as e:
            print(f"[提示] 无法打开资源管理器: {e}")


def _archive_format_type(value):
    v = value.lower()
    if v not in ("zip", "7z"):
        raise argparse.ArgumentTypeError("须为 zip 或 7z")
    return v


def main():
    parser = argparse.ArgumentParser(description="C# 项目编译打包工具")
    parser.add_argument("-c", action="store_true", help="仅编译，不打包")
    parser.add_argument(
        "-f",
        "--format",
        dest="archive_format",
        type=_archive_format_type,
        default="zip",
        metavar="FMT",
        help="打包格式：zip（默认）；7z 表示若 PATH 中有 7z 则用 7z，否则用 zip",
    )
    parser.add_argument(
        "-d",
        "--solution-dir",
        dest="solution_dir",
        default=None,
        help="解决方案目录路径，默认为当前工作目录",
    )
    args = parser.parse_args()

    solution_dir = args.solution_dir or os.getcwd()
    print(f"[项目目录] {solution_dir}")

    csproj_file = find_exe_csproj(solution_dir)
    print(f"[项目文件] {csproj_file}")

    version, file_version = read_versions(csproj_file)
    if version:
        version_tag = f"{version}-{file_version}" if file_version else version
    else:
        version_tag = os.path.splitext(os.path.basename(csproj_file))[0]
        print(f"[提示] 未找到 <Version>，使用项目名作为文件夹名")
    print(f"[版本] {version_tag}")

    build_dir = os.path.join(solution_dir, "build")
    output_dir = os.path.join(build_dir, version_tag)

    prepare_build_dir(build_dir)
    run_build(csproj_file, output_dir)
    delete_pdb(output_dir)

    print("[编译完成]")

    if args.c:
        print("[跳过打包]")
        return

    exe_path = find_latest_exe(output_dir)
    app_name = os.path.splitext(os.path.basename(exe_path))[0]

    create_archive(output_dir, app_name, version_tag, build_dir, args.archive_format)


if __name__ == "__main__":
    main()
