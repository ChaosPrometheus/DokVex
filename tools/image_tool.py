import io
import os
from flask import request, render_template
from PIL import Image
from tools.common import validate_file, format_size, save_temp_file, ALLOWED_EXTENSIONS


def image_tool():
    if request.method == "GET":
        return render_template("image.html")

    file = request.files.get("file")
    data, filename_or_error = validate_file(file, ALLOWED_EXTENSIONS["image"])
    if data is None:
        return render_template("image.html", error=filename_or_error), 400

    try:
        image = Image.open(io.BytesIO(data))
        fmt = request.form.get("format", "original")
        quality = int(request.form.get("quality", 80))
        width = request.form.get("width")

        if width:
            width = int(width)
            h = int(image.height * width / image.width)
            image = image.resize((width, h), Image.Resampling.LANCZOS)

        fmt = (image.format or "JPEG") if fmt == "original" else fmt.upper()

        if fmt in ("JPG", "JPEG"):
            if image.mode in ("RGBA", "LA", "P"):
                image = image.convert("RGBA")
                bg = Image.new("RGB", image.size, "white")
                mask = image.getchannel("A") if "A" in image.getbands() else None
                bg.paste(image, mask=mask)
                image = bg
            else:
                image = image.convert("RGB")
            ext, mime = "jpg", "image/jpeg"
            save_fmt = "JPEG"
        elif fmt == "PNG":
            ext, mime = "png", "image/png"
            save_fmt = "PNG"
        elif fmt == "WEBP":
            ext, mime = "webp", "image/webp"
            save_fmt = "WEBP"
        elif fmt == "BMP":
            ext, mime = "bmp", "image/bmp"
            save_fmt = "BMP"
        else:
            return render_template("image.html", error="Неподдерживаемый формат"), 400

        output = io.BytesIO()
        options = {}
        if save_fmt in ("JPEG", "WEBP"):
            options = {"quality": quality, "optimize": True}
        image.save(output, format=save_fmt, **options)
        compressed = output.getvalue()

        original_size = len(data)
        compressed_size = len(compressed)

        out_name = os.path.splitext(filename_or_error)[0] + "_converted." + ext
        temp_path = save_temp_file(compressed, "." + ext)

        return render_template(
            "result.html",
            tool_name="Обработка изображений",
            original_name=filename_or_error,
            original_size=format_size(original_size),
            compressed_size=format_size(compressed_size),
            saved_percent=round((1 - compressed_size / original_size) * 100, 1) if original_size else 0,
            download_name=out_name,
            download_path=temp_path,
            back_url="/image",
            mimetype=mime,
        )
    except Exception as e:
        return render_template("image.html", error=f"Ошибка обработки изображения: {e}"), 500
