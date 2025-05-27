import os
import whisper



# Carrega o modelo do Whisper
model = whisper.load_model("small")  # ou "medium"/"large" se quiser mais precisão

prompt = (
    "Analise com atenção e precisão o conteúdo deste vídeo, no qual um médico discute temas relacionados a antibióticos, incluindo beta-lactâmicos, penicilina, amoxicilina, cefalosporinas e outros medicamentos ligados à microbiologia. Certifique-se de identificar corretamente os termos técnicos relacionados a fármacos e verifique cuidadosamente se estão presentes ou não na transcrição ou no conteúdo analisado.")


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


# Nova função para dividir texto com dois critérios
def split_text_by_char_and_word_limit(text, max_chars=18, max_words=4):
    words = text.strip().split()
    chunks = []
    current = []

    for word in words:
        temp = current + [word]
        temp_text = " ".join(temp)

        if len(temp_text) <= max_chars and len(temp) <= max_words:
            current = temp
        else:
            if current:
                chunks.append(" ".join(current))
            current = [word]

    if current:
        chunks.append(" ".join(current))

    return chunks


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

        # Transcrição com idioma português
        result = model.transcribe(
            new_path,
            language="pt",
            initial_prompt=prompt
        )

        # Base do nome do vídeo sem extensão
        base_name = os.path.splitext(new_filename)[0]
        srt_path = os.path.join(output_folder, base_name + ".srt")

        # Gera o arquivo .srt respeitando ambos os limites
        with open(srt_path, "w", encoding="utf-8") as srt_file:
            count = 1  # contador de blocos .srt
            for segment in result["segments"]:
                full_text = segment["text"].strip()
                start = segment["start"]
                end = segment["end"]

                # Chunks que respeitam palavras E caracteres
                chunks = split_text_by_char_and_word_limit(
                    full_text, max_chars=15, max_words=3
                )
                num_chunks = len(chunks)

                if num_chunks == 0:
                    continue

                total_duration = end - start
                chunk_duration = total_duration / num_chunks

                for i, chunk in enumerate(chunks):
                    chunk_start = start + i * chunk_duration
                    chunk_end = chunk_start + chunk_duration

                    srt_file.write(f"{count}\n")
                    srt_file.write(f"{format_srt_time(chunk_start)} --> {format_srt_time(chunk_end)}\n")
                    srt_file.write(chunk + "\n\n")
                    count += 1
