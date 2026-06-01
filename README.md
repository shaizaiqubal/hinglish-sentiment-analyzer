---
title: Hinglish Sentiment Analyzer API
emoji: 🎬
colorFrom: pink
colorTo: purple
sdk: docker
app_port: 7860
---
# Hinglish Sentiment Analyzer API

FastAPI backend serving a fine-tuned XLM-RoBERTa model for sentiment analysis of Hinglish text
## Endpoints

- `GET /` — health check
- `POST /predict` — accepts a batch of comments, returns XLM-RoBERTa and VADER predictions side by side

## Model

Fine-tuned on a self-annotated dataset of 3,000+ Hinglish YouTube comments. Achieves weighted F1 of 0.67 vs VADER's 0.39 on the same test set.

[Model on HuggingFace](https://huggingface.co/shae2977/xlm-roberta-hinglish-sentiment-analysis) | [Dataset on HuggingFace](https://huggingface.co/datasets/shae2977/hinglish-youtube-sentiment-dataset)