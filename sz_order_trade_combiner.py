"""
将深市的Order和Trade合并为同一个订单流，且订单流是根据RecID排序的
其中Type用于区分是Order, Trade还是撤单
若Type为'1', '2', 或'U', 则为委托（其中'2'为限价单, '1'为市价单, 'U'为本方最优单)
若Type为'F'则为成交
若Type为'4'则为撤单，要撤的订单号是BuyOrderID和SellOrderID中较大的那个（另一个是0）

逐笔委托的订单号，可采用BuyOrderID和SellOrderID中较大的那个（另一个是0）
"""

import pandas as pd

data_root = '/data/DataCenter'

def sz_combiner(stock: str, date: str):
    """
    :param stock: 股票代码，例如 "000001.SZ"
    :param date: 日期，例如"20251106"
    :return: 返回一个按RecID排序好的、将Order和Trade合并的行情流
    """
    order = pd.read_pickle(f'{data_root}/CleanOrderData/{stock}/Order_{date}.pickle')
    trade = pd.read_pickle(f'/{data_root}/CleanData/{stock}/Trade_{date}.pickle')

    # 这一段是为了将Order的列名和内容改成与Trade兼容, 以便合并成flow
    order['BuyOrderID'] = order['RecID']
    order['SellOrderID'] = order['RecID']
    order.loc[order['OrderCode'] == 1, 'SellOrderID'] = 0
    order.loc[order['OrderCode'] == 2, 'BuyOrderID'] = 0

    # 将委托的买卖改成'B'和'S'
    order['OrderCode'] = order['OrderCode'].map({1: 'B', 2: 'S'})

    # 修改委托的列名，使之与后续的逐笔成交相协调
    order.columns = ['Symbol', 'TradingDate', 'MDTime', 'SetID', 'RecID', 'Price', 'Volume', 'Type', 'BSFlag',
                     'BuyOrderID', 'SellOrderID']
    order['Type'] = order['Type'].astype(str)

    # 委托的金额都设为0
    order['Amount'] = 0

    # 将逐笔成交的列名也修改得与委托相协调
    trade.columns = ['Symbol', 'TradingDate', 'BuyOrderID', 'SellOrderID', 'Price', 'Volume', 'Type', 'SetID', 'RecID',
                     'Amount', 'MDTime']

    # 设置BSFlag, 且集合竞价期间的BSFlag应当设为0
    trade['BSFlag'] = trade[['BuyOrderID', 'SellOrderID']].apply(lambda x: 'B' if x['BuyOrderID'] > x['SellOrderID'] else 'S', axis=1)
    trade.loc[trade['MDTime'] < 92600000, 'BSFlag'] = 'N'
    trade.loc[trade['MDTime'] > 145800000, 'BSFlag'] = 'N'

    # 将改造后的Order与Trade合并成flow, 并按RecID排序
    flow = pd.concat([order, trade])
    flow = flow.sort_values('RecID')
    flow = flow.reset_index(drop=True)

    return flow
