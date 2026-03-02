@echo off
cd /d "%~dp0.."
auto-py-to-exe --config "%~dp0wavefilter-autopytoexe.json"
