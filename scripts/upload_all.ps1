$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJBZG1pbiIsImV4cCI6MTc3OTY4NTc0MH0.LMsMKUQgGA1U1gyt37fTLi9a7U3TyMV0tt-BkBCeXhw"
$files = Get-ChildItem -Path "benchmarks/data/raw" -Filter "*.pdf"
foreach ($file in $files) {
    if ($file.Name -eq "dist_509_body_34838_1.pdf") {
        Write-Host "Skipping $($file.Name) (already uploaded)"
        continue
    }
    Write-Host "Uploading $($file.Name)..."
    curl.exe -X POST "http://localhost:8000/upload" -H "Authorization: Bearer $token" -F "file=@$($file.FullName)"
}
