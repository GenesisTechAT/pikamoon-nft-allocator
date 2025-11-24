#!/usr/bin/env python3
"""
Pikamoon NFT Allocator
Randomly assigns NFT assets to eligible wallets based on their ORBIO token holdings.
Uses a deterministic seed for transparency and community verification.
"""

import json
import os
import random
import sys
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict


@dataclass
class NFT:
    """Represents an NFT with its asset address and rarity."""
    asset: str
    rarity: str


@dataclass
class WalletAllocation:
    """Represents the allocation for a wallet."""
    wallet: str
    nfts: List[Dict[str, any]]
    total_nfts: int


class NFTAllocator:
    """Handles the random allocation of NFTs to eligible wallets."""
    
    def __init__(self, seed: str):
        """
        Initialize the allocator with a seed for reproducibility.
        
        Args:
            seed: String seed for random number generation
        """
        self.seed = seed
        random.seed(seed)
        
    def generate_nft_pool(self, nft_assets: List[Tuple[str, str]], rarity_percentages: Dict[str, float] = None) -> List[NFT]:
        """
        Generate a pool of NFTs with assigned rarities.
        
        If rarities are pre-assigned in nft_assets, use them directly.
        Otherwise, assign rarities based on percentages.
        
        Args:
            nft_assets: List of tuples (asset_address, rarity) where rarity can be None
            rarity_percentages: Optional dict with rarity names and their percentages (only used if rarities not pre-assigned)
            
        Returns:
            List of NFT objects with asset addresses and rarities
        """
        total_nfts = len(nft_assets)
        nft_pool = []
        
        # Check if rarities are already assigned
        pre_assigned_rarities = [rarity for _, rarity in nft_assets if rarity is not None]
        
        if len(pre_assigned_rarities) == total_nfts:
            # All rarities are pre-assigned - use them directly
            print(f"\n🎨 Using pre-assigned rarities from assets file")
            
            # Count rarities
            rarity_counts = {}
            for _, rarity in nft_assets:
                rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
            
            print(f"\n🎨 NFT Rarity Distribution:")
            for rarity, count in sorted(rarity_counts.items()):
                actual_percentage = (count / total_nfts) * 100
                print(f"  {rarity}: {count} NFTs ({actual_percentage:.2f}%)")
            
            # Create NFT objects with pre-assigned rarities
            for asset, rarity in nft_assets:
                nft_pool.append(NFT(asset=asset, rarity=rarity))
            
            # Shuffle the pool to randomize allocation order (but keep rarities)
            random.shuffle(nft_pool)
            
        else:
            # Need to assign rarities based on percentages
            if not rarity_percentages:
                print(f"\n❌ Error: No rarities pre-assigned and no rarity_percentages provided in config!")
                sys.exit(1)
            
            print(f"\n🎨 Assigning rarities based on percentages")
            
            # Extract just the asset addresses
            asset_addresses = [asset for asset, _ in nft_assets]
            
            # Calculate how many NFTs of each rarity
            rarity_counts = {}
            remaining_nfts = total_nfts
            
            # Sort rarities to ensure consistent ordering
            sorted_rarities = sorted(rarity_percentages.items())
            
            for i, (rarity, percentage) in enumerate(sorted_rarities):
                # For the last rarity, assign all remaining NFTs to avoid rounding errors
                if i == len(sorted_rarities) - 1:
                    count = remaining_nfts
                else:
                    count = int(total_nfts * percentage / 100)
                    remaining_nfts -= count
                
                rarity_counts[rarity] = count
                
            print(f"\n🎨 NFT Rarity Distribution:")
            for rarity, count in sorted(rarity_counts.items()):
                actual_percentage = (count / total_nfts) * 100
                print(f"  {rarity}: {count} NFTs ({actual_percentage:.2f}%)")
            
            # Create a list of (asset, rarity) pairs
            asset_rarity_pairs = []
            asset_index = 0
            
            # Assign rarities to assets based on percentages
            for rarity, count in sorted(rarity_counts.items()):
                for _ in range(count):
                    if asset_index < len(asset_addresses):
                        asset_rarity_pairs.append((asset_addresses[asset_index], rarity))
                        asset_index += 1
            
            # Shuffle the pairs to randomize which assets get which rarity
            random.shuffle(asset_rarity_pairs)
            
            # Create NFT objects
            for asset, rarity in asset_rarity_pairs:
                nft_pool.append(NFT(asset=asset, rarity=rarity))
        
        return nft_pool
    
    def allocate_nfts(self, nft_pool: List[NFT], eligible_wallets: Dict[str, int]) -> List[WalletAllocation]:
        """
        Allocate NFTs from the pool to eligible wallets.
        
        Args:
            nft_pool: List of available NFTs
            eligible_wallets: Dict mapping wallet addresses to number of NFTs they should receive
            
        Returns:
            List of WalletAllocation objects
        """
        allocations = []
        nft_index = 0
        
        # Sort wallets for consistent ordering (deterministic allocation)
        sorted_wallets = sorted(eligible_wallets.items())
        
        for wallet, nft_count in sorted_wallets:
            wallet_nfts = []
            
            for _ in range(nft_count):
                if nft_index >= len(nft_pool):
                    print(f"⚠️  Warning: Ran out of NFTs to allocate! Wallet {wallet} needs more NFTs.")
                    break
                    
                nft = nft_pool[nft_index]
                wallet_nfts.append({
                    "asset": nft.asset,
                    "rarity": nft.rarity
                })
                nft_index += 1
            
            allocations.append(WalletAllocation(
                wallet=wallet,
                nfts=wallet_nfts,
                total_nfts=len(wallet_nfts)
            ))
        
        return allocations
    
    def validate_allocation(self, allocations: List[WalletAllocation], 
                          eligible_wallets: Dict[str, int],
                          total_nfts: int) -> bool:
        """
        Validate that the allocation is correct.
        
        Args:
            allocations: List of wallet allocations
            eligible_wallets: Expected wallet eligibility
            total_nfts: Total NFTs that should be allocated
            
        Returns:
            True if validation passes
        """
        print("\n✅ Validation:")
        
        # Check all wallets got correct amount
        total_allocated = 0
        unique_ids = set()
        
        for allocation in allocations:
            expected = eligible_wallets.get(allocation.wallet, 0)
            if allocation.total_nfts != expected:
                print(f"  ❌ Wallet {allocation.wallet} expected {expected} NFTs but got {allocation.total_nfts}")
                return False
            
            total_allocated += allocation.total_nfts
            
            # Check for duplicate assets
            for nft in allocation.nfts:
                nft_asset = nft["asset"]
                if nft_asset in unique_ids:
                    print(f"  ❌ Duplicate NFT asset {nft_asset} found!")
                    return False
                unique_ids.add(nft_asset)
        
        # Check total allocated matches expected
        expected_total = sum(eligible_wallets.values())
        if total_allocated != expected_total:
            print(f"  ❌ Total allocated ({total_allocated}) doesn't match expected ({expected_total})")
            return False
        
        # Check we didn't allocate more NFTs than exist
        if total_allocated > total_nfts:
            print(f"  ❌ Allocated more NFTs ({total_allocated}) than exist ({total_nfts})")
            return False
            
        print(f"  ✓ All {len(allocations)} wallets received correct NFT count")
        print(f"  ✓ Total NFTs allocated: {total_allocated}/{total_nfts}")
        print(f"  ✓ All NFT assets are unique")
        
        return True


def load_config(config_path: str) -> Dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Config file not found at {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in config file: {e}")
        sys.exit(1)


def load_eligible_wallets(wallets_path: str) -> Dict[str, int]:
    """Load eligible wallets from JSON file.
    
    Expected format: {"0x...": number, "0x...": number}
    The numbers represent how many times each wallet can draw from the NFT pool.
    If all values are the same (or if you want random assignment), the system will
    randomly reassign counts such that the total equals the number of NFTs.
    """
    try:
        with open(wallets_path, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, dict):
            return data
        elif isinstance(data, list):
            # Convert list to dict with placeholder values (will be randomly assigned)
            return {wallet: 0 for wallet in data}
        else:
            print(f"❌ Error: Wallets file must contain a dict or list")
            sys.exit(1)
    except FileNotFoundError:
        print(f"❌ Error: Wallets file not found at {wallets_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in wallets file: {e}")
        sys.exit(1)


def load_nft_assets(assets_path: str) -> List[Tuple[str, str]]:
    """Load NFT assets from JSON file.
    
    Expected format (with pre-assigned rarities):
    [
        {"asset": "6Gywa7GWkggRc7BXynvqvpyDGr5uHbVAjCLUxWckLa3D", "rarity": "Common"},
        {"asset": "7Hzwa8GWkggRc7BXynvqvpyDGr5uHbVAjCLUxWckLa4E", "rarity": "Rare"},
        ...
    ]
    
    Or (without rarities - will be assigned based on percentages):
    [
        {"asset": "6Gywa7GWkggRc7BXynvqvpyDGr5uHbVAjCLUxWckLa3D"},
        ...
    ]
    
    Returns:
        List of tuples (asset_address, rarity) where rarity is None if not pre-assigned
    """
    try:
        with open(assets_path, 'r') as f:
            data = json.load(f)
        
        assets_with_rarities = []
        has_rarities = False
        
        # Handle both list format and object format
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "asset" in item:
                    asset = item["asset"]
                    rarity = item.get("rarity")  # None if not present
                    if rarity:
                        has_rarities = True
                    assets_with_rarities.append((asset, rarity))
                elif isinstance(item, str):
                    assets_with_rarities.append((item, None))
        elif isinstance(data, dict):
            # If it's a dict, try to find an "assets" key or similar
            if "assets" in data:
                for item in data["assets"]:
                    if isinstance(item, dict) and "asset" in item:
                        asset = item["asset"]
                        rarity = item.get("rarity")
                        if rarity:
                            has_rarities = True
                        assets_with_rarities.append((asset, rarity))
                    elif isinstance(item, str):
                        assets_with_rarities.append((item, None))
            else:
                print(f"❌ Error: Unexpected format in assets file. Expected list or dict with 'assets' key.")
                sys.exit(1)
        else:
            print(f"❌ Error: Assets file must contain a list or dict")
            sys.exit(1)
        
        if has_rarities:
            print(f"  ✓ Found pre-assigned rarities in assets file")
        else:
            print(f"  ℹ️  No rarities found - will assign based on percentages")
        
        return assets_with_rarities
    except FileNotFoundError:
        print(f"❌ Error: Assets file not found at {assets_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in assets file: {e}")
        sys.exit(1)


def save_allocations(allocations: List[WalletAllocation], output_path: str):
    """Save allocations to JSON file."""
    output_data = {
        "allocations": [asdict(alloc) for alloc in allocations],
        "total_wallets": len(allocations),
        "total_nfts_allocated": sum(alloc.total_nfts for alloc in allocations)
    }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n💾 Allocation saved to: {output_path}")


def print_summary(allocations: List[WalletAllocation], nft_pool: List[NFT]):
    """Print a summary of the allocation."""
    print("\n" + "="*60)
    print("📊 ALLOCATION SUMMARY")
    print("="*60)
    
    # Rarity distribution in allocations
    rarity_counts = {}
    for allocation in allocations:
        for nft in allocation.nfts:
            rarity = nft["rarity"]
            rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
    
    print("\n🎯 Allocated NFTs by Rarity:")
    for rarity, count in sorted(rarity_counts.items()):
        print(f"  {rarity}: {count}")
    
    print(f"\n👥 Total Wallets: {len(allocations)}")
    print(f"🎁 Total NFTs Allocated: {sum(alloc.total_nfts for alloc in allocations)}")
    
    # Show sample allocations
    print("\n📋 Sample Allocations (first 5):")
    for allocation in allocations[:5]:
        nft_assets = [nft["asset"] for nft in allocation.nfts]
        rarities = [nft["rarity"] for nft in allocation.nfts]
        print(f"  {allocation.wallet[:10]}...{allocation.wallet[-8:]}: {allocation.total_nfts} NFTs")
        print(f"    Assets: {nft_assets[:3]}{'...' if len(nft_assets) > 3 else ''}")
        print(f"    Rarities: {rarities}")


def main():
    """Main execution function."""
    print("🚀 Pikamoon NFT Allocator")
    print("="*60)
    
    # Determine working directory (where config.json is located)
    # This allows running from any directory by finding config.json
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = 'config.json'
    
    # Try current directory first, then script directory
    if not os.path.exists(config_path):
        config_path = os.path.join(script_dir, 'config.json')
    
    if not os.path.exists(config_path):
        # Try to find config.json in current working directory
        cwd_config = os.path.join(os.getcwd(), 'config.json')
        if os.path.exists(cwd_config):
            config_path = cwd_config
        else:
            print(f"❌ Error: config.json not found in current directory or script directory")
            print(f"   Current directory: {os.getcwd()}")
            print(f"   Script directory: {script_dir}")
            sys.exit(1)
    
    # Change to directory containing config.json
    config_dir = os.path.dirname(os.path.abspath(config_path))
    if config_dir:
        os.chdir(config_dir)
        print(f"📂 Working directory: {os.getcwd()}")
    
    # Load configuration
    config = load_config('config.json')
    
    seed = config.get('seed', 'pikamoon-nft-airdrop-2025')
    rarity_percentages = config.get('rarity_percentages')  # Optional - only needed if rarities not pre-assigned
    assets_file = config.get('assets_file', 'nft_assets.json')
    
    print(f"\n🌱 Seed: {seed}")
    print(f"📁 Assets file: {assets_file}")
    
    # Load NFT assets
    print("\n📦 Loading NFT assets...")
    nft_assets = load_nft_assets(assets_file)
    total_nfts = len(nft_assets)
    print(f"🎨 Total NFTs minted: {total_nfts}")
    
    # Load eligible wallets
    eligible_wallets_data = load_eligible_wallets('eligible_wallets.json')
    wallet_list = list(eligible_wallets_data.keys())
    
    # Check initial distribution request
    initial_requested = sum(eligible_wallets_data.values())
    
    print(f"\n✓ Validation Check:")
    print(f"  - Wallets in list: {len(wallet_list)}")
    print(f"  - NFTs requested (sum in file): {initial_requested}")
    print(f"  - NFTs minted (available): {total_nfts}")
    
    if initial_requested == total_nfts:
        print(f"  ✓ Perfect match! Requested = Minted")
    else:
        print(f"\n❌ ERROR: Mismatch detected!")
        if initial_requested > total_nfts:
            print(f"   Requested ({initial_requested}) > Minted ({total_nfts})")
            print(f"   Need to mint {initial_requested - total_nfts} more NFTs")
        else:
            print(f"   Requested ({initial_requested}) < Minted ({total_nfts})")
            print(f"   Need to add {total_nfts - initial_requested} more NFTs to wallets")
        print(f"\n💡 Fix required:")
        print(f"   Option 1: Adjust eligible_wallets.json so sum = {total_nfts}")
        print(f"   Option 2: Mint {initial_requested} NFTs instead of {total_nfts}")
        sys.exit(1)
    
    # Validate that all wallets have valid NFT counts (> 0)
    has_valid_counts = all(count > 0 for count in eligible_wallets_data.values())
    
    if not has_valid_counts:
        print(f"\n❌ ERROR: All wallets in eligible_wallets.json must have NFT counts > 0")
        print(f"   Each wallet must specify how many NFTs it should receive")
        sys.exit(1)
    
    # Use the counts from the file directly
    print(f"\n✓ Using NFT counts from eligible_wallets.json")
    eligible_wallets = eligible_wallets_data
    print(f"  ✓ Each wallet will receive exactly the number of NFTs specified in the file")
    
    print(f"\n👥 Eligible Wallets: {len(eligible_wallets)}")
    
    total_nfts_needed = sum(eligible_wallets.values())
    print(f"🎁 Total Draws (NFTs to Allocate): {total_nfts_needed}/{total_nfts}")
    
    if total_nfts_needed != total_nfts:
        print(f"⚠️  Warning: Total draws ({total_nfts_needed}) doesn't match available NFTs ({total_nfts})")
    
    # Show distribution
    nft_count_dist = {}
    for wallet, count in eligible_wallets.items():
        nft_count_dist[count] = nft_count_dist.get(count, 0) + 1
    
    print(f"\n📊 Draw Count Distribution:")
    for draw_count in sorted(nft_count_dist.keys()):
        wallet_count = nft_count_dist[draw_count]
        print(f"  {draw_count} draw(s): {wallet_count} wallet(s)")
    
    # Initialize allocator
    allocator = NFTAllocator(seed)
    
    # Generate NFT pool
    print("\n🎲 Generating NFT pool...")
    nft_pool = allocator.generate_nft_pool(nft_assets, rarity_percentages)
    
    # Allocate NFTs
    print("\n🎯 Allocating NFTs to wallets...")
    allocations = allocator.allocate_nfts(nft_pool, eligible_wallets)
    
    # Validate
    if not allocator.validate_allocation(allocations, eligible_wallets, total_nfts):
        print("\n❌ Allocation validation failed!")
        sys.exit(1)
    
    # Final verification: Check all NFTs from assets were distributed
    print("\n🔍 Final Verification:")
    
    # Collect all allocated assets
    allocated_assets = set()
    for allocation in allocations:
        for nft in allocation.nfts:
            allocated_assets.add(nft["asset"])
    
    # Collect all original assets
    original_assets = set(asset for asset, _ in nft_assets)
    
    # Check for missing or extra NFTs
    missing = original_assets - allocated_assets
    extra = allocated_assets - original_assets
    
    if missing:
        print(f"  ❌ Missing NFTs (not allocated): {len(missing)}")
        for asset in list(missing)[:5]:
            print(f"     - {asset}")
        if len(missing) > 5:
            print(f"     ... and {len(missing) - 5} more")
        sys.exit(1)
    
    if extra:
        print(f"  ❌ Extra NFTs (not in original list): {len(extra)}")
        for asset in list(extra)[:5]:
            print(f"     - {asset}")
        if len(extra) > 5:
            print(f"     ... and {len(extra) - 5} more")
        sys.exit(1)
    
    print(f"  ✓ All {len(original_assets)} NFTs from nft_assets.json were allocated")
    print(f"  ✓ No duplicate NFTs")
    print(f"  ✓ No missing NFTs")
    print(f"  ✓ Random distribution verified")
    
    # Save results
    save_allocations(allocations, 'nft_allocation.json')
    
    # Print summary
    print_summary(allocations, nft_pool)
    
    print("\n" + "="*60)
    print("✅ Allocation complete!")
    print("="*60)
    print("\n💡 To verify the allocation, anyone can run:")
    print("   python3 allocator.py")
    print("   with the same config.json, nft_assets.json, and eligible_wallets.json files")
    print(f"\n🔐 Verification Seed: {seed}")
    print("   Share this seed publicly so the community can verify the allocation!")


if __name__ == "__main__":
    main()

