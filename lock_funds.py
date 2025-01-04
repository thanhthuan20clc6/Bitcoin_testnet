from bitcoinlib.wallets import Wallet
from bitcoinlib.transactions import Transaction, Output, Input

# Tạo hoặc tải ví
wallet = Wallet.create('BTC_testnetwallet')  # Hoặc bạn có thể dùng Wallet.load('your_wallet_name')

# Lấy khóa bí mật và địa chỉ từ ví
private_key = wallet.get_key()
address = private_key.address  # Lấy địa chỉ từ private_key mà không gọi như một hàm
print(address)
# Lấy thông tin về UTXO từ ví
utxos = wallet.utxos()

# Giả sử bạn có một UTXO cần chi tiêu
txid = utxos[0]['txid']
output_index = utxos[0]['output_n']

# Tạo input và output giao dịch
txin = Input(txid=txid, index=output_index, value=utxos[0]['value'])
txout = Output(amount=100000, address='mzDzdQF6XhRoB7aoft5RonaTqNz5MKu45m')

# Tạo giao dịch
tx = Transaction(inputs=[txin], outputs=[txout])

# Ký giao dịch
tx.sign(wallet)

# Chuyển giao dịch
wallet.send_transaction(tx)

print("Transaction sent: ", tx.info())
