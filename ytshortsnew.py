import math
import random
from moviepy.editor import AudioFileClip, concatenate_audioclips, VideoFileClip, CompositeAudioClip, TextClip, CompositeVideoClip
import whisper_timestamped
from tiktokvoice import tts

# creating tts audio
text = input('input text: ')
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
audioClips.write_audiofile('text.mp3')

# getting audio and video lengths
audiofile = AudioFileClip('text.mp3')
soundduration = math.floor(audiofile.duration)  # + 1
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

# making subtitles
model = whisper_timestamped.load_model('base')
audio = whisper_timestamped.load_audio('text.mp3')
results = whisper_timestamped.transcribe(model, audio)

# adding subtitles
subs = []
subs.append(clip)
for segment in results['segments']:
    text = segment['text'].upper()
    words = text.split()
    for word in words:
        start = segment['start']  # problem?
        end = segment['end']  # problem?
        duration = end - start
        txt_clip = TextClip(txt=word, fontsize=40, font='Arial-Bold', stroke_width=2, stroke_color='black', color='white')
        txt_clip = txt_clip.set_start(start).set_duration(duration).set_pos(('center', 'center'))
        subs.append(txt_clip)

# outputting video
final_clip = CompositeVideoClip(subs)
final_clip.write_videofile('output.mp4', fps=30, audio_codec='aac', audio_bitrate='192k')
