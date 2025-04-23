import os
import json
import torch
import numpy as np
from typing import List, Dict, Tuple, Union, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from transformers import TextClassificationPipeline

class TarotKnowledgeGraph:
    """Knowledge graph for tarot cards and their meanings"""
    
    def __init__(self, data_path: str = "../data/tarot_knowledge.json"):
        """Initialize the tarot knowledge graph
        
        Args:
            data_path: Path to the tarot knowledge JSON file
        """
        self.cards = {}
        self.load_knowledge(data_path)
    
    def load_knowledge(self, data_path: str) -> None:
        """Load tarot knowledge from JSON file
        
        Args:
            data_path: Path to the tarot knowledge JSON file
        """
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.cards = data.get('cards', {})
                self.spreads = data.get('spreads', {})
        except FileNotFoundError:
            print(f"Warning: Tarot knowledge file not found at {data_path}. Using default knowledge.")
            self._init_default_knowledge()
    
    def _init_default_knowledge(self) -> None:
        """Initialize default knowledge in case the JSON file is not found"""
        # Basic major arcana cards as default
        self.cards = {
            "0": {
                "name": "The Fool",
                "upright": "Beginnings, innocence, spontaneity, a free spirit",
                "reversed": "Holding back, recklessness, risk-taking, uncertainty"
            },
            "1": {
                "name": "The Magician",
                "upright": "Manifestation, resourcefulness, power, inspired action",
                "reversed": "Manipulation, poor planning, untapped talents"
            },
            # More cards would be defined here
        }
        
        # Basic spreads
        self.spreads = {
            "three_card": {
                "name": "Three Card Spread",
                "positions": ["Past", "Present", "Future"]
            },
            "celtic_cross": {
                "name": "Celtic Cross",
                "positions": ["Present", "Challenge", "Past", "Future", "Above", "Below", 
                              "Advice", "External Influence", "Hopes/Fears", "Outcome"]
            }
        }
    
    def get_card_info(self, card_id: int, is_reversed: bool) -> Dict:
        """Get card information based on ID and orientation
        
        Args:
            card_id: The ID of the card (0-77)
            is_reversed: Whether the card is in reversed position
            
        Returns:
            Dictionary with card information
        """
        card_key = str(card_id)
        if card_key not in self.cards:
            return {"error": f"Card ID {card_id} not found"}
        
        card_info = self.cards[card_key].copy()
        card_info["orientation"] = "reversed" if is_reversed else "upright"
        card_info["meaning"] = card_info["reversed"] if is_reversed else card_info["upright"]
        
        return card_info
    
    def get_spread_info(self, spread_name: str) -> Dict:
        """Get spread information by name
        
        Args:
            spread_name: Name of the spread
            
        Returns:
            Dictionary with spread information
        """
        if spread_name not in self.spreads:
            return {"error": f"Spread {spread_name} not found"}
        
        return self.spreads[spread_name]


class SentimentAnalyzer:
    """Analyze sentiment of user questions to adapt interpretation tone"""
    
    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        """Initialize sentiment analyzer
        
        Args:
            model_name: The pre-trained model to use for sentiment analysis
        """
        self.pipeline = pipeline(
            "sentiment-analysis",
            model=model_name,
            tokenizer=model_name
        )
    
    def analyze(self, text: str) -> Dict:
        """Analyze the sentiment of a given text
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary with sentiment information (positive/negative and confidence)
        """
        result = self.pipeline(text)[0]
        
        # Map sentiment to emotional state
        emotional_state = {
            "POSITIVE": ["hopeful", "optimistic", "excited"],
            "NEGATIVE": ["concerned", "anxious", "worried"] 
        }
        
        emotion = np.random.choice(emotional_state.get(result["label"], ["neutral"]))
        
        return {
            "sentiment": result["label"].lower(),
            "confidence": result["score"],
            "emotion": emotion
        }


class TarotInterpreter:
    """AI-powered tarot card interpretation engine"""
    
    def __init__(
        self, 
        model_name: str = "meta-llama/Llama-3-8b-chat-hf",
        knowledge_path: str = "../data/tarot_knowledge.json",
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        """Initialize the tarot interpreter
        
        Args:
            model_name: The pre-trained language model to use
            knowledge_path: Path to tarot knowledge data
            device: Device to run the model on (cuda/cpu)
        """
        self.device = device
        self.knowledge_graph = TarotKnowledgeGraph(knowledge_path)
        self.sentiment_analyzer = SentimentAnalyzer()
        
        print(f"Loading model {model_name} on {device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto"
        )
        
        # System prompt template
        self.system_prompt = """You are an expert tarot reader with deep knowledge of symbolism and psychology.
        Your interpretations are insightful, nuanced, and respectful of the querent's circumstances.
        Based on the cards drawn and their positions, provide a detailed interpretation that is helpful and clear.
        """
    
    def interpret(
        self, 
        question: str, 
        cards: List[Dict[str, Union[int, bool]]], 
        spread: str = "three_card",
        max_length: int = 1500
    ) -> Dict:
        """Generate an interpretation for a tarot reading
        
        Args:
            question: The user's question
            cards: List of card data (each with card_id and is_reversed)
            spread: The spread type to use
            max_length: Maximum length of the generated interpretation
            
        Returns:
            Dictionary containing the interpretation
        """
        # Analyze question sentiment
        sentiment = self.sentiment_analyzer.analyze(question)
        
        # Get spread information
        spread_info = self.knowledge_graph.get_spread_info(spread)
        if "error" in spread_info:
            spread_info = {"name": "Basic Reading", "positions": ["Card"]}
        
        # Limit cards to the number of positions in the spread
        num_positions = len(spread_info["positions"])
        cards = cards[:num_positions]
        
        # Build card information
        card_details = []
        for i, card in enumerate(cards):
            position = spread_info["positions"][i % num_positions]
            card_info = self.knowledge_graph.get_card_info(card["card_id"], card["is_reversed"])
            card_details.append({
                "position": position,
                "name": card_info.get("name", f"Unknown Card {card['card_id']}"),
                "orientation": card_info.get("orientation", "upright"),
                "meaning": card_info.get("meaning", "No meaning available")
            })
        
        # Build prompt for language model
        prompt = f"{self.system_prompt}\n\n"
        prompt += f"Question: {question}\n"
        prompt += f"Querent's emotional state: {sentiment['emotion']}\n\n"
        prompt += f"Spread: {spread_info['name']}\n\n"
        
        for card in card_details:
            prompt += f"{card['position']}: {card['name']} ({card['orientation']})\n"
        
        prompt += "\nProvide a detailed tarot interpretation:"
        
        # Generate interpretation
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        interpretation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        interpretation = interpretation.replace(prompt, "").strip()
        
        return {
            "question": question,
            "cards": card_details,
            "spread": spread_info["name"],
            "sentiment": sentiment,
            "interpretation": interpretation
        }


if __name__ == "__main__":
    # Example usage
    interpreter = TarotInterpreter()
    
    # Example reading
    question = "What does my career path look like for the next six months?"
    cards = [
        {"card_id": 0, "is_reversed": False},  # The Fool
        {"card_id": 1, "is_reversed": False},  # The Magician
        {"card_id": 7, "is_reversed": True},   # The Chariot (reversed)
    ]
    
    result = interpreter.interpret(question, cards, spread="three_card")
    print(f"Question: {result['question']}")
    print("\nCards:")
    for card in result["cards"]:
        print(f"  - {card['position']}: {card['name']} ({card['orientation']})")
    
    print("\nInterpretation:")
    print(result["interpretation"]) 