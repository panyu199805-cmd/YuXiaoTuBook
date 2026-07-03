# 宇小兔每日读书 — 本机构建前端并打包上传清单（Windows）
# 用法：在 PowerShell 中执行  .\deploy.ps1

$ErrorActionPreference = "Stop"
$DeployDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendDir = Join-Path $DeployDir "..\frontend"
$DistDir = Join-Path $FrontendDir "dist"
$Archive = Join-Path $DeployDir "release-dist.zip"

Write-Host "[deploy] 构建前端..." -ForegroundColor Cyan
Push-Location $FrontendDir
if (Test-Path "package-lock.json") { npm ci } else { npm install }
npm run build
Pop-Location

if (-not (Test-Path $DistDir)) {
    throw "前端构建失败：未找到 $DistDir"
}

Write-Host "[deploy] 打包 frontend/dist -> release-dist.zip" -ForegroundColor Cyan
if (Test-Path $Archive) { Remove-Item $Archive -Force }
Compress-Archive -Path (Join-Path $DistDir "*") -DestinationPath $Archive

Write-Host ""
Write-Host "本机构建完成。" -ForegroundColor Green
Write-Host "  产物：$DistDir"
Write-Host "  压缩包：$Archive （可上传到服务器解压到 frontend/dist）"
Write-Host ""
Write-Host "服务器上完整部署步骤见：deploy/DEPLOY.md" -ForegroundColor Yellow
