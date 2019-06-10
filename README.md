## oejia_weshop
Odoo 微信小程序商城模块

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
5. 小程序客户端: 使用的开源项目 [wechat-app-mall](https://github.com/EastWorld/wechat-app-mall), 下载后修改接口api调用路径为您的odoo url即可，可参考[这里](https://github.com/JoneXiong/wechat-app-mall/pull/4/files)修改，也可使用我们[fork的版本](https://github.com/JoneXiong/wechat-app-mall)

- 只需将 wxapi/main.js 中的 API_BASE_URL 改为https://您的odoo地址 
- 将config.js中的subDomain改为您设置的小程序接口前缀 （“小程序接口前缀”为您在odoo后台对接配置中设置的值），appid 改为您的小程序的appid

参考资料: [常见问题处理](http://oejia.net/blog/2018/12/21/oejia_weshop_qa.html)

## 试用

小程序客户端

![官方小程序商城](http://oejia.net/files/201812/29163543453_gh_1fec54367c48_258.jpg)

Odoo后台

[https://sale.calluu.cn/](https://sale.calluu.cn/)

## 效果
![用户管理](http://oejia.net/files/201809/13165725703.jpeg)

![产品管理](http://oejia.net/files/201809/13172849146.jpeg)

![对接配置](http://oejia.net/files/201809/13165316092.jpeg)

![小程序客户端](http://oejia.net/files/201809/13172406513.jpeg)


![我的订单](http://oejia.net/files/201809/13172524213.jpeg)

## 商业版及扩展

扩展功能模块 [oejia_weshop_ent](https://www.calluu.cn/shop/product/odoo-12)

包含微信商城的全功能进销存系统套件 [https://sale.calluu.cn/](https://sale.calluu.cn/)

小程序客服集成 [http://oejia.net/blog/2018/12/21/odoo_kf.html](http://oejia.net/blog/2018/12/21/odoo_kf.html)


## 交流
技术分享
[http://www.oejia.net/](http://www.oejia.net/)

Odoo-OpenERP扩展开发2群：796367461

Odoo-OpenERP扩展开发1群：260160505 (已满)
