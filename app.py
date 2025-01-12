import json
import random
import streamlit as st
import os

os.system('pip install PyGithub')

from github import Github

gh_token = os.getenv('GITHUB_TOKEN')
g = Github(gh_token)

repo = g.get_repo('sci-m-wang/psy_label')
branch = "main"

def load_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def select_sample(status, data):
    for index,key in enumerate(status, start=0):
        if status[key] == -1:
            first_index = index
            break
        pass
    return first_index, data[first_index]
    # unsubmitted_sample_ids = [key for key in status if status[key] == -1]
    # unsubmitted_samples = [sample for sample in data if sample['id'] in unsubmitted_sample_ids]
    # # print(unsubmitted_samples)
    # if unsubmitted_samples:
    #     return random.choice(unsubmitted_samples)
    # else:
    #     return None

def app():
    data = load_data('D4_seek_chain.json')
    # 检查是否存在标注状态文件，若不存在，创建并将所有样例的标注状态初始化为-1
    if not os.path.exists(f'annotator_{state.account}'):
        os.mkdir(f'annotator_{state.account}')
    if not os.path.exists(f'annotator_{state.account}/D4_label_status.json'):
        with open(f'annotator_{state.account}/D4_label_status.json', 'w') as f:
            json.dump({sample['id']: -1 for sample in data}, f)
            pass
        pass
    status = load_data(f'annotator_{state.account}/D4_label_status.json')
    index, sample = select_sample(status, data)
    # progess bar
    st.write(f'当前样例：{index+1}/{len(data)}')
    # print(sample)
    if sample:
        # Display portrait information
        st.write('# 基本信息')
        st.write(f'年龄: {sample["portrait"]["age"]}')
        st.write(f'性别: {sample["portrait"]["gender"]}')
        st.write(f'职业: {sample["portrait"]["occupation"]}')
        st.write(f'婚姻状况: {sample["portrait"]["martial_status"]}')
        st.write(f'症状: {sample["portrait"]["symptoms"]}')

        # Display event information
        st.write('# 近期遭遇事件')
        st.write(sample['event'])

        # Display log information as chat messages
        st.write('# 咨访记录')
        for log in sample['log']:
            if log['speaker'] == 'patient':
                st.chat_message('患者', avatar="👱‍♂️").write(log['text'])
            else:
                st.chat_message('医生', avatar="🧑‍⚕️").write(log['text'])

        # Display report information
        st.write('# 报告')
        for key, value in sample['report'].items():
            if key != '案例标题' and key != 'id':
                st.write(f'### {key}')
                for item in value:
                    st.write(item)
                    pass
                pass
            elif key == 'id':
                continue
            else:
                st.write(f'### {key}: {value}')

        # Display chain information
        st.write('# 诉求变化链')
        chain = sample['chain']
        for i in range(len(chain)):
            for stage in chain:
                if stage["stage"] == i+1:
                    st.write(f'阶段 {stage["stage"]}: {stage["content"]}')

        # Create buttons for submitting the sample
        file_path = f'annotator_{state.account}/D4_label_status.json'
        if st.button('推理链合理'):
            # Save the sample with status 0
            status[sample['id']] = 0
            with open(file_path, 'w') as f:
                json.dump(status, f)
                pass
        if st.button('需要修改'):
            # Save the sample with status 1
            status[sample['id']] = 1
            with open(file_path, 'w') as f:
                json.dump(status, f)
                pass
            pass
        if st.button("上一个"):
            status[index-1] = -1
            with open(file_path, 'w') as f:
                json.dump(status, f)
                pass
            pass
        # push to github
        try:
            repo.get_contents(f'annotator_{state.account}/D4_label_status.json')
            repo.update_file(f'annotator_{state.account}/D4_label_status.json', 'Update label status', json.dumps(status), sha=repo.get_contents(f'annotator_{state.account}/D4_label_status.json').sha)
        except:
            repo.create_file(f'annotator_{state.account}/D4_label_status.json', 'Create label status', json.dumps(status))
        pass

    else:
        st.write('No more samples to annotate.')

if __name__ == '__main__':
    state = st.session_state
    if 'signed_in' not in state:
        state.signed_in = False
        pass
    if not state.signed_in:
        state.account = st.text_input('账号')
        state.password = st.text_input('密码', type='password')
        if st.button('登录'):
            if os.getenv(f"annotator_{state.account}_password") is None:
                st.error('账号不存在')
                pass
            std_password = os.getenv(f"annotator_{state.account}_password")
            if state.password == std_password:
                state.signed_in = True
                st.rerun()
                pass
            else:
                st.error('密码错误')
                pass
            pass
        pass
    else:
        app()