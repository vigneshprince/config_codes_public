# %%
import subprocess
from pytube import YouTube
import math
import re
import pathlib
import os
import ffmpeg
import win32clipboard
from pytube.cli import on_progress

# %%


def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])
# %%
while True:
    try:
        win32clipboard.OpenClipboard()
        data=win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        yt = YouTube(data, on_progress_callback=on_progress)
        # %%
        streams=yt.streams.filter(adaptive=True)
        keys=['en','a.en']
        sub=''
        for k in keys:
            if k in yt.captions.keys():
                sub=yt.captions[k].download(title='sub')
                break
    except:
        input('Copy YT link and Enter to continue ')
        continue
    print(streams[0].title)
    # %%
    video_streams=list(filter(lambda x: x.type=='video', streams))
    audio_streams=list(filter(lambda x: x.type=='audio', streams))
    try:
        video_streams=[{'id':stream.itag,'res':stream.resolution,'codec':stream.video_codec,'size':int(stream.filesize)} for stream in video_streams]
        video_streams=sorted(video_streams,key=lambda x:x['size'],reverse=True)

        audio_streams=[{'id':stream.itag,'bitrate':stream.abr,'codec':stream.audio_codec,'size':int(stream.filesize)} for stream in audio_streams]
        audio_streams=sorted(audio_streams,key=lambda x:x['size'],reverse=True)

        print('-----------------Video Streams-----------------')
        for i,r in enumerate(video_streams,1):

            print(f"{i}. {r['res']} - {r['codec']} - {convert_size(r['size'])}")
        print('-----------------Audio Streams-----------------')
        for i, r in enumerate(audio_streams,1):
            print(f"{i}. {r['bitrate']} - {r['codec']} - {convert_size(r['size'])}")
    except:
        video_streams=[{'id':stream.itag,'res':stream.resolution,'codec':stream.video_codec} for stream in video_streams]

        audio_streams=[{'id':stream.itag,'bitrate':stream.abr,'codec':stream.audio_codec} for stream in audio_streams]

        print('-----------------Video Streams-----------------')
        for i,r in enumerate(video_streams,1):

            print(f"{i}. {r['res']} - {r['codec']}")
        print('-----------------Audio Streams-----------------')
        for i, r in enumerate(audio_streams,1):
            print(f"{i}. {r['bitrate']} - {r['codec']}")

    # %%
    ips=input('Enter Video# and Audio# seperated by comma (default 1,1) / "c" to cancel : ').split(',')
    if ips[0]=='':
        ips=['1','1']
    if ips[0]=='c':
        input('Copy YT link and Enter to continue ')
        continue
    if len(ips)==1:
        ips.append('1')
    # %%
    vid_stream=streams.get_by_itag(video_streams[int(ips[0])-1]['id'])
    vid_path=vid_stream.download(skip_existing=False,filename_prefix='video_')
    audio_path=streams.get_by_itag(audio_streams[int(ips[1])-1]['id']).download(skip_existing=False,filename_prefix='audio_')

    # %%
    if sub!='':
        print('Subtitle found')
        subprocess.call(f'ffmpeg -loglevel panic -y  -i \"{vid_path}\"  -i \"{audio_path}\" -i \"{sub}\" -c:v copy -c:a copy -c:s mov_text \"{pathlib.Path(vid_path).stem.replace("video_","",1)}_{vid_stream.resolution}.mp4\"', shell=True)
        os.remove(sub)

    else:
        subprocess.call(f'ffmpeg -loglevel panic -y -i \"{audio_path}\" -i \"{vid_path}\" -c:v copy -c:a copy \"{pathlib.Path(vid_path).stem.replace("video_","",1)}_{vid_stream.resolution}.mp4\"', shell=True)

    # %%
    os.remove(vid_path)
    os.remove(audio_path)
    input('Copy YT link and Enter to continue ')
# %%



