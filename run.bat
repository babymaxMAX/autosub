@echo off
echo Starting AutoSub Bot...
echo.

REM Check if Docker is running
docker info > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

echo Docker is running. Starting services...
echo.

REM Start Docker Compose
docker-compose up -d

echo.
echo Services started! Check status with: docker-compose ps
echo View logs with: docker-compose logs -f
echo.
pause

