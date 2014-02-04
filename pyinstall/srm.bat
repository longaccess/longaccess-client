@echo off
rem call eraserl.exe with first argument
rem exit codes:
rem 0 if success
rem 1 if argument is missing
rem 2 if eraser was not found
rem 3 if argument doesn't exist
rem 4 if eraser failed
rem 5 if file still exists after eraser called
set file="%~s1"
if %file% == "" exit /b 1
if "%eraser%" == "" (
	set eraser=%~d0%~p0\..\Eraser\eraserl.exe
	set eraserargs=-silent -file
)
if not exist %eraser% exit /b 2
if not exist %file% exit /b 3
%eraser% %eraserargs% %file%
if errorlevel 1 exit /b 4
if exist %file% exit /b 5
exit
