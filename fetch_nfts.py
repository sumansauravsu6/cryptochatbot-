import requests
import json

# Fetch NFT list from CoinGecko API
response = requests.get('https://api.coingecko.com/api/v3/nfts/list')
data = response.json()

print(f'Fetched {len(data)} NFTs')

# Save to nft.json
with open('nft.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print('Saved to nft.json')
print(f'\nFirst 3 NFTs:')
for nft in data[:3]:
    print(f"  - {nft['name']} (ID: {nft['id']})")
