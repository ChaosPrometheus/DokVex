import io
import zipfile
from flask import request, render_template, send_file
from PIL import Image

def word_compress():
    if request.method == "GET":
        return render_template("word_compress.html")
    file = request.files.get("file")
    if not file or not file.filename:
        return "Файл не выбран", 400
    if not file.filename.lower().endswith(".docx"):
        return "Поддерживается только DOCX", 400
    try:
        quality = int(request.form.get("quality", 65))
        max_width = int(request.form.get("max_width", 1920))
        source = zipfile.ZipFile(io.BytesIO(file.read()), "r")
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as result:
            for item in source.infolist():
                data = source.read(item.filename)
                if item.filename.startswith("word/media/"):
                    try:
                        image = Image.open(io.BytesIO(data))
                        original = len(data)
                        if image.width > max_width:
                            h = int(image.height * max_width / image.width)
                            image = image.resize((max_width, h), Image.Resampling.LANCZOS)
                        temp = io.BytesIO()
                        if image.format in ("JPEG", "JPG"):
                            image.convert("RGB").save(temp, "JPEG", quality=quality, optimize=True)
                        elif image.format == "PNG":
                            if "A" in image.getbands():
                                image.save(temp, "PNG", optimize=True)
                            else:
                                image.convert("RGB").save(temp, "JPEG", quality=quality, optimize=True)
                        new = temp.getvalue()
                        if new and len(new) < original:
                            data = new
                    except Exception:
                        pass
                result.writestr(item, data)
        source.close()
        output.seek(0)
        name = file.filename.rsplit(".", 1)[0] + "_compressed.docx"
        return send_file(output, as_attachment=True, download_name=name,
                         mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    except Exception as e:
        return f"Ошибка сжатия DOCX: {e}", 500
