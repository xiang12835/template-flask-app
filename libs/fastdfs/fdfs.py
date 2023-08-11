

import os

from fdfs_client.client import get_tracker_conf, Fdfs_client

from base.settings import BASE_DIR


class FastDFSStorage:
    """
    自定义文件上传类
    """

    def __init__(self, conf_path=None, ip=None):
        if conf_path is None:
            conf_path = os.path.join(BASE_DIR, 'libs/fastdfs/client.conf')
            # print(conf_path)
        self.tracker_path = get_tracker_conf(conf_path)

        if ip is None:
            ip = '设置一个默认的IP，防止么有IP的情况'
        self.ip = ip

    def _save(self, file_path):

        # 创建client对象
        client = Fdfs_client(self.tracker_path)
        # 获取文件
        # with open(file_path, 'rb') as f:
        #     file_data = f.read()
        # # 上传
        # result = client.upload_by_buffer(file_data)  # 需要在url加上文件的后缀
        result = client.upload_by_filename(file_path)

        # 判断上传结果
        if result.get('Status') == 'Upload successed.':
            print(result)
            # 返回上传的字符串
            return result.get('Remote file_id')
        else:
            raise Exception('上传失败')

    def url(self, file_path):
        # 返回文件的完整URL路径
        return self.ip + str(self._save(file_path), encoding='utf-8')

# print(FastDFSStorage().url('./yb.png'))
