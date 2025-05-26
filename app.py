from flask import Flask, render_template, request
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator  # Install with `pip install deep_translator`

# Load spaCy model
nlp = spacy.load("en_core_web_sm")
vader = SentimentIntensityAnalyzer()

def translate_text(text):
    """Detects language and translates to English using GoogleTranslator."""
    try:
        translated_text = GoogleTranslator(source='auto', target='en').translate(text)
        return translated_text if translated_text else text  # Fallback to original if translation fails
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Fallback to original text

def analyze_sentiment(sentence):
    """Translates text and applies sentiment analysis."""
    translated_sentence = translate_text(sentence)  # Convert non-English text to English
    if not translated_sentence:  # Handle empty translations
        return "Neutral", "😐", "#2196F3"

    doc = nlp(translated_sentence)
    sentiment_score = vader.polarity_scores(translated_sentence)["compound"]

    negation_words = {"not", "never", "no"}
    negated = any(token.text in negation_words for token in doc)

    if sentiment_score > 0.2:
        sentiment = "Positive" if not negated else "Negative"
        emoji = "😊" if not negated else "😢"
        color = "#4CAF50" if not negated else "#F44336"
    elif sentiment_score < -0.2:
        sentiment = "Negative" if not negated else "Positive"
        emoji = "😢" if not negated else "😊"
        color = "#F44336" if not negated else "#4CAF50"
    else:
        sentiment = "Neutral"
        emoji = "😐"
        color = "#2196F3"

    return sentiment, emoji, color

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
    chart_path, bar_chart_path = None, None

    if request.method == "POST":
        text = request.form.get("text", "").strip()  # Prevent missing input error
        sentences = [s.strip() for s in text.splitlines() if s.strip()]

        for sentence in sentences:
            sentiment, emoji, color = analyze_sentiment(sentence)
            sentiment_counts[sentiment] += 1
            results.append({"sentence": sentence, "sentiment": sentiment, "emoji": emoji, "color": color})

        static_dir = "static"
        os.makedirs(static_dir, exist_ok=True)

        labels, sizes = list(sentiment_counts.keys()), list(sentiment_counts.values())
        colors = ["#4CAF50", "#F44336", "#2196F3"]

        if sum(sizes) > 0:
            # Pie Chart
            plt.figure(figsize=(6, 6))
            plt.pie(sizes, labels=labels, colors=colors,
                    autopct=lambda p: f'{p:.1f}% ({int(p * sum(sizes) / 100)})', startangle=90)
            plt.axis("equal")
            chart_path = "static/pie_chart.png"
            plt.savefig(chart_path)
            plt.close()

            # Bar Chart
            plt.figure(figsize=(6, 4))
            bars = plt.bar(labels, sizes, color=colors)
            plt.title("Sentiment Counts")
            plt.xlabel("Sentiment")
            plt.ylabel("Number of Sentences")
            plt.grid(axis='y', linestyle='--', alpha=0.7)

            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, yval + 0.2, int(yval), ha='center', va='bottom')

            bar_chart_path = "static/bar_chart.png"
            plt.tight_layout()
            plt.savefig(bar_chart_path)
            plt.close()

    return render_template("index.html", results=results, chart_path=chart_path, bar_chart_path=bar_chart_path)

@app.route("/charts")
def charts():
    chart_path = "pie_chart.png"
    bar_chart_path = "bar_chart.png"
    
    # Render the charts page with the images
    return render_template("charts.html", chart_path=chart_path, bar_chart_path=bar_chart_path)
if __name__ == "__main__":
    app.run(debug=True)