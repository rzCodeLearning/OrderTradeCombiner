"""
将沪市的Order和Trade合并为同一个订单流，且订单流是根据RecID排序的
其中Type用于区分是Order, Trade还是撤单
若Type为'A'则为委托 （A是Add的首字母）
若Type为'T'则为成交
若Type为'D'则为撤单 （D是Delete的首字母），要撤的订单号是BuyOrderID和SellOrderID中较大的那个（另一个是0）

逐笔委托的订单号，可采用BuyOrderID和SellOrderID中较大的那个（另一个是0）
"""

import pandas as pd

data_root = '/data/DataCenter'


def sh_combiner(stock: str, date: str):
    """
    :param stock: 股票代码，例如 "601179.SH"
    :param date: 日期，例如"20251106"
    :return: 返回一个按RecID排序好的、将Order和Trade合并的行情流
    """
    order = pd.read_pickle(f'{data_root}/CleanOrderData/{stock}/Order_{date}.pickle')
    trade = pd.read_pickle(f'/{data_root}/CleanData/{stock}/Trade_{date}.pickle')

    # 这一段是为了将Order的列名和内容改成与Trade兼容, 以便合并成flow
    order['BuyOrderID'] = order['OrderID']
    order['SellOrderID'] = order['OrderID']
    order.loc[order['OrderCode'] == 'B', 'SellOrderID'] = 0
    order.loc[order['OrderCode'] == 'S', 'BuyOrderID'] = 0

    order = order.drop('OrderID', axis=1)
    order = order.drop('RecNO', axis=1)

    order.columns = ['Symbol', 'TradingDate', 'MDTime', 'SetID', 'RecID', 'Price', 'Type', 'BSFlag', 'Volume', 'BuyOrderID', 'SellOrderID']

    # 2) 上海合并行情有个字段叫Money, 在Trade中是成交金额，对于新增委托是"已成交的委托数量"；
    #    在本地的（国泰安格式的）上海逐笔委托中，这一数据在Order的清洗过程中被删去了，这里统一赋为0
    order['Money'] = 0


    # 这一段是为了将Trade的列名改成与Order兼容, 以便合并成flow
    trade = trade.drop('RecNO', axis=1)
    trade.columns = ['Symbol', 'TradingDate', 'RecID', 'SetID', 'Price', 'Volume', 'Money', 'BuyOrderID', 'SellOrderID', 'MDTime']
    trade['Type'] = 'T'

    # 设置BSFlag, 且集合竞价期间的BSFlag应当设为0
    trade['BSFlag'] = trade[['BuyOrderID', 'SellOrderID']].apply(lambda x: 'B' if x['BuyOrderID'] > x['SellOrderID'] else 'S', axis=1)
    trade.loc[trade['MDTime'] < 92600000, 'BSFlag'] = 'N'
    trade.loc[trade['MDTime'] > 145800000, 'BSFlag'] = 'N'

    # 将改造后的Order与Trade合并成flow, 并按RecID排序
    flow = pd.concat([order, trade])
    flow = flow.sort_values('RecID')
    flow = flow.reset_index(drop=True)

    return flow
