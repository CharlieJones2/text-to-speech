import math
import random
import requests
import playsound
from moviepy.editor import AudioFileClip, concatenate_audioclips, VideoFileClip, CompositeAudioClip, TextClip, CompositeVideoClip
from moviepy.video.fx import crop
import whisper
import whisper_timestamped
from tiktokvoice import tts
import os

# creating tts audio
text = input('paste text')
if text[-1] == '.':
    text = text[:-1]
sentences = text.split('.')
audio_files = []
for x in range(len(sentences)):
    tts(sentences[x], 'en_us_006', 'audiooutputcontainer/output' + str(x) + '.mp3', play_sound=False)
    audio_files.append('audiooutputcontainer/output' + str(x) + '.mp3')
audios = []
for audio in audio_files:
    audios.append(AudioFileClip(audio))
audioClips = concatenate_audioclips([audio for audio in audios])
audioClips.write_audiofile('text.mp3')  # writing the file as 'text.mp3'

# Failed attempt to get the program to recognise the file
# with audioClips as file:
#     file.write_audiofile('text.mp3')

# getting audio and video lengths
audiofile = AudioFileClip('text.mp3')
soundduration = math.floor(audiofile.duration) + 1
videofile = VideoFileClip('resources/parkour.mp4')
duration = math.floor(videofile.duration)

# getting a random point in the video
point = random.randint(0, duration - soundduration)

# mixing the tts with music
music = AudioFileClip('resources/music.mp3').subclip(0, soundduration)
music = music.volumex(0.2)
mixed = CompositeAudioClip([audiofile, music])

# cropping and adding audio
clip = VideoFileClip('resources/parkour.mp4').subclip(point, point + soundduration)
w, h = clip.size
clip = clip.crop(width=480, height=720, x_center=w/2, y_center=h/2)
clip.audio = mixed

# checking text.mp3 has been created successfully
print(os.path.exists('text.mp3'))

# checking path
current_directory = os.path.abspath(os.path.dirname(__file__))
file_path = os.path.join(current_directory, 'text.mp3')
print('file path:', file_path)

# making subtitles
model = whisper.load_model('base')
audio = whisper.load_audio('text.mp3')  # FileNotFoundError: [WinError 2] The system cannot find the file specified
results = model.transcribe(audio)

# adding subtitles
subs = list()
subs.append(clip)
for segment in results['segments']:
    for word in segment['words']:
        text = word['text'].upper()
        start = word['start']
        end = word['end']
        duration = end - start
        txt_clip = TextClip(txt=text, fontsize=40, font='Arial-Bold', stroke_width=2, stroke_color='black', color='white')
        txt_clip = txt_clip.set_start(start).set_duration(duration).set_pos(('center', 'center'))
        subs.append(txt_clip)

clip = CompositeVideoClip(subs)

# outputting video
clip.write_videofile('output.mp4')
