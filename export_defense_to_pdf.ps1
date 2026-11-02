$docxPath = "D:\dsp\LeTanDung_24150654\bao_ve_bai_lam.docx"
$pdfPath  = "D:\dsp\LeTanDung_24150654\bao_ve_bai_lam.pdf"

Write-Host "Starting Word Application..."
$word = New-Object -ComObject Word.Application
$word.Visible = $false

try {
    Write-Host "Opening document: $docxPath"
    $doc = $word.Documents.Open($docxPath)
    
    Write-Host "Updating fields..."
    try { $doc.Fields.Update() } catch {}
    
    $wdFormatPDF = 17
    Write-Host "Exporting to PDF: $pdfPath"
    $doc.SaveAs([ref]$pdfPath, [ref]$wdFormatPDF)
    
    $workspacePdf = "D:\Xử lý tín hiệu số\bao_ve_bai_lam.pdf"
    Write-Host "Exporting backup PDF: $workspacePdf"
    $doc.SaveAs([ref]$workspacePdf, [ref]$wdFormatPDF)
    
    $doc.Close([ref]0)
    Write-Host "PDF EXPORT SUCCESSFUL!"
} catch {
    Write-Host "Error during export: $($_.Exception.Message)"
} finally {
    try { $word.Quit() } catch {}
}
