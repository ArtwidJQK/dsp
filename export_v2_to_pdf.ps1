$docxPath = "D:\dsp\LeTanDung_24150654\LeTanDung_24150654_v2.docx"
$pdfPath  = "D:\dsp\LeTanDung_24150654\LeTanDung_24150654_v2.pdf"

Write-Host "Starting Word Application..."
$word = New-Object -ComObject Word.Application
$word.Visible = $false

try {
    Write-Host "Opening document: $docxPath"
    $doc = $word.Documents.Open($docxPath)
    
    Write-Host "Updating all document fields (TOC, LOF, LOT, SEQ, STYLEREF)..."
    try {
        $doc.Fields.Update()
    } catch {
        Write-Host "Note: Fields.Update() exception: $($_.Exception.Message)"
    }
    
    foreach ($toc in $doc.TablesOfContents) {
        try { $toc.Update() } catch {}
    }
    foreach ($tof in $doc.TablesOfFigures) {
        try { $tof.Update() } catch {}
    }
    
    Write-Host "Saving updated docx with populated fields..."
    $doc.Save()
    
    Write-Host "Exporting to PDF: $pdfPath"
    $wdFormatPDF = 17
    $doc.SaveAs([ref]$pdfPath, [ref]$wdFormatPDF)
    
    Write-Host "Closing document..."
    $doc.Close([ref]0)
    Write-Host "PDF EXPORT SUCCESSFUL!"
} catch {
    Write-Host "Error during export: $($_.Exception.Message)"
} finally {
    try {
        $word.Quit()
    } catch {}
}
