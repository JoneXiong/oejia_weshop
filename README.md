## oejia_weshop

oejia_weshop（OE商城） 是一套包含强大电商ERP后台的小程序商城系统。

oejia_weshop 是 Odoo 对接微信小程序实现的商城应用。

如果您使用odoo的销售模块，而想要在微信小程序上实现自己的商城卖odoo里的商品，装上 oejia_weshop 模块即可。

如果您想要搭建一套进销存(ERP)系统并实现对接微信商城的管理，用 Odoo + oejia_weshop 模块，是个快捷方法。

## 特性
* 和 odoo 销售模块无缝集成，产品和订单统一管理
* 微信用户集成到 odoo 统一的客户（partner）管理
* 支持 Odoo 10.0、11.0、12.0

## 使用
1. 下载源码 (odoo10、11为master分支，odoo12为12.0分支）
2. 将整个oejia_weshop目录(名称不能变)放到你的 addons 目录下
3. 安装依赖的python库：xmltodict、pycrypto、itsdangerous；安装模块，可以看到产生了顶部“小程序”主菜单
4. 进入【设置】-【对接设置】页填写你的微信小程序相关对接信息
5. 小程序客户端: 见项目 [wechat-app-mall](https://github.com/JoneXiong/wechat-app-mall), 下载后修改接口api调用路径为您的odoo url即可，可参考[这里](https://github.com/JoneXiong/wechat-app-mall/blob/f2/README.md)修改

参考资料: [常见问题处理](http://oejia.net/blog/2018/12/21/oejia_weshop_qa.html)

## 试用

小程序客户端

![Odoo小程序商城](https://raw.githubusercontent.com/JoneXiong/oejia_weshop/master/static/description/odoo_wxapp.jpg)

Odoo后台

[https://sale.calluu.cn/](https://sale.calluu.cn/)

## 效果图

详见 [http://oejia.net/blog/2018/09/13/oejia_weshop_about.html](http://oejia.net/blog/2018/09/13/oejia_weshop_about.html)

![用户管理](http://oejia.net/files/201809/13165725703.jpeg)

![产品管理](http://oejia.net/files/201809/13172849146.jpeg)

![对接配置](http://oejia.net/files/201809/13165316092.jpeg)

![小程序客户端](http://oejia.net/files/201809/13172406513.jpeg)


![我的订单](http://oejia.net/files/201809/13172524213.jpeg)

## 商业版及扩展

商业扩展模块 [oejia_weshop_ent](https://www.calluu.cn/shop/product/odoo-12)

分销模块 [weshop_commission](https://www.calluu.cn/shop/product/odoo-23)

H5商城模块 [weshop_h5](https://www.calluu.cn/shop/product/odoo-h5-24)

OE商城系统（全功能进销存系统套件） [https://sale.calluu.cn/](https://sale.calluu.cn/)

## 交流
技术分享
[http://www.oejia.net/](http://www.oejia.net/)

Odoo-OpenERP扩展开发2群：796367461

Odoo-OpenERP扩展开发1群：260160505 (已满)
