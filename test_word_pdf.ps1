$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $docPath = "D:\dsp\LeTanDung_24150654\LeTanDung_24150654.docx"
    $doc = $word.Documents.Open($docPath)
    Write-Host "Opened document successfully."
    $pdfPath = "D:\dsp\LeTanDung_24150654\test_word_export.pdf"
    # wdFormatPDF = 17
    $doc.SaveAs([ref]$pdfPath, [ref]17)
    $doc.Close([ref]0)
    Write-Host "Exported PDF successfully!"
} catch {
    Write-Host "Error: $($_.Exception.Message)"
} finally {
    $word.Quit()
}
