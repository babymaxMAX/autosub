# 🚀 Руководство по развертыванию AutoSub

Полное руководство по развертыванию на различных платформах.

## Содержание

1. [VPS (Ubuntu/Debian)](#vps-ubuntudebian)
2. [AWS EC2](#aws-ec2)
3. [DigitalOcean](#digitalocean)
4. [Google Cloud Platform](#google-cloud-platform)
5. [Heroku (без Docker)](#heroku)
6. [Kubernetes](#kubernetes)
7. [Docker Swarm](#docker-swarm)

---

## VPS (Ubuntu/Debian)

### Требования
- Ubuntu 20.04+ или Debian 11+
- Минимум 2GB RAM
- 10GB свободного места
- Доступ по SSH

### Шаг 1: Подключение к серверу

```bash
ssh root@your-server-ip
```

### Шаг 2: Установка Docker

```bash
# Обновление системы
apt update && apt upgrade -y

# Установка зависимостей
apt install -y apt-transport-https ca-certificates curl software-properties-common

# Добавление Docker репозитория
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Установка Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io

# Установка Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Проверка
docker --version
docker-compose --version
```

### Шаг 3: Клонирование проекта

```bash
# Установка Git
apt install -y git

# Клонирование
cd /opt
git clone <your-repository-url> autosub
cd autosub
```

### Шаг 4: Настройка

```bash
# Создание .env
cp .env.example .env
nano .env

# Измените:
# - BOT_TOKEN
# - ADMIN_IDS
# - DB_PASSWORD
# - PLATEGA_* (если используете)
```

### Шаг 5: Запуск

```bash
# Запуск
docker-compose up -d

# Проверка
docker-compose ps
docker-compose logs -f bot
```

### Шаг 6: Настройка автозапуска

```bash
# Создание systemd service
cat > /etc/systemd/system/autosub.service << 'EOF'
[Unit]
Description=AutoSub Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/autosub
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Активация
systemctl daemon-reload
systemctl enable autosub
systemctl start autosub
```

---

## AWS EC2

### Шаг 1: Создание EC2 инстанса

1. Войдите в AWS Console
2. EC2 -> Launch Instance
3. Выберите:
   - **AMI:** Ubuntu Server 22.04 LTS
   - **Instance Type:** t3.medium (или больше)
   - **Storage:** 20GB gp3
   - **Security Group:**
     - SSH (22) - Your IP
     - HTTP (80) - Anywhere
     - HTTPS (443) - Anywhere
     - Custom (8000) - Anywhere (для webhook)

4. Скачайте .pem ключ

### Шаг 2: Подключение

```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@ec2-xx-xx-xx-xx.compute.amazonaws.com
```

### Шаг 3: Установка и настройка

Следуйте шагам из раздела [VPS](#vps-ubuntudebian)

### Шаг 4: Настройка Elastic IP (опционально)

1. EC2 -> Elastic IPs -> Allocate
2. Actions -> Associate -> Выберите ваш инстанс

---

## DigitalOcean

### Шаг 1: Создание Droplet

1. Войдите в DigitalOcean
2. Create -> Droplets
3. Выберите:
   - **Image:** Ubuntu 22.04
   - **Plan:** Basic ($12/mo - 2GB RAM)
   - **Region:** Ближайший к вам
   - **Authentication:** SSH Key

### Шаг 2: Подключение

```bash
ssh root@your-droplet-ip
```

### Шаг 3: Установка Docker (быстрый способ)

```bash
# Используйте готовый скрипт DigitalOcean
apt update
snap install docker
```

Далее следуйте шагам из раздела [VPS](#vps-ubuntudebian)

### Шаг 4: Настройка домена (опционально)

1. Networking -> Domains -> Add Domain
2. Добавьте A-запись:
   - **Hostname:** @ или subdomain
   - **Will Direct To:** Your Droplet

---

## Google Cloud Platform

### Шаг 1: Создание VM Instance

1. Compute Engine -> VM Instances -> Create
2. Настройки:
   - **Machine type:** e2-medium (2 vCPU, 4GB RAM)
   - **Boot disk:** Ubuntu 22.04 LTS, 20GB
   - **Firewall:** Allow HTTP/HTTPS traffic

### Шаг 2: Настройка Firewall

```bash
# В GCP Console:
VPC Network -> Firewall -> Create Rule
- Name: allow-webhook
- Targets: All instances
- Source: 0.0.0.0/0
- Ports: tcp:8000
```

### Шаг 3: SSH подключение

```bash
# Через браузер: SSH button в консоли
# Или через gcloud CLI:
gcloud compute ssh your-instance-name
```

Далее следуйте шагам из раздела [VPS](#vps-ubuntudebian)

---

## Heroku

> ⚠️ Heroku не поддерживает Docker Compose напрямую. Требуется адаптация.

### Вариант 1: Heroku Container Registry

```bash
# Установка Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Логин
heroku login
heroku container:login

# Создание приложения
heroku create autosub-bot

# Деплой bot
heroku container:push bot -a autosub-bot
heroku container:release bot -a autosub-bot

# Деплой worker
heroku container:push worker -a autosub-bot
heroku container:release worker -a autosub-bot
```

### Вариант 2: Использовать VPS

Рекомендуется использовать VPS вместо Heroku для этого проекта.

---

## Kubernetes

### Предварительные требования

- Kubernetes кластер (minikube, GKE, EKS, AKS)
- kubectl установлен

### Шаг 1: Создание манифестов

Создайте `k8s/` директорию:

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: autosub
---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: autosub-config
  namespace: autosub
data:
  DB_HOST: postgres-service
  REDIS_HOST: redis-service
  # ... другие настройки
---
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: autosub-secrets
  namespace: autosub
type: Opaque
stringData:
  BOT_TOKEN: "your-token"
  DB_PASSWORD: "your-password"
  PLATEGA_API_KEY: "your-key"
---
# k8s/postgres.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: autosub
spec:
  serviceName: postgres-service
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: autosub-secrets
              key: DB_PASSWORD
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
---
# k8s/redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: autosub
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
---
# k8s/bot.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bot
  namespace: autosub
spec:
  replicas: 1
  selector:
    matchLabels:
      app: bot
  template:
    metadata:
      labels:
        app: bot
    spec:
      containers:
      - name: bot
        image: your-registry/autosub-bot:latest
        envFrom:
        - configMapRef:
            name: autosub-config
        - secretRef:
            name: autosub-secrets
---
# k8s/worker.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker
  namespace: autosub
spec:
  replicas: 3
  selector:
    matchLabels:
      app: worker
  template:
    metadata:
      labels:
        app: worker
    spec:
      containers:
      - name: worker
        image: your-registry/autosub-worker:latest
        resources:
          limits:
            memory: "4Gi"
            cpu: "2"
        envFrom:
        - configMapRef:
            name: autosub-config
        - secretRef:
            name: autosub-secrets
---
# k8s/webhook.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webhook
  namespace: autosub
spec:
  replicas: 2
  selector:
    matchLabels:
      app: webhook
  template:
    metadata:
      labels:
        app: webhook
    spec:
      containers:
      - name: webhook
        image: your-registry/autosub-webhook:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: autosub-config
        - secretRef:
            name: autosub-secrets
---
apiVersion: v1
kind: Service
metadata:
  name: webhook-service
  namespace: autosub
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: webhook
```

### Шаг 2: Применение

```bash
# Создание namespace
kubectl apply -f k8s/namespace.yaml

# Применение всех манифестов
kubectl apply -f k8s/

# Проверка
kubectl get pods -n autosub
kubectl logs -f deployment/bot -n autosub
```

---

## Docker Swarm

### Шаг 1: Инициализация Swarm

```bash
docker swarm init
```

### Шаг 2: Создание docker-compose.swarm.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - autosub_network
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure

  redis:
    image: redis:7-alpine
    networks:
      - autosub_network
    deploy:
      replicas: 1

  bot:
    image: your-registry/autosub-bot:latest
    env_file:
      - .env
    networks:
      - autosub_network
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure

  worker:
    image: your-registry/autosub-worker:latest
    env_file:
      - .env
    networks:
      - autosub_network
    deploy:
      replicas: 5
      resources:
        limits:
          cpus: '2'
          memory: 4G
      restart_policy:
        condition: on-failure

  webhook:
    image: your-registry/autosub-webhook:latest
    env_file:
      - .env
    ports:
      - "8000:8000"
    networks:
      - autosub_network
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

volumes:
  postgres_data:

networks:
  autosub_network:
    driver: overlay
```

### Шаг 3: Деплой

```bash
docker stack deploy -c docker-compose.swarm.yml autosub

# Проверка
docker service ls
docker service logs autosub_bot
```

---

## SSL/HTTPS настройка

### Certbot с Nginx

```bash
# Установка Nginx
apt install -y nginx

# Конфигурация
cat > /etc/nginx/sites-available/autosub << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location /webhook/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Активация
ln -s /etc/nginx/sites-available/autosub /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Установка Certbot
apt install -y certbot python3-certbot-nginx

# Получение сертификата
certbot --nginx -d your-domain.com

# Автообновление
crontab -e
# Добавьте:
0 0 1 * * certbot renew --quiet
```

---

## Мониторинг

### Prometheus + Grafana

```yaml
# Добавьте в docker-compose.yml:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## Резервное копирование

### Автоматический бэкап

```bash
# Создайте скрипт
cat > /opt/autosub/backup.sh << 'EOF'
#!/bin/bash
cd /opt/autosub
./scripts/backup_db.sh
# Загрузка в S3/другое хранилище
aws s3 cp backups/ s3://your-bucket/backups/ --recursive
EOF

chmod +x /opt/autosub/backup.sh

# Добавьте в cron
crontab -e
0 2 * * * /opt/autosub/backup.sh
```

---

## Troubleshooting

### Проверка логов

```bash
# Docker Compose
docker-compose logs -f --tail=100

# Kubernetes
kubectl logs -f deployment/bot -n autosub

# Docker Swarm
docker service logs -f autosub_bot
```

### Проверка подключений

```bash
# PostgreSQL
docker-compose exec postgres psql -U autosub -c "SELECT 1;"

# Redis
docker-compose exec redis redis-cli ping
```

---

**Вопросы?** Создайте [issue](https://github.com/your-repo/issues)

