# AIArcana

<div align="center">
  <img src="./Logo.png" alt="AIArcana Logo" width="200" />
  <h3>The First Fair-Launch AI Tarot Divination Platform in the Solana Ecosystem</h3>
  <p>
    <a href="https://www.aiarcana.lat" target="_blank">Official Website</a> •
    <a href="https://x.com/AIArcanaSol" target="_blank">Twitter</a>
  </p>
</div>

## 📜 Overview

AIArcana represents a groundbreaking fusion of ancient mystical wisdom and cutting-edge technology. By integrating advanced artificial intelligence with Solana's high-performance blockchain, we've created a transparent, decentralized, and community-driven divination platform that delivers personalized insights with verifiable results.

Our platform employs Switchboard VRF (Verifiable Random Function) to ensure tamper-proof card draws, while our advanced AI interpretation engine leverages sentiment analysis and a comprehensive tarot knowledge graph to deliver nuanced, culturally-adapted readings.

## 🔮 Key Features

- **AI-Powered Tarot Readings**: Advanced NLP models (LLaMA 3 or Mistral-based) with sentiment analysis
- **Blockchain Verification**: Tamper-proof card draws secured by Switchboard VRF
- **Fair-Launch $ARC Token**: 100% community-controlled with no presale or team allocations
- **Multilingual Support**: Culturally-adapted readings in multiple languages
- **Decentralized Governance**: Community-driven platform development via Snapshot voting

## 🛠 Architecture & Technical Implementation

### Blockchain Component

Our Solana program uses Anchor framework to ensure secure, transparent card draws:

```rust
pub fn draw_cards(
    ctx: Context<DrawCards>,
    user_question: String,
    num_cards: u8,
    vrf_result: [u8; 32],
) -> Result<()> {
    // Validate input
    require!(num_cards > 0 && num_cards <= 10, ErrorCode::InvalidCardCount);
    require!(!user_question.is_empty(), ErrorCode::EmptyQuestion);
    
    // Generate cards using VRF result for true randomness
    let mut cards = Vec::new();
    for i in 0..num_cards {
        // Use VRF bytes to generate card ID (0-77) and orientation (0-1)
        let card_index = (vrf_result[i as usize % 32] as u8) % 78;
        let orientation = (vrf_result[(i as usize + 8) % 32] as u8) % 2;
        
        cards.push(CardData {
            card_id: card_index,
            is_reversed: orientation == 1,
        });
    }
    
    // Record reading on-chain for transparency
    reading.cards = cards;
    reading.ipfs_hash = None; // Updated later with AI interpretation
    
    // Emit event for indexers
    emit!(CardDrawEvent {
        user: ctx.accounts.user.key(),
        reading_id: reading.key(),
        timestamp,
        num_cards,
    });
    
    Ok(())
}
```

### AI Interpretation Engine

Our AI engine combines a tarot knowledge graph with advanced language models:

```python
def interpret(
    self, 
    question: str, 
    cards: List[Dict[str, Union[int, bool]]], 
    spread: str = "three_card",
    max_length: int = 1500
) -> Dict:
    # Analyze question sentiment
    sentiment = self.sentiment_analyzer.analyze(question)
    
    # Get spread information
    spread_info = self.knowledge_graph.get_spread_info(spread)
    
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
    
    # Generate personalized interpretation using advanced LLM
    interpretation = self._generate_interpretation(question, sentiment, spread_info, card_details)
    
    return {
        "question": question,
        "cards": card_details,
        "spread": spread_info["name"],
        "sentiment": sentiment,
        "interpretation": interpretation
    }
```

### System Architecture

Our platform integrates multiple components through a secure, scalable architecture:

```
┌───────────────┐     ┌─────────────────┐     ┌──────────────────┐
│ React.js SPA  │◄───►│ Express.js API  │◄───►│ Solana Blockchain│
└───────┬───────┘     └────────┬────────┘     └──────────────────┘
        │                      │
        │                      ▼
┌───────▼───────┐     ┌────────────────┐     ┌──────────────────┐
│ Wallet Adapter │     │ AI Model API   │◄───►│ Tarot Knowledge  │
└───────────────┘     │ (LLaMA/Mistral) │     │ Graph            │
                      └────────┬────────┘     └──────────────────┘
                               │
                      ┌────────▼────────┐
                      │ IPFS Storage    │
                      │ for Readings    │
                      └─────────────────┘
```

## 🚀 Getting Started

### Prerequisites

- Node.js 20+
- Rust and Solana CLI
- Anchor Framework
- Python 3.9+ (for AI models)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-organization/aiarcana.git
cd aiarcana

# Install dependencies
npm install

# Setup Solana development environment
solana-keygen new -o id.json
solana config set --keypair ./id.json
solana config set --url localhost

# Start local Solana validator
solana-test-validator

# Deploy smart contracts
cd blockchain
anchor build
anchor deploy

# Start frontend development server
cd ../app
npm run dev
```

## 🌟 Core Technology Stack

- **Frontend**: React.js, Next.js, Solana Wallet Adapter, WebSocket
- **Backend**: Node.js, Express, MongoDB, Redis
- **Blockchain**: Solana (Rust/Anchor framework), Switchboard VRF
- **AI**: LLaMA 3 or Mistral-based models, Sentiment Analysis
- **Storage**: IPFS for divination records
- **Infrastructure**: QuickNode, Cloudflare CDN

## 🛣️ Roadmap

- **2025 Q2**: MVP Development
- **2025 Q3**: Testnet Launch
- **2025 Q4**: Mainnet Deployment & Fair Token Launch
- **2026 Q1-Q4**: Community Expansion & Mobile App

## 💎 Tokenomics

The $ARC token is designed as a 100% fair launch with:
- Total Supply: 1 billion $ARC
- No presale, no team allocation, no VC distribution
- 50% of divination fees used for buy-back and burn

## 📄 License

This project is licensed under the MIT License. 
