
import numpy as np
import json
import happybase
import faiss

color_list = ["#D1EEEE", "#CDC9C9", "#CDB38B", "#CD919E", "#CD6839", "#CD3700", "#CD2990", "#CD00CD", "#436EEE",
              "#080808"]

color_list2 = ["#FF9966", "#FF6666", "#FFCCCC", "#CC9966", "#666666", "#CC9999", "#FF6666", "#FFFF66", "#99CC66",
               "#CCFFFF"]
color_list.reverse()
color_list2.reverse()


#
# connection = happybase.Connection('10.20.10.168', port=9090)
# connection.open()
#
# # table = connection.table('t11')
# # # f1的row1的内容输出
# # row = table.row('row1', columns=['f1'])
# # print("---------------------")
# # for key, value in row.items():
# #     # 同一行的字段进行循环
# #     if (key.decode("utf8") == 'f1:name'):
# #         # name的场合，输出名字
# #         print(value.decode("utf8"))
# print(connection.tables())
# connection.close()


class HappyHbase(object):
    """
     :param str name:table name
     :param str row: the row key
     :param list_or_tuple columns: list of columns (optional)
    """

    def __init__(self, host, port=9090):
        self.conn = happybase.Connection(host, port=port, autoconnect=False)
        self.conn.open()

    def list_tables(self):
        tabels = self.conn.tables()
        return tabels

    def table(self, name):
        table = self.conn.table(name)
        return table

    def creat(self, name, kw):
        """
        :param name: str
        :param kw: dict
        exp:
            kw = {"":dict()}
        :return: None
        """
        self.conn.create_table(name, kw)

    def delete(self, name, row):
        table = self.table(name)
        table.delete(row)

    def delete_column(self, name, row, columns):
        self.table(name).delete(row, columns=columns)

    def drop(self, name):
        self.conn.disable_table(name)
        self.conn.delete_table(name)

    def cell(self, name, row, column):
        """
        :return: list
        """
        return self.table(name).cells(row, column)

    def families(self, name):
        """
        :return: dict
        """
        return self.conn.table(name).families()

    def put(self, name, row, kw):
        self.table(name).put(row, kw)

    def get(self, name, row):
        """
        :return: dict
        """
        return self.table(name).row(row)

    def get_column(self, name, row, columns):
        """
        :return: dict
        """
        return self.table(name).row(row, columns)

    def incr(self, name, row, column):
        self.table(name).counter_inc(row, column=column)

    def dec(self, name, row, column):
        self.table(name).counter_dec(row, column=column)

    def close(self):
        self.conn.close()

    def scan(self, name):
        nu = self.conn.table(name).scan()
        for i in nu:
            print(i)
        # return [{self.b2str(i[0]): self.b2str(i[1][b'play:duration'])} for i in nu]
        # return [{str(i[0], encoding="utf8"): str(i[1][b'play:duration'], encoding='utf8')} for i in nu]

    @staticmethod
    def b2str(b_data):
        return str(b_data, encoding="utf8")

    def eb_scan_start_stop(self, name, row_start, row_stop):
        nu = self.conn.table(name=name).scan(row_start=row_start, row_stop=row_stop)
        user_embedding = None
        for i in nu:
            user_embedding = i[1][b'embedding:mf']
            user_embedding = np.array(json.loads(user_embedding.decode('utf-8')))
            user_embedding = np.expand_dims(user_embedding, axis=0).astype(np.float32)
        return user_embedding

    def two_tower_scan_start_stop(self, name, row_start, row_stop):
        nu = self.conn.table(name=name).scan(row_start=row_start, row_stop=row_stop)
        embedding = None
        for i in nu:
            embedding = i[1][b'embedding:two-tower']
            embedding = np.array(embedding.decode('utf-8').split(','))
            embedding = np.expand_dims(embedding, axis=0).astype(np.float32)
        return embedding

    def scan_start_stop(self, name):
        nu = self.conn.table(name=name).scan(row_start='000001', row_stop='000011')
        play_counts_list = []
        play_times_list = []
        for i in nu:
            if b'play:duration' in i[1].keys():
                play_times_list.append({
                    'content_id': int(self.b2str(i[1][b'video:content_id'])),
                    'play_time': int(self.b2str(i[1][b'play:duration'])),
                })
            else:
                play_counts_list.append({
                    'content_id': int(self.b2str(i[1][b'video:content_id'])),
                    'play_counts': int(self.b2str(i[1][b'play:times'])),
                })

        return play_counts_list, play_times_list

    def parse(self, name):
        nu = self.conn.table(name).scan()
        return [
            {
                'content_id': self.b2str(i[0]),
                'play_time': int(self.b2str(i[1][b'play:duration'])),
                'play_counts': int(self.b2str(i[1][b'play:times'])),
            } for i in nu if i
        ]

    def parse_data(self, name):
        data = self.parse(name)
        sorted_time = sorted(data, key=lambda x: x['play_time'], reverse=True)[:10]
        sorted_counts = sorted(data, key=lambda x: x['play_counts'], reverse=True)[:10]
        # 播放时长排行前10
        time_x_data = [i.get('content_id') for i in sorted_time]
        time_y_data = [{
            'value': v.get('play_time'),
            'name': v.get('content_id'),
            'itemStyle': {
                'color': color_list[k]
            }
        } for k, v in enumerate(sorted_time)]
        counts_x_data = [i.get('content_id') for i in sorted_counts]
        counts_y_data = [{
            'value': v.get('play_counts'),
            'name': v.get('content_id'),
            'itemStyle': {
                'color': color_list[k]
            }
        } for k, v in enumerate(sorted_counts)]
        return {
            'time_x_data': time_x_data,
            'time_y_data': time_y_data,
            'counts_x_data': counts_x_data,
            'counts_y_data': counts_y_data,
        }


if __name__ == '__main__':
    hap = HappyHbase(host='10.20.36.137', port=19090)
    # d = {
    #     'user': dict(),
    #     'info': dict(),
    # }
    # hap.creat('test_3', d)
    # print(hap.list_tables())
    # table_name = b"test_3"
    # date = {
    #     b'user': b'zhangchunyang',
    #     b'info:address': b'bj',
    #     b'info:sex': b'f',
    # }
    # hap.put(b"test_3", b"1", {b"user": b"zhangchunyang", b"info:add": b"kskdskf", b"info:sex": b"nan"})

    # print(hap.table("test_3"))
    # print(hap.families('video'))
    # print(hap.scan(b'video'))
    # data = hap.parse(b'video')
    # print(hap.parse_data(data))
    # print(hap.list_tables())
    user_embedding = hap.eb_scan_start_stop('user', '000005', '000006')
    print(user_embedding)
    hap.close()
    movie_index = faiss.read_index('/opt/cili/data/faiss-movie.index')
    topk = 100
    D, I = movie_index.search(user_embedding, topk)
    print(I)
