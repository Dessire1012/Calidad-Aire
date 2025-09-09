@echo off
cd /d C:\Users\dessi\ProyectoClima

:: Activar el entorno virtual
call C:\Users\dessi\ProyectoClima\env\Scripts\activate

:: Ejecutar el nuevo script con el Python del entorno virtual
C:\Users\dessi\ProyectoClima\env\Scripts\python.exe C:\Users\dessi\ProyectoClima\clima_app\scripts\IQAir.py >> C:\Users\dessi\ProyectoClima\clima_app\scripts\logIQAIR.txt 2>&1
