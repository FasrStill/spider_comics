# -*-coding:utf-8-*-
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from multiprocessing import Pool
from lxml import etree
import requests, os, re


def get_index_page(offset):
    url = 'http://*****/****manhua/list_4_%s.html' % offset
    try:
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        if response.status_code == 200:
            return response.text
        print('链接返回出现异常')
        return None
    except RequestException:
        print('爬虫出现异常')
        return None


def parser_index_page(html):
    soup = BeautifulSoup(html, 'lxml')
    listcon_tag = soup.find('ul', class_='listcon')
    if listcon_tag:
        url_list = listcon_tag.find_all('a', attrs={'href': True})
        if url_list:
            urls = ['http://www.svmhz.com' + url['href'] for url in url_list]
            return urls


def get_image_page(url, total):
    list_url = []
    list_url.append(url)
    url = url.split('.html', 2)[0]
    for i in range(2, total+1):
        urls = url + '_' + str(i) + '.html'
        list_url.append(urls)
    return list_url


def parser_image_page(url):
    try:
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        if response.status_code == 200:
            html = response.text
            htmls = etree.HTML(html)
            total = htmls.xpath('//*[@id="mh_content"]/div[@class="dede_pages_all"]/div/ul/li[1]/a/text()')[0]
            if total:
                return total
        print('链接异常')
        return None
    except RequestException:
        print('爬虫异常')
        return None


def get_image_src(url):
    try:
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        if response.status_code == 200:
            return response.text
        print('链接异常')
        return None
    except RequestException:
        print('爬虫异常')
        return None


def parser_img_src(html):
    soup = BeautifulSoup(html, 'lxml')
    titles = soup.select('title')[0].get_text()
    title_page = titles.split('_', 2)[0]
    title = title_page.split('(', 2)[0]
    img_span = soup.find('ul', {'class': 'mnlt'})
    if img_span:
        img_src = img_span.find_all('img', src=re.compile('^http://tu.goldlevi.com/svmhz/uploads2/allimg/[0-9]{1,}/(.*?).jpg$'))
        if img_src:
            for url in img_src:
                urls = url['src']
                down_image(urls, title, titles)


def down_image(url, title, titles):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_image(response.content, title, url, titles)
        print('链接异常')
        return None
    except RequestException:
        print('爬虫异常')
        return None


def save_image(content, title, url, titles):
    path = 'F:/pic/' + str(title)
    if not os.path.exists(path):
        os.mkdir(path)
    file_name = '{0}/{1}.{2}'.format(path, titles, '.jpg')
    if not os.path.exists(file_name):
        with open(file_name, 'wb') as f:
            f.write(content)
            print('保存漫画成功', title, url)
            f.close()


def main(offset):
    html = get_index_page(offset)
    for url in parser_index_page(html):
        html = parser_image_page(url)
        total = int(re.compile('(\d+)').search(html).group(1))
        for img_url in get_image_page(url, total):
            htmls = get_image_src(img_url)
            parser_img_src(htmls)


if __name__ == '__main__':
    groups = [x for x in range(1, 86)]
    pool = Pool()
    pool.map(main, groups)