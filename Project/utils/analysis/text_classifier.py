from transformers import pipeline, Pipeline, AutoTokenizer
import ollama


class TextClassifier:
    """A class that handles text-classification models"""

    def __init__(self):
        self.bias_pipeline: Pipeline | None = None
        self.leaning_pipeline: Pipeline | None = None
        self.is_political_pipeline: Pipeline | None = None
        self.sentiment_pipeline: Pipeline | None = None
        self.emotion_pipeline: Pipeline | None = None
        self.system_prompt: str | None = None

    def get_political_bias(self, texts: list[str]) -> list[str | None]:
        """Returns 'RIGHT', 'LEFT' or 'CENTER' """
        if not self.bias_pipeline:
            self.bias_pipeline = pipeline(
                "text-classification",
                model="bucketresearch/politicalBiasBERT",
                tokenizer="bert-base-cased"
            )

        try:
            results = self.bias_pipeline(texts, batch_size=16, truncation=True)
        except Exception as e:
            print(e)
            return [None] * len(texts)

        labels = []
        for result in results:
            labels.append(result.get("label", None))
        return labels

    def get_political_leaning(self, texts: list[str]) -> list[str | None]:
        """Returns 'RIGHT', 'LEFT' or 'CENTER' """
        if not self.leaning_pipeline:
            tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-v3-large", use_fast=True)

            self.leaning_pipeline = pipeline(
                "text-classification",
                model="matous-volf/political-leaning-deberta-large",
                tokenizer=tokenizer,
            )

        try:
            results = self.leaning_pipeline(texts, batch_size=16, truncation=True)
        except Exception as e:
            print(e)
            return [None] * len(texts)

        labels = []
        for result in results:
            leaning = result.get('label', None)
            match leaning:
                case "LABEL_0":
                    labels.append("LEFT")
                case "LABEL_2":
                    labels.append("RIGHT")
                case "LABEL_1":
                    labels.append("CENTER")
                case _:
                    labels.append(None)
        return labels

    def is_political(self, texts: list[str]) -> list[bool | None]:
        if not self.is_political_pipeline:
            self.is_political_pipeline = pipeline(
                "text-classification",
                model="mlburnham/Political_DEBATE_large_v1.0",
            )

        hypothesis = "This sentence is about politics."

        texts = [f"{text} </s> {hypothesis}" for text in texts]

        try:
            results = self.is_political_pipeline(texts, batch_size=16, truncation=True)
        except Exception as e:
            print(e)
            return [None] * len(texts)

        labels = []
        for result in results:
            label = result.get("label", None)
            labels.append(label == "entailment" if label else None)
        return labels

    def get_sentiment(self, texts: list[str]) -> list[str | None]:
        """Returns 'Positive', 'Negative' or 'Neutral' """
        if not self.sentiment_pipeline:
            self.sentiment_pipeline = pipeline(
                "text-classification",
                model="cardiffnlp/xlm-twitter-politics-sentiment",
            )

        try:
            results = self.sentiment_pipeline(texts, batch_size=16, truncation=True)
        except Exception as e:
            print(e)
            return [None] * len(texts)

        labels = []
        for result in results:
            labels.append(result.get("label", None))
        return labels

    def get_emotion(self, texts: list[str]) -> list[str | None]:
        """Returns one between "", anger, anticipation, disgust, fear, joy, love, optimism, pessimism, sadness, surprise, trust"""
        if not self.emotion_pipeline:
            self.emotion_pipeline = pipeline(
                "text-classification",
                model="cardiffnlp/twitter-roberta-base-emotion-multilabel-latest",
            )

        try:
            results = self.emotion_pipeline(texts, batch_size=16, truncation=True)
        except Exception as e:
            print(e)
            return [None] * len(texts)

        labels = []
        for result in results:
            labels.append(result.get("label", None))
        return labels

    def get_llm_political_stance(self, candidates: list[str], texts: list[str]) -> list[str]:
        """Returns 'Republican', 'Democratic' or 'Neutral' """
        if not self.system_prompt:
            with open("../prompts/political_stance_yt.txt", "r", encoding="utf-8") as f:
                self.system_prompt = f.read()

        labels = []
        for i in range(len(candidates)):
            candidate = candidates[i]
            text = texts[i]

            text = text.replace("'", "")
            json = '{"candidate": ' + candidate + ', "comment": "' + text + '"}'

            response = ollama.chat(
                model="gemma3:4b",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": json},
                ],
            )

            result = response['message']['content'].strip()
            if result in ["Democratic", "Republican", "Neutral"]:
                labels.append(result)
            else:
                labels.append(None)

        return labels
