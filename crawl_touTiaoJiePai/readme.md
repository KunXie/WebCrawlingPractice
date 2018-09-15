This script downloading the street naps from [Toutiao](https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D)

现在的头条不太一样了，AJAX里面没有完整的图片url, 需要点进去找。


思路：
1. 分析ajax区别发现url中只有offset参数不同，可以通过传递offset参数来得到不同的ajax url
2. parse_ajax(): 对于每一个html，挑选出街拍组图的url，集合成list传递出去
3. get_image(): 对于每一个街拍组图的html，拿到图片的address 传递出去，这里我用了selenium，让整个抓取变得很慢，没办法，这样最容易拿到image address
4. save_image():  将images存起来