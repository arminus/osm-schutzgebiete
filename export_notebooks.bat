@ECHO OFF
for /r %%f in (*.ipynb) do (
    jupyter nbconvert --to script %%f
    dos2unix "%%~nf.py"
    move "%%~nf.py" python-out
)