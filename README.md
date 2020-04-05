
# Gladius #

Демонстрационная реализация рекомендательной системы, основанной на метаданных.  

## Описание рекомендательной системы

[Гугл док](https://docs.google.com/document/d/1ghBJUfZedJay11J3kvcns7jFPd59_lWbxCI1tOmwvYg/)

## Установка

Установка зависимостей
```bash
$ python3.8 -m pip install -r requirments.txt
```

Компиляция расширений на С
```bash
$ make
```

## Конфигурация

Настройка осуществляется через конфиругационный файл - `conf/private.py`  
Пример настройки:
```python

# web-server settings
# more at https://github.com/moff4/k2
aeon = {
    'host': 'localhost',
    'port': 8080,
}

# SQL settings
db = {  
    'provider': 'mysql',
    'host': 'localhost',
    'port': 3306,
    'user': 'admin',
    'passwd': 'admin',
    'db': 'hashtag',
}
``` 

## Запуск  

```bash
$ python3.8 main.py <cmd> [args [...]]
```
