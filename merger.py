import os
import re
import json
from datetime import datetime
from pathlib import Path
import argparse

# 尝试导入EPUB相关库，如果没有则提示安装
try:
    from ebooklib import epub
    EPUB_AVAILABLE = True
except ImportError:
    EPUB_AVAILABLE = False
    print("警告: 未安装ebooklib库，EPUB导出功能不可用")
    print("请安装: pip install ebooklib")

class NovelMerger:
    def __init__(self, novel_name, download_dir="downloads", output_dir="output"):
        """
        初始化小说合并器
        
        Args:
            novel_name: 小说名称（文件夹名）
            download_dir: 下载目录
            output_dir: 输出目录
        """
        self.novel_name = novel_name
        self.download_path = os.path.join(download_dir, novel_name)
        self.output_path = os.path.join(output_dir, novel_name)
        
        # 创建输出目录
        os.makedirs(self.output_path, exist_ok=True)
        
        # 章节文件列表
        self.chapter_files = []
        
        # 小说元数据
        self.metadata = {
            'title': novel_name,
            'author': '未知作者',
            'language': 'zh-CN',
            'publisher': 'Novel Downloader',
            'description': f'《{novel_name}》电子书',
            'date': datetime.now().strftime('%Y-%m-%d'),
        }
    
    def scan_chapters(self):
        """
        扫描下载目录中的所有章节文件
        按文件名排序（支持数字编号）
        """
        if not os.path.exists(self.download_path):
            print(f"错误: 下载目录不存在 {self.download_path}")
            return False
        
        # 获取所有txt文件
        all_files = os.listdir(self.download_path)
        txt_files = [f for f in all_files if f.endswith('.txt')]
        
        # 排除进度文件
        txt_files = [f for f in txt_files if f != 'download_progress.json']
        
        if not txt_files:
            print(f"在 {self.download_path} 中没有找到章节文件")
            return False
        
        # 自定义排序函数
        def extract_number(filename):
            """从文件名中提取数字编号"""
            # 尝试匹配开头的数字（如 001章、123章）
            match = re.match(r'^(\d+)', filename)
            if match:
                return int(match.group(1))
            
            # 尝试匹配其他数字
            numbers = re.findall(r'\d+', filename)
            if numbers:
                return int(numbers[0])
            
            # 如果没有数字，返回一个很大的数，排到最后
            return 999999
        
        # 按数字排序
        self.chapter_files = sorted(txt_files, key=extract_number)
        
        print(f"找到 {len(self.chapter_files)} 个章节文件")
        
        # 显示前几个章节
        print("\n章节顺序预览（前10章）:")
        for i, f in enumerate(self.chapter_files[:10], 1):
            print(f"  {i:3d}. {f}")
        
        if len(self.chapter_files) > 10:
            print(f"  ... 共 {len(self.chapter_files)} 章")
        
        return True
    
    def read_chapter_content(self, filename):
        """
        读取单个章节文件内容
        返回标题和内容
        """
        filepath = os.path.join(self.download_path, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取标题（第一行）
            lines = content.split('\n')
            title = lines[0].strip() if lines else filename.replace('.txt', '')
            
            # 内容从第三行开始（跳过标题和来源行）
            if len(lines) >= 3 and '来源:' in lines[1]:
                body = '\n'.join(lines[2:]).strip()
            else:
                body = '\n'.join(lines[1:]).strip()
            
            return title, body
            
        except Exception as e:
            print(f"读取文件失败 {filepath}: {e}")
            return filename.replace('.txt', ''), ''
    
    def export_txt(self, output_filename=None):
        """
        导出为TXT文件
        """
        if not output_filename:
            output_filename = f"{self.novel_name}.txt"
        
        output_filepath = os.path.join(self.output_path, output_filename)
        
        print(f"\n开始导出TXT: {output_filepath}")
        
        try:
            with open(output_filepath, 'w', encoding='utf-8') as outfile:
                # 写入标题
                outfile.write(f"{self.novel_name}\n")
                outfile.write("=" * 50 + "\n")
                outfile.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                outfile.write(f"章节总数: {len(self.chapter_files)}\n")
                outfile.write("=" * 50 + "\n\n")
                
                # 写入目录
                outfile.write("【目录】\n")
                outfile.write("-" * 30 + "\n")
                for i, filename in enumerate(self.chapter_files, 1):
                    title, _ = self.read_chapter_content(filename)
                    outfile.write(f"{i:3d}. {title}\n")
                outfile.write("\n" + "=" * 50 + "\n\n")
                
                # 写入正文
                total_chars = 0
                for i, filename in enumerate(self.chapter_files, 1):
                    print(f"  处理第 {i}/{len(self.chapter_files)} 章: {filename}")
                    
                    title, content = self.read_chapter_content(filename)
                    
                    outfile.write(f"\n\n{' ':-^50}\n".format(f' 第{i}章 {title} '))
                    outfile.write(content)
                    
                    total_chars += len(content)
                
                outfile.write("\n\n" + "=" * 50 + "\n")
                outfile.write(f"全文完\n")
            
            file_size = os.path.getsize(output_filepath) / 1024  # KB
            print(f"\n✅ TXT导出成功!")
            print(f"  文件: {output_filepath}")
            print(f"  大小: {file_size:.2f} KB")
            print(f"  字数: 约 {total_chars} 字")
            
            return True
            
        except Exception as e:
            print(f"导出TXT失败: {e}")
            return False
    
    def export_epub(self, output_filename=None):
        """
        导出为EPUB格式
        """
        if not EPUB_AVAILABLE:
            print("\n❌ EPUB导出失败: 未安装ebooklib库")
            print("请安装: pip install ebooklib")
            return False
        
        if not output_filename:
            output_filename = f"{self.novel_name}.epub"
        
        output_filepath = os.path.join(self.output_path, output_filename)
        
        print(f"\n开始导出EPUB: {output_filepath}")
        
        try:
            # 创建EPUB书籍
            book = epub.EpubBook()
            
            # 设置元数据
            book.set_identifier(f'novel_{self.novel_name}_{datetime.now().strftime("%Y%m%d%H%M%S")}')
            book.set_title(self.metadata['title'])
            book.set_language(self.metadata['language'])
            book.add_author(self.metadata['author'])
            book.add_metadata('DC', 'description', self.metadata['description'])
            book.add_metadata('DC', 'publisher', self.metadata['publisher'])
            book.add_metadata('DC', 'date', self.metadata['date'])
            
            # 添加CSS样式
            css_style = '''
            @namespace epub "http://www.idpf.org/2007/ops";
            body {
                font-family: "Microsoft YaHei", "SimHei", "Helvetica", "Arial", sans-serif;
                line-height: 1.6;
                margin: 2em;
            }
            h1 {
                text-align: center;
                font-size: 1.8em;
                margin: 1em 0;
            }
            h2 {
                text-align: center;
                font-size: 1.4em;
                margin: 1.5em 0 1em;
                color: #333;
            }
            p {
                text-indent: 2em;
                margin: 0.5em 0;
                text-align: justify;
            }
            .chapter-title {
                text-align: center;
                font-size: 1.6em;
                font-weight: bold;
                margin: 2em 0 1.5em;
            }
            .toc-item {
                margin: 0.5em 0;
            }
            .copyright {
                text-align: center;
                font-size: 0.9em;
                color: #666;
                margin-top: 3em;
            }
            '''
            
            # 添加CSS文件
            nav_css = epub.EpubItem(
                uid="style_nav",
                file_name="style/nav.css",
                media_type="text/css",
                content=css_style
            )
            book.add_item(nav_css)
            
            # 创建目录页
            toc_content = f'''
            <html xmlns="http://www.w3.org/1999/xhtml">
            <head>
                <title>目录 - {self.novel_name}</title>
                <link rel="stylesheet" type="text/css" href="style/nav.css"/>
            </head>
            <body>
                <h1>{self.novel_name}</h1>
                <h2>目录</h2>
            '''
            
            # 创建章节列表
            chapters = []
            spine = ['nav']
            
            # 处理每个章节
            for i, filename in enumerate(self.chapter_files, 1):
                print(f"  处理第 {i}/{len(self.chapter_files)} 章: {filename}")
                
                title, content = self.read_chapter_content(filename)
                
                # 处理内容中的段落
                paragraphs = content.split('\n')
                content_html = ''
                for para in paragraphs:
                    if para.strip():
                        content_html += f'<p>{para.strip()}</p>\n'
                
                # 创建章节HTML
                chapter_html = f'''
                <html xmlns="http://www.w3.org/1999/xhtml">
                <head>
                    <title>{title}</title>
                    <link rel="stylesheet" type="text/css" href="style/nav.css"/>
                </head>
                <body>
                    <h1 class="chapter-title">{title}</h1>
                    {content_html}
                    <p class="copyright">—— 本章完 ——</p>
                </body>
                </html>
                '''
                
                # 创建EPUB章节
                chap = epub.EpubHtml(
                    title=title,
                    file_name=f'chap_{i:03d}.xhtml',
                    lang='zh-CN'
                )
                chap.content = chapter_html
                chap.add_item(nav_css)
                
                book.add_item(chap)
                chapters.append(chap)
                spine.append(chap)
                
                # 添加到目录
                toc_content += f'<p class="toc-item"><a href="chap_{i:03d}.xhtml">{i:03d}. {title}</a></p>\n'
            
            # 完成目录页
            toc_content += '''
                <p class="copyright">—— 全书完 ——</p>
            </body>
            </html>
            '''
            
            # 创建目录页章节
            toc_chap = epub.EpubHtml(
                title='目录',
                file_name='toc.xhtml',
                lang='zh-CN'
            )
            toc_chap.content = toc_content
            toc_chap.add_item(nav_css)
            
            book.add_item(toc_chap)
            spine.insert(1, toc_chap)  # 在导航页之后插入目录
            
            # 设置目录
            book.toc = [
                (epub.Section('目录'), [toc_chap]),
                (epub.Section('正文'), chapters)
            ]
            
            # 设置书脊
            book.spine = spine
            
            # 添加导航文件
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            
            # 生成EPUB文件
            epub.write_epub(output_filepath, book, {})
            
            file_size = os.path.getsize(output_filepath) / 1024  # KB
            print(f"\n✅ EPUB导出成功!")
            print(f"  文件: {output_filepath}")
            print(f"  大小: {file_size:.2f} KB")
            
            return True
            
        except Exception as e:
            print(f"导出EPUB失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def set_metadata(self, **kwargs):
        """
        设置小说元数据
        """
        for key, value in kwargs.items():
            if key in self.metadata:
                self.metadata[key] = value
    
    def generate_info_file(self):
        """
        生成信息文件
        """
        info_filepath = os.path.join(self.output_path, f"{self.novel_name}_info.txt")
        
        try:
            with open(info_filepath, 'w', encoding='utf-8') as f:
                f.write(f"小说名称: {self.novel_name}\n")
                f.write(f"作者: {self.metadata['author']}\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"章节总数: {len(self.chapter_files)}\n")
                f.write(f"源文件目录: {self.download_path}\n")
                f.write(f"输出目录: {self.output_path}\n")
                f.write("\n【章节列表】\n")
                
                for i, filename in enumerate(self.chapter_files, 1):
                    title, _ = self.read_chapter_content(filename)
                    f.write(f"{i:4d}. {title} - {filename}\n")
            
            print(f"信息文件已生成: {info_filepath}")
            return True
            
        except Exception as e:
            print(f"生成信息文件失败: {e}")
            return False

