@echo off
cd /d C:\Users\dessi\ProyectoClima

:: Activar el entorno virtual
call C:\Users\dessi\ProyectoClima\env\Scripts\activate

:: Ejecutar el nuevo script con el Python del entorno virtual
C:\Users\dessi\ProyectoClima\env\Scripts\python.exe C:\Users\dessi\ProyectoClima\clima_app\scripts\iqAir.py >> C:\Users\dessi\ProyectoClima\clima_app\scripts\logIQAir.txt 2>&1
