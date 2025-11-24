# Pikamoon NFT Allocator

A transparent and verifiable NFT allocation system for fair distribution of pre-minted NFTs to eligible wallets. This system uses deterministic randomness to ensure fairness and allows complete community verification.

## 🎯 What This Does

This allocator distributes NFTs to eligible wallets in a way that:
- Is completely **transparent** and **verifiable**
- Produces the **same results** every time (using a seed)
- Uses **exact NFT counts** specified in `eligible_wallets.json` for each wallet
- Randomly assigns **which specific NFTs** each wallet receives (based on seed)
- Cannot be manipulated or changed after announcement
- Can be **verified by anyone** in the community

## 🔐 How to Verify an Allocation

Anyone in the community can verify the fairness of an allocation:

### 1. Get the Files

The project should provide:
- `config.json` - Contains the seed used
- `eligible_wallets.json` - List of eligible wallets
- `nft_assets.json` - List of minted NFTs
- `nft_allocation.json` - The final allocation results

### 2. Run the Allocator

```bash
# Clone the repository
git clone <repository-url>
cd pikamoon-nft-allocator

# Copy the provided files to example folder
# (or the specific airdrop folder they published)

# Run the allocator
cd example  # or the airdrop folder name
python3 ../allocator.py
```

### 3. Compare Results

Compare the generated `nft_allocation.json` with the published one:
- If they're **identical** → The allocation is verified! ✅
- If they're **different** → Something is wrong ❌

**Same seed + same input files = same results, always!**

## 🔍 How It Works

### The Process

1. **Input**: Eligible wallets (with NFT counts) and minted NFTs are loaded
2. **Validation**: System checks that numbers match (stops if they don't)
3. **Shuffle**: Randomly shuffles the NFT pool using the seed
4. **Distribution**: Each wallet receives exactly the number of NFTs specified in `eligible_wallets.json`, drawn from the shuffled pool
5. **Verification**: Triple-checks everything was distributed correctly

### The Seed

The **seed** is the key to verification:
- It's a public string announced before allocation
- Same seed always produces the same random distribution
- Anyone can use the seed to reproduce the results
- This proves the allocation was fair and not manipulated

### Example

```
Seed: "pikamoon-airdrop-december-2025"
Wallets: 100
NFTs: 500

→ Run allocator → Same results every time
→ Anyone can verify → Trust but verify!
```

## 📊 What Gets Allocated

### Input: Eligible Wallets

```json
{
  "6oqtDTCShJpJSWYswXfTj4wwz3TicBZTckfxzrZXoDAV": 5,
  "nMCpeCDnd2mqXmAo6RvxREKpz6GSfkaMjuCTByx56eK": 6,
  "77ftdCz6uLBHQpLPxqbKxUUHtLYto68fqH3NXePmsw9p": 3
}
```

The numbers represent how many NFTs each wallet should receive. **Each wallet must have a count > 0.** The sum must equal the total minted NFTs.

### Input: Minted NFTs

```json
[
  {
    "asset": "6Gywa7GWkggRc7BXynvqvpyDGr5uHbVAjCLUxWckLa3D",
    "rarity": "Common"
  },
  {
    "asset": "7Hzwa8GWkggRc7BXynvqvpyDGr5uHbVAjCLUxWckLa4E",
    "rarity": "Rare"
  }
]
```

These are the actual minted NFTs with their addresses and rarities.

### Output: Final Allocation

```json
{
  "allocations": [
    {
      "wallet": "6oqtDTCShJpJSWYswXfTj4wwz3TicBZTckfxzrZXoDAV",
      "nfts": [
        {
          "asset": "6Gywa7GWkggRc7BXynvqvpyDGr5uHbVAjCLUxWckLa3D",
          "rarity": "Rare"
        }
      ],
      "total_nfts": 1
    }
  ]
}
```

Shows exactly which NFTs each wallet received.

## ✅ Verification Steps

The allocator performs three levels of verification:

### 1. Pre-Allocation Check
```
✓ Validation Check:
  - Wallets in list: 20
  - NFTs requested (sum): 100
  - NFTs minted (available): 100
  ✓ Perfect match!
```

**Ensures the numbers add up before allocation starts.**

### 2. Allocation Validation
```
✅ Validation:
  ✓ All wallets received correct NFT count
  ✓ Total NFTs allocated: 100/100
  ✓ All NFT assets are unique
```

**Ensures no NFT was assigned twice and everyone got the right amount.**

### 3. Final Verification
```
🔍 Final Verification:
  ✓ All 100 NFTs were allocated
  ✓ No duplicate NFTs
  ✓ No missing NFTs
  ✓ Random distribution verified
```

**Confirms every single NFT was distributed properly.**

## 🧪 Try the Example

Test the system yourself with the included example:

```bash
cd example
python3 ../allocator.py
```

This runs a complete allocation with:
- 20 example wallets (each with specified NFT counts)
- 100 example NFTs with pre-assigned rarities
- Exact NFT counts per wallet defined in `eligible_wallets.json`

The example demonstrates how the system works and can be verified.

## 🛡️ Why This is Trustworthy

### Deterministic
- Same seed = same results, every single time
- No room for changing results after the fact

### Transparent
- All code is open source
- All input files can be shared
- All output can be verified

### Verifiable
- Anyone can run the code
- Anyone can compare results
- No special access needed

### Fair
- NFT counts are transparently defined in `eligible_wallets.json`
- Random assignment of which specific NFTs go to each wallet (based on seed)
- No way to predict which NFTs go where
- No way to favor specific wallets

## 📋 Requirements

To verify an allocation, you need:
- **Python 3.6+** (no external dependencies)
- The published input files
- The allocator code (this repository)

Works on Linux, macOS, and Windows.

## ❓ Common Questions

**Q: How do I know the allocation is fair?**  
A: Run the allocator yourself with the published files and seed. If your results match the published results, it's verified.

**Q: Can the seed be changed after allocation?**  
A: Yes, but it would produce completely different results. That's why the seed is announced publicly beforehand.

**Q: What if the numbers don't match when I verify?**  
A: Either you're using different input files, or there's an issue with the published allocation. The community should investigate.

**Q: Can someone manipulate the results?**  
A: No. Once the seed is announced publicly, the results are determined. Changing anything would be immediately detectable by verification.

**Q: Do I need to trust the project?**  
A: No! That's the point. **Don't trust, verify.** Run it yourself and compare the results.

## 🎯 What You Should Check

When verifying an allocation:

1. ✓ The seed was announced publicly **before** allocation
2. ✓ The sum of `eligible_wallets.json` equals the number of NFTs in `nft_assets.json`
3. ✓ All NFTs in `nft_assets.json` appear in the allocation
4. ✓ Running the allocator produces identical results
5. ✓ No NFT appears twice in the allocation

## 📜 License

MIT License - See [LICENSE](LICENSE) file.

## 🤝 For the Community

This system was built for transparency and trust. We encourage:
- Everyone to verify allocations independently
- Questions and scrutiny
- Open discussion about the process
- Sharing verification results

**Don't trust, verify!** 🔍
