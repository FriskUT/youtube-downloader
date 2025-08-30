from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import traceback
import glob

app = Flask(__name__)

# Diretório de downloads
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)
    print(f"[INFO] Criado diretório de downloads: {DOWNLOAD_DIR}")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        format_type = request.form.get("format")

        print(f"[DEBUG] URL recebida: {url}")
        print(f"[DEBUG] Formato solicitado: {format_type}")

        if not url or not format_type:
            print("[ERROR] URL ou formato ausente")
            return "URL ou formato ausente", 400

        # Nome do arquivo com base no título do vídeo
        output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

        ydl_opts = {
            "outtmpl": output_template,
        }

        if format_type == "mp4":
            ydl_opts.update({
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
                "merge_output_format": "mp4",
            })
        elif format_type == "flac":
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "flac",
                    "preferredquality": "0",
                }],
            })
        else:
            print("[ERROR] Formato inválido")
            return "Formato inválido", 400

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("[INFO] Iniciando download com yt-dlp...")
                info = ydl.extract_info(url, download=True)
                print("[INFO] Download concluído.")

                # Recupera nome final do arquivo
                filename = ydl.prepare_filename(info)
                if format_type == "flac":
                    filename = os.path.splitext(filename)[0] + ".flac"

            if os.path.exists(filename):
                print(f"[INFO] Arquivo pronto: {filename}")
                return send_file(filename, as_attachment=True)

            print("[ERROR] Arquivo não encontrado.")
            return "Falha no download ou arquivo ausente", 500

        except Exception as e:
            print("[EXCEPTION] Ocorreu um erro:")
            traceback.print_exc()
            return f"Ocorreu um erro: {str(e)}", 500

    try:
        return render_template("index.html")
    except Exception as e:
        print("[ERROR] Não foi possível renderizar index.html.")
        traceback.print_exc()
        return "Erro ao renderizar template. Veja os logs do servidor.", 500


if __name__ == "__main__":
    app.run(debug=True)
