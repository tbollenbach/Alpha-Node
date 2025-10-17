# 💎 Ravencoin Mining Guide - Distributed Mining Setup

## 🚀 Quick Start - Get Mining in 5 Steps

### Step 1: Get a Ravencoin Wallet

**Option A: Official Desktop Wallet (Recommended)**
- Download: https://ravencoin.org/wallet/
- Create new wallet and backup your seed phrase
- Copy your receiving address (starts with "R")

**Option B: Exchange Wallet (Easy)**
- Binance, Coinbase, or other exchanges
- Go to RVN deposit section
- Copy your RVN deposit address

**Option C: Mobile Wallet**
- Trust Wallet, Atomic Wallet, or Ravencoin Mobile
- Create wallet and get your RVN address

### Step 2: Choose a Mining Pool

**Recommended Pools:**

| Pool | Fee | URL |
|------|-----|-----|
| **2Miners** | 1% | `stratum+tcp://rvn.2miners.com:6060` |
| **Ravenminer** | 0.5% | `stratum+tcp://stratum.ravenminer.com:3838` |
| **Flypool** | 1% | `stratum+tcp://rvn-us.flypool.org:3333` |
| **WoolyPooly** | 0.9% | `stratum+tcp://rvn.woolypooly.com:55555` |
| **HeroMiners** | 0.9% | `stratum+tcp://ravencoin.herominers.com:10241` |

### Step 3: Download Mining Software

**For NVIDIA GPUs:**

1. **T-Rex Miner** (Recommended)
   ```bash
   # Windows
   https://github.com/trexminer/T-Rex/releases
   # Extract to: C:\Users\travi\Desktop\seed\miners\t-rex\
   
   # Linux
   wget https://github.com/trexminer/T-Rex/releases/download/0.26.8/t-rex-0.26.8-linux.tar.gz
   tar -xzf t-rex-0.26.8-linux.tar.gz -C miners/t-rex/
   ```

2. **NBMiner** (Alternative)
   ```bash
   https://github.com/NebuTech/NBMiner/releases
   ```

**For AMD GPUs:**

1. **TeamRedMiner** (Recommended)
   ```bash
   # Windows
   https://github.com/todxx/teamredminer/releases
   # Extract to: C:\Users\travi\Desktop\seed\miners\teamredminer\
   
   # Linux
   wget https://github.com/todxx/teamredminer/releases/download/v0.10.12/teamredminer-v0.10.12-linux.tgz
   tar -xzf teamredminer-v0.10.12-linux.tgz -C miners/teamredminer/
   ```

2. **lolMiner** (Alternative)
   ```bash
   https://github.com/Lolliedieb/lolMiner-releases/releases
   ```

### Step 4: Configure Your Nodes

**On EACH node you want to mine with:**

```bash
# 1. Set your Ravencoin wallet address
export RVN_WALLET=RYourWalletAddressHere123456789

# 2. Set mining pool (optional, uses 2miners by default)
export RVN_POOL_URL=stratum+tcp://rvn.2miners.com:6060

# 3. Set coordinator URL
export COORDINATOR_URL=https://alpha-node.onrender.com

# 4. Update config to enable mining module
# Edit config.json:
{
    "version": "2.0.0",
    "update_server": "https://alpha-node.onrender.com/updates.json",
    "check_interval": 3600,
    "auto_update": true,
    "modules_enabled": [
        "simple_coordinator.py",
        "resource_pool.py",
        "ravencoin_miner.py"
    ],
    "backup_count": 3,
    "log_file": "agent.log"
}

# 5. Start mining!
python main.py run
```

### Step 5: Monitor Your Mining

**Dashboard:** https://alpha-node.onrender.com

You'll see:
- 💻 Active miners and their hashrates
- 📊 Total combined hashrate (MH/s)
- ✅ Accepted shares from all nodes
- 🎯 Mining efficiency across the network
- ⚡ Individual worker statistics

## 🎯 Mining Configuration Options

### Environment Variables

```bash
# Required
export RVN_WALLET=RYourWalletAddress

# Optional
export RVN_POOL_URL=stratum+tcp://rvn.2miners.com:6060
export RVN_INTENSITY=auto  # or 0-25 for manual control
export COORDINATOR_URL=https://alpha-node.onrender.com
```

### Pool Configuration

Edit `modules/ravencoin_miner.py` or set environment variables:

```python
MINING_CONFIG = {
    'pool_url': 'stratum+tcp://rvn.2miners.com:6060',
    'wallet_address': 'RYourWalletAddress',
    'worker_name': 'auto',  # Uses agent_id
    'intensity': 'auto',    # GPU intensity
}
```

## 📊 Expected Hashrates

### NVIDIA GPUs (KawPow Algorithm)
- **RTX 4090**: ~60 MH/s (~260W)
- **RTX 4080**: ~45 MH/s (~220W)
- **RTX 3090**: ~45 MH/s (~300W)
- **RTX 3080**: ~40 MH/s (~240W)
- **RTX 3070**: ~30 MH/s (~150W)
- **RTX 3060 Ti**: ~28 MH/s (~140W)
- **RTX 2080 Ti**: ~30 MH/s (~200W)
- **GTX 1080 Ti**: ~20 MH/s (~180W)

### AMD GPUs (KawPow Algorithm)
- **RX 7900 XTX**: ~50 MH/s (~280W)
- **RX 6900 XT**: ~35 MH/s (~230W)
- **RX 6800 XT**: ~32 MH/s (~200W)
- **RX 5700 XT**: ~22 MH/s (~150W)
- **RX 580**: ~10 MH/s (~100W)

## 💰 Profitability Calculation

**Example Setup:**
- 2x RTX 3080 = 80 MH/s total
- Power consumption: ~480W
- Electricity cost: $0.10/kWh

**Estimated Daily Earnings (as of 2024):**
- ~80 RVN per day
- ~$2-4 USD per day (varies with RVN price)
- Minus electricity: ~$1.15/day
- Net profit: ~$0.85-2.85/day per node

**Check current profitability:**
- WhatToMine: https://whattomine.com/coins/234-rvn-kawpow
- CoinWarz: https://www.coinwarz.com/mining/ravencoin

## 🔧 Advanced Setup

### Custom Miner Configuration

Create a custom mining script in `miners/`:

```bash
#!/bin/bash
# custom_rvn_miner.sh

./t-rex -a kawpow \
  -o stratum+tcp://rvn.2miners.com:6060 \
  -u $RVN_WALLET.$HOSTNAME \
  -p x \
  --intensity 20 \
  --temperature-limit 80 \
  --api-bind-http 127.0.0.1:4067
```

### Multiple GPU Optimization

```bash
# NVIDIA - Optimize each GPU separately
nvidia-smi -i 0 -pl 200  # Set power limit to 200W for GPU 0
nvidia-smi -i 1 -pl 200  # Set power limit to 200W for GPU 1

# AMD - Use TeamRedMiner tuning
./teamredminer -a kawpow \
  --eth_config=B1024 \
  --eth_aggr_mode \
  --fan_control=80
```

### Overclocking (Proceed with Caution!)

**NVIDIA (MSI Afterburner or nvidia-smi):**
```bash
# Core: +100-150 MHz
# Memory: +800-1200 MHz
# Power Limit: 70-80%
# Fan: 70-80%
```

**AMD (AMD Radeon Software or OverdriveNTool):**
```bash
# Core: 1250-1350 MHz
# Memory: 1850-2000 MHz  
# Core Voltage: 850-900 mV
# Fan: 70-80%
```

## 📈 Dashboard Mining Panel

Once configured, your dashboard will show:

```
╔═══════════════════════════════════════════════════════════════╗
║  💎 RAVENCOIN MINING POOL                                     ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  [Total Hashrate]  [Active Miners]  [Accepted]  [Efficiency] ║
║     120.5 MH/s          3              2,456       99.8%      ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ┌─ Active Miners ──────────────────────────────────────┐    ║
║  │                                                       │    ║
║  │  Node 1 (Adam_c1d77889)                              │    ║
║  │  ⛏️  Mining - 40.5 MH/s                               │    ║
║  │  ✅ 845 shares | Uptime: 2h 15m                       │    ║
║  │                                                       │    ║
║  │  Node 2 (Desktop_8f4a2b11)                           │    ║
║  │  ⛏️  Mining - 40.0 MH/s                               │    ║
║  │  ✅ 832 shares | Uptime: 2h 10m                       │    ║
║  │                                                       │    ║
║  │  Node 3 (Laptop_3c7d9a55)                            │    ║
║  │  ⛏️  Mining - 40.0 MH/s                               │    ║
║  │  ✅ 779 shares | Uptime: 1h 55m                       │    ║
║  │                                                       │    ║
║  └───────────────────────────────────────────────────────┘    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

## 🛠️ Troubleshooting

### "No GPU detected"
- Install GPU drivers (NVIDIA/AMD)
- Restart computer
- Check `nvidia-smi` or `rocm-smi`

### "Mining software not found"
- Download miner from links above
- Extract to correct `miners/` directory
- Make executable: `chmod +x miner_name` (Linux)

### Low hashrate
- Update GPU drivers
- Check temperatures (should be <75°C)
- Try different miner software
- Reduce other GPU usage
- Check overclocking settings

### Connection errors
- Verify pool URL is correct
- Check firewall settings
- Try different pool
- Check internet connection

### High rejected shares
- Reduce overclock settings
- Check pool latency (ping pool server)
- Update mining software
- Check GPU stability

## 📚 Additional Resources

- **Ravencoin Official**: https://ravencoin.org
- **Mining Calculator**: https://whattomine.com
- **Pool Comparison**: https://miningpoolstats.stream/ravencoin
- **Discord Community**: https://discord.gg/ravencoin
- **Reddit**: https://reddit.com/r/Ravencoin

## ⚠️ Important Notes

1. **Electricity Costs**: Calculate profitability with your local electricity rates
2. **Hardware Wear**: Mining puts stress on GPUs - ensure adequate cooling
3. **Warranty**: Mining may void GPU warranty
4. **Tax**: Mining income may be taxable in your jurisdiction
5. **Security**: Keep wallet private keys secure
6. **Pool Fees**: Factor in 0.5-1% pool fees
7. **Minimum Payout**: Pools have minimum payout thresholds (usually 10-50 RVN)

## 🎯 Next Steps

1. ✅ Set up wallet
2. ✅ Download mining software
3. ✅ Configure all nodes
4. ✅ Start mining
5. 📊 Monitor dashboard
6. 💰 Collect rewards
7. 🚀 Scale up with more nodes!

**Happy Mining!** ⛏️💎
