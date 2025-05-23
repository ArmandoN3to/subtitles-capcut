import os
import whisper
import textwrap


# Carrega o modelo do Whisper
model = whisper.load_model("small")  # ou "medium"/"large" se quiser mais precisão

# Pasta dos vídeos e de saída das legendas
video_folder = "videos"
output_folder = "legendas"
os.makedirs(output_folder, exist_ok=True)


# Função para formatar tempo estilo SRT
def format_srt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

# Processamento de todos os vídeos
for filename in os.listdir(video_folder):
    if filename.endswith(".mp4"):
        old_path = os.path.join(video_folder, filename)

        # Remove espaços do nome
        new_filename = filename.replace(" ", "")
        new_path = os.path.join(video_folder, new_filename)
        if old_path != new_path:
            os.rename(old_path, new_path)

        print(f"Transcrevendo: {new_filename}")

        # Transcrição com idioma português + prompt contextual
        result = model.transcribe(
            new_path,
            language="pt"
        )
        # Base do nome do vídeo sem extensão
        base_name = os.path.splitext(new_filename)[0]
        srt_path = os.path.join(output_folder, base_name + ".srt")
        

        # Salva .srt com divisão de tempo proporcional por subblocos de até 50 caracteres
    with open(srt_path, "w", encoding="utf-8") as srt_file:
        count = 1  # contador das legendas
        for segment in result["segments"]:
            full_text = segment["text"].strip()
            start = segment["start"]
            end = segment["end"]

            # Quebra o texto em blocos de até 50 caracteres
            chunks = textwrap.wrap(full_text, width=25)
            num_chunks = len(chunks)

            if num_chunks == 0:
                continue

            # Duração total do segmento
            duration = end - start
            chunk_duration = duration / num_chunks

            for i, chunk in enumerate(chunks):
                chunk_start = start + i * chunk_duration
                chunk_end = chunk_start + chunk_duration

                srt_file.write(f"{count}\n")
                srt_file.write(f"{format_srt_time(chunk_start)} --> {format_srt_time(chunk_end)}\n")
                srt_file.write(chunk + "\n\n")

                count += 1

      
