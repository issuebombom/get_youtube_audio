import os
import random
import requests
import json
import re
from collections import defaultdict
import pandas as pd
from tqdm import tqdm
from pytube import YouTube
import streamlit as st
import whisper

class YoutubeAudioExtractor:
    """Youtube 링크를 리스트 형식으로 받으면 해당 링크에서 음원 추출
    """

    def __init__(self, urls, user_name):
        self.user_dir = os.path.join("userdata", user_name)
        self.url_list = re.findall('http[a-zA-Z0-9:/.?=_\-]+', urls)

    def extract(self):
        """Youtube 음원 추출 및 폴더 내 음원 목록 저장
        """
        if not os.path.exists(self.user_dir): # 지정한 디렉토리가 없을 경우 신규 생성
            os.popen(f"mkdir -p {self.user_dir}")

        self.get_mp3_from_youtube()

        # 저장된 음원 목록 txt파일로 저장
        # os.popen(f"ls -tr {self.user_dir} | grep -E '.mp3' > {os.path.join(self.user_dir, 'audio_list.txt')}").read()
        
    def get_mp3_from_youtube(self):
        """입력된 유튜브 url에서 mp4 확장자를 가지는 음원을 추출하여 지정한 디렉토리에 저장합니다.
        pytube docs: https://pytube.io/en/latest/_modules/pytube/streams.html#Stream.download
        """
        my_bar = st.progress(0)
        for i, url in enumerate(tqdm(self.url_list)):
            youtube = YouTube(url)
            condition = youtube.streams.filter(only_audio=True, file_extension='mp4', type='audio', abr='128kbps').order_by('abr').last()
            condition.download(output_path=self.user_dir, filename='extract_file.mp4') # 다운로드가 완료되면 다음 line을 실행하는 것 확인

            # convert mp4a to mp3
            title = re.sub('[^가-힣A-Za-z0-9\s]', '', youtube.title).strip() # 특수문자 제외
            title = re.sub(' ', '\\ ', title) # 한글 띄어쓰기 앞에 \ 넣기
            save_file_path = os.path.join(self.user_dir, 'extract_file.mp4')
            converted_file_path = os.path.join(self.user_dir, title + '.mp3')

            os.popen(f"""
                    ffmpeg -i {save_file_path} {converted_file_path} -y &&
                    rm -f {save_file_path}
                    """).read()
            
            my_bar.progress((i+1) * 100//len(self.url_list)) # 프로그래스 바
    
class AudioEditor:

    def __init__(self, user_dir):
        self.user_dir = user_dir
        self.cache_dir = os.path.join(self.user_dir, 'cache') # cache 폴더 경로 지정

        if not os.path.exists(self.cache_dir): # cache 디렉토리가 없을 경우 신규 생성
            os.popen(f"mkdir -p {self.cache_dir}")

    def clean_cache(self):
        """cache 폴더를 리셋합니다.
        """

        if not os.path.exists(self.cache_dir): # 지정한 디렉토리가 없을 경우 신규 생성
            os.popen(f"mkdir -p {self.cache_dir}").read()
        
        else: # 기존 폴더 삭제 후 재생성
            os.popen(f"rm -rf {self.cache_dir} && mkdir -p {self.cache_dir}").read()
    
    def concat_mp3_file(self, concat_list, clean_cache=True):
        """여러 mp3 파일을 concat합니다.
        """

        if clean_cache:
            self.clean_cache()

        file_name = '[concat]output.mp3'
        concat_audio_path = os.path.join(self.cache_dir, file_name)
        concat_list_txt = os.path.join(self.user_dir, '[Temp]concat_list.txt') # concat 파일의 경로
        
        with open(concat_list_txt, 'w') as txt: # concat용 command text 작성
            for name in concat_list:
                txt.write(f"""file '{name}'\n""")

        os.popen(f"""
                    ffmpeg -f concat -safe 0 -i {concat_list_txt} -c copy {concat_audio_path} &&
                    rm -f {concat_list_txt}
                """).read()
        
        return concat_audio_path, file_name
        
    def trim_audio(self, audio_path, start_sec, end_sec, clean_cache=True):
        """오디오 자르기
        """

        if clean_cache:
            self.clean_cache()

        file_name = '[Trim]output.mp3'
        trim_audio_path = os.path.join(self.cache_dir, file_name)

        os.popen(f"""ffmpeg -i '{audio_path}' -ss {start_sec} -to {end_sec} -acodec copy '{trim_audio_path}' -y""").read()

        return trim_audio_path, file_name

    def fade_audio(self, audio_path, audio_length, fade_type='edge', duration=0.05, clean_cache=True):
        """오디오 페이드인/아웃
        """

        if clean_cache:
            self.clean_cache()

        file_name = f'[Fade_{fade_type}]output.mp3'
        fade_audio_path = os.path.join(self.cache_dir, file_name)

        if fade_type == 'edge':
            os.popen(f"""ffmpeg -i '{audio_path}' -af "afade=t=in:st=0:d={duration},afade=t=out:st={audio_length-duration}:d={duration}" '{fade_audio_path}' -y""").read()
        elif fade_type == 'in':
            os.popen(f"""ffmpeg -i '{audio_path}' -af "afade=t=in:st=0:d={duration}" '{fade_audio_path}' -y""").read()
        elif fade_type == 'out':
            os.popen(f"""ffmpeg -i '{audio_path}' -af "afade=t=out:st={audio_length-duration}:d={duration}" '{fade_audio_path}' -y""").read()
        
        return fade_audio_path, file_name
    
    def normalize_audio(self, audio_path, target_level=-14, clean_cache=True):
        """오디오 노멀라이즈
        """

        if clean_cache:
            self.clean_cache()

        file_name = '[Norm]output.mp3'
        norm_audio_path = os.path.join(self.cache_dir, file_name)

        os.popen(f"""ffmpeg-normalize '{audio_path}' -o '{norm_audio_path}' -f -v \
            -c:a libmp3lame --normalization-type ebu --target-level {target_level} \
            --keep-loudness-range-target --true-peak -0.2""").read()

        return norm_audio_path, file_name
        
    def rename_audio(self, audio_path, audio_name, switch_name):
        """지정한 파일 이름을 수정합니다.
        """

        extention = audio_name[audio_name.rfind('.'):]
        os.popen(f"""
                    mv '{audio_path}' '{os.path.join(self.user_dir, switch_name+extention)}'
                """).read()

    def delete_audio(self, audio_path):
        """지정한 파일을 삭제합니다.
        """

        os.popen(f"""
                    rm '{audio_path}'
                """).read()
        
    def save_edit_audio(self, audio_name, save_name):
        """편집한 음원을 사용자 폴더에 저장합니다.
        """
        extention = audio_name[audio_name.rfind('.'):]
        edited_audio_path = os.path.join(self.cache_dir, audio_name)
        save_file_path = os.path.join(self.user_dir, save_name+extention)

        os.popen(f"""mv -f '{edited_audio_path}' '{save_file_path}'""").read()


def audio_player(file_path, file_name):
    """오디오 플레이어를 생성합니다.
    """
    random_key = random.randint(1, 1e06)
    # 샘플 오디오 플레이어
    st.audio(file_path, format='audio/mp3')

    # 선택한 오디오 파일 읽기
    with open(file_path, "rb") as file:
        # 오디오 다운로드 버튼
        st.download_button(label='Download', mime='audio/mp3', data=file, file_name=file_name, key=random_key)
    
    # NOTE: 압축 후 다운로드 기능 구현 고민 (st.download버튼을 직접 클릭 외 실행하는 방법을 찾아야 함)
    '''
    if user_dir is not None:

        st.button(on_click=zip_and_download)

        def zip_and_download(user_dir):

            os.popen(f"""zip audio.zip {user_dir}/*.mp3""").read() # 압축

            zipfile_path = os.path.join(user_dir, 'audio.zip') # 압축파일 경로
            with st.spinner('Wait for zip...'): # 압축파일 생성 전까지 대기
                while True:
                    if os.path.exists(zipfile_path):
                        break
                    time.sleep(0.5)

            with open(zipfile_path, "rb") as zipfile:
                st.download_button(label='Download all', data=zipfile, file_name='audio.zip')
    '''

def get_audio_length(file_path):
    """오디오 총 길이를 확인합니다.

    Args:
        file_path (str): audio file path

    Returns:
        int: 
    """
    
    # SoudFile이 우분투에서 정상적으로 작동하지 않아 대체함
    # samplerate = sf.SoundFile(file_path).samplerate # extract samplerate
    # frames = sf.SoundFile(file_path).frames # extract audio frames
    # length = int(round(frames / samplerate)) # switch audio frames to second length

    duration_infos = os.popen(f"""ffmpeg -i '{file_path}' 2>&1 | grep 'Duration'""").read()
    hour, minute, second = duration_infos.strip().split(sep=',')[0][-11:].split(sep=':')
    length = int(hour) * 3600 + int(minute) * 60 + round(float(second))

    return length

def get_audio_list(user_dir, txt_file_name='audio_list.txt'):
    """사용자 폴더 내 mp3 파일을 탐색하여 audio_list.txt 파일에 기록합니다.
    """

    audio_txt_path = os.path.join(user_dir, txt_file_name)
    os.popen(f"""ls -tr {user_dir} | grep -E '.mp3' > {audio_txt_path}""").read() # mp3 목록을 갱신합니다.

    return audio_txt_path

def translator(msg, source="en", target="ko"):
    """language translator
    """

    # NOTE: must hide!!
    NAVER_CLIENT_ID, NAVER_CLIENT_SECRET = "", ""

    # Make Request Datas
    url = "https://openapi.naver.com/v1/papago/n2mt"
    headers = {
    "Content-Type": "application/json",
    "X-Naver-Client-Id": NAVER_CLIENT_ID,
    "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {"source": source, "target": target, "text": msg}

    # request(korean text) > response(english text)
    response = requests.post(url, json.dumps(params), headers=headers)

    # return english text
    return response.json()["message"]["result"]["translatedText"]

def speech_to_text(file_path, translate=False, translate_language=None):
    """extract text from audio

    Args:
        file_path (str): audio file path

    Returns:
        pandas.DataFrame: text script
    """

    model = whisper.load_model("base")
    result = model.transcribe(file_path, verbose=False)
    script_info = defaultdict(list)

    for segment in result['segments']:
        script_info['start'].append(segment['start'])
        script_info['end'].append(segment['end'])
        script_info['text'].append(segment['text'])
        if translate:
            script_info['translate'].append(translator(segment['text'], source=translate_language[0], target=translate_language[1]))

    script_info_df = pd.DataFrame(script_info).round(2)

    return script_info_df