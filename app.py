from flask import Flask, render_template, request, redirect, url_for
from textblob import TextBlob
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for charts
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}  # Initialize sentiment counters
    chart_path = None  # Initialize the pie chart path
    bar_chart_path = None  # Initialize the bar chart path
    
    if request.method == "POST":
        text = request.form["text"]
        sentences = [s.strip() for s in text.splitlines() if s.strip()]  # Split on newlines
        
        # Analyze each sentence
        for sentence in sentences:
            analysis = TextBlob(sentence).sentiment.polarity
            if analysis > 0:
                sentiment = "Positive"
                color = "#4CAF50"  # Green
                sentiment_counts["Positive"] += 1
            elif analysis < 0:
                sentiment = "Negative"
                color = "#F44336"  # Red
                sentiment_counts["Negative"] += 1
            else:
                sentiment = "Neutral"
                color = "#2196F3"  # Blue
                sentiment_counts["Neutral"] += 1
            results.append({"sentence": sentence, "sentiment": sentiment, "color": color})
        
        # Create static directory if it doesn't exist
        static_dir = "static"
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        
        # Generate pie chart
        labels = list(sentiment_counts.keys())
        sizes = list(sentiment_counts.values())
        colors = ["#4CAF50", "#F44336", "#2196F3"]  # Matching CSS colors
        
        if sum(sizes) > 0:  # Ensure there is at least one non-zero value
            plt.figure(figsize=(6, 6))
            plt.pie(
                sizes,
                labels=labels,
                colors=colors,
                autopct=lambda p: f'{p:.1f}% ({int(p * sum(sizes) / 100)})',  # Show percentages and counts
                startangle=90
            )
            plt.axis("equal")  # Ensure the pie chart is a perfect circle
            chart_path = "pie_chart.png"  # Directly use the image filename
            plt.savefig(os.path.join(static_dir, chart_path))
            plt.close()

            # Generate bar chart
            plt.figure(figsize=(6, 4))
            bars = plt.bar(labels, sizes, color=colors)
            plt.title("Sentiment Counts")
            plt.xlabel("Sentiment")
            plt.ylabel("Number of Sentences")
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Annotate with numbers on top of bars
            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, yval + 0.2, int(yval), ha='center', va='bottom')
            
            bar_chart_path = "bar_chart.png"  # Directly use the image filename
            plt.tight_layout()
            plt.savefig(os.path.join(static_dir, bar_chart_path))
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
