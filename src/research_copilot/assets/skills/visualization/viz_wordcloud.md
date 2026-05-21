# Skill: Word Clouds for NLP & Text Corpora

## Purpose
Word clouds provide a quick visual representation of text data, where the size of each word indicates its frequency or statistical importance (e.g. TF-IDF weight).

## Installation
```bash
pip install wordcloud
```

## Protocol & Best Practices
1. **Pre-Process Text:** Remove stop words, punctuation, perform lemmatization or stemming, and lowercase all terms prior to rendering.
2. **Constrain Shape & Color:** Use a mask image (e.g. circle or rectangle) to keep word boundaries clean. Apply a custom color function to bind word colors to the Okabe-Ito palette instead of using random default colors.
3. **Use Frequency Maps:** Pass predefined keyword-frequency dictionaries (e.g. `generate_from_frequencies`) rather than feeding raw text directly to the renderer for fine-grained control.

## Code Template

```python
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import random

def color_func_okabe_ito(word, font_size, position, orientation, random_state=None, **kwargs):
    # Okabe-Ito colors excluding black/yellow for better contrast
    colors = ["#E69F00", "#56B4E9", "#009E73", "#0072B2", "#D55E00", "#CC79A7"]
    return random.choice(colors)

def generate_wordcloud(frequencies: dict, output_path: str):
    wordcloud = WordCloud(
        background_color="white",
        width=800,
        height=400,
        max_words=100,
        color_func=color_func_okabe_ito,
        prefer_horizontal=0.7
    ).generate_from_frequencies(frequencies)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(output_path, dpi=300)
    plt.close()
```
