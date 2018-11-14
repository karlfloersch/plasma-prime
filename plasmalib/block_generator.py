from plasmalib.utils import NullTx
from eth_utils import int_to_big_endian
from web3 import Web3

class EphemDB():
    def __init__(self, kv=None):
        self.kv = kv or {}

    def get(self, k):
        return self.kv.get(k, None)

    def put(self, k, v):
        self.kv[k] = v

    def delete(self, k):
        del self.kv[k]

class TxBucket():
    def __init__(self, db, start, offset, txs):
        self.start = start
        self.txs = txs
        self.hashes = []
        for tx in txs:
            self.hashes.append(tx.h)
            db.put(tx.h, tx.plaintext())
        if len(self.hashes) > 0:
            root_hash = merklize(db, self.hashes)
            self.tx_merkle_tree_root_hash = add_sum_to_hash(root_hash, offset)

def add_sum_to_hash(raw_hash, int_sum):
    return b''.join([raw_hash, int_to_big_endian(int_sum).rjust(8, b"\x00")])

def create_tx_buckets(db, txs):
    starts_and_ends = set()
    starts_and_ends.add(0)
    txs_by_start = dict()
    # Compute the bucket boundaries based on where txs start & end
    for tx in txs:
        starts_and_ends.add(tx.start)
        starts_and_ends.add(tx.start+tx.offset)
        if tx.start not in txs_by_start:
            txs_by_start[tx.start] = []
        txs_by_start[tx.start].append(tx)

    list_of_starts_and_ends = sorted(starts_and_ends)
    active_txs = []
    buckets = []
    # Iterate over txs, adding them to their respective buckets
    for idx, i in enumerate(list_of_starts_and_ends):
        if i in txs_by_start:
            active_txs = active_txs + txs_by_start[i]
        # Remove all active txs which end here
        active_txs = [tx for tx in active_txs if tx.start + tx.offset != i]
        if len(active_txs) == 0 and idx+1 == len(list_of_starts_and_ends):
            continue
        bucket_offset = list_of_starts_and_ends[idx+1] - i
        if len(active_txs) == 0 and idx+1 != len(list_of_starts_and_ends):
            buckets.append(TxBucket(db, i, bucket_offset, [NullTx(i, list_of_starts_and_ends[idx+1] - i)]))
        else:
            buckets.append(TxBucket(db, i, bucket_offset, active_txs))
        # print('starts:', [tx.start for tx in active_txs])
        # print('ends:', [tx.start + tx.offset for tx in active_txs])
        # print('current value:', i)
        # print("~~~~")
    return buckets

# def create_merkle_sum_tree(db, tx_buckets):
#     if len(nodes) == 1:
#         return nodes[0]
#     remaining_nodes = []
#     for i in range(0, len(nodes), 2):
#         if i+1 == len(nodes):
#             remaining_nodes.append(nodes[i])
#             break
#         new_value = b''.join([nodes[i], nodes[i+1]])
#         new_hash = Web3.sha3(new_value)
#         db.put(new_hash, new_value)
#         remaining_nodes.append(new_hash)
#     return merklize(db, remaining_nodes)

def merklize(db, nodes):
    if len(nodes) == 1:
        return nodes[0]
    remaining_nodes = []
    for i in range(0, len(nodes), 2):
        if i+1 == len(nodes):
            remaining_nodes.append(nodes[i])
            break
        new_value = b''.join([nodes[i], nodes[i+1]])
        new_hash = Web3.sha3(new_value)
        db.put(new_hash, new_value)
        remaining_nodes.append(new_hash)
    return merklize(db, remaining_nodes)
