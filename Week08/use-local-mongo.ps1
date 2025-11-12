# Script to use local MongoDB
Write-Host "Switching to local MongoDB..." -ForegroundColor Green
Copy-Item .env.local .env -Force
Write-Host "Done! Now using MongoDB at localhost:27017" -ForegroundColor Green
Write-Host "Restart your FastAPI server for changes to take effect" -ForegroundColor Yellow
