cd "$PSScriptRoot"

Write-Output "[Git Auto Push] Checking for changes..."

$changes = git status --porcelain

if (-not [string]::IsNullOrWhiteSpace($changes)) {
    $date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $msg = "auto: files updated [$date]"

    git add .
    git commit -m "$msg"
    git push

    Write-Output "[Git Auto Push] ✅ Changes committed and pushed"
} else {
    Write-Output "[Git Auto Push] No changes to push."
}
