#### 这里学习怎么维护一个代理池

这个project会经常更新，毕竟我也是要用的

4大模块：
1. 存储模块 db.py : 负责保存抓下来的代理，保证代理不重复，并且标出代理的可使用情况，使用redis的Sorted Set
2. 获取模块 crawler.py: 定时在各大网站中抓取代理，(目前以公开的为主，尽量选取高匿代理)
3. 检测模块 tester.py : 定时检测数据库中的代理，设置代理的状态：100分为可用，检测一次不可用则减1分，低于50分则删除出数据库；检测一次可用则直接变成100分；未检测的新代理初始得分80分。
4. 接口模块 api.py: 对外提供Web API作为接口, 通过随机返回代理的方式获得可用代理的接口，实现「均衡负载」