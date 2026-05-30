import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from fetcher import fetch_data

def get_score(comments):
    
    neg = comments.count('Negative')
    neu = comments.count('Neutral')
    pos = comments.count('Positive')
    total = len(comments)

    score = (neg * -1 + neu * 0 + pos * 1) / total

    return score

def make_gauge(score, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={
            'font': {'size': 36, 'color': '#102a43'},
        },
        title={
            'text': title,
            'font': {'size': 21, 'color': '#243b53'},
        },
        gauge={
            'axis': {
                'range': [-1, 1],
                'tickwidth': 0,
                'tickcolor': '#9fb3c8',
                'tickfont': {'size': 13, 'color': '#486581'},
            },
            'bar': {'color':'#0f172a', 'thickness': 0.2},
            'bgcolor': 'rgba(0,0,0,0)',
            'borderwidth': 0,
            'steps': [
                {'range': [-1, -0.33], 'color':'rgba(240, 67, 55,0.50)'},
                {'range': [-0.33, 0.33], 'color': 'rgba(227, 201, 34,0.50)'},
                {'range': [0.33, 1], 'color': 'rgba(35, 207, 49,0.50)'}
            ],
            'threshold': {
                'line': {'color': '#0f172a', 'width': 5},
                'thickness': 0.85,
                'value': score,
            },
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=24, r=24, t=64, b=24),
        height=300,
        font=dict(color='#243b53'),
    )
    return fig

st.set_page_config(page_title="Hinglish Sentiment Analyzer", page_icon="🎬", layout='centered',)

st.title("Hinglish Sentiment Analyzer",text_alignment='center',anchor=False)

st.caption(
    "Paste a YouTube URL to analyse the comment sentiment and view the difference between a fine-tuned [**XLM-RoBERTa**](https://huggingface.co/docs/transformers/en/model_doc/xlm-roberta) and [**VADER**](https://github.com/cjhutto/vadersentiment)",text_alignment='center')

st.divider()

input_col, action_col = st.columns([5, 1], vertical_alignment="bottom")

with input_col:
    url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

with action_col:
    analyse_clicked = st.button("Analyse", type="primary", width="stretch")

if analyse_clicked:
    if not url.strip():
        st.error("Please enter a YouTube URL.")
    else:
        with st.spinner("Fetching comments…"):
            vid, vid_title, comments = fetch_data(url)

        if not vid_title:
            st.error("Video not found! Double-check the URL and try again.")
        else:
            st.header(vid_title,anchor=False)
            st.divider()
            st.iframe(f"https://www.youtube.com/embed/{vid}", height=280, width="stretch")
            st.divider()

        if len(comments) == 0 :
            st.error("The video has no comments! Please try another.")
        try:
            with st.spinner('Running sentiment analysis...'):
                response = requests.post(
                    'http://127.0.0.1:8000/predict',
                    json={'comments': comments},
                )

                if response.status_code == 400:
                    st.warning(response.json()["detail"])

                elif response.status_code != 200:
                    st.error(f"API request failed with status {response.status_code}: {response.text}")
                else:
                    result     = response.json()
                    roberta_pred = result["xlm-ROBERTa Predictions"]
                    vader_pred = result["VADER Predictions"]
                    roberta_score = get_score(roberta_pred)
                    vader_score = get_score(vader_pred)

                    delta = abs(roberta_score - vader_score)
                    if delta < 0.15:
                        st.success(
                            f"Strong agreement between models  \n"
                            f"Score delta: **{delta:.3f}** &nbsp;|&nbsp; "
                            f"RoBERTa: **{roberta_score:.3f}** &nbsp;|&nbsp; "
                            f"VADER: **{vader_score:.3f}**"
                        )
                    elif delta < 0.4:
                        st.warning(
                            f"Moderate divergence between models  \n"
                            f"Score delta: **{delta:.3f}** &nbsp;|&nbsp; "
                            f"RoBERTa: **{roberta_score:.3f}** &nbsp;|&nbsp; "
                            f"VADER: **{vader_score:.3f}**"
                        )
                    else:
                        st.error(
                            f"High divergence between models  \n"
                            f"Score delta: **{delta:.3f}** &nbsp;|&nbsp; "
                            f"RoBERTa: **{roberta_score:.3f}** &nbsp;|&nbsp; "
                            f"VADER: **{vader_score:.3f}**"
                        )

                    col1,col2 = st.columns(2,gap='large')

                    with col1:
                        st.header('XLM-RoBERTa',text_alignment="center",anchor=False)
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Total",    len(comments))
                        c2.metric("Positive", roberta_pred.count('Positive'))
                        c3.metric("Negative", roberta_pred.count('Negative'))
                        c4.metric("Neutral",  roberta_pred.count('Neutral'))
                        st.plotly_chart(make_gauge(roberta_score,'XLM-RoBERTa'))
                        
                    with col2:
                        st.header("VADER",text_alignment="center",anchor=False)
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Total",    len(comments))
                        c2.metric("Positive", vader_pred.count('Positive'))
                        c3.metric("Negative", vader_pred.count('Negative'))
                        c4.metric("Neutral",  vader_pred.count('Neutral'))
                        st.plotly_chart(make_gauge(vader_score,'VADER'))

                    

        except requests.RequestException as e:
            st.error(f"Could not reach the API server: {e}")
