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

def get_overall_sentiment(score):
    if score > 0.6:
        return "success", "↑ Overwhelmingly Positive"
    if score > 0.2:
        return "success", "↑ Mostly Positive"
    if score >= -0.2:
        return "warning", "→ Mixed Reactions"
    if score >= -0.6:
        return "error", "↓ Mostly Negative"
    return "error", "↓ Overwhelmingly Negative"

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

def get_percentage(comments,predictions):
    total = len(comments)
    pos = (predictions.count('Positive')/total )* 100
    neg = (predictions.count('Negative')/total )* 100
    neu = (predictions.count('Neutral')/total )* 100
    return pos, neg, neu

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

st.divider()

cards = st.empty()

with cards.container():


    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("""
        **🤖 This Project**
        
        500M+ Indians type in Hinglish — a mix of Hindi and English. Most sentiment tools were built for English and fail silently on code-mixed text. This tool was built specifically for it.
        """)

    with col2:
        st.success("""
        **🤖 XLM-RoBERTa**
        
        A multilingual transformer pre-trained on 100 languages. Fine-tuned on more that 3000 manually annotated Hinglish YouTube comments. Understands context, slang, and code-mixing.
        """)

    with col3:
        st.warning("""
        **🤖 VADER**
        
        A rule-based sentiment tool specifically attuned to sentiments expressed in social media. *English* social media. Fast, popular and effective, but fails to capture hinglish sentiment accurately.
        """)

if analyse_clicked:
    cards.empty()
    if not url.strip():
        st.error("Please enter a YouTube URL.")
        st.stop

    if "youtube.com" not in url and "youtu.be" not in url:
        st.error("Please enter a valid YouTube URL.")
        st.stop()
    
    with st.spinner("Fetching comments…"):
        vid, vid_title, comments = fetch_data(url)

    if not vid_title:
        st.error("Video not found! Double-check the URL and try again.")
        st.stop
    
    st.header(vid_title,anchor=False)
    st.divider()
    st.iframe(f"https://www.youtube.com/embed/{vid}", height=350, width="stretch")
    st.divider()

    if len(comments) == 0 :
        st.error("The video has no comments! Please try another.")
        st.stop
        
    try:
        with st.spinner('Running sentiment analysis...'):
            response = requests.post(
                'https://huggingface.co/spaces/shae2977/hinglish-sentiment-analyzer/predict',
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

                 #MODEL AGREEMENT
                roberta_score = get_score(roberta_pred)
                vader_score = get_score(vader_pred)
            
                delta = abs(roberta_score - vader_score)
                if delta < 0.2:
                    st.success(
                        f"↑ Strong agreement between models  \n"
                        f"Score delta: **{delta:.3f}** &nbsp;|&nbsp; "
                        f"RoBERTa: **{roberta_score:.3f}** &nbsp;|&nbsp; "
                        f"VADER: **{vader_score:.3f}**"
                    )
                elif delta < 0.4:
                    st.warning(
                        f"→ Moderate divergence between models  \n"
                        f"Score delta: **{delta:.3f}** &nbsp;|&nbsp; "
                        f"RoBERTa: **{roberta_score:.3f}** &nbsp;|&nbsp; "
                        f"VADER: **{vader_score:.3f}**"
                    )
                else:
                    st.error(
                        f"↓ High divergence between models  \n"
                        f"Score delta: **{delta:.3f}** &nbsp;|&nbsp; "
                        f"RoBERTa: **{roberta_score:.3f}** &nbsp;|&nbsp; "
                        f"VADER: **{vader_score:.3f}**"
                    )

                col1,col2 = st.columns(2,gap='large')

                with col1:
                    st.header('XLM-RoBERTa',text_alignment="center",anchor=False)

                    #MODEL REACTION
                    reaction_type, reaction_text = get_overall_sentiment(roberta_score)
                    getattr(st, reaction_type)(reaction_text)

                    pos, neg, neu = get_percentage(comments,roberta_pred)
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Total",    len(comments))
                    c2.metric("Positive", f"{pos :.0f}%")
                    c3.metric("Negative", f"{neg :.0f}%")
                    c4.metric("Neutral",  f"{neu :.0f}%")
                    
                    st.plotly_chart(make_gauge(roberta_score,'XLM-RoBERTa'))
                    
                with col2:
                    st.header("VADER",text_alignment="center",anchor=False)

                    #MODEL REACTION
                    reaction_type, reaction_text = get_overall_sentiment(vader_score)
                    getattr(st, reaction_type)(reaction_text)
                    pos, neg, neu = get_percentage(comments,vader_pred)
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Total Comments",    len(comments))
                    c2.metric("Positive", f"{pos :.0f}%")
                    c3.metric("Negative", f"{neg :.0f}%")
                    c4.metric("Neutral",  f"{neu :.0f}%")
                    st.plotly_chart(make_gauge(vader_score,'VADER'))

                if delta>0:
                    df_results = pd.DataFrame({
                    'Comment': comments,
                    'XLM-RoBERTa': roberta_pred,
                    'VADER': vader_pred })
                    
                    disagreements = df_results[df_results['XLM-RoBERTa'] != df_results['VADER']]
                    
                    st.header("Where The Models Disagree",anchor=None,text_alignment='center')
                    st.dataframe(disagreements.sample(min(10, len(disagreements))), use_container_width=True,hide_index=True)

    except requests.RequestException as e:
        st.error(f"Could not reach the API server: {e}")
