use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer};
use switchboard_v2::AggregatorAccountData;

declare_id!("ArcnaXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX");

#[program]
pub mod aiarcana {
    use super::*;

    // Draw tarot cards using Switchboard VRF for fair, tamper-proof random card generation
    pub fn draw_cards(
        ctx: Context<DrawCards>,
        user_question: String,
        num_cards: u8,
        vrf_result: [u8; 32],
    ) -> Result<()> {
        let clock = Clock::get()?;
        let timestamp = clock.unix_timestamp;
        
        // Validate input
        require!(num_cards > 0 && num_cards <= 10, ErrorCode::InvalidCardCount);
        require!(!user_question.is_empty(), ErrorCode::EmptyQuestion);
        
        // Create reading record
        let reading = &mut ctx.accounts.reading;
        reading.owner = ctx.accounts.user.key();
        reading.timestamp = timestamp;
        reading.question = user_question;
        reading.num_cards = num_cards;
        
        // Generate cards using VRF result
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
        
        reading.cards = cards;
        reading.ipfs_hash = None; // Will be updated later with AI interpretation
        
        // Emit card draw event
        emit!(CardDrawEvent {
            user: ctx.accounts.user.key(),
            reading_id: reading.key(),
            timestamp,
            num_cards,
        });
        
        Ok(())
    }
    
    // Store IPFS hash of the AI-generated interpretation
    pub fn store_interpretation(
        ctx: Context<StoreInterpretation>,
        ipfs_hash: String,
    ) -> Result<()> {
        let reading = &mut ctx.accounts.reading;
        
        // Only the reading owner can store the interpretation
        require!(reading.owner == ctx.accounts.user.key(), ErrorCode::Unauthorized);
        
        // Store IPFS hash
        reading.ipfs_hash = Some(ipfs_hash);
        
        emit!(InterpretationStoredEvent {
            user: ctx.accounts.user.key(),
            reading_id: reading.key(),
            timestamp: Clock::get()?.unix_timestamp,
        });
        
        Ok(())
    }
    
    // Pay for premium divination using $ARC tokens
    pub fn pay_for_divination(
        ctx: Context<PayForDivination>,
        amount: u64,
    ) -> Result<()> {
        // Transfer tokens from user to treasury
        let transfer_instruction = Transfer {
            from: ctx.accounts.user_token_account.to_account_info(),
            to: ctx.accounts.treasury_token_account.to_account_info(),
            authority: ctx.accounts.user.to_account_info(),
        };
        
        let cpi_ctx = CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            transfer_instruction,
        );
        
        token::transfer(cpi_ctx, amount)?;
        
        // Store payment record
        let payment = &mut ctx.accounts.payment;
        payment.user = ctx.accounts.user.key();
        payment.amount = amount;
        payment.timestamp = Clock::get()?.unix_timestamp;
        
        emit!(PaymentEvent {
            user: ctx.accounts.user.key(),
            amount,
            timestamp: payment.timestamp,
        });
        
        Ok(())
    }
}

#[derive(Accounts)]
pub struct DrawCards<'info> {
    #[account(mut)]
    pub user: Signer<'info>,
    
    #[account(
        init,
        payer = user,
        space = 8 + 32 + 8 + 256 + 1 + (33 * 10) + 100
    )]
    pub reading: Account<'info, TarotReading>,
    
    // Verify VRF result using Switchboard
    pub vrf_account: AccountInfo<'info>,
    
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct StoreInterpretation<'info> {
    #[account(mut)]
    pub user: Signer<'info>,
    
    #[account(mut)]
    pub reading: Account<'info, TarotReading>,
}

#[derive(Accounts)]
pub struct PayForDivination<'info> {
    #[account(mut)]
    pub user: Signer<'info>,
    
    #[account(
        mut,
        constraint = user_token_account.owner == user.key(),
        constraint = user_token_account.mint == treasury_token_account.mint
    )]
    pub user_token_account: Account<'info, TokenAccount>,
    
    #[account(mut)]
    pub treasury_token_account: Account<'info, TokenAccount>,
    
    #[account(
        init,
        payer = user,
        space = 8 + 32 + 8 + 8
    )]
    pub payment: Account<'info, PaymentRecord>,
    
    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

#[account]
pub struct TarotReading {
    pub owner: Pubkey,
    pub timestamp: i64,
    pub question: String,
    pub num_cards: u8,
    pub cards: Vec<CardData>,
    pub ipfs_hash: Option<String>,
}

#[account]
pub struct PaymentRecord {
    pub user: Pubkey,
    pub amount: u64,
    pub timestamp: i64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct CardData {
    pub card_id: u8,      // 0-77 (78 tarot cards)
    pub is_reversed: bool, // false=upright, true=reversed
}

#[event]
pub struct CardDrawEvent {
    pub user: Pubkey,
    pub reading_id: Pubkey,
    pub timestamp: i64,
    pub num_cards: u8,
}

#[event]
pub struct InterpretationStoredEvent {
    pub user: Pubkey,
    pub reading_id: Pubkey,
    pub timestamp: i64,
}

#[event]
pub struct PaymentEvent {
    pub user: Pubkey,
    pub amount: u64,
    pub timestamp: i64,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Number of cards must be between 1 and 10")]
    InvalidCardCount,
    #[msg("Question cannot be empty")]
    EmptyQuestion,
    #[msg("Unauthorized access")]
    Unauthorized,
} 