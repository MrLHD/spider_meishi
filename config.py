MONGO_URL = '192.168.1.11'
MONGO_Port = 27017
MONGO_DB = 'taobao'
MONGO_TABLE = 'product'
#这里我们搜索美食，当然也可以搜索别的，因为框架都是一样的。
KEYWORD = '美食'
#使用PhantomJS让浏览器不加载图片默认是加载，还有启用硬盘缓存
SERVICE_ARGS = ['--load-images=false','--disk-cache=true']
