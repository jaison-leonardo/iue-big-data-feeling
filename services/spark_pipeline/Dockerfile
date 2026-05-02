FROM python:3.11-slim-bookworm

# Instalar Java y procps (requerido por PySpark)
RUN apt-get update && \
    apt-get install -y default-jdk-headless procps && \
    rm -rf /var/lib/apt/lists/*

# Detectar JAVA_HOME automáticamente
RUN echo "JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))" >> /etc/environment
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Sobreescribir JAVA_HOME con el valor real al momento del build
RUN REAL_JAVA=$(dirname $(dirname $(readlink -f $(which java)))) && \
    echo "export JAVA_HOME=$REAL_JAVA" >> /etc/bash.bashrc && \
    ln -sfn $REAL_JAVA /usr/local/java

ENV JAVA_HOME=/usr/local/java
ENV PATH=/usr/local/java/bin:$PATH

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "jobs/predict_batch.py"]