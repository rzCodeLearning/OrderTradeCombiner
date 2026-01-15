两个文件都是将逐笔委托与逐笔成交合并为一个订单流文件

【不分沪深】
BSFlag - 在逐笔委托中，B表示买、S表示卖
BSFlag - 在逐笔成交中，集合竞价期间为空，连续竞价期间B表示主买、S表示主卖

逐笔委托的订单号，可采用BuyOrderID和SellOrderID中较大的那个（另一个是0）

【沪市】
其中Type用于区分是Order, Trade还是撤单
若Type为'A'则为委托 （A代表Add）
若Type为'T'则为成交
若Type为'D'则为撤单 （D代表Delete），要撤的订单号是BuyOrderID和SellOrderID中较大的那个（另一个是0）

【深市】
其中Type用于区分是Order, Trade还是撤单
若Type为'1', '2', 或'U', 则为委托（其中'2'为限价单, '1'为市价单, 'U'为本方最优单)
若Type为'F'则为成交
若Type为'4'则为撤单，要撤的订单号是BuyOrderID和SellOrderID中较大的那个（另一个是0）


【写给自己的其他注释】
Order中的Amount是自己造的，为0；
逐笔成交中的BSFlag其实是自己造的，可以通过BuyOrderID和SellOrderID推得，是冗余信息；
深市的BSFlag原来是1和2，为了方便和逐笔成交对应所以改成了'B'和'S'；
沪深两市的RecID的意义是一样的——都是同一个频道下单调递增的统一编号，可用于对Order/Trade/Cancel进行排序，但深市的逐笔委托中RecID就是委托编号，沪市的另有一个字段；
取“BuyOrderID和SellOrderID中较大的那个（另一个是0）”的好办法是两者直接相加