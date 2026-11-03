# Perm Transport для Home Assistant

> Сенсор с актуальным расписанием автобусов с сайта [map.gortransperm.ru](https://www.map.gortransperm.ru/)

Интеграция опрашивает внутренний API карты ГорТранса Перми и превращает ответ в удобный сенсор Home Assistant. Одна остановка — один сенсор. Внутри сенсора — только те маршруты, которые вы указали при настройке.

---

## ✨ Возможности

- 🚌 **Один сенсор = одна остановка** — удобно раскладывать по панелям.
- 🎯 **Фильтр по маршрутам** — показываются только нужные вам автобусы.
- 🕒 **Читаемый формат** — время прибытия вида `18:46 18:54 19:11` прямо в атрибуте.
- 📊 **Числовые данные для автоматизаций** — массив минут до прибытия.
- ⚙️ **Настраиваемый интервал** — от 15 секунд до 1 часа.
- 🔄 **Обновление без переустановки** — через Options Flow.
- 🧩 **Полностью UI-настройка** — YAML не требуется.

---

## 📦 Установка

### Через HACS (рекомендуется)

1. Откройте **HACS → Интеграции**.
2. Нажмите **⋮ (три точки) → Пользовательские репозитории**.
3. Введите URL репозитория:
   ```
   https://github.com/YOUR_USERNAME/perm_transport
   ```
4. Категория — **Integration**. Нажмите **Добавить**.
5. Найдите **Perm Transport** в списке и установите.
6. Перезагрузите Home Assistant.

### Вручную

1. Скачайте последний релиз.
2. Скопируйте папку `custom_components/perm_transport/` в `config/custom_components/` вашего Home Assistant.
3. Перезагрузите Home Assistant.

---

## ⚙️ Настройка

1. Перейдите в **Настройки → Устройства и службы → Добавить интеграцию**.
2. Найдите **Perm Transport**.
3. Заполните поля:

| Поле | Описание | Пример |
|---|---|---|
| **Название сенсора** | Как будет называться сущность (для удобства) | `Остановка Мира` |
| **ID остановки** | Число из URL карты ГорТранса | `106200` |
| **Маршруты через запятую** | Какие автобусы отслеживать | `40, 27` |
| **Интервал обновления, сек** | От 15 до 3600 | `60` |

### Как узнать ID остановки

1. Откройте [map.gortransperm.ru](https://www.map.gortransperm.ru/).
2. Кликните по нужной остановке на карте.
3. Откройте панель разработчика браузера (**F12 → Network**).
4. Найдите запрос вида `arrival-times-vehicles/106200` — число после последнего `/` и есть ID остановки.

### Изменение настроек

**Настройки → Устройства и службы → Perm Transport → ⋮ → Настроить** — можно изменить название, список маршрутов и интервал без удаления интеграции.

---

## 🧠 Описание сенсора

Для каждой настроенной остановки создаётся сущность `sensor.<название>`, например `sensor.ostanovka_106200`.

### Состояние (state)

**Минуты до ближайшего автобуса** среди всех выбранных маршрутов. Тип — число (или `unknown`, если автобусов нет в поле зрения).

### Атрибуты

| Атрибут | Тип | Пример | Назначение |
|---|---|---|---|
| `stop_id` | строка | `"106200"` | ID остановки |
| `stop_name` | строка | `"Остановка Мира"` | Название сенсора |
| `tracked_routes` | список | `["40", "27"]` | Отслеживаемые маршруты |
| `routes` | словарь | `{"40": "18:46 18:54 19:11"}` | Читаемое время прибытия |
| `routes_minutes` | словарь | `{"40": [1, 10, 27]}` | Минуты до прибытия |
| `last_update` | число | `1730642187.12` | Unix-timestamp обновления |

### Пример состояния в Инструментах разработчика

```yaml
sensor.ostanovka_106200:
  state: 1
  attributes:
    stop_id: "106200"
    stop_name: "Остановка Мира"
    tracked_routes: ["40", "27"]
    routes:
      "40": "18:46 18:54 19:11"
      "27": "18:54 18:59 19:06"
    routes_minutes:
      "40": [1, 10, 27]
      "27": [10, 15, 22]
    last_update: 1730642187.123
```

---

## 🖼️ Примеры карточек Lovelace

### 1. Простая Markdown-карточка

Подходит, если нужно просто видеть ближайшие автобусы.

```yaml
type: markdown
title: 🚌 Остановка Мира
content: |
  {% set r = state_attr('sensor.ostanovka_106200', 'routes') %}
  {% for route, times in r.items() %}
  **№{{ route }}**: {{ times if times else '— нет данных —' }}
  {% endfor %}
```

Результат:

> 🚌 **№40**: 18:46 18:54 19:11
> 🚌 **№27**: 18:54 18:59 19:06

---

### 2. Markdown с обратным отсчётом

Показывает время и через сколько минут придёт ближайший.

```yaml
type: markdown
title: 🚌 Остановка Мира
content: |
  {% set r = state_attr('sensor.ostanovka_106200', 'routes') %}
  {% set m = state_attr('sensor.ostanovka_106200', 'routes_minutes') %}
  {% for route, times in r.items() %}
  **№{{ route }}**: {{ times if times else '— нет данных —' }}
  {%- if m[route] %} ⏱ через {{ m[route][0] }} мин{% endif %}
  {% endfor %}
```

Результат:

> 🚌 **№40**: 18:46 18:54 19:11 ⏱ через 1 мин
> 🚌 **№27**: 18:54 18:59 19:06 ⏱ через 10 мин

---

### 3. Карточка-шаблон (entities-card)

Показывает один маршрут на строке.

```yaml
type: entities
title: 🚌 Остановка Мира
entities:
  - type: attribute
    entity: sensor.ostanovka_106200
    attribute: routes
    name: Все маршруты
  - type: attribute
    entity: sensor.ostanovka_106200
    attribute: routes_minutes
    name: Минуты
```

---

### 4. Таблица через `flex-table-card`

Установите через HACS карточку [`flex-table-card`](https://github.com/custom-cards/flex-table-card) — она умеет рендерить словари в таблицу.

```yaml
type: custom:flex-table-card
title: 🚌 Остановка Мира
entities:
  - sensor.ostanovka_106200
columns:
  - name: Маршрут
    data: routes
    modify: Object.keys(x).join(', ')
  - name: Прибытие
    data: routes
    modify: Object.values(x).join(' | ')
  - name: Минут
    data: routes_minutes
    modify: Object.values(x).map(a => a[0]).join(' | ')
```

---

### 5. Карточка для нескольких остановок

Если у вас несколько сенсоров, объедините их в одну карточку:

```yaml
type: markdown
title: 🚌 Ближайший транспорт
content: |
  {% for e in [
    'sensor.ostanovka_106200',
    'sensor.ostanovka_102203'
  ] %}
  {%- set name = state_attr(e, 'stop_name') %}
  {%- set r = state_attr(e, 'routes') %}
  {%- set m = state_attr(e, 'routes_minutes') %}
  ### {{ name }}
  {% for route, times in r.items() %}
  **№{{ route }}**: {{ times if times else '—' }}
  {%- if m[route] %} ({{ m[route][0] }} мин){% endif %}
  {% endfor %}
  {%- endfor %}
```

---

## 🤖 Примеры автоматизаций

### 1. Уведомление, когда любой автобус ближе 5 минут

```yaml
automation:
  - alias: "Автобус близко"
    trigger:
      - platform: numeric_state
        entity_id: sensor.ostanovka_106200
        below: 6
    action:
      - service: notify.notify
        data:
          title: "🚌 Пора выходить"
          message: >-
            Ближайший автобус через
            {{ states('sensor.ostanovka_106200') }} мин.
            Маршруты: {{ state_attr('sensor.ostanovka_106200', 'routes') }}
```

### 2. Триггер на конкретный маршрут (№40) ближе 5 минут

```yaml
automation:
  - alias: "Автобус 40 близко"
    trigger:
      - platform: template
        value_template: >-
          {{ (state_attr('sensor.ostanovka_106200', 'routes_minutes')['40'] or [999])[0] <= 5 }}
    action:
      - service: notify.notify
        data:
          message: >-
            Автобус 40 будет через
            {{ state_attr('sensor.ostanovka_106200', 'routes_minutes')['40'][0] }} мин.
            Прибытие: {{ state_attr('sensor.ostanovka_106200', 'routes')['40'].split(' ')[0] }}
```

### 3. Утреннее оповещение в 07:30 со всеми ближайшими

```yaml
automation:
  - alias: "Утреннее расписание"
    trigger:
      - platform: time
        at: "07:30:00"
    action:
      - service: notify.notify
        data:
          title: "Расписание на утро"
          message: >-
            {% set r = state_attr('sensor.ostanovka_106200', 'routes') %}
            {% for route, times in r.items() %}
            №{{ route }}: {{ times }}{{ '\n' }}
            {%- endfor %}
```

### 4. Отправка в Telegram-канал

```yaml
action:
  - service: telegram_bot.send_message
    data:
      message: |
        🚌 Остановка Мира
        {% set r = state_attr('sensor.ostanovka_106200', 'routes') %}
        {% for route, times in r.items() %}
        **№{{ route }}**: {{ times }}
        {%- endfor %}
      parse_mode: markdown
```

### 5. Условие «не выходить, если следующего нет»

```yaml
condition:
  - condition: template
    value_template: >-
      {{ state_attr('sensor.ostanovka_106200', 'routes_minutes')['40'] | length > 0 }}
```

---

## 🔧 Troubleshooting

### «cannot_connect» при настройке

1. Проверьте, что ID остановки — число и существует на карте.
2. Откройте в браузере:
   ```
   https://www.map.gortransperm.ru/json/arrival-times-vehicles/106200
   ```
   Если возвращает JSON — ID рабочий, проблема в сети Home Assistant.
3. Проверьте доступ Home Assistant к внешним сайтам.

### Сенсор показывает `unknown`

Это нормально — значит, ни одного автобуса из выбранных маршрутов сейчас нет в поле зрения системы. Атрибуты при этом остаются валидными (пустые строки/списки).

### Маршрут настроен, но не появляется в атрибутах

Проверьте написание — номера должны точно совпадать с теми, что отдаёт сайт. Например, `40` и `040` — это разные значения. Уточните номер в ответе API:
```
https://www.map.gortransperm.ru/json/arrival-times-vehicles/106200
```

### Интеграция не обновляется

1. Настройки → Устройства и службы → Perm Transport → ⋮ → **Перезагрузить**.
2. Проверьте `scan_interval` — не стоит ли слишком большое значение.
3. Посмотрите логи Home Assistant: **Настройки → Система → Логи** — ищите `perm_transport`.

### Ошибка «Уже настроено»

Эта остановка уже добавлена. Используйте **⋮ → Настроить** для редактирования или удалите старую запись.

---

## 🛠️ Разработка

### Структура проекта

```
perm_transport/
├── custom_components/perm_transport/
│   ├── __init__.py
│   ├── manifest.json
│   ├── const.py
│   ├── coordinator.py
│   ├── config_flow.py
│   ├── sensor.py
│   ├── strings.json
│   ├── brand/
│   │   ├── icon.png
│   │   ├── icon@2x.png
│   │   ├── logo.png
│   │   └── logo@2x.png
│   └── translations/
│       ├── en.json
│       └── ru.json
├── hacs.json
└── README.md
```

### Используемые технологии

- `DataUpdateCoordinator` — стандартный паттерн HA для опроса API.
- `ConfigFlow` + `OptionsFlow` — полная UI-настройка.
- `aiohttp` — асинхронные запросы к API.
- `CoordinatorEntity` — интеграция сенсора с координатором.

### Зависимости

- Home Assistant `2024.11.0` или новее.

---
