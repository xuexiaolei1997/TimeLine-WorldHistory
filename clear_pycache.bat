@echo off
echo 正在清除当前目录及其子目录下的 __pycache__ 文件夹...
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        echo 正在删除 "%%d"
        rd /s /q "%%d"
        if exist "%%d" (
            echo 删除 "%%d" 失败，可能文件被占用。
        )
    )
)
echo 清除完成。
pause