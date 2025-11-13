FROM python:3.11-slim

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple -r requirements.txt 

# 复制源代码
COPY . .

# 创建data目录
RUN mkdir -p data

# 运行主程序
CMD ["python", "main.py"]