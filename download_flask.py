"""下载 Flask 源码用于演示"""
import requests, zipfile, io, os, shutil

print("下载 Flask 3.1.0 源码...")
r = requests.get("https://github.com/pallets/flask/archive/refs/tags/3.1.0.zip")
z = zipfile.ZipFile(io.BytesIO(r.content))

target = os.path.join("examples", "flask_src")
if os.path.exists(target):
    shutil.rmtree(target)

z.extractall("examples")
extracted = os.path.join("examples", "flask-3.1.0", "src", "flask")
src_target = os.path.join("examples", "flask_src")

if os.path.exists(extracted):
    shutil.copytree(extracted, src_target)
    shutil.rmtree(os.path.join("examples", "flask-3.1.0"))
    print(f"✅ Flask 源码已解压到 {src_target}")
    py_files = [f for f in os.listdir(src_target) if f.endswith(".py")]
    total_lines = 0
    for f in py_files:
        with open(os.path.join(src_target, f), "r", encoding="utf-8", errors="ignore") as fh:
            total_lines += len(fh.readlines())
    print(f"   Python 文件: {len(py_files)} 个, 总行数: {total_lines}")
    print(f"   文件列表: {', '.join(py_files)}")
else:
    print(f"❌ 解压路径错误: {extracted}")
