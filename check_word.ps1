try {
    $w = New-Object -ComObject Word.Application
    Write-Host "Word Version: $($w.Version)"
    $w.Quit()
} catch {
    Write-Host "No Word COM: $($_.Exception.Message)"
}
