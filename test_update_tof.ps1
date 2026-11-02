$w = New-Object -ComObject Word.Application
$w.Visible = $false
try {
    $d = $w.Documents.Open("D:\Xử lý tín hiệu số\test_caption_style.docx")
    $d.Fields.Update()
    foreach ($tof in $d.TablesOfFigures) { $tof.Update() }
    $d.Save()
    Write-Host "Updated successfully."
    $d.Close([ref]0)
} catch {
    Write-Host "Error: $($_.Exception.Message)"
} finally {
    try { $w.Quit() } catch {}
}
