##################
# 最小限の開発環境
##################


FROM python:3.12
USER root
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt

CMD ["bash"]