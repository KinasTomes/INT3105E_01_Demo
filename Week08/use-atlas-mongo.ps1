# Script to use MongoDB Atlas
Write-Host "Switching to MongoDB Atlas..." -ForegroundColor Green
Copy-Item .env.atlas .env -Force
Write-Host "Done! Now using MongoDB Atlas" -ForegroundColor Green
Write-Host "Restart your FastAPI server for changes to take effect" -ForegroundColor Yellow
