#!/usr/bin/env python3
"""Check current USD/CHF prices and validate trade levels."""

import sys
sys.path.append('src')

from oanda_trader import OANDATrader
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Your OANDA credentials
    api_key = "fe92315bee29b117825fed529cf3fa99-173e927b8cdbb1fc244993e24e33fd93"
    account_id = "101-004-31788297-001"
    
    trader = OANDATrader(api_key, account_id, environment="practice")
    
    # Get current USD/CHF prices
    instrument = "USD_CHF"
    prices = trader.get_bid_ask_prices(instrument)
    
    if prices:
        logger.info(f"Current {instrument} prices:")
        logger.info(f"  Bid: {prices['bid']:.5f}")
        logger.info(f"  Ask: {prices['ask']:.5f}")
        logger.info(f"  Mid: {prices['mid']:.5f}")
        logger.info(f"  Spread: {prices['spread_pips']:.1f} pips")
        
        # Check the trade levels from the error
        sell_entry = 0.80683
        sell_tp = 0.79683
        sell_sl = 0.81183
        
        logger.info(f"\nAnalyzing SELL trade:")
        logger.info(f"  Entry: {sell_entry:.5f}")
        logger.info(f"  Target: {sell_tp:.5f}")
        logger.info(f"  Stop Loss: {sell_sl:.5f}")
        
        # For SELL, we enter at BID
        current_bid = prices['bid']
        current_ask = prices['ask']
        
        logger.info(f"\nValidation (SELL order):")
        logger.info(f"  Current BID: {current_bid:.5f} (where we enter)")
        logger.info(f"  Current ASK: {current_ask:.5f}")
        
        # Check if TP is valid (must be below current BID for SELL)
        if sell_tp >= current_bid:
            logger.error(f"  ❌ TP {sell_tp:.5f} is >= BID {current_bid:.5f} - Would be immediate loss!")
        else:
            logger.info(f"  ✅ TP {sell_tp:.5f} is below BID {current_bid:.5f} - Valid")
            
        # Check if SL is valid (must be above current ASK for SELL)
        if sell_sl <= current_ask:
            logger.error(f"  ❌ SL {sell_sl:.5f} is <= ASK {current_ask:.5f} - Invalid!")
        else:
            logger.info(f"  ✅ SL {sell_sl:.5f} is above ASK {current_ask:.5f} - Valid")
            
        # Calculate distances
        pip_size = 0.0001
        tp_distance = abs(current_bid - sell_tp) / pip_size
        sl_distance = abs(sell_sl - current_bid) / pip_size
        
        logger.info(f"\nPip distances from current BID:")
        logger.info(f"  TP distance: {tp_distance:.1f} pips")
        logger.info(f"  SL distance: {sl_distance:.1f} pips")
        
        # Check minimum requirements
        min_sl = 80  # CHF pairs need 80+ pips
        min_tp = 120  # CHF pairs need 120+ pips
        
        logger.info(f"\nMinimum requirements for USD/CHF:")
        logger.info(f"  Min SL: {min_sl} pips - Current: {sl_distance:.1f} {'✅ OK' if sl_distance >= min_sl else '❌ TOO CLOSE'}")
        logger.info(f"  Min TP: {min_tp} pips - Current: {tp_distance:.1f} {'✅ OK' if tp_distance >= min_tp else '❌ TOO CLOSE'}")
        
    else:
        logger.error("Could not get current prices")

if __name__ == "__main__":
    main() 