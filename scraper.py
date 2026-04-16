import asyncio
import json
import re
from datetime import datetime, timezone, timedelta
from playwright.async_api import async_playwright

KST = timezone(timedelta(hours=9))

SITES = [
    {
        "name": "타이탄클래스",
        "url": "https://www.titanclass.co.kr/free-courses",
        "selectors": [".course-card", ".card", "[class*='course']", "[class*='lecture']", "article"],
        "title_sel": ["h3", "h2", ".title", "[class*='title']", "[class*='name']"],
        "date_sel": ["[class*='date']", "[class*='schedule']", "[class*='time']", "time"],
    },
    {
        "name": "코주부클래스",
        "url": "https://www.cojooboo.co.kr/courses?courseType=FREE",
        "selectors": [".course-card", ".card", "[class*='course']", "article", "li"],
        "title_sel": ["h3", "h2", ".title", "[class*='title']"],
        "date_sel": ["[class*='date']", "[class*='schedule']", "time"],
    },
    {
        "name": "아이비클래스",
        "url": "https://www.ivyclass.co.kr/courses",
        "selectors": [".course-card", ".card", "[class*='course']", "article"],
        "title_sel": ["h3", "h2", ".title", "[class*='title']"],
        "date_sel": ["[class*='date']", "[class*='schedule']", "time"],
    },
    {
        "name": "인베이더스쿨",
        "url": "https://www.invader.co.kr/courses",
        "selectors": [".course-card", ".card", "[class*='course']", "article"],
        "title_sel": ["h3", "h2", ".title", "[class*='title']"],
        "date_sel": ["[class*='date']", "[class*='schedule']", "time"],
    },
    {
        "name": "밀레니얼머니스쿨",
        "url": "https://millmus.com/lecture/coin/1",
        "selectors": [".lecture-item", ".card", "[class*='lecture']", "[class*='item']", "li", "article"],
        "title_sel": ["h3", "h2", "h4", ".title", "[class*='title']"],
        "date_sel": ["[class*='date']", "[class*='time']", "time"],
    },
    {
        "name": "시행착오",
        "url": "https://shco.co.kr/66",
        "selectors": ["article", ".post", ".entry", "[class*='post']", "li", ".item"],
        "title_sel": ["h2", "h3", ".entry-title", "[class*='title']"],
        "date_sel": [".date", "[class*='date']", "time", ".published"],
    },
    {
        "name": "엔잡연구소",
        "url": "https://www.nlab.kr/courses?categoryId=free-courses",
        "selectors": [".course-card", ".card", "[class*='course']", "article"],
        "title_sel": ["h3", "h2", ".title", "[class*='title']"],
        "date_sel": ["[class*='date']", "[class*='schedule']", "time"],
    },
    {
        "name": "핏크닉",
        "url": "https://www.fitchnic.com/free-courses",
        "selectors": [".course-card", ".card", "[class*='course']", "article", "li"],
        "title_sel": ["h3", "h2", ".title", "[class*='title']"],
        "date_sel": ["[class*='date']", "[class*='schedule']", "time"],
    },
    {
        "name": "머니업클래스",
        "url": "https://www.moneyupclass.com/free-courses",
        "selectors": [".course-card", ".card", "[class*='course']", "article"],
        "title_sel": ["h3", "h2", ".title", "[class*='title']"],
        "date_sel": ["[class*='date']", "[class*='schedule']", "time"],
    },
    {
        "name": "사이클해커스",
        "url": "https://cyclehackers.com/",
        "selectors": [".course-card", ".card", "[class*='course']", "[class*='lecture']", "article", "li"],
        "title_sel": ["h3", "h2", "h4", ".title", "[class*='title']"],
        "date_sel": ["[class*='date']", "[class*='schedule']", "time"],
    },
    {
        "name": "황금후추",
        "url": "https://www.goldpepper.kr/103/",
        "selectors": ["article", ".post", "li", "[class*='post']", "[class*='item']"],
        "title_sel": ["h2", "h3", ".title", "[class*='title']", "strong"],
        "date_sel": ["[class*='date']", "time", ".date", ".published"],
    },
    {
        "name": "터닝포인트스쿨",
        "url": "https://www.tpschool.co.kr/p/webinar",
        "selectors": [".webinar-item", ".card", "[class*='webinar']", "[class*='event']", "article", "li"],
        "title_sel": ["h3", "h2", "h4", ".title", "[class*='title']"],
        "date_sel": ["[class*='date']", "[class*='schedule']", "[class*='time']", "time"],
    },
    {
        "name": "아마겟돈클래스",
        "url": "https://amag-class.kr/Free-Class",
        "selectors": [".card", "[class*='class']", "[class*='course']", "article", "li"],
        "title_sel": ["h3", "h2", "h4", ".title", "[class*='title']"],
        "date_sel": ["[class*='date']", "[class*='schedule']", "time"],
    },
    {
        "name": "돈버는클래스",
        "url": "https://donclass.liveklass.com/p/donbropage",
        "selectors": [".card", "[class*='class']", "[class*='course']", "[class*='lecture']", "article", "li"],
        "title_sel": ["h3", "h2", "h4", ".title", "[class*='title']"],
        "date_sel": ["[class*='date']", "[class*='schedule']", "time"],
    },
    {
        "name": "래피드클래스",
        "url": "https://rapidclass.co.kr/search?categoryId=qrm00hkmg69hyp8jbdyqa579&searchTitle=%EB%AC%B4%EB%A3%8C%EA%B0%95%EC%9D%98",
        "selectors": [".course-card", ".card", "[class*='course']", "article", "li"],
        "title_sel": ["h3", "h2", ".title", "[class*='title']"],
        "date_sel": ["[class*='date']", "[class*='schedule']", "time"],
    },
    {
        "name": "머니루트",
        "url": "https://moneyroot.co.kr/lectures/free",
        "selectors": [".lecture-card", ".card", "[class*='lecture']", "[class*='course']", "article", "li"],
        "title_sel": ["h3", "h2", "h4", ".title", "[class*='title']"],
        "date_sel": ["[class*='date']", "[class*='schedule']", "time"],
    },
    {
        "name": "피터팬스쿨",
        "url": "https://www.peterpanschool.co.kr/courses/free",
        "selectors": [".course-card", ".card", "[class*='course']", "article", "li"],
        "title_sel": ["h3", "h2", ".title", "[class*='title']"],
        "date_sel": ["[class*='date']", "[class*='schedule']", "time"],
    },
    {
        "name": "프레스런",
        "url": "https://presslearn.co.kr/fc",
        "selectors": [".card", "[class*='course']", "[class*='lecture']", "article", "li"],
        "title_sel": ["h3", "h2", "h4", ".title", "[class*='title']"],
        "date_sel": ["[class*='date']", "[class*='schedule']", "time"],
    },
    {
        "name": "인사이트머니랩",
        "url": "https://insightmoneylab.com/course-category/free-class/",
        "selectors": ["article", ".course", ".card", "[class*='course']", "li"],
        "title_sel": ["h2", "h3", ".entry-title", "[class*='title']"],
        "date_sel": ["[class*='date']", "time", ".date", ".published"],
    },
    {
        "name": "온부자",
        "url": "https://www.onbuja.com/courses?courseType=FREE",
        "selectors": [".course-card", ".card", "[class*='course']", "article", "li"],
        "title_sel": ["h3", "h2", ".title", "[class*='title']"],
        "date_sel": ["[class*='date']", "[class*='schedule']", "time"],
    },
    {
        "name": "클래스101",
        "url": "https://class101.net/ko/live",
        "selectors": ["[class*='ProductCard']", "[class*='card']", "[class*='live']", "[class*='item']", "li"],
        "title_sel": ["[class*='title']", "[class*='Title']", "h3", "h2", "h4"],
        "date_sel": ["[class*='date']", "[class*='Date']", "[class*='schedule']", "time"],
    },
    {
        "name": "부자친구들",
        "url": "https://buchinclass.com/class?mainCategory=5",
        "selectors": [".class-card", ".card", "[class*='class']", "[class*='course']", "article", "li"],
        "title_sel": ["h3", "h2", "h4", ".title", "[class*='title']"],
        "date_sel": ["[class*='date']", "[class*='schedule']", "time"],
    },
]


def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip())


async def scrape_site(page, site):
    name = site["name"]
    url = site["url"]
    courses = []

    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        # 스크롤해서 lazy load 콘텐츠 로드
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        await page.wait_for_timeout(1000)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)

        # 카드 요소 찾기
        cards = []
        for sel in site["selectors"]:
            try:
                elements = await page.query_selector_all(sel)
                if elements and len(elements) >= 2:
                    cards = elements[:20]  # 최대 20개
                    break
            except:
                continue

        if not cards:
            # 카드를 못 찾으면 페이지 전체 텍스트에서 제목 추출
            body_text = await page.inner_text("body")
            lines = [l.strip() for l in body_text.split('\n') if len(l.strip()) > 10 and len(l.strip()) < 100]
            for line in lines[:10]:
                courses.append({
                    "title": line,
                    "date": "",
                    "link": url,
                    "thumbnail": ""
                })
        else:
            for card in cards:
                title = ""
                date = ""
                link = url
                thumbnail = ""

                # 제목 추출
                for sel in site["title_sel"]:
                    try:
                        el = await card.query_selector(sel)
                        if el:
                            t = await el.inner_text()
                            t = clean_text(t)
                            if t and len(t) > 2:
                                title = t
                                break
                    except:
                        continue

                if not title:
                    try:
                        title = clean_text(await card.inner_text())
                        title = title[:80] if title else ""
                    except:
                        pass

                # 날짜 추출
                for sel in site["date_sel"]:
                    try:
                        el = await card.query_selector(sel)
                        if el:
                            d = await el.inner_text()
                            d = clean_text(d)
                            if d:
                                date = d
                                break
                    except:
                        continue

                # 링크 추출
                try:
                    a = await card.query_selector("a")
                    if a:
                        href = await a.get_attribute("href")
                        if href:
                            if href.startswith("http"):
                                link = href
                            elif href.startswith("/"):
                                from urllib.parse import urlparse
                                parsed = urlparse(url)
                                link = f"{parsed.scheme}://{parsed.netloc}{href}"
                except:
                    pass

                # 썸네일 추출
                try:
                    img = await card.query_selector("img")
                    if img:
                        src = await img.get_attribute("src")
                        if src and not src.endswith(".svg"):
                            thumbnail = src if src.startswith("http") else url + src
                except:
                    pass

                if title and len(title) > 2:
                    courses.append({
                        "title": title,
                        "date": date,
                        "link": link,
                        "thumbnail": thumbnail
                    })

        print(f"✅ {name}: {len(courses)}개 수집")
        return {"name": name, "url": url, "courses": courses, "error": None}

    except Exception as e:
        print(f"❌ {name}: {e}")
        return {"name": name, "url": url, "courses": [], "error": str(e)}


async def main():
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="ko-KR"
        )

        for site in SITES:
            page = await context.new_page()
            result = await scrape_site(page, site)
            results.append(result)
            await page.close()
            await asyncio.sleep(1)

        await browser.close()

    output = {
        "updated_at": datetime.now(KST).strftime("%Y-%m-%d %H:%M"),
        "sites": results
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ data.json 저장 완료 — {sum(len(s['courses']) for s in results)}개 강의 수집")


if __name__ == "__main__":
    asyncio.run(main())
