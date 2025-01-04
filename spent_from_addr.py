import bitcoin
import bitcoin.wallet
import bitcoin.core
import bitcoin.core.script
import bitcoin.core.scripteval
from bitcoin import SelectParams

# Thiết lập môi trường làm việc là testnet
SelectParams("testnet")

# ---------------------------------------------------------
# 1. KHAI BÁO VÀ XỬ LÝ CÁC THÔNG TIN VỀ KHÓA
# ---------------------------------------------------------
source_wif_key = "cQuQE369Shpsekke7eLCrc4UAmhVHs7QmmqTUQhmRrBd7LViAoHn"
change_wif_key = "cUGzSMWw24p4G6ei98KCfRw5A31BYa6L2f1bSPukhF7gLtbJdZLP"

sender_priv = bitcoin.wallet.CBitcoinSecret(source_wif_key)
sender_pub = sender_priv.pub
sender_addr = bitcoin.wallet.P2PKHBitcoinAddress.from_pubkey(sender_pub)

change_priv = bitcoin.wallet.CBitcoinSecret(change_wif_key)
change_pub = change_priv.pub
change_addr = bitcoin.wallet.P2PKHBitcoinAddress.from_pubkey(change_pub)

print("Sender address  :", sender_addr)
print("Change address  :", change_addr)

# ---------------------------------------------------------
# 2. THÔNG TIN UTXO & THIẾT LẬP GIAO DỊCH
# ---------------------------------------------------------
# Giả sử UTXO của bạn có txid và index (vout)
raw_txid_str = "50f61e081622ad573076a3ce30f6f3f35b209dcc92337c6230e38f5ce9ab3e6b"
raw_txid = bitcoin.core.lx(raw_txid_str)  # Đảo ngược chuỗi hex

# Số BTC trong UTXO, dùng để tính fee và số dư còn lại
input_amount_btc = 0.00028168
vout_index = 0

# Tạo đối tượng TxIn (điểm đầu vào - UTXO)
tx_in = bitcoin.core.CMutableTxIn(
    bitcoin.core.COutPoint(raw_txid, vout_index)
)

# ScriptPubKey (chứa logic để xác định “tiêu” UTXO này) 
script_pub_key_in = bitcoin.core.script.CScript([
    bitcoin.core.script.OP_DUP, 
    bitcoin.core.script.OP_HASH160,
    bitcoin.core.Hash160(sender_pub),
    bitcoin.core.script.OP_EQUALVERIFY, 
    bitcoin.core.script.OP_CHECKSIG
])

# ---------------------------------------------------------
# 3. CÁC ĐẦU RA (TXOUT): NGƯỜI NHẬN & “TIỀN THỐI”
# ---------------------------------------------------------
# Địa chỉ đích muốn gửi
destination_addr = bitcoin.wallet.CBitcoinAddress("n1rNgcdK9YEVomJ84KaJJLWBbfs8x6BiN6")
btc_to_recipient = 0.00005

# Phí giao dịch
fee_btc = 0.0002

# Tính toán tiền thối (nếu có)
change_back = input_amount_btc - btc_to_recipient - fee_btc
if change_back < 0:
    raise ValueError("Số dư không đủ để trả người nhận và phí giao dịch!")

tx_out_recipient = bitcoin.core.CMutableTxOut(
    int(btc_to_recipient * bitcoin.core.COIN),
    destination_addr.to_scriptPubKey()
)

tx_out_change = bitcoin.core.CMutableTxOut(
    int(change_back * bitcoin.core.COIN),
    change_addr.to_scriptPubKey()
)

# ---------------------------------------------------------
# 4. TẠO VÀ KÝ GIAO DỊCH
# ---------------------------------------------------------
# Khởi tạo đối tượng giao dịch
new_tx = bitcoin.core.CMutableTransaction()
new_tx.nVersion = 2  # nVersion 2, tuỳ mục đích
new_tx.vin = [tx_in]
new_tx.vout = [tx_out_recipient, tx_out_change]

# Tính hàm băm (Signature Hash)
sig_hash = bitcoin.core.script.SignatureHash(
    script_pub_key_in, 
    new_tx, 
    inIdx=0, 
    hashtype=bitcoin.core.script.SIGHASH_ALL
)

# Ký với khóa riêng nguồn
sig_source = sender_priv.sign(sig_hash) + bytes([bitcoin.core.script.SIGHASH_ALL])

# Gắn chữ ký và khóa công khai vào scriptSig của TxIn
new_tx.vin[0].scriptSig = bitcoin.core.script.CScript([sig_source, sender_pub])


# ---------------------------------------------------------
# 5. HIỂN THỊ GIAO DỊCH Ở DẠNG HEX
# ---------------------------------------------------------
signed_raw_tx = bitcoin.core.b2x(new_tx.serialize())
print("Signed Transaction (hex):\n", signed_raw_tx)