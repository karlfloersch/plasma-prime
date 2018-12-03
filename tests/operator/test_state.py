import time
from plasmalib.state import State
from plasmalib.operator.transactions import TransferRecord, DepositRecord

def test_deposit():
    db_path = '/tmp/test_db/'
    file_log_path = '/tmp/test_tx_log/'
    state = State(db_path, file_log_path, backup_timeout=60)
    start_time = time.time()
    for i in range(100000):
        deposit_record = DepositRecord(b'\00'*20, 10, 0)
        state.add_deposit(deposit_record)
    print('end time', time.time()-start_time)
    # test_tx = TransferRecord(b'\00'*20, b'\00'*20, 1001, 5, 0, 10, 3)
    # state.add_tx(test_tx)

# def test_

#     # it = state.db.iterator(include_value=False)
#     # for i in range(100):
#     #     key = next(it)
#     #     print(key, state.db.get(key))