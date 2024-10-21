FROM python:3.11.5
MAINTAINER eblis
# 设置工作目录
WORKDIR /var/jenkins_home/workspace/ProFileSys

# 复制应用程序代码到容器中
COPY . /var/jenkins_home/workspace/ProFileSys

RUN pip cache purge
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ || echo "Error installing requirements"
RUN pip install uwsgi
RUN pip  install openai==0.28
RUN pip list
#RUN #chmod -R 777 start_uwsgi.sh
# 暴露应用程序监听的端口
#EXPOSE 9091 20901
ENV FLASK_PORT=9091
# 容器启动时的命令
#CMD ["python3", "app.py"]
CMD ["uwsgi", "--ini", "uwsgi.ini"]
#CMD ["./start_uwsgi.sh"]