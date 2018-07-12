
[公司註冊處綜合資訊系統](https://www.icris.cr.gov.hk/csci/)(ICRIS)爬虫

- 根据[给定的公司编号范围](./IcrisCrawler/settings.py)进行自动登陆和爬取
- 现有代码依赖[FP-Server](https://github.com/Karmenzind/fp-server)提供代理
- 爬取速度与代理质量呈正相关，可自行更换代理中间件以采用更高质量代理


Points:

- 基于内置CookiesMiddleware的[Cookie池中间件](./IcrisCrawler/middlewares.py)，用随机代理作为CookieJarKey
    - 新IP自动登陆，对应唯一Cookies
    - 验证、记错、淘汰、数量控制机制
