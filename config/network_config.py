NETWORK_CONFIG = {
    'sepolia': {
        'chain_id': 11155111,
        'rpc_url': 'https://sepolia.infura.io/v3/',
        'block_explorer': 'https://sepolia.etherscan.io',
        'network_name': 'Sepolia',
        'currency_symbol': 'SEP',
        'network_type': 'testnet'
    },
    'local': {
        'chain_id': 1337,
        'rpc_url': 'http://127.0.0.1:7545',
        'network_name': 'Local Network',
        'currency_symbol': 'ETH',
        'network_type': 'local'
    }
}

def get_network_config(network_name='sepolia'):
    """קבלת הגדרות רשת"""
    config = NETWORK_CONFIG.get(network_name)
    if not config:
        raise ValueError(f"Unsupported network: {network_name}")
    return config