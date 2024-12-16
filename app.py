import streamlit as st
from audiorecorder import audiorecorder
import openai_api
from streamlit_chat import message as msg

def main():

    st.set_page_config(
        page_title='🎙️Voice Chatbot🎙️',
        page_icon='🎙️',
        layout='wide',
    )

    st.header('🎙️Voice Chatbot🎙️')
    st.markdown('---')


    with st.expander('Voice Chatbot 프로그램을 사용하는 방법', expanded=True):
        st.write(
            """
            1. 녹음하기 버튼을 눌러 질문을 시작해주세요.
            2. 녹음이 완료되면, 자동으로 Whisper 모델을 이용해 녹음된 음성을 텍스트로 변환 후 LLM에 질의합니다.
            3. LLM의 응답을 다시 TTS모델을 사용해 음성으로 변환하고 이를 사용자에게 응답합니다.
            4. LLM의 OpenAI사의 GPT모델을 사용합니다.
            5. 모든 질문/답변은 텍스트로 제공 가능합니다.
            """
        )
    system_instruction = '당신은 친절한 챗봇입니다.'

    # session state 초기화
    # - chats: 웹페이지 시각화용 대화 내역
    # - messages: LLM 질의/웹페이지 시각화를 위한 대화 내역
    # - check_reset: 초기화를 위한 flag

    if 'messages' not in st.session_state:
        st.session_state['messages'] = [
            {'role':'system', 'content': system_instruction}
        ]

    if 'check_reset' not in st.session_state:
        st.session_state['check_reset'] = False


    with st.sidebar:
        model = st.radio(label='GPT 모델', options=['gpt-3.5-turbo','gpt-4-turbo','gpt-4o'])
        print(model)

        if st.button(label='초기화'):
            st.session_state['messages'] = [
                {'role': 'system', 'content': system_instruction}
            ]
            st.session_state['check_reset'] = True # 화면 정리

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('녹음하기')

        audio = audiorecorder()

        if (audio.duration_seconds > 0) and (st.session_state['check_reset'] == False):
            # 화면상의 재생기능
            st.audio(audio.export().read())
            # 사용자 음성에서 텍스트 추출
            query = openai_api.stt(audio)
            print('Q:',query)
            # LLM 질의
            st.session_state['messages'].append({'role':'user', 'content':query})
            response = openai_api.ask_gpt(st.session_state['messages'], model)
            print('A:',response)
            st.session_state['messages'].append({'role':'assistant', 'content':response})
            # TTS 음성 변환
            audio_tag = openai_api.tts(response)
            st.html(audio_tag) # 시각화되지 않고 자동으로 재생

    with col2:
        st.subheader('질문/답변')
        if (audio.duration_seconds > 0) and (st.session_state['check_reset'] == False):
            for i, message in enumerate(st.session_state['messages']):
                role = message['role']
                content = message['content']
                if role == 'user':
                    msg(content, is_user=True, key=str(i))
                elif role == 'assistant': # ai답변
                    msg(content, is_user=False, key=str(i))

        else:
            # 초기화버튼 누르면 화면이 정리되고 다시 check-reset을 원상 복구(이후에 또 그려내야 하니까)
            st.session_state['check_reset'] = False


if __name__ == '__main__':
    main()