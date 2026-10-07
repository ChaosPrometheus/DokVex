import io
import os
import zipfile
import tempfile
from werkzeug.utils import secure_filename
from PIL import Image
from flask import current_app


ALLOWED_EXTENSIONS = {
    "pdf": {"pdf"},
    "word": {"docx"},
    "pptx": {"pptx"},
    "excel": {"xlsx"},
    "image": {"jpg", "jpeg", "png", "webp", "bmp", "tiff", "tif"},
}


def get_max_file_size():
    """Максимальный размер файла в байтах (по умолчанию 50 МБ)."""
    return current_app.config.get("MAX_CONTENT_LENGTH", 50 * 1024 * 1024)


def validate_file(file, allowed_exts):
    """Проверяет наличие файла, расширение и размер.
    Расширение берём из оригинального имени (чтобы не ломаться на кириллице),
    а для безопасного имени файла используем secure_filename + сохраняем расширение.
    """
    if not file or not file.filename:
        return None, "Файл не выбран"

    original = file.filename

    # Расширение — только из оригинального имени
    if "." not in original:
        return None, f"Поддерживаются только: {', '.join(sorted(allowed_exts))}"

    ext = original.rsplit(".", 1)[-1].lower()
    if ext not in allowed_exts:
        return None, f"Поддерживаются только: {', '.join(sorted(allowed_exts))}"

    # Безопасное имя: secure_filename может вырезать всю кириллицу,
    # поэтому если имя стало пустым — подставляем "file"
    base = original.rsplit(".", 1)[0]
    safe_base = secure_filename(base) or "file"
    filename = f"{safe_base}.{ext}"

    # Читаем содержимое один раз
    data = file.read()
    if len(data) == 0:
        return None, "Файл пустой"

    max_size = get_max_file_size()
    if len(data) > max_size:
        mb = max_size // (1024 * 1024)
        return None, f"Файл слишком большой (максимум {mb} МБ)"

    return data, filename


def format_size(size_bytes):
    """Человекочитаемый размер."""
    if size_bytes < 1024:
        return f"{size_bytes} Б"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} КБ"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} МБ"


def compress_image_data(data, quality=65, max_width=1920):
    """
    Сжимает изображение (bytes) с помощью Pillow.
    Возвращает новые bytes или исходные, если сжатие не дало выигрыша.
    """
    try:
        image = Image.open(io.BytesIO(data))
        original_size = len(data)

        # Ресайз по ширине
        if image.width > max_width:
            h = int(image.height * max_width / image.width)
            image = image.resize((max_width, h), Image.Resampling.LANCZOS)

        temp = io.BytesIO()
        fmt = (image.format or "").upper()

        if fmt in ("JPEG", "JPG"):
            image.convert("RGB").save(temp, "JPEG", quality=quality, optimize=True)
        elif fmt == "PNG":
            if "A" in image.getbands():
                # Сохраняем прозрачность
                image.save(temp, "PNG", optimize=True)
            else:
                # Без альфы — конвертируем в JPEG (обычно сильно меньше)
                image.convert("RGB").save(temp, "JPEG", quality=quality, optimize=True)
        else:
            # Другие форматы пробуем как JPEG
            image.convert("RGB").save(temp, "JPEG", quality=quality, optimize=True)

        new_data = temp.getvalue()
        if new_data and len(new_data) < original_size:
            return new_data
    except Exception:
        pass
    return data


def compress_office_document(file_data, media_prefix, quality=65, max_width=1920):
    """
    Общая функция сжатия Office-документов (docx / pptx / xlsx).
    media_prefix — например "word/media/", "ppt/media/", "xl/media/"
    Возвращает (compressed_bytes, original_size, compressed_size)
    """
    original_size = len(file_data)
    source = zipfile.ZipFile(io.BytesIO(file_data), "r")
    output = io.BytesIO()

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as result:
        for item in source.infolist():
            data = source.read(item.filename)
            if item.filename.startswith(media_prefix):
                data = compress_image_data(data, quality=quality, max_width=max_width)
            result.writestr(item, data)

    source.close()
    compressed = output.getvalue()
    return compressed, original_size, len(compressed)


def save_temp_file(data, suffix):
    """Сохраняет данные во временный файл и возвращает путь."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
    except Exception:
        os.close(fd)
        raise
    return path
