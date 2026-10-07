# DocVex

Веб-инструменты для сжатия документов и просмотра изображений.

## Возможности

| Инструмент | Описание |
|------------|----------|
| **Сжатие PDF** | Уменьшение размера PDF (изображения + очистка) |
| **Сжатие Word** | Оптимизация DOCX и картинок внутри |
| **Сжатие PowerPoint** | Оптимизация PPTX и картинок |
| **Сжатие Excel** | Оптимизация XLSX и картинок |
| **Изображения** | Сжатие и конвертация (JPG, PNG, WEBP, BMP) |

После сжатия показывается размер **до / после** и процент экономии.

## Установка

```bash
pip install -r requirements.txt
python app.py
```

Откройте в браузере: [http://localhost:5000](http://localhost:5000)

В локальной сети (с телефона и т.п.): `http://IP-вашего-ПК:5000`

## Зависимости

- Python 3.10+
- Flask
- Pillow
- PyMuPDF (`fitz`) ≥ 1.24
- Werkzeug

```text
flask>=3.0.0
Pillow>=10.0.0
PyMuPDF>=1.24.0
Werkzeug>=3.0.0
```

## Галерея

### С ПК
На странице **Галерея** → вкладка «С ПК» → выбрать папку или файлы.  
Фото **не загружаются** на сервер — отображаются только в браузере.

### С сервера
По умолчанию папка:

- Windows: `C:\Users\<Имя>\DocVexGallery`
- Linux / macOS: `~/DocVexGallery`

Положите туда JPG/PNG/WEBP и нажмите **Обновить**.

Своя папка:

```bash
# Windows (PowerShell)
$env:DOCVEX_GALLERY_DIR = "D:\Photos"
python app.py

# Linux / macOS
export DOCVEX_GALLERY_DIR=/home/user/Photos
python app.py
```

Или в `app.py`:

```python
app.config["GALLERY_DIR"] = r"D:\Photos"
```

## Ограничения

- Максимальный размер загружаемого файла: **50 МБ**
- Поддерживаются форматы: PDF, DOCX, PPTX, XLSX и распространённые изображения

## Структура проекта

```text
docvex/
├── app.py                 # Точка входа Flask
├── requirements.txt
├── README.md
├── templates/             # HTML-шаблоны
│   ├── base.html
│   ├── index.html
│   └── ...
└── tools/                 # Логика инструментов
    ├── common.py          # Общие функции (валидация, сжатие Office)
    ├── pdf_tool.py
    ├── word_tool.py
    ├── pptx_tool.py
    ├── excel_tool.py 
    └── image_tool.py
```

## Примечания

- Для продакшена лучше запускать через gunicorn / waitress, а не `python app.py`
- Имена файлов с кириллицей поддерживаются
- Временные файлы после скачивания результата удаляются
- 
## 🤝 Contributing

Предложения, исправления и новые функции приветствуются.

Если вы нашли ошибку или хотите предложить новый инструмент, создайте **Issue** или **Pull Request**.
