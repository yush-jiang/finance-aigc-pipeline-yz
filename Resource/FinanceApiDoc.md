# Fiance Api document

## Quotes Api
Qoutes api 主要包含股票的实时价格信息，包括开盘价，当前价格，收盘价，最高最低价等等

### 具体的请求信息：
Endpoint: https://assets.msn.com/service/Finance/Quotes

Method: **Get request**

Required property( **key - value**):
- apiKey:0QfOX3Vn51YCzitbLaRkTTBadtWpgTN8NZLW0C1SEM
- ocid: finance-utils-peregrine
- cm: en-us
- ids: {stock Id list}
- wrapodata: false (by default, use false)

Sample request:
https://assets.msn.com/service/Finance/Quotes?apikey=0QfOX3Vn51YCzitbLaRkTTBadtWpgTN8NZLW0C1SEM&activityId=02BAC3B4-4FF9-46B0-AEF6-AA414576FE1B&ocid=finance-utils-peregrine&cm=en-us&it=web&scn=ANON&ids=a1u3rw,a1nhlh,a1xzim,a24kar,a1mou2,a1slm7,a3oxnm,a1u3p2,a6qja2,c2111,c2112,c2113,a33k6h,a1ndlh,c2114,a1tyxm,c2117,a1sjw7,auvwzr,auvwoc,c2115,c2116,a23www,a1o79c,a1yv52,a23rm7,a269ec,bjqejc,a1ndww,a1zqnm,a1waa2,a1ythw,axyhnm,a1o4sm,auvwr7,a1vmf2,a1tyrw&wrapodata=false


Sample Entity Response:
```
{
  "price": 168.95,
  "priceChange": -0.28,
  "priceDayHigh": 169.43,
  "priceDayLow": 167.16,
  "timeLastTraded": "2024-11-29T21:59:52.642Z",
  "priceDayOpen": 168.5,
  "pricePreviousClose": 169.23,
  "datePreviousClose": "2024-11-27T00:00:00Z",
  "priceAsk": 168.95,
  "askSize": 1,
  "priceBid": 168.91,
  "bidSize": 1,
  "accumulatedVolume": 14257244,
  "averageVolume": 29837690,
  "peRatio": 22.4069,
  "priceChangePercent": -0.1655,
  "price52wHigh": 191.75,
  "price52wLow": 127.9,
  "priceClose": 168.95,
  "yieldPercent": 0.4727,
  "priceChange1Week": 4.19,
  "priceChange1Month": -2.16,
  "priceChange3Month": 5.57,
  "priceChange6Month": -3.55,
  "priceChangeYTD": 29.26,
  "priceChange1Year": 37.09,
  "return1Week": 2.5431,
  "return1Month": -1.2623,
  "return3Month": 3.4092,
  "return6Month": -2.058,
  "returnYTD": 20.9464,
  "return1Year": 28.1283,
  "sourceExchangeCode": "XNAS",
  "sourceExchangeName": "Nasdaq Stock Market",
  "icon": "https://bing.com/th?id=OSK.QaqQLH8CKdKQjoy2locprcJquIjVkEDHdW8DJJwPjDg",
  "preMarketTradeTime": "2024-11-29T14:30:00.941331Z",
  "postMarketTradeTime": "2024-11-29T21:59:52.6422367Z",
  "marketCap": 2078499000000,
  "marketCapCurrency": "USD",
  "exchangeId": "r6dwop",
  "exchangeCode": "XNAS",
  "exchangeName": "Nasdaq Stock Market",
  "offeringStatus": "regular",
  "displayName": "Alphabet Inc",
  "shortName": "Alphabet",
  "securityType": "stock",
  "instrumentId": "a1u3rw",
  "symbol": "GOOGL",
  "country": "US",
  "market": "en-us",
  "localizedAttributes": {
    "en-us": {
      "displayName": "ALPHABET INC."
    }
  },
  "timeLastUpdated": "2024-12-02T02:47:45.4457084Z",
  "currency": "USD",
  "_p": "a1u3rw",
  "id": "37fdd5d1-42d5-427a-85d5-0b2284e02cba",
  "_t": "Quote"
}
```




## Feed api
金融咨询的Feed流，主要是围绕某些场景下，渲染新闻资讯列表的API，

### 具体的请求信息

Endpoint: https://assets.msn.com/service/Finance/Quotes
Method: **Get request**

Required property( **key - value**):
- apiKey:0QfOX3Vn51YCzitbLaRkTTBadtWpgTN8NZLW0C1SEM
- ocid: finance-data-feeds
- top: 30 (Request entity count)
- contentType: article,video,slideshow,webcontent
- cm: en-us
- entityids: {stock Id}
- query: finance_stock
- wrapodata: false (by default, use false)

Sample Request:
https://assets.msn.com/service/MSN/Feed/me?$top=30&DisableTypeSerialization=true&apikey=0QfOX3Vn51YCzitbLaRkTTBadtWpgTN8NZLW0C1SEM&cm=en-us&contentType=article,video,slideshow,webcontent&entityids=a1u3rw&ocid=finance-data-feeds&query=finance_stock&responseSchema=cardview&scn=ANON&timeOut=3000&wrapodata=false

Sample Entity Response:

```
{
  "id": "AA1v5Moa",
  "type": "article",
  "title": "Analyst: Alphabet (GOOG) AI Overviews Impact Positive But Search Business ‘Not Out of The Woods Yet",
  "abstract": "We recently published a list of 10 Trending AI Stocks to Watch in December. In this article, we are going to take a look at where Alphabet Inc (NASDAQ:GOOG) stands against other trending AI stocks to watch in December. Jared Cohen, Goldman Sachs president of global affairs, co-head of the Goldman Sachs Global Institute, said […]",
  "readTimeMin": 6,
  "url": "https://www.msn.com/en-us/money/topstocks/analyst-alphabet-goog-ai-overviews-impact-positive-but-search-business-not-out-of-the-woods-yet/ar-AA1v5Moa",
  "locale": "en-us",
  "financeMetadata": {
    "stocks": [
      {
        "stockId": "a1u3p2",
        "score": 80000098
      },
      {
        "stockId": "a1u7xm",
        "score": 60000100
      }
    ],
    "sentimentRatings": [
      {
        "topic": "wf_sentiment_positive",
        "score": 9168
      },
      {
        "topic": "wf_sentiment_negative",
        "score": 294
      },
      {
        "topic": "wf_sentiment_neutral",
        "score": 536
      }
    ],
    "categories": [
      {
        "topic": "top stocks",
        "score": 10000
      }
    ]
  },
  "publishedDateTime": "2024-12-02T03:26:47Z",
  "isFeatured": false,
  "images": [
    {
      "width": 1920,
      "height": 1280,
      "url": "https://th.bing.com/th?id=ORMS.16a9a3c11bee1ac6954e2cdb3a9bea7b&pid=Wdp",
      "title": "Is Alphabet Inc (NASDAQ:GOOG) Trending AI Stock on Latest Analyst Ratings and News?",
      "caption": "Is Alphabet Inc (NASDAQ:GOOG) Trending AI Stock on Latest Analyst Ratings and News?",
      "source": "msn",
      "colorSamples": [
        {
          "isDarkMode": true,
          "hexColor": "#614624"
        },
        {
          "isDarkMode": false,
          "hexColor": "#F5E8DD"
        }
      ]
    }
  ],
  "colorSamples": [
    {
      "isDarkMode": true,
      "hexColor": "#614624"
    },
    {
      "isDarkMode": false,
      "hexColor": "#F5E8DD"
    }
  ],
  "provider": {
    "id": "AA1nwXcJ",
    "name": "Insider Monkey",
    "logoUrl": "https://img-s-msn-com.akamaized.net/tenant/amp/entityid/AA1nEZLu.img",
    "profileId": "vid-gagmsykmdy5sdenk6w0ctuws7r8p6e5h8ws3sgeyauu5i8c7yfea"
  },
  "category": "money",
  "reactionSummary": {
    "totalCount": 0
  },
  "reactionStatus": "on",
  "commentStatus": "off",
  "relevanceScore": 10094,
  "subscriptionProductType": "undefined",
  "feed": {
    "id": "Y_f714b6e2-e9db-41d0-9b5f-b2e0a52f85da",
    "feedName": "Money"
  },
  "topics": [
    {
      "label": "Money",
      "weight": 0.8912153840065002,
      "feedId": "Y_f714b6e2-e9db-41d0-9b5f-b2e0a52f85da",
      "locale": "en-us"
    },
    {
      "label": "Business",
      "weight": 0.8912153840065002,
      "feedId": "Y_367b7be1-6bd2-44e7-95b3-b0d077ccc28d",
      "locale": "en-us"
    },
    {
      "label": "News",
      "weight": 0.6737902164459229,
      "feedId": "Y_9eb0ac10-32bc-43cf-816e-5beaaf524f7a",
      "locale": "en-us"
    },
    {
      "label": "Technology",
      "weight": 0.6737902164459229,
      "feedId": "Y_d1cad308-780e-4a75-ba34-6460811ccfe3",
      "locale": "en-us"
    }
  ],
  "isWorkNewsContent": false,
  "recoId": "M8TTlqwkTMsQkCclJWLcwhgTga",
  "source": "msn"
}
```

这个API的结果，我们通常只关注三个字段，一个是他的简略内容abstract，还有他的新闻标题title，和具体的链接url，作为prompt的input参数。

