# DokVex

Локальный веб-портал для работы с документами и изображениями на Python.

## Возможности

* 📄 Сжатие PDF
* 📝 Сжатие DOCX
* 📊 Сжатие XLSX
* 📽️ Сжатие PPTX
* 🖼️ Сжатие и конвертация изображений
* 🌙 Светлая и тёмная тема
* 📥 Автоматическое скачивание результата
* 🌐 Работа в локальной сети

## Технологии

* Python 3
* Flask
* Pillow
* ZIP / Open XML
* HTML / CSS / JavaScript

Проект не использует LibreOffice и другие офисные программы для обработки DOCX, XLSX и PPTX.

## Установка

```bash
git clone https://github.com/ChaosPrometheus/DokVex.git
cd DokVex
pip install -r requirements.txt
```

## Запуск

```bash
python app.py
```

По умолчанию:

```text
http://127.0.0.1
```

Для локальной сети:

```text
http://IP-АДРЕС-СЕРВЕРА
```

## Локальный адрес `dokvex.local`

Чтобы открывать портал по адресу:

```text
http://dokvex.local
```

на компьютере пользователя добавьте в файл:

```text
C:\Windows\System32\drivers\etc\hosts
```

строку:

```text
192.168.2.222    dokvex.local
```

`192.168.2.222` замените на IP компьютера, где запущен DokVex.

После этого:

```text
http://dokvex.local
```

## Структура

```text
DokVex/
│
├── app.py
├── requirements.txt
│
├── tools/
│   ├── pdf.py
│   ├── word.py
│   ├── excel.py
│   ├── pptx.py
│   └── image.py
│
├── templates/
│   ├── index.html
│   ├── pdf_compress.html
│   ├── word_compress.html
│   ├── excel_compress.html
│   ├── pptx_compress.html
│   └── image.html
│
├── uploads/
└── output/
```

## Статус

Проект находится в разработке.

## 🤝 Contributing

Предложения, исправления и новые функции приветствуются.

Если вы нашли ошибку или хотите предложить новый инструмент, создайте **Issue** или **Pull Request**.
