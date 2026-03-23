param (
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$FolderPathToAdd
)

# 规范化路径（去掉末尾反斜杠）
$FolderPathToAdd = $FolderPathToAdd.TrimEnd('\', '/')

# 检查路径是否存在
if (-not (Test-Path -Path $FolderPathToAdd -PathType Container)) {
    Write-Warning "路径不存在或不是一个文件夹：$FolderPathToAdd"
    $confirm = Read-Host "是否仍要添加？(y/N)"
    if ($confirm -notmatch '^[Yy]$') {
        Write-Host "已取消。"
        exit 1
    }
}

# 获取当前用户 Path
$currentPath = [System.Environment]::GetEnvironmentVariable("Path", "User")

# 检查是否已存在（不区分大小写）
$existingEntries = $currentPath -split ';' | Where-Object { $_ -ne '' }
$alreadyExists = $existingEntries | Where-Object { $_.TrimEnd('\', '/') -ieq $FolderPathToAdd }

if ($alreadyExists) {
    Write-Host "该路径已存在于用户 Path 中，无需重复添加：$FolderPathToAdd"
    exit 0
}

# 拼接新 Path
$newPath = if ($currentPath.TrimEnd(';') -eq '') {
    $FolderPathToAdd
} else {
    $currentPath.TrimEnd(';') + ';' + $FolderPathToAdd
}

# 写入用户环境变量
[System.Environment]::SetEnvironmentVariable("Path", $newPath, "User")

# 同步更新当前会话的 Path，使其立即生效
$env:Path = $env:Path.TrimEnd(';') + ';' + $FolderPathToAdd

Write-Host "成功将以下路径添加至用户 Path：$FolderPathToAdd"
Write-Host "当前终端会话已立即生效。"
