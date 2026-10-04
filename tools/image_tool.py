import io
import os
from flask import request, render_template, send_file
from PIL import Image

def image_tool():
    if request.method == "GET":
        return render_template("image.html")
    file = request.files.get("file")
    if not file or not file.filename:
        return "Файл не выбран", 400
    try:
        image = Image.open(file)
        fmt = request.form.get("format", "original")
        quality = int(request.form.get("quality", 80))
        width = request.form.get("width")
        height = request.form.get("height")

        if width:
            width = int(width)
            if height:
                image.thumbnail((width, int(height)), Image.Resampling.LANCZOS)
            else:
                h = int(image.height * width / image.width)
                image = image.resize((width, h), Image.Resampling.LANCZOS)

        fmt = (image.format or "JPEG") if fmt == "original" else fmt.upper()

        if fmt in ("JPG", "JPEG"):
            if image.mode in ("RGBA", "LA", "P"):
                image = image.convert("RGBA")
                bg = Image.new("RGB", image.size, "white")
                bg.paste(image, mask=image.getchannel("A"))
                image = bg
            else:
                image = image.convert("RGB")
            ext, mime = "jpg", "image/jpeg"
        elif fmt == "PNG":
            ext, mime = "png", "image/png"
        elif fmt == "WEBP":
            ext, mime = "webp", "image/webp"
        elif fmt == "BMP":
            ext, mime = "bmp", "image/bmp"
        else:
            return "Неподдерживаемый формат", 400

        output = io.BytesIO()
        options = {}
        if fmt in ("JPG", "JPEG", "WEBP"):
            options = {"quality": quality, "optimize": True}
        image.save(output, format=fmt, **options)
        output.seek(0)

        name = os.path.splitext(file.filename)[0] + "_converted." + ext
        return send_file(output, as_attachment=True, download_name=name, mimetype=mime)
    except Exception as e:
        return f"Ошибка обработки изображения: {e}", 500
