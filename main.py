from downloader import NovelDownloader,wait
from merger import NovelMerger
import argparse,os,json
default='''{
  "ad_patterns": [
    "本章未完，请点击下一页继续阅读",
    "手机阅读本章",
    "请记住本书首发域名",
    "天才一秒记住",
    "推荐阅读",
    "最新章节",
    "最新章节全文阅读",
    "温馨提示：",
    "如果您喜欢，",
    "求收藏",
    "求推荐",
    "第.*?章"
  ],
  "replace": [
    "首页",
    "下一章",
    "下一页",
    "关灯",
    "护眼",
    "上一页",
    "上一章",
    "中",
    "小",
    "字体",
    "字体：大",
    "大",
    "返回",
    "返回目录",
    "加入书签",
    "书架",
    "|",
    "阅读记录",
    "下—章",
    "下—页",
    "上—章",
    "上—页",
    "^.^，请点击下一页继续阅读，后面更精彩！",
    "尊贵特权，7天免广告阅读特权卡，所有注册用户均可免费领取！！",
    "小主子，这个章节后面还有哦"
  ],
  "chapter_next_patterns": [
    ".next",
    "#next",
    ".page-next",
    ".next-page",
    ".bottem1 a:contains(\"下一页\")",
    ".pagebar a:contains(\"下一页\")",
    ".bottem1 a:contains(\"下—页\")",
    ".pagebar a:contains(\"下—页\")",
    ".content_next a",
    ".pagination a:contains(\"下一页\")",
    ".pagination a:contains(\"下—页\")",
    "a:contains(\"下页\")",
    "a:contains(\"下一页\")",
    "a:contains(\">>\")",
    "a:contains(\"»\")",
    "a:contains(\"下—页\")",
    "a[rel=\"next\"]"
  ],
  "next_page_patterns": [
    ".next",
    "#next",
    ".pagination .next",
    "a:contains(\"下一页\")",
    "a:contains(\"下—页\")",
    "a:contains(\"下页\")",
    "a:contains(\">\")",
    "a:contains(\"»\")",
    "a.next-page",
    ".page-next",
    ".paginator a:last-child",
    ".pager a:last-child",
    "a[rel=\"next\"]",
    "link[rel=\"next\"]"
  ],
  "selectors_column": [
    "#list dd a",
    "#list a",
    ".listmain dd a",
    ".listmain a",
    ".chapter-list dd a",
    ".chapter-list a",
    ".chapter a",
    ".book-list a",
    "#readerlists a",
    ".catalog a",
    ".volume a",
    "ul.chapter li a",
    ".chapterlist a",
    ".dir-list a",
    ".novel-list a",
    ".article-list a",
    ".text-list a",
    ".main-content a",
    ".content a"
  ],
  "user_agents": [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.38",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0"
  ]
}'''

if not os.path.exists('novel_cfg.json'):
    w=open('novel_cfg.json','w',encoding='utf-8')
    w.write(default)
    w.close()
elif os.stat('novel_cfg.json').st_size<32:
    w=open('novel_cfg.json','w',encoding='utf-8')
    w.write(default)
    w.close()
else:
    pass
data={'ad_patterns': ['本章未完，请点击下一页继续阅读', '手机阅读本章', '请记住本书首发域名', '天才一秒记住', '推荐阅读', '最新章节', '最新章节全文阅读', '温馨提示：', '如果您喜欢，', '求收藏', '求推荐', '第.*?章'], 'replace': ['首页', '下一章', '下一页', '关灯', '护眼', '上一页', '上一章', '中', '小', '字体', '字体：大', '大', '返回', '返回目录', '加入书签', '书架', '|', '阅读记录', '下—章', '下—页', '上—章', '上—页', '^.^，请点击下一页继续阅读，后面更精彩！', '尊贵特权，7天免广告阅读特权卡，所有注册用户均可免费领取！！', '小主子，这 个章节后面还有哦'], 'chapter_next_patterns': ['.next', '#next', '.page-next', '.next-page', '.bottem1 a:contains("下一页")', '.pagebar a:contains("下一页")', '.bottem1 a:contains("下—页")', '.pagebar a:contains("下—页")', '.content_next a', '.pagination a:contains("下一页")', '.pagination a:contains("下—页")', 'a:contains("下页")', 'a:contains("下一页")', 'a:contains(">>")', 'a:contains("»")', 'a:contains("下—页")', 'a[rel="next"]'], 'next_page_patterns': ['.next', '#next', '.pagination .next', 'a:contains("下一页")', 'a:contains("下—页")', 'a:contains("下页")', 'a:contains(">")', 'a:contains("»")', 'a.next-page', '.page-next', '.paginator a:last-child', '.pager a:last-child', 'a[rel="next"]', 'link[rel="next"]'], 'selectors_column': ['#list dd a', '#list a', '.listmain dd a', '.listmain a', '.chapter-list dd a', '.chapter-list a', '.chapter a', '.book-list a', '#readerlists a', '.catalog a', '.volume a', 'ul.chapter li a', '.chapterlist a', '.dir-list a', '.novel-list a', '.article-list a', '.text-list a', '.main-content a', '.content a'], 'user_agents': ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.38', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0', 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0']}
try:
    r=open('novel_cfg.json','r',encoding='utf-8')
    d=json.load(r);r.close()
    for i in d.keys():
        data[i]=d[i]
except:
    pass
try:
    from ebooklib import epub
    EPUB_AVAILABLE = True
except ImportError:
    EPUB_AVAILABLE = False
    print("警告: 未安装ebooklib库，EPUB导出功能不可用")
    print("请安装: pip install ebooklib")


def interactive_mode():
    
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
    wait(novel_url)
    
    downloader = NovelDownloader(novel_url, novel_name, max_workers=workers, max_pages=max_pages, use_cache=use_cache,datas=data)
    downloader.run(clear_cache_first=clear_cache)
    
    
    
    # 创建合并器
    merger = NovelMerger(novel_name)
    
    # 设置作者
    author = input("请输入作者（可选，直接回车跳过）: ").strip()
    if author:
        merger.set_metadata(author=author)
    
    # 扫描章节
    if not merger.scan_chapters():
        input("\n按回车键退出...")
        return
    
    print("\n" + "=" * 50)
    
    # 选择导出格式
    print("请选择导出格式：")
    print("1. TXT 格式")
    print("2. EPUB 格式")
    print("3. 两种格式都导出")
    print("4. 仅生成信息文件")
    
    choice = input("请输入选项 (1-4，默认1): ").strip() or "1"
    
    if choice == "1":
        merger.export_txt()
    elif choice == "2":
        if EPUB_AVAILABLE:
            merger.export_epub()
        else:
            print("EPUB导出不可用，请安装: pip install ebooklib")
    elif choice == "3":
        merger.export_txt()
        if EPUB_AVAILABLE:
            merger.export_epub()
        else:
            print("EPUB导出不可用，请安装: pip install ebooklib")
    elif choice == "4":
        pass
    else:
        print("无效选项，默认导出TXT")
        merger.export_txt()
    
    # 生成信息文件
    merger.generate_info_file()
    
    print("\n" + "=" * 50)
    print(f"处理完成！文件保存在: {merger.output_path}")
    print("=" * 50)
    
    input("\n按回车键退出...")



def main():
    parser = argparse.ArgumentParser(description='小说下载工具 - 将下载的章节合成为TXT或EPUB')
    parser.add_argument('novel_url', help='小说网址')
    parser.add_argument('novel_name', help='小说名称')
    parser.add_argument('--workers', type=int, default=5, help='线程数')
    parser.add_argument('--max-pages', type=int, default=100, help='最大分页数')
    parser.add_argument('--use-cache', action='store_true', help='使用缓存')
    parser.add_argument('--clear-cache', action='store_true', help='清除缓存')
    parser.add_argument('-o', '--output', help='输出文件名（不包含扩展名）')
    parser.add_argument('--author', default='未知作者', help='设置作者')
    parser.add_argument('--download-dir', default='downloads', help='下载目录（默认：downloads）')
    parser.add_argument('--output-dir', default='output', help='输出目录（默认：output）')
    
    args = parser.parse_args()
    print("小说下载器")
    print("="*40)
    
    if not args.novel_url or not args.novel_name:
        print("URL和小说名称不能为空！")
        return
    
    # 可选：设置线程数
    try:
        if args.workers < 1:
            workers = 5
        else:
            workers=args.workers
    except ValueError:
        workers = 5
    
    # 设置目录页最大分页数
    if args.max_pages < 1:
        max_pages = 100
    else:
        max_pages=args.max_pages
    
    if not args.use_cache:
        clear_cache = False
    elif args.clear_cache:
        clear_cache=True
    else:
        clear_cache=False
    downloader = NovelDownloader(args.novel_url, args.novel_name, max_workers=workers, max_pages=max_pages, use_cache=args.use_cache,datas=data)
    downloader.run(clear_cache_first=clear_cache)
    
    
    # 创建合并器
    merger = NovelMerger(
        novel_name=args.novel_name,
        download_dir=args.download_dir,
        output_dir=args.output_dir
    )
    
    # 设置作者
    merger.set_metadata(author=args.author)
    
    # 扫描章节
    if not merger.scan_chapters():
        print("\n请检查：")
        print("1. 小说名称是否正确")
        print(f"2. 下载目录是否存在: {merger.download_path}")
        print("3. 目录中是否有章节文件")
        return
    
    
    # 导出TXT
    if args.output:
        merger.export_txt(f"{args.output}.txt")
    else:
        merger.export_txt()
    
    if not EPUB_AVAILABLE:
        print("\n跳过EPUB导出: 请先安装ebooklib库")
        print("pip install ebooklib")
    else:
        if args.output:
            merger.export_epub(f"{args.output}.epub")
        else:
            merger.export_epub()
    
    # 生成信息文件
    merger.generate_info_file()
    
    print("\n" + "=" * 50)
    print(f"处理完成！文件保存在: {merger.output_path}")




if __name__ == "__main__":
    import sys
    
    # 如果没有命令行参数，进入交互式模式
    if len(sys.argv) == 1:
        interactive_mode()
    else:
        main()