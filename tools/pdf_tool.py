import io
import fitz
from flask import request, render_template, send_file

def pdf_compress():
    if request.method == "GET":
        return render_template("pdf_compress.html")
    file = request.files.get("file")
    if not file or not file.filename:
        return "Файл не выбран", 400
    if not file.filename.lower().endswith(".pdf"):
        return "Можно загружать только PDF", 400
    try:
        document = fitz.open(stream=file.read(), filetype="pdf")
        quality = request.form.get("quality", "ebook")
        settings = {
            "screen": (45, 1500),
            "ebook": (65, 2000),
            "printer": (80, 3000),
            "prepress": (90, 4000),
        }
        image_quality, max_size = settings.get(quality, settings["ebook"])

        for page in document:
            for info in page.get_images(full=True):
                xref = info[0]
                try:
                    extracted = document.extract_image(xref)
                    ext = extracted["ext"]
                    if ext not in ("jpg", "jpeg", "png"):
                        continue
                    pix = fitz.Pixmap(extracted["image"])
                    if pix.alpha:
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    if pix.width > max_size:
                        scale = max_size / pix.width
                        pix = fitz.Pixmap(
                            pix, 0, int(pix.width * scale),
                            int(pix.height * scale), [], False
                        )
                    new_data = pix.tobytes("jpg", jpg_quality=image_quality)
                    if len(new_data) < len(extracted["image"]):
                        document.replace_image(xref, stream=new_data)
                except Exception:
                    pass

        output = io.BytesIO()
        document.save(output, garbage=4, deflate=True, clean=True,
                      deflate_images=True, deflate_fonts=True)
        document.close()
        output.seek(0)
        name = file.filename.rsplit(".", 1)[0] + "_compressed.pdf"
        return send_file(output, as_attachment=True, download_name=name,
                         mimetype="application/pdf")
    except Exception as e:
        return f"Ошибка обработки PDF: {e}", 500
