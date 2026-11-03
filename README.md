# Perm Transport для Home Assistant

Сенсор с актуальным расписанием автобусов с https://www.map.gortransperm.ru/

## Возможности
- Один сенсор = одна остановка.
- Состояние — минуты до ближайшего автобуса из выбранных маршрутов.
- В атрибутах — полное расписание по каждому выбранному маршруту.
- Настраиваемый интервал опроса.

## Установка через HACS
1. HACS → Custom repositories → добавьте URL этого репозитория, категория `Integration`.
2. Установите, перезагрузите Home Assistant.
3. Настройки → Устройства и службы → Добавить интеграцию → `Perm Transport`.
4. Введите название, ID остановки (из URL на карте), маршруты и интервал.

## Пример автоматизации
```yaml
automation:
  - alias: "Выйти, если автобус 40 через 5 минут"
    trigger:
      - platform: numeric_state
        entity_id: sensor.ostanovka_106200
        below: 6
    action:
      - service: notify.notify
        data:
          message: "Автобус 40 уже близко!"