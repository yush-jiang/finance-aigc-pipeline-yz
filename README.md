# Finance AIGC Pipeline

## 介绍

目标还是通过大模型，针对股市收盘的场景，给一些热门股票生成股市收评，能够批量生产。

## 代码结构

代码放在自己名字的文件下下面即可，Resource文件夹下，放置一些必要的资源文件，以及一些学习的资料，仅供阅读。

## 环境以及语言

1. 编程语言不限，选择自己熟练的编程语言即可。
2. 金融数据接口采用MSN Fiance的公开API
3. 数据库存储暂时采用文档或者CSV格式存储在本地,如果同学本身有数据库方面的基础，也可以存储在数据库中。此处不做强制要求

## Week 1

### Git
参考Resource文件夹下面的相关资源学习git基本知识，要求能在文件夹下提交一次文件作为完成标志。
Note: git的教程关注的点是git很多的常用命令，这里自己区分一下对于自己在已有仓库的基础上如何提交代码, 也可以不参考资料，直接查阅相关内容。

### 大模型选择
参考Resource文件夹下面的相关资源学习，要求是注册好账号，并且拿到ApiKey以及Endpoint，能够通过代码跟大模型Say hello，并拿到回复。

### HTTP/HTTPS request & json format
参考Resource文件夹下面的相关资源学习，要求能够理解get请求，理解请求参数的含义以及格式，在后面的学习过程中还会涉及如何处理数据请求。

## Week 2
1. 完成金融数据的接口集成，能够获取包括Quotes，Feeds两个数据
    - 具体的api信息参考Resource 文件夹下面的FinanceApi文档
2. 构建Prompt template，结合数据进行测试，要求如下：
    1. 输出内容需要包括一个Title，一个Summary body，一个Poll Question and 3 options
    2. 需要有内容校验，生成的内容格式不合规，需要抛弃，重新生成
3. 理解Api请求里面的Role，构建第一版Prompt，写入到PromptV1文件中 (Resource文件夹)
4. 理解常用的参数信息，以及含义。
5. 预期的输出结果 仅供参考：
```
<Title>Company Performance Today: Is AMD a Good Investment?</Title> 
<Content> Today, AMD opened at 84.47 and closed at 82.67, which is a 1.6185% decrease from the previous close. The 52 week high is 125.67 and the 52 week low is 54.57. Meanwhile, the NASDAQ Composite Index opened at 11325.36 and closed at 11138.888, which is a 1.7592% decrease from the previous close. The 52 week high is 14646.902 and the 52 week low is 10088.828. Wall Street analysts are debating whether Advanced Micro (AMD) is a good investment. There are also predictions for AMD, SPY, and JD stocks. In addition, Nvidia and AMD are grappling with the latest U.S. curbs on China's Inspur. AMD is also offering The Last of Us for free. Finally, AMD has effectively announced a $100 price cut for the RX 7900 XT. What do you think about AMD's performance today? Do you think AMD is a good investment? What do you think about the news headlines and the $100 price cut?</Content>
<Poll> 
<Question>Do you think AMD is a good investment?</Question>
 <Answer>Yes</Answer> 
<Answer>No</Answer> 
<Answer>Not Sure</Answer> 
</Poll>
```

## Week 3

TBD

## Week 4
1. 批量执行，生成的内容写入CSV中，保存在本地

扩展：
1. 代码的重用性，如何构建代码，让他可以快速的集成更多的场景，代码修改量少。
2. 定时任务
3. 数据库存储
etc