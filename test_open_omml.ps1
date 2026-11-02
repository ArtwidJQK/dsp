$w = New-Object -ComObject Word.Application
$w.Visible = $false
try {
    $d = $w.Documents.Open('D:\Xử lý tín hiệu số\test_omml_insert.docx')
    Write-Host "Doc opened successfully! Paragraphs: $($d.Paragraphs.Count)"
    $d.Close([ref]0)
} finally {
    $w.Quit()
}
