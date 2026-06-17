@echo off
title نقابة المحامين بالفيوم - السيرفر المحلي
echo.
echo  ========================================
echo   نقابة المحامين بالفيوم
echo   جاري تشغيل الموقع على المنفذ 8003...
echo  ========================================
echo.
echo  الموقع:        http://127.0.0.1:8003/
echo  لوحة التحكم:  http://127.0.0.1:8003/dashboard/login/
echo  المستخدم:      admin
echo  كلمة المرور:   admin123
echo.
cd /d "%~dp0"
call venv\Scripts\activate
python manage.py runserver 8003
pause
