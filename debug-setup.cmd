@echo off
echo 🚀 Starting Flask Debug Environment...

REM Build and start the debug containers
docker-compose -f docker-compose.debug.yml up --build -d

echo ✅ Debug environment started!
echo.
echo 📋 Next steps:
echo 1. Wait for the containers to fully start ^(check with: docker-compose -f docker-compose.debug.yml ps^)
echo 2. In VS Code, go to Run and Debug ^(Ctrl+Shift+D^)
echo 3. Select 'Debug Flask in Docker' configuration
echo 4. Press F5 to start debugging
echo.
echo 🌐 Your Flask app will be available at: http://localhost:5000
echo 🔧 Debug port is available at: localhost:5678
echo.
echo 📝 Useful commands:
echo   - View logs: docker-compose -f docker-compose.debug.yml logs -f app
echo   - Stop debug environment: docker-compose -f docker-compose.debug.yml down
echo   - Rebuild: docker-compose -f docker-compose.debug.yml up --build
pause 