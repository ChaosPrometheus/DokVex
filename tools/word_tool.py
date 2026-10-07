from flask import request, render_template
from tools.common import (
    validate_file,
    compress_office_document,
    format_size,
    save_temp_file,
    ALLOWED_EXTENSIONS,
)


def word_compress():
    if request.method == "GET":
        return render_template("word_compress.html")

    file = request.files.get("file")
    data, filename_or_error = validate_file(file, ALLOWED_EXTENSIONS["word"])
    if data is None:
        return render_template("word_compress.html", error=filename_or_error), 400

    try:
        quality = int(request.form.get("quality", 70))
        max_width = int(request.form.get("max_width", 1920))

        compressed, original_size, compressed_size = compress_office_document(
            data,
            media_prefix="word/media/",
            quality=quality,
            max_width=max_width,
        )

        out_name = filename_or_error.rsplit(".", 1)[0] + "_compressed.docx"
        temp_path = save_temp_file(compressed, ".docx")

        return render_template(
            "result.html",
            tool_name="Сжатие Word",
            original_name=filename_or_error,
            original_size=format_size(original_size),
            compressed_size=format_size(compressed_size),
            saved_percent=round((1 - compressed_size / original_size) * 100, 1) if original_size else 0,
            download_name=out_name,
            download_path=temp_path,
            back_url="/word-compress",
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except Exception as e:
        return render_template("word_compress.html", error=f"Ошибка сжатия: {e}"), 500
