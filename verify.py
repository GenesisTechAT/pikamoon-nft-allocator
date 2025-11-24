#!/usr/bin/env python3
"""
Verification script for Pikamoon NFT Allocation
Allows community members to verify the allocation results.
"""

import json
import sys


def verify_allocation():
    """Verify the allocation results."""
    print("🔍 Pikamoon NFT Allocation Verifier")
    print("="*60)
    
    try:
        # Load all files
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        with open('eligible_wallets.json', 'r') as f:
            eligible_wallets = json.load(f)
        
        with open('nft_allocation.json', 'r') as f:
            allocation_data = json.load(f)
        
        allocations = allocation_data['allocations']
        
        print(f"\n✓ Loaded config (seed: {config['seed']})")
        print(f"✓ Loaded {len(eligible_wallets)} eligible wallets")
        print(f"✓ Loaded allocation with {len(allocations)} wallets")
        
        # Verification checks
        print("\n🔎 Running verification checks...")
        
        all_checks_passed = True
        
        # Check 1: All eligible wallets are in allocation
        print("\n1️⃣  Checking all eligible wallets received NFTs...")
        allocation_wallets = {alloc['wallet'] for alloc in allocations}
        for wallet in eligible_wallets:
            if wallet not in allocation_wallets:
                print(f"   ❌ Wallet {wallet} is eligible but not in allocation!")
                all_checks_passed = False
        
        if all_checks_passed:
            print("   ✓ All eligible wallets are present")
        
        # Check 2: Each wallet received correct number of NFTs
        print("\n2️⃣  Checking NFT counts per wallet...")
        for alloc in allocations:
            wallet = alloc['wallet']
            expected = eligible_wallets.get(wallet, 0)
            actual = alloc['total_nfts']
            
            if expected != actual:
                print(f"   ❌ Wallet {wallet}: expected {expected}, got {actual}")
                all_checks_passed = False
        
        if all_checks_passed:
            print("   ✓ All wallets received correct NFT count")
        
        # Check 3: No duplicate NFT IDs
        print("\n3️⃣  Checking for duplicate NFT IDs...")
        all_nft_ids = []
        for alloc in allocations:
            for nft in alloc['nfts']:
                all_nft_ids.append(nft['id'])
        
        if len(all_nft_ids) != len(set(all_nft_ids)):
            print("   ❌ Duplicate NFT IDs found!")
            all_checks_passed = False
        else:
            print(f"   ✓ All {len(all_nft_ids)} NFT IDs are unique")
        
        # Check 4: NFT IDs are within valid range
        print("\n4️⃣  Checking NFT ID ranges...")
        total_nfts = config['total_nfts']
        for nft_id in all_nft_ids:
            if nft_id < 1 or nft_id > total_nfts:
                print(f"   ❌ Invalid NFT ID: {nft_id} (must be 1-{total_nfts})")
                all_checks_passed = False
        
        if all_checks_passed:
            print(f"   ✓ All NFT IDs are within range 1-{total_nfts}")
        
        # Check 5: Rarity distribution matches config
        print("\n5️⃣  Checking rarity distribution...")
        rarity_counts = {}
        for alloc in allocations:
            for nft in alloc['nfts']:
                rarity = nft['rarity']
                rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
        
        total_allocated = sum(rarity_counts.values())
        print(f"   Total NFTs allocated: {total_allocated}")
        
        for rarity, count in sorted(rarity_counts.items()):
            expected_pct = config['rarity_percentages'].get(rarity, 0)
            actual_pct = (count / total_allocated) * 100
            print(f"   {rarity}: {count} ({actual_pct:.1f}% - expected ~{expected_pct}%)")
        
        # Final result
        print("\n" + "="*60)
        if all_checks_passed:
            print("✅ ALL VERIFICATION CHECKS PASSED")
            print("="*60)
            print("\n🎉 The allocation is valid and can be trusted!")
            return 0
        else:
            print("❌ VERIFICATION FAILED")
            print("="*60)
            print("\n⚠️  The allocation has issues and should be reviewed!")
            return 1
            
    except FileNotFoundError as e:
        print(f"\n❌ Error: Required file not found: {e}")
        print("\nMake sure you have:")
        print("  - config.json")
        print("  - eligible_wallets.json")
        print("  - nft_allocation.json")
        return 1
    except json.JSONDecodeError as e:
        print(f"\n❌ Error: Invalid JSON: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(verify_allocation())

