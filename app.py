import os
import tempfile
from flask import Flask, render_template, send_file, request, abort

from tools.pdf_tool import pdf_compress
from tools.word_tool import word_compress
from tools.pptx_tool import pptx_compress
from tools.excel_tool import excel_compress
from tools.image_tool import image_tool

app = Flask(__name__)

# Лимит размера загружаемого файла — 50 МБ
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

# Секретный ключ (для flash и т.п., если понадобится)
app.secret_key = os.environ.get("SECRET_KEY", "docvex-dev-secret-change-me")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/download")
def download_file():
    """Скачивание временного файла после сжатия."""
    path = request.args.get("path")
    name = request.args.get("name", "file")
    mimetype = request.args.get("mimetype", "application/octet-stream")

    if not path or not os.path.isfile(path):
        abort(404)

    # Разрешаем только файлы из системной временной директории
    real_path = os.path.realpath(path)
    tmp_dir = os.path.realpath(tempfile.gettempdir())
    if not real_path.startswith(tmp_dir + os.sep):
        abort(403)

    response = send_file(
        path,
        as_attachment=True,
        download_name=name,
        mimetype=mimetype,
    )

    # Удаляем временный файл после отправки
    try:
        os.unlink(path)
    except Exception:
        pass

    return response


app.add_url_rule("/pdf-compress", view_func=pdf_compress, methods=["GET", "POST"])
app.add_url_rule("/word-compress", view_func=word_compress, methods=["GET", "POST"])
app.add_url_rule("/pptx-compress", view_func=pptx_compress, methods=["GET", "POST"])
app.add_url_rule("/excel-compress", view_func=excel_compress, methods=["GET", "POST"])
app.add_url_rule("/image", view_func=image_tool, methods=["GET", "POST"])


@app.errorhandler(413)
def too_large(e):
    return render_template("error.html", message="Файл слишком большой (максимум 50 МБ)"), 413


if __name__ == "__main__":
    # Для разработки. В продакшене используйте gunicorn
    app.run(host="0.0.0.0", port=5000, debug=True)
