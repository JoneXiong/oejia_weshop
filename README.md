## oejia_weshop
Odoo 微信小程序商城模块

oejia_weshop 是 Odoo 对接微信小程序实现的商城应用。

如果您使用odoo的销售模块，而想要在微信小程序上实现自己的商城卖odoo里的商品，装上 oejia_weshop 模块即可。

如果您想要搭建一套进销存(ERP)系统并实现对接微信商城的管理，用 Odoo + oejia_weshop 模块，是个快捷方法。

## 特性
* 和 odoo 销售模块无缝集成，产品和订单统一管理
* 微信用户集成到 odoo 统一的客户（partner）管理
* 支持 Odoo 10.0、11.0

## 使用
1. 下载源码
2. 将整个oejia_weshop 目录放到你的 addons 目录下
3. 安装模块，可以看到产生了顶部“小程”主菜单
4. 进入【设置】-【对接设置】页填写你的微信小程序相关对接信息
5. 小程序客户端: 使用的开源项目 [wechat-app-mall](https://github.com/EastWorld/wechat-app-mall), 下载后修改接口api调用路径为您的odoo url即可

## 效果
![用户管理](http://oejia.net/files/201809/13165725703.jpeg)

![产品管理](http://oejia.net/files/201809/13172849146.jpeg)

![对接配置](http://oejia.net/files/201809/13165316092.jpeg)

![小程序客户端](http://oejia.net/files/201809/13172406513.jpeg)


![我的订单](http://oejia.net/files/201809/13172524213.jpeg)


<figure class="half">
    <img src="http://oejia.net/files/201809/13172406513.jpeg" width="100">
    <img src="http://oejia.net/files/201809/13172524213.jpeg" width="100">
</figure>
