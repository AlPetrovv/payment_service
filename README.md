# Payment Service

Асинхронный сервис процессинга платежей на FastAPI + RabbitMQ + PostgreSQL.

## Запуск

```bash
make build && make run
```

API: http://localhost:8000  
RabbitMQ Management: http://localhost:15672


## Архитектура

Три процесса (контейнера), общающихся через PostgreSQL и RabbitMQ

### Pipeline (краткая схема)
1. Создание заказа через API 
   1. Проверка Idempotency-Key
   2. Создание payment и outbox
2. Outbox relay для created payments через сервис relay(можно сделать в одном сервисе -> api или отдельным сервисом сос своей кодовой базой)  
   1. Поиск в БД unpublished payments и отправка их через брокер по очередям через "gateway"(maps) в зависимости от статуса
3. status = created
   1. Сделать random process и обновить статус payment 
   2. Если ошибка -> retry -> DLQ
4. Outbox relay для success payments
   1. Отправка в webhooks.send для оповещения
5. Webhook logic 
   1. Отправка webhook с retry, если больше retry_max_attempts -> DLQ


### Retry и DLQ
```
payments.new  --(ошибка, attempt < N)-->  payments.retry
payments.retry --(TTL истёк)-->           payments.new
payments.new  --(attempt >= N)-->         payments.dead
```
Аналогично с webhook

## Плюсы
1. Отказоустойчивость, при отключении relay -> api будет получать новые payments, consumer будет ждать новые сообщения и обрабатывать текущие
2. Идемпотентность создания
3. Outbox pattern обеспечивает  атомарность а и независимость с api
## Минусы
1. Одна кодовая база - Можно сделать core сервис для платежей и отдельные сервисы для relay, consumer


## Переменные окружения

| Переменная | Описание | По умолчанию |
|---|---|---|
| `APP__DB__URL` | PostgreSQL URL | — |
| `APP__RABBITMQ__URL` | RabbitMQ URL | `amqp://guest:guest@rabbitmq:5672/` |
| `APP__API_KEY` | Статический API ключ | `secret` |
| `APP__LOG_LEVEL` | Уровень логирования | `INFO` |
| `APP__OUTBOX_POLL_INTERVAL` | Интервал опроса outbox (сек) | `1.0` |
| `APP__RETRY_MAX_ATTEMPTS` | Кол-во попыток до DLQ | `3` |
| `APP__RETRY_BASE_DELAY` | Базовая задержка backoff (сек) | `2.0` |
