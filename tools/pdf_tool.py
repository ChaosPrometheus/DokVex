import io
import fitz
from flask import request, render_template
from tools.common import validate_file, format_size, save_temp_file, ALLOWED_EXTENSIONS


def pdf_compress():
    if request.method == "GET":
        return render_template("pdf_compress.html")

    file = request.files.get("file")
    data, filename_or_error = validate_file(file, ALLOWED_EXTENSIONS["pdf"])
    if data is None:
        return render_template("pdf_compress.html", error=filename_or_error), 400

    try:
        document = fitz.open(stream=data, filetype="pdf")
        quality = request.form.get("quality", "ebook")

        # preset → (jpeg_quality, max_dimension)
        settings = {
            "screen": (40, 1200),
            "ebook": (60, 1600),
            "printer": (80, 2400),
            "prepress": (90, 3200),
        }
        image_quality, max_dim = settings.get(quality, settings["ebook"])

        # --- Способ 1: встроенный rewrite_images (PyMuPDF ≥ 1.24) ---
        used_rewrite = False
        if hasattr(document, "rewrite_images"):
            try:
                dpi_map = {
                    "screen": 72,
                    "ebook": 100,
                    "printer": 150,
                    "prepress": 200,
                }
                target_dpi = dpi_map.get(quality, 100)
                document.rewrite_images(
                    dpi_threshold=target_dpi + 30,
                    dpi_target=target_dpi,
                    quality=image_quality,
                    lossy=True,
                    lossless=True,
                    bitonal=True,
                    color=True,
                    gray=True,
                    set_to_gray=False,
                )
                used_rewrite = True
            except Exception:
                used_rewrite = False

        # --- Способ 2: ручная замена (fallback) ---
        if not used_rewrite:
            # xref → номер страницы, на которой картинка встречается
            xref_to_page = {}
            for page_index in range(len(document)):
                for img in document[page_index].get_images(full=True):
                    xref_to_page.setdefault(img[0], page_index)

            for xref, page_index in xref_to_page.items():
                try:
                    pix = fitz.Pixmap(document, xref)

                    # Не трогаем картинки с прозрачностью
                    if pix.alpha:
                        continue

                    # CMYK / многоканальные → RGB
                    if pix.n - pix.alpha >= 4:
                        pix = fitz.Pixmap(fitz.csRGB, pix)

                    # Уменьшаем крупные изображения (shrink делит стороны пополам)
                    while max(pix.width, pix.height) > max_dim * 1.4:
                        pix.shrink(1)

                    new_stream = pix.tobytes("jpeg", jpg_quality=image_quality)

                    try:
                        old_size = len(document.xref_stream_raw(xref))
                    except Exception:
                        old_size = len(new_stream) + 1

                    if len(new_stream) < old_size:
                        document[page_index].replace_image(xref, stream=new_stream)

                except Exception:
                    continue

        # Сохраняем с максимальной очисткой
        output = io.BytesIO()
        document.save(
            output,
            garbage=4,
            deflate=True,
            clean=True,
            deflate_images=True,
            deflate_fonts=True,
        )
        document.close()
        compressed = output.getvalue()

        original_size = len(data)
        compressed_size = len(compressed)

        out_name = filename_or_error.rsplit(".", 1)[0] + "_compressed.pdf"
        temp_path = save_temp_file(compressed, ".pdf")

        return render_template(
            "result.html",
            tool_name="Сжатие PDF",
            original_name=filename_or_error,
            original_size=format_size(original_size),
            compressed_size=format_size(compressed_size),
            saved_percent=round((1 - compressed_size / original_size) * 100, 1)
            if original_size
            else 0,
            download_name=out_name,
            download_path=temp_path,
            back_url="/pdf-compress",
            mimetype="application/pdf",
        )
    except Exception as e:
        return (
            render_template(
                "pdf_compress.html",
                error=f"Ошибка обработки PDF: {type(e).__name__}: {e}",
            ),
            500,
        )
