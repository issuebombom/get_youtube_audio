import streamlit as st
import datetime as dt
import time
import os
from utils import YoutubeAudioExtractor, AudioEditor, audio_player, get_audio_list, get_audio_length, speech_to_text

st.title('Youtube mp3 file extractor')
st.markdown("""##### 유튜브 링크를 입력하면 mp3 파일을 추출합니다.""")

user_name = st.text_input(label='사용자 이름 입력', 
                          max_chars=20
                          )

if len(user_name) == 0:
    st.info('사용자 이름을 입력해 주세요.', icon="ℹ️")
    st.stop()

st.markdown("""##### """) # empty space for layer

# 링크 입력
urls = st.text_area('링크를 입력합니다.')
youtube = YoutubeAudioExtractor(urls, user_name)

# 추출 시작 버튼
if st.button('Extract', disabled=False if len(urls) != 0 else True):
    with st.spinner('Wait for it...'):
        title_to_url = youtube.extract()

user_dir = os.path.join('userdata', user_name)
user_cache_dir = os.path.join(user_dir, 'cache')

# 한 번이라도 추출을 해야 userdata에 사용자 폴더가 생성됨
if os.path.exists(user_dir):
    audio_txt_path = get_audio_list(user_dir) # refresh audio list

    with open(audio_txt_path, 'r') as txt:
        read_txt = txt.read()
        audio_list = read_txt.strip().split(sep='\n')

        st.markdown("""## """) # empty space for layer

        # 음원 리스트 보기
        col1, col2 = st.columns([8, 1.4])
        with col1:
            selected_audio_name = st.selectbox("저장된 음원 목록", audio_list, label_visibility='collapsed')
        with col2:
            if st.button('Refresh'):
                get_audio_list(user_dir)
        
        # metadata
        editor = AudioEditor(user_dir)
        audio_name = selected_audio_name
        audio_path = os.path.join(user_dir, audio_name)
        audio_length = get_audio_length(audio_path)

        # 플레이어 및 다운로드 기능 생성
        audio_player(audio_path, audio_name)

    st.markdown("""# """) # empty space for layer
    st.markdown("""# """) # empty space for layer
    
    with st.expander('음원 편집'):
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(['이름 변경', '음원 삭제', 
                                                            '음원 편집', '페이드인/아웃', 
                                                            '노멀라이즈', '음원 합치기', 
                                                            '편집 음원 저장'])

        with tab1:
            # 오디오 파일 이름 수정
            st.markdown(f'현재 선택된 파일은 :red[{audio_name}] 입니다.')
            col1, col2 = st.columns(2)
            with col1:
                switch_name = st.text_input('수정할 파일명을 적어주세요. ex) fixed_audio', label_visibility='collapsed')
            with col2:
                if st.button('Rename'):
                    editor.rename_audio(audio_path, audio_name, switch_name)

        with tab2:
            st.markdown(f'현재 선택된 파일은 :red[{audio_name}] 입니다.')
            if st.button('Delete'):
                editor.delete_audio(audio_path)

        with tab3:
            st.markdown(f'현재 선택된 파일은 :red[{audio_name}] 입니다.')
            # 최소 최대 시간 값 선택 바
            time_range = [str(dt.timedelta(seconds=seconds)) for seconds in range(audio_length+1)] # 0:00:00 형태로 출력
            start_sec, end_sec = st.select_slider('편집 범위를 선택해주세요',
                                                options=time_range,
                                                value=(time_range[0], time_range[-1])
                                                )
            st.markdown(f"You seleted length between :red[{start_sec}] and :red[{end_sec}]")
            
            if st.button('Trim'):
                with st.spinner('Wait for it...'):
                    # Trim
                    trim_audio_path, _ = editor.trim_audio(audio_path, start_sec, end_sec)

                    while True: # Trim이 완료될 때 까지 대기
                        if os.path.exists(trim_audio_path):
                            trim_audio_length = get_audio_length(trim_audio_path)
                            break
                        time.sleep(0.5)
                    # 임시파일 음원 양 끝단에 fade in/out처리 후 최종 저장합니다.
                    fade_audio_path, file_name = editor.fade_audio(trim_audio_path, trim_audio_length, fade_type='edge', duration=0.05, clean_cache=False)

                # 플레이어 및 다운로드 기능 생성
                audio_player(fade_audio_path, file_name)

        with tab4:
            st.markdown(f'현재 선택된 파일은 :red[{audio_name}] 입니다.')
            fade_type = st.radio('페이드 타입을 선택하세요.', ('in', 'out', 'edge'))
            duration = st.number_input('페이드 길이를 입력하세요. (초)')
            if st.button(f'Fade {fade_type}'):
                with st.spinner('Wait for it...'):
                    # Fade in/out
                    fade_audio_path, file_name = editor.fade_audio(audio_path, audio_length, fade_type=fade_type, duration=duration, clean_cache=False)

                # 플레이어 및 다운로드 기능 생성
                audio_player(fade_audio_path, file_name)

        with tab5:
            st.markdown(f'현재 선택된 파일은 :red[{audio_name}] 입니다.')
            target_level = st.slider('Target level을 선택하세요. (default: -14dB/LUFS)', -23, -10, -14)

            if st.button(f'Normalize'):
                with st.spinner('Wait for it...'):
                    # normalize
                    norm_audio_path, file_name = editor.normalize_audio(audio_path, target_level)

                # 플레이어 및 다운로드 기능 생성
                audio_player(norm_audio_path, file_name)

        with tab6:
            st.markdown(f':blue[*선택된 음원을 모두 합쳐줍니다.*]')
            # NOTE: multiselect에서 중복 선택도 가능하도록 수정하면 좋겠음
            concat_list = st.multiselect('음원을 순서대로 선택하세요.', audio_list)
            if st.button('Concatenate'):
                with st.spinner('Wait for it...'):
                    concat_audio_path, file_name = editor.concat_mp3_file(concat_list)

                # 플레이어 및 다운로드 기능 생성
                audio_player(concat_audio_path, file_name)

        with tab7:
            st.markdown(f':blue[*편집이 완료된 음원을 저장하면 음원 목록에서 볼 수 있습니다.*]')
            # cache 폴더 내 음원 목록 조회
            edited_audio_text = os.popen(f"""ls -tr '{user_cache_dir}' | grep -E '.mp3'""").read()
            edited_audio_list = edited_audio_text.strip().split(sep='\n') # 리스트 변환
            selected_edited_audio_name = st.selectbox('저장할 파일을 선택하세요.', edited_audio_list)
            
            if len(selected_edited_audio_name) != 0:
                # 플레이어 및 다운로드 기능 생성
                edited_audio_path = os.path.join(user_cache_dir, selected_edited_audio_name)
                audio_player(edited_audio_path, selected_edited_audio_name)

                save_name = st.text_input('저장할 이름을 입력하세요.', 'edited_audio')
                if st.button('Save'):
                    editor.save_edit_audio(selected_edited_audio_name, save_name)

    st.markdown("""# """) # empty space for layer

    with st.expander('텍스트 추출'):
        st.markdown(f':blue[*스피치 음원에서만 괜찮은 성능을 보여줍니다.* (*보통 20sec/min 정도의 시간이 소요됩니다.*)]')
        st.markdown(f'현재 선택된 파일은 :red[{audio_name}] 입니다.')
        
        translate_language = None
        translate = st.checkbox('translate')

        if translate:
            lang = st.radio(" ", ('영/한', '한/영'), label_visibility='collapsed')

            if lang == '영/한':
                translate_langunge = ['en', 'ko']
            else:
                translate_langunge = ['ko', 'en']

        # NOTE: 소요시간 추가 필요
        if st.button('Start'):
            with st.spinner('Wait for it...'):
                script = speech_to_text(audio_path, translate, translate_language)
            
            csv = script.to_csv(index=False).encode('utf-8')
            st.download_button("Download to CSV",
                            data=csv,
                            file_name="my_script.csv",
                            mime="text/csv",
                            key='download-csv'
            )
            st.dataframe(script.style.format(precision=2), use_container_width=True)


