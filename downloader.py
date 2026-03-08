import requests
from bs4 import BeautifulSoup
import threading
import queue
import os
import time
from urllib.parse import urljoin, urlparse
import re
import random
import json
import hashlib

class NovelDownloader:
    def __init__(self, base_url, novel_name, max_workers=5, max_pages=200, use_cache=True):
        """
        初始化小说下载器
        
        Args:
            base_url: 小说目录页URL
            novel_name: 小说名称，用于创建文件夹
            max_workers: 最大线程数
            max_pages: 最大分页数（目录页）
            use_cache: 是否使用缓存
        """
        self.base_url = base_url
        self.novel_name = novel_name
        self.max_workers = max_workers
        self.max_pages = max_pages  # 目录页最大分页数
        self.use_cache = use_cache  # 是否使用缓存
        self.chapter_queue = queue.Queue()  # 章节队列
        self.result_queue = queue.Queue()   # 结果队列
        
        # 丰富的User-Agent列表（比线程数多）
        self.user_agents = [
            # Windows Chrome 系列
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
            
            # Windows Edge 系列
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.38',
            
            # Windows Firefox 系列
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',
            
            # macOS Safari 系列
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
            
            # macOS Chrome 系列
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
            
            # Linux Chrome 系列
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            
            # Linux Firefox 系列
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
            
            # 移动端 User-Agent
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.115 Mobile Safari/537.36',
        ]
        
        # 初始化session但不设置固定的UA
        self.session = requests.Session()
        
        # 创建保存小说的目录
        self.save_dir = f"downloads/{novel_name}"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        # 创建缓存目录
        self.cache_dir = f"cache/{novel_name}"
        if self.use_cache and not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        # 创建进度记录文件
        self.progress_file = f"{self.save_dir}/download_progress.json"
        
        # 统计UA使用情况
        self.ua_counter = {}
        self.ua_lock = threading.Lock()
        
        # 已下载章节记录
        self.downloaded_chapters = set()
        self.downloaded_lock = threading.Lock()
        
        # 加载已下载的章节记录
        self.load_progress()
    
    def get_cache_path(self, url):
        """根据URL生成缓存文件路径"""
        # 对URL进行哈希处理，避免文件名过长
        #url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        # 提取URL中的路径部分作为可读标识
        parsed = urlparse(url)
        path_part = parsed.path.replace('/', '_').strip('_')
        #if len(path_part) > 50:
            #path_part = path_part[:50]
        # 组合文件名：可读部分_哈希值.html
        filename = f"{path_part}.html"
        return os.path.join(self.cache_dir, filename)
    
    def load_from_cache(self, url):
        """从缓存加载页面内容"""
        if not self.use_cache:
            return None
        
        cache_path = self.get_cache_path(url)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"从缓存加载: {url}")
                return content
            except Exception as e:
                print(f"读取缓存失败 {cache_path}: {e}")
        return None
    
    def save_to_cache(self, url, content):
        """保存页面内容到缓存"""
        if not self.use_cache or not content:
            return
        
        cache_path = self.get_cache_path(url)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(content)
            # print(f"已缓存: {url}")
        except Exception as e:
            print(f"保存缓存失败 {cache_path}: {e}")
    
    def load_progress(self):
        """加载下载进度"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                    self.downloaded_chapters = set(progress.get('downloaded', []))
                print(f"加载历史进度: 已下载 {len(self.downloaded_chapters)} 章")
            except Exception as e:
                print(f"加载进度文件失败: {e}")
    
    def save_progress(self):
        """保存下载进度"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'downloaded': list(self.downloaded_chapters)
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存进度文件失败: {e}")
    
    def is_chapter_downloaded(self, chapter_url):
        """检查章节是否已下载"""
        with self.downloaded_lock:
            return chapter_url in self.downloaded_chapters
    
    def mark_chapter_downloaded(self, chapter_url):
        """标记章节为已下载"""
        with self.downloaded_lock:
            self.downloaded_chapters.add(chapter_url)
            self.save_progress()
    
    def get_random_ua(self):
        """随机获取一个User-Agent"""
        return random.choice(self.user_agents)
    
    def get_ua_stats(self):
        """获取UA使用统计"""
        with self.ua_lock:
            return dict(self.ua_counter)
    
    def update_ua_stats(self, ua):
        """更新UA使用统计"""
        with self.ua_lock:
            self.ua_counter[ua] = self.ua_counter.get(ua, 0) + 1
    
    def get_page_content(self, url, encoding='utf-8', retry=3, use_cache=True):
        """
        获取页面内容，支持重试、随机UA和缓存
        
        Args:
            url: 要访问的URL
            encoding: 页面编码
            retry: 重试次数
            use_cache: 是否使用缓存
        """
        # 尝试从缓存加载
        if use_cache and self.use_cache:
            cached_content = self.load_from_cache(url)
            if cached_content:
                return cached_content
        
        for attempt in range(retry):
            try:
                # 每次请求都随机选择新的UA
                current_ua = self.get_random_ua()
                self.session.headers.update({
                    'User-Agent': current_ua,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                })
                
                # 更新统计
                self.update_ua_stats(current_ua)
                
                #print(f"正在访问: {url} (UA: {current_ua[:50]}...)")
                
                # 添加随机延迟，避免请求过快
                time.sleep(random.uniform(0.5, 1))
                
                response = self.session.get(url, timeout=15)
                response.encoding = encoding
                
                # 检查响应状态
                if response.status_code == 200:
                    #print(f"页面大小: {len(response.text)} 字符")
                    content = response.text
                    
                    # 保存到缓存
                    if use_cache and self.use_cache:
                        self.save_to_cache(url, content)
                    
                    return content
                elif response.status_code == 403:
                    print(f"被拒绝访问 (403)，尝试更换UA... 第{attempt + 1}次")
                elif response.status_code == 429:
                    wait_time = random.uniform(3, 8)
                    print(f"请求过于频繁 (429)，等待 {wait_time:.1f} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"HTTP错误: {response.status_code}，第{attempt + 1}次")
                
            except requests.exceptions.ConnectionError as e:
                print(f"连接错误: {e}，第{attempt + 1}次")
            except requests.exceptions.Timeout as e:
                print(f"超时错误: {e}，第{attempt + 1}次")
            except Exception as e:
                print(f"未知错误: {e}，第{attempt + 1}次")
            
            # 重试前等待随机时间
            if attempt < retry - 1:
                wait_time = random.uniform(1, 3)
                print(f"等待 {wait_time:.1f} 秒后重试...")
                time.sleep(wait_time)
        
        print(f"所有重试都失败: {url}")
        return None
    
    def debug_page_structure(self, html_content):
        """
        调试页面结构，打印可能的章节链接
        """
        return
        # 原有的调试代码保持不变
        soup = BeautifulSoup(html_content, 'html.parser')
        
        print("\n=== 页面调试信息 ===")
        
        # 打印所有链接
        all_links = soup.find_all('a')
        print(f"页面中共有 {len(all_links)} 个链接")
        
        # 查找可能的章节容器
        possible_containers = [
            soup.find('div', id='list'),
            soup.find('div', class_='listmain'),
            soup.find('div', class_='chapter-list'),
            soup.find('ul', class_='chapter'),
            soup.find('div', id='chapter-list'),
            soup.find('div', class_='book-list'),
            soup.find('div', id='readerlists'),
        ]
        
        print("\n可能的章节容器:")
        for container in possible_containers:
            if container:
                print(f"找到容器: {container.name} - class/id: {container.get('class', container.get('id', '无'))}")
                # 打印容器中的前5个链接
                links = container.find_all('a')
                print(f"  该容器中有 {len(links)} 个链接")
                
        # 查找下一页链接（目录分页）
        next_selectors = [
            soup.find('a', string=re.compile(r'下一页|下页|next|>|下—页')),
            soup.find('a', class_='next'),
            soup.find('a', id='next'),
            soup.find('a', rel='next'),
        ]
        
        print("\n下一页链接（目录分页）:")
        for selector in next_selectors:
            if selector:
                print(f"找到: {selector.get_text()} -> {selector.get('href', '')}")
        
        print("===================\n")
    
    def parse_chapter_list(self, html_content):
        """
        解析目录页面，获取所有章节链接
        需要根据具体网站结构调整选择器
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        chapters = []
        
        # 首先调试页面结构
        self.debug_page_structure(html_content)
        
        # 扩展的选择器列表
        selectors = [
            # 常见的小说目录选择器
            '#list dd a',
            '#list a',
            '.listmain dd a',
            '.listmain a',
            '.chapter-list dd a',
            '.chapter-list a',
            '.chapter a',
            '.book-list a',
            '#readerlists a',
            '.catalog a',
            '.volume a',
            'ul.chapter li a',
            '.chapterlist a',
            '.dir-list a',
            '.novel-list a',
            '.article-list a',
            '.text-list a',
            '.main-content a',
            '.content a',
        ]
        
        # 如果上面的选择器都没找到，尝试查找所有链接
        found_chapters = False
        for selector in selectors:
            chapter_links = soup.select(selector)
            if chapter_links and len(chapter_links) > 0:
                print(f"使用选择器 '{selector}' 找到 {len(chapter_links)} 个链接")
                
                for link in chapter_links:
                    href = link.get('href')
                    if href:
                        # 构建完整URL
                        full_url = urljoin(self.base_url, href)
                        title = link.get_text().strip()
                        
                        # 过滤掉非章节链接
                        if title and len(title) < 50:
                            # 检查是否像是章节标题（包含第、章等关键词）
                            if (any(key in title for key in ['第', '章', '节', '卷',"番外","结局"]) or re.match(r'\d+(.|)',title)) or not found_chapters:
                                chapters.append({
                                    'title': title,
                                    'url': full_url
                                })
                
                if len(chapters) > 0:
                    found_chapters = True
                    break
        
        # 如果还是没有找到，尝试获取所有链接
        if not found_chapters:
            print("尝试获取所有链接...")
            all_links = soup.find_all('a')
            for link in all_links:
                href = link.get('href')
                text = link.get_text().strip()
                
                if href and text and len(text) < 50 and len(text) > 2:
                    # 检查是否包含常见的小说关键词
                    novel_keywords = ['第', '章', '节', '卷', '序', '引子',"结局","番外", '楔子', '后记', '尾声']
                    if any(keyword in text for keyword in novel_keywords) or re.match(r'\d+(.|)',text):
                        full_url = urljoin(self.base_url, href)
                        chapters.append({
                            'title': text,
                            'url': full_url
                        })
        
        return chapters
    
    def parse_next_page(self, html_content, current_url):
        """
        解析下一页链接（目录分页）
        需要根据具体网站结构调整
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 扩展下一页选择器
        next_patterns = [
            # 常见的下一页选择器
            '.next',
            '#next',
            '.pagination .next',
            'a:contains("下一页")',
            'a:contains("下—页")',
            'a:contains("下页")',
            'a:contains(">")',
            'a:contains("»")',
            'a.next-page',
            '.page-next',
            '.paginator a:last-child',
            '.pager a:last-child',
            'a[rel="next"]',
            'link[rel="next"]',
        ]
        
        for pattern in next_patterns:
            # 处理:contains选择器的警告
            if ':contains' in pattern:
                # 手动实现contains逻辑
                text_to_find = pattern.split('"')[1]
                for a in soup.find_all('a'):
                    if text_to_find in a.get_text():
                        next_url = a.get('href')
                        if next_url:
                            return urljoin(current_url, next_url)
            else:
                next_link = soup.select_one(pattern)
                if next_link and next_link.get('href'):
                    next_url = urljoin(current_url, next_link.get('href'))
                    if next_url != current_url:
                        return next_url
        
        return None
    
    def parse_chapter_next_page(self, html_content, current_url):
        """
        解析章节内容的下页链接（章节分页）
        需要根据具体网站结构调整
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 章节内下一页的选择器
        chapter_next_patterns = [
            # 常见的章节内下一页选择器
            '.next',
            '#next',
            '.page-next',
            '.next-page',
            '.bottem1 a:contains("下一页")',
            '.pagebar a:contains("下一页")',
            '.bottem1 a:contains("下—页")',
            '.pagebar a:contains("下—页")',
            '.content_next a',
            '.pagination a:contains("下一页")',
            '.pagination a:contains("下—页")',
            'a:contains("下页")',
            'a:contains("下一页")',
            'a:contains(">>")',
            'a:contains("»")',
            # 有些网站用数字链接
            'a:contains("下—页")',
            'a[rel="next"]',
        ]
        
        # 先尝试查找特定选择器
        for pattern in chapter_next_patterns:
            if ':contains' in pattern:
                text_to_find = pattern.split('"')[1]
                for a in soup.find_all('a'):
                    if text_to_find in a.get_text():
                        href = a.get('href')
                        if href and not href.startswith('#'):
                            next_url = urljoin(current_url, href)
                            # 避免重复获取同一页
                            if next_url != current_url:
                                #print(f"找到章节下一页: {next_url}")
                                return next_url
            else:
                next_link = soup.select_one(pattern)
                if next_link and next_link.get('href'):
                    href = next_link.get('href')
                    if href and not href.startswith('#'):
                        next_url = urljoin(current_url, href)
                        if next_url != current_url:
                            #print(f"找到章节下一页: {next_url}")
                            return next_url
        
        # 如果没找到，尝试查找常见的分页链接模式
        # 有些网站使用类似 "1/3" 的分页
        pagination_links = soup.find_all('a', href=re.compile(r'(_|\?|&)(page|p)=\d+'))
        if pagination_links:
            # 获取当前页码
            current_page_match = re.search(r'(_|\?|&)(page|p)=(\d+)', current_url)
            current_page = int(current_page_match.group(3)) if current_page_match else 1
            
            for link in pagination_links:
                href = link.get('href')
                page_match = re.search(r'(_|\?|&)(page|p)=(\d+)', href)
                if page_match:
                    page_num = int(page_match.group(3))
                    # 如果链接的页码大于当前页码，可能是下一页
                    if page_num == current_page + 1:
                        next_url = urljoin(current_url, href)
                        #print(f"通过页码模式找到章节下一页: {next_url}")
                        return next_url
        
        return None
    
    def crawl_chapter_list(self):
        """
        爬取所有章节链接（处理分页）
        """
        all_chapters = []
        current_url = self.base_url
        page_num = 1
        
        print("开始获取章节列表...")
        print(f"最大分页数设置为: {self.max_pages} 页")
        
        # 尝试从缓存加载章节列表（如果存在）
        list_cache_file = f"{self.cache_dir}/chapter_list.json"
        if self.use_cache and os.path.exists(list_cache_file):
            try:
                with open(list_cache_file, 'r', encoding='utf-8') as f:
                    cached_chapters = json.load(f)
                print(f"从缓存加载章节列表: {len(cached_chapters)} 章")
                return cached_chapters
            except Exception as e:
                print(f"加载章节列表缓存失败: {e}")
        
        while current_url and page_num <= self.max_pages:
            print(f"\n正在获取第 {page_num} 页目录...")
            html = self.get_page_content(current_url, use_cache=True)
            
            if not html:
                break
            
            # 获取当前页的章节列表
            chapters = self.parse_chapter_list(html)
            print(f"第 {page_num} 页找到 {len(chapters)} 个章节")
            
            if len(chapters) == 0:
                print(f"第 {page_num} 页没有找到任何章节，停止获取")
                break
            
            all_chapters.extend(chapters)
            
            # 检查是否有下一页
            next_url = self.parse_next_page(html, current_url)
            if next_url:
                print(f"找到下一页: {next_url}")
                current_url = next_url
            else:
                print("没有找到下一页链接")
                break
            
            page_num += 1
            
            # 避免请求过快
            time.sleep(0.5)
        
        # 去重
        unique_chapters = []
        seen_urls = set()
        for chapter in all_chapters:
            if chapter['url'] not in seen_urls:
                seen_urls.add(chapter['url'])
                unique_chapters.append(chapter)
        
        # 保存章节列表到缓存
        if self.use_cache:
            try:
                with open(list_cache_file, 'w', encoding='utf-8') as f:
                    json.dump(unique_chapters, f, ensure_ascii=False, indent=2)
                print(f"章节列表已缓存: {list_cache_file}")
            except Exception as e:
                print(f"保存章节列表缓存失败: {e}")
        
        print(f"\n总共找到 {len(unique_chapters)} 个唯一章节")
        if page_num >= self.max_pages:
            print(f"提示: 已达到最大分页数限制 ({self.max_pages} 页)")
        
        return unique_chapters
    
    def parse_chapter_content_with_pagination(self, start_url):
        """
        解析章节内容，处理可能的分页
        
        Args:
            start_url: 章节第一页的URL
            
        Returns:
            合并后的完整章节内容
        """
        all_content = []
        current_url = start_url
        page_num = 1
        max_chapter_pages = 10  # 防止无限循环，单章最大页数
        
        #print(f"开始获取章节内容（可能分页）: {start_url}")
        
        while current_url and page_num <= max_chapter_pages:
            #print(f"  获取第 {page_num} 页内容...")
            html = self.get_page_content(current_url, use_cache=True)
            
            if not html:
                break
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # 获取当前页的内容
            content = self.extract_chapter_content_from_page(soup)
            if content:
                if page_num == 1:
                    # 第一页，包含标题
                    title = self.extract_chapter_title(soup) or f"第{page_num}页"
                    all_content.append(f"{title}\n\n{content}")
                else:
                    # 后续页，只加内容
                    all_content.append(content)
                #print(f"  第 {page_num} 页内容长度: {len(content)} 字符")
            else:
                print(f"  第 {page_num} 页未找到内容")
            
            # 查找下一页
            next_url = self.parse_chapter_next_page(html, current_url)
            if next_url and next_url != current_url:
                current_url = next_url
                page_num += 1
                time.sleep(0.3)  # 避免请求过快
            else:
                break
        
        # 合并所有内容
        full_content = "\n\n".join(all_content)
        print(f"章节总页数: {page_num}, 总内容长度: {len(full_content)} 字符")
        
        return full_content
    
    def extract_chapter_title(self, soup):
        """
        提取章节标题
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            章节标题
        """
        # 常见的标题选择器
        title_selectors = [
            '.bookname h1',
            '.chapter-title',
            '.title',
            'h1',
            '.content h1',
            '.article-title',
            '.novel-title',
            'h2',
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                if title:
                    return title
        
        return None
    
    def extract_chapter_content_from_page(self, soup):
        """
        从单页中提取章节内容
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            当前页的内容文本
        """
        # 扩展内容选择器
        content_selectors = [
            '#content',
            '.content',
            '.read-content',
            '.chapter-content',
            '#chaptercontent',
            '.chapter_content',
            '.article-content',
            '.novel-content',
            '.text-content',
            '.book-content',
            '#booktext',
            '.txt',
            '.article-body',
            '.post-content',
            'article',
            '.page-content',
        ]
        
        content = None
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                content = content_div.get_text()
                # 清理多余的空行和空格
                content = re.sub(r'\s+', '\n', content.strip())
                break
        
        if not content:
            # 如果没找到特定选择器，尝试获取body中的文本
            # 但排除脚本、样式等
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            content = soup.get_text()
            content = re.sub(r'\s+', '\n', content.strip())
        
        # 移除常见的广告和导航文本
        ad_patterns = [
            r'本章未完，请点击下一页继续阅读',
            r'手机阅读本章',
            r'请记住本书首发域名',
            r'天才一秒记住',
            r'推荐阅读',
            r'最新章节',
            r'最新章节全文阅读',
            r'温馨提示：',
            r'如果您喜欢，',
            r'求收藏',
            r'求推荐',
            r'第.*?章'
        ]
        
        for pattern in ad_patterns:
            content = re.sub(pattern, '', content)
        
        return content
    
    def chinese_to_arabic(self, chinese_num):
        """
        将中文数字转换为阿拉伯数字
        例如：'第一一一章' -> 111, '第一千一百一十章' -> 1110
        """
        # 中文数字映射
        chinese_num_map = {
            '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '百': 100, '千': 1000, '万': 10000, '亿': 100000000
        }
        
        # 单位映射
        units = {'十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000}
        
        # 如果输入为空，返回None
        if not chinese_num:
            return None
        
        # 提取数字部分（去掉"第"和"章"）
        num_part = chinese_num
        if num_part.startswith('第'):
            num_part = num_part[1:]
        if num_part.endswith('章'):
            num_part = num_part[:-1]
        
        # 如果是纯数字，直接返回
        if num_part.isdigit():
            return int(num_part)
        
        # 处理中文数字
        result = 0
        temp = 0
        last_unit = 1
        
        for char in num_part:
            if char in chinese_num_map:
                if char in units:  # 是单位
                    if temp == 0:
                        temp = 1  # 处理"十"开头的情况，如"十一"中的"十"
                    result += temp * units[char]
                    temp = 0
                else:  # 是数字
                    temp = chinese_num_map[char]
            else:
                # 如果不是中文数字字符，返回None（表示无法转换）
                return None
        
        # 处理最后剩余的数字
        if temp > 0:
            result += temp
        
        return result if result > 0 else None
    
    def format_chapter_filename(self, title):
        """
        格式化章节文件名，将中文数字章节转换为阿拉伯数字
        例如：'第一章' -> '001章 第一章'
        """
        # 先清理文件名中的非法字符
        clean_title = re.sub(r'[\\/*?:"<>|]', "", title)
        
        # 尝试匹配章节模式：第xxx章
        chapter_pattern = r'^第([^章]+)章(.*)$'
        match = re.match(chapter_pattern, clean_title)
        
        if match:
            num_part = match.group(1)  # 数字部分
            rest_part = match.group(2)  # 剩余部分
            
            # 尝试转换为阿拉伯数字
            arabic_num = self.chinese_to_arabic(f"第{num_part}章")
            
            if arabic_num is not None:
                # 格式化数字为3位，不足补零
                formatted_num = f"{arabic_num:03d}"
                # 生成新文件名：001章 剩余部分
                if rest_part:
                    return f"{formatted_num}章 {rest_part.strip()}"
                else:
                    return f"{formatted_num}章"
        
        # 如果不是标准章节格式或转换失败，返回原标题
        return clean_title
    
    def save_chapter(self, chapter):
        """
        保存单个章节到文件
        """
        # 获取格式化的文件名
        formatted_title = self.format_chapter_filename(chapter['title'])
        
        # 限制文件名长度
        if len(formatted_title) > 100:
            formatted_title = formatted_title[:100]
        
        filepath = f"{self.save_dir}/{formatted_title}.txt"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                ct=''
                cht=chapter['content']
                for j in cht.replace('\r\n','\n').replace('\r','\n').split('\n'):
                    if not j in ("首页","下一章","下一页","关灯","护眼","上一页","上一章","中","小","字体","字体：大","大","返回","返回目录","加入书签","书架","|","阅读记录","下—章","下—页","上—章","上—页","^.^，请点击下一页继续阅读，后面更精彩！","尊贵特权，7天免广告阅读特权卡，所有注册用户均可免费领取！！","小主子，这个章节后面还有哦"):
                        ct+=j+'\n'
                f.write(f"{chapter['title']}\n\n")
                f.write(f"来源: {chapter['url']}\n\n")
                f.write(ct)
            print(f"已保存: {formatted_title} (原标题: {chapter['title']})")
            return True
        except Exception as e:
            print(f"保存章节 {chapter['title']} 失败: {e}")
            return False
    
    def download_worker(self):
        """
        下载线程的工作函数
        """
        while True:
            try:
                chapter = self.chapter_queue.get(timeout=3)
            except queue.Empty:
                break
            
            # 检查章节是否已下载
            if self.is_chapter_downloaded(chapter['url']):
                print(f"线程 {threading.current_thread().name} 跳过已下载: {chapter['title']}")
                self.chapter_queue.task_done()
                continue
            
            try:
                # 每个线程下载时也使用线程号标记
                thread_name = threading.current_thread().name
                #print(f"线程 {thread_name} 开始下载: {chapter['title']}")
                
                # 获取章节内容（处理可能的分页）
                full_content = self.parse_chapter_content_with_pagination(chapter['url'])
                
                if full_content:
                    # 保存到结果队列
                    self.result_queue.put({
                        'title': chapter['title'],
                        'content': full_content,
                        'url': chapter['url']
                    })
                    
                    print(f"✓ 线程 {thread_name} 已完成: {chapter['title']}")
                else:
                    print(f"✗ 线程 {thread_name} 下载失败: {chapter['title']}")
                
            except Exception as e:
                print(f"下载章节 {chapter['title']} 时出错: {e}")
            
            finally:
                self.chapter_queue.task_done()
    
    def clear_cache(self):
        """清空缓存"""
        if os.path.exists(self.cache_dir):
            import shutil
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir)
            print(f"缓存已清空: {self.cache_dir}")
    
    def run(self, clear_cache_first=False):
        """
        运行下载器
        
        Args:
            clear_cache_first: 是否先清空缓存
        """
        print(f"开始下载小说: {self.novel_name}")
        print(f"目录页: {self.base_url}")
        print(f"User-Agent池大小: {len(self.user_agents)} (线程数: {self.max_workers})")
        print(f"目录页最大分页数: {self.max_pages}")
        print(f"缓存功能: {'开启' if self.use_cache else '关闭'}")
        
        if clear_cache_first:
            self.clear_cache()
        
        # 1. 获取所有章节链接
        chapters = self.crawl_chapter_list()
        
        if not chapters:
            print("\n❌ 未找到任何章节，请检查：")
            print("1. 网站URL是否正确")
            print("2. 网站是否需要登录")
            print("3. 网站是否有反爬虫机制")
            print("4. 可能需要调整HTML解析器")
            print("5. 可以尝试增加最大分页数")
            return
        
        # 过滤掉已下载的章节
        chapters_to_download = []
        for chapter in chapters:
            if not self.is_chapter_downloaded(chapter['url']):
                chapters_to_download.append(chapter)
        
        print(f"\n✅ 找到 {len(chapters)} 个章节，其中 {len(chapters_to_download)} 个未下载")
        
        if len(chapters_to_download) == 0:
            print("所有章节都已下载完成！")
            return
        
        # 2. 将章节放入队列
        for chapter in chapters_to_download:
            self.chapter_queue.put(chapter)
        
        # 3. 创建并启动下载线程
        threads = []
        for i in range(self.max_workers):
            t = threading.Thread(target=self.download_worker, name=f"W{i+1}")
            t.daemon = True
            t.start()
            threads.append(t)
        
        # 4. 等待所有下载任务完成
        self.chapter_queue.join()
        
        # 5. 保存所有章节
        print("\n开始保存章节...")
        success_count = 0
        fail_count = 0
        
        while not self.result_queue.empty():
            chapter = self.result_queue.get()
            if self.save_chapter(chapter):
                success_count += 1
                # 标记为已下载
                self.mark_chapter_downloaded(chapter['url'])
            else:
                fail_count += 1
        
        # 6. 打印UA使用统计
        ua_stats = self.get_ua_stats()
        print("\n" + "="*40)
        print("User-Agent 使用统计:")
        for ua, count in sorted(ua_stats.items(), key=lambda x: x[1], reverse=True)[:10]:  # 只显示前10个
            short_ua = ua[:50] + "..." if len(ua) > 50 else ua
            print(f"  {short_ua}: {count}次")
        
        print(f"\n{'='*40}")
        print(f"下载完成！")
        print(f"本次成功: {success_count} 章")
        print(f"本次失败: {fail_count} 章")
        print(f"累计已下载: {len(self.downloaded_chapters)} 章")
        print(f"保存位置: {os.path.abspath(self.save_dir)}")
        print(f"缓存位置: {os.path.abspath(self.cache_dir)}")
        print(f"{'='*40}")

def main():
    # 使用示例 - 请替换为实际的小说目录页URL
    print("小说下载器")
    print("="*40)
    
    # 让用户输入URL
    novel_url = input("请输入小说目录页URL: ").strip()
    novel_name = input("请输入小说名称: ").strip()
    
    if not novel_url or not novel_name:
        print("URL和小说名称不能为空！")
        return
    
    # 可选：设置线程数
    try:
        workers = int(input("请输入下载线程数(默认5): ") or "5")
        if workers < 1:
            workers = 5
    except ValueError:
        workers = 5
    
    # 设置目录页最大分页数
    try:
        max_pages_input = input("请输入目录页最大分页数(默认100，0表示不限制): ").strip()
        if max_pages_input == "0":
            max_pages = float('inf')  # 不限制
            print("已设置为不限制目录页分页数")
        else:
            max_pages = int(max_pages_input or "100")
            if max_pages < 1:
                max_pages = 100
    except ValueError:
        max_pages = 100
        print("输入无效，使用默认值100")
    
    # 是否使用缓存
    use_cache_input = input("是否使用缓存功能(可以断点续传)(y/n，默认y): ").strip().lower()
    use_cache = use_cache_input != 'n'
    
    # 是否清空缓存
    clear_cache = False
    if use_cache:
        clear_cache_input = input("是否清空已有缓存(重新下载所有章节)(y/n，默认n): ").strip().lower()
        clear_cache = clear_cache_input == 'y'
    
    downloader = NovelDownloader(novel_url, novel_name, max_workers=workers, max_pages=max_pages, use_cache=use_cache)
    downloader.run(clear_cache_first=clear_cache)

if __name__ == "__main__":
    main()