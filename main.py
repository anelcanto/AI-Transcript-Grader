import os

import moviepy.editor as mp
import openai
from sys import argv
from os.path import exists, dirname, splitext

if argv[1] == "":
    print("No directory given")
    exit(1)

directory = dirname(argv[1])
included_extensions = ['.mov', '.mp4', '.mkv']
file_names = [fn for fn in os.listdir(dirname(argv[1])) if any(fn.endswith(ext) for ext in included_extensions)]

openai.api_key = os.getenv('OPENAI_API_KEY')
system_message = open("system_message.txt").read()
rubric = open("rubric.txt").read() + "\n\nDo you understand the requirements?"
rubric_response = "Yes, I understand the requirements."

os.makedirs(directory + "/transcripts", exist_ok=True)
os.makedirs(directory + "/grades", exist_ok=True)
os.makedirs("temp", exist_ok=True)

for fname in file_names:
    file = directory + "/" + fname
    audio_fname = "temp/" + splitext(fname)[0] + ".mp3"
    transcript_fname = directory + "/transcripts/" + splitext(fname)[0] + ".txt"
    response_fname = directory + "/grades/" + splitext(fname)[0] + ".txt"
    if exists(response_fname):
        continue

    print("Processing " + fname + "...")

    try:
        if exists(audio_fname):
            print("Using existing audio file: " + audio_fname)
        else:
            clip = mp.VideoFileClip(file)
            clip.audio.write_audiofile(audio_fname)

        if exists(transcript_fname):
            print("Reusing old transcript...")
            transcript = open(transcript_fname).read()
        else:
            audio_file = open(audio_fname, "rb")
            print("Transcribing audio...")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)["text"]
            with open(transcript_fname, "w") as f:
                f.write(transcript)

        print("Checking against rubric...")
        completion = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": rubric},
            {"role": "assistant", "content": rubric_response},
            {"role": "user", "content": "Here is the student's transcript:\n" + transcript},
          ]
        )
        grade = completion['choices'][0]['message']['content']
        with open(response_fname, "w") as f:
            f.write(grade)
        print("Response saved.\t", grade.count("Yes"), "Yes.\t", grade.count("No"), "No.\t",
              grade.count("Partial"), "Partial.")
        print()
    except BaseException as e:
        print("Error encountered processing this student's submission")
        print(e)
print("Done.")