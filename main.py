import os
import requests
from openai import OpenAI

# 1. 금고(Secrets)에서 열쇠 꺼내기
# os.environ['이름']이 금고에 적은 이름표와 정확히 같아야 함
OPENAI_KEY = os.environ.get('OPENAI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
NEWS_KEY = os.environ.get('NEWS_API_KEY')

client = OpenAI(api_key=OPENAI_KEY)

def get_news():
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&apikey={NEWS_KEY}'
    r = requests.get(url).json()
    news_list = []
    if 'feed' in r:
        for item in r['feed'][:5]:
            news_list.append(f"제목: {item['title']}\n요약: {item['summary']}")
        return "\n\n".join(news_list)
    return None

def summarize(text):
    # GPT-4o 모델 사용
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "너는 15년차 개인 투자자야. 말투는 짧고 단정하게, 반말 70% + 존댓말 30%를 섞어서 써줘. 정답보다 확률을 줄여주는 관점에서 요약해."},
            {"role": "user", "content": f"다음 미국 뉴스를 스레드 스타일(제목 후킹, 인사이트, 내용 요약)로 500자 이내 요약해줘:\n\n{text}"}
        ]
    )
    return response.choices[0].message.content

def send_msg(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': CHAT_ID, 'text': msg})

# 실행부
if __name__ == "__main__":
    news_data = get_news()
    if news_data:
        summary = summarize(news_data)
        send_msg(summary)
    else:
        send_msg("가져온 뉴스가 없어. 시장 휴장 여부를 확인해봐.")
