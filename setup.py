from setuptools import setup,find_packages
import chardet
from irails import __version__
version = __version__
def update_readme(source,spec,content=""):
    assert source or content

    if not content:
        with open(source, 'r') as file:
            content = file.read()
    with open('README.md', 'r') as file:
        lines = file.readlines() 
    start = None
    end = None 
    for i, line in enumerate(lines):
        if spec in line:
            start = i
        elif start  and '```' in line:
            end = i
            break 
    if start is None or end is None:
        raise ValueError('Failed to find Python code block in readme')

    code_lines = content.split('\n')   
    code_block = spec + '\n' + '\n'.join(code_lines) + '\n```\n'
    lines = lines[:start] + [code_block] + lines[end+1:]

    with open('readme.md', 'w') as file:
        file.writelines(lines)

update_readme('apps/app/controllers/test_controller.py','```python')
update_readme('apps/app/views/test/home.html','```html')
# import subprocess
# result = subprocess.run(['cmd','/c','tree','./app'], capture_output=True)
# gbk_to_utf8 = result.stdout.decode("gbk").encode("utf-8")
# gbk_to_utf8=gbk_to_utf8.replace(b'\r',b'\n')
# if gbk_to_utf8: 
#     gbk_to_utf8 = gbk_to_utf8.decode("utf-8")
#     gbk_to_utf8 = gbk_to_utf8.split("\n")[3:]
#     gbk_to_utf8 = '\n'.join(gbk_to_utf8)
# update_readme('','```dir',gbk_to_utf8)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open('requirements.txt', encoding="utf-8-sig") as f:
    requirements = f.readlines()


setup(
    name='irails',
    version=version,
    license='Apache License 2.0',
    author='Bruce chou',
    author_email='smjkzsl@gmail.com',
    description='Simple and elegant use of FastApi in MVC mode',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    url='https://github.com/smjkzsl/irails',
    packages=['irails','irails.scripts',],
    
    include_package_data=True,
 
    entry_points={  # 指定脚本文件和其安装路径
        'console_scripts': [
            'irails=irails.scripts.main:main',
        ],
    },
    scripts=['irails/scripts/main.py'],  # 指定要打包进可执行文件中的脚本文件路径列表

    keywords=[
        'web framework', 'mvc framework', 'fastapi framework',
    ],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9', 
        'Programming Language :: Python :: 3.10', 
        'Programming Language :: Python :: 3.11', 
    ],
    python_requires='>=3.6',
)
