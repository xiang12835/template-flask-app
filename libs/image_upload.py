from qiniu import Auth, put_file, etag, urlsafe_base64_encode, put_data
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key
from utils.constants import QINIU_DOMIN_PREFIX

access_key = 'IGwLUvXx5BKXjW9pZwpyQVTvuDMIpxibqjCezh0q'
secret_key = '9Ttq77KTl-9DHUWMxRIxG_TjBeIBMQU6YtTa8i58'

# 构建鉴权对象
q = Auth(access_key, secret_key)

# 要上传的空间
bucket_name = 'cili-avatar'


token = q.upload_token(bucket_name, None, 3600)


def image_storage(image_data):
    # 上传图片
    ret, info = put_data(token, None, image_data)

    # 判断图片是否有上传成功
    if info.status_code == 200:
        return ret.get("key")
    else:
        return ""


if __name__ == '__main__':
    with open('图片名称', 'rb') as f:
        # print(image_storage(f.read()))
        image_name = image_storage(f.read())
    url = QINIU_DOMIN_PREFIX + image_name
    # print(url)
