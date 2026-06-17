import sys
import os
import re
import json
import time
import random
import requests
import subprocess
import dm_pb2#这是自定义

from bs4 import BeautifulSoup
from PyQt6.QtCore import Qt, QThread, pyqtSignal,QUrl
from urllib.parse import urlparse, urlunparse,parse_qs
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette,QDesktopServices
from PyQt6.QtWidgets import (
    QApplication,QInputDialog, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QFileDialog, QProgressBar, QMessageBox,QComboBox,QDialog,QTextEdit,QFrame
)

#爬虫类
class BiliCrawler:
    def __init__(self, cookie=None):
        self.head = {
            'referer': 'https://www.bilibili.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
        }
        if cookie:
            self.head['cookie'] = cookie

    def update_cookie(self, cookie):
        """更新Cookie"""
        self.head['cookie'] = cookie

    def get_page_text(self, url):
        resp = requests.get(url=url, headers=self.head)
        resp.encoding = 'utf-8'
        return resp.text

    def sanitize_title(self, title):
        """清理标题中的非法字符，用于文件名"""
        return re.sub(r'[\\/*?:"<>|]', '-', title)

    def huoqu_shouchangjia_dange_url_biaoti(self,html):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            h1 = soup.find('h1')

            if h1 and h1.get('data-title'):
                title = h1.get('data-title')
            else:
                title = "视频不见了"
        except Exception as e:
            print(f"获取标题时出错: {e}")
            title = "视频不见了"

        print(title)
        return title

    def huoqu_danye_shouchang_url_list(self,js):
        # 接受传入的json数据，将json数据转换为字典
        data = json.loads(js, strict=False)  # 将字符串转为字典
        bv_list = [item['bv_id'] for item in data['data']['medias']]  # 获取所有bvid号
        # print(bv_list,len(bv_list))

        qianzhui_url = 'https://www.bilibili.com/video/'  # b站视频url的前缀
        l = []  # 存储b站视频url
        for i in bv_list:
            bili_shiping_url = qianzhui_url + i + '/'  # b站视频url的前缀+视频bvid号
            # print(bili_shiping_url)
            l.append(bili_shiping_url)
        return l

    def huoqu_danye_shouchang_biaoqian(self,js):
        # 接受传入的json数据，将json数据转换为字典
        data = json.loads(js, strict=False)  # 将字符串转为字典
        # b站通过has_more的true或者false来判断是否有更多的收藏页
        flag = data['data']['has_more']  # 获取has_more这个标识符
        return flag

    def get_duo_bvid_page_title(self,html_text):

        # 假设html_text是你提供的HTML字符串
        soup = BeautifulSoup(html_text, 'html.parser')

        # 查找所有包含data-key属性的div元素
        video_items = soup.find_all('div', {'class': 'pod-item', 'data-key': True})

        results = []

        for item in video_items:
            # # 提取bvid
            # bvid = item.get('data-key')
            #
            # 提取标题
            title_element = item.find('div', class_='title-txt')
            title = title_element.get_text(strip=True) if title_element else "无标题"
            #
            # # 提取时长
            # duration_element = item.find('div', class_='duration')
            # duration = duration_element.get_text(strip=True) if duration_element else "未知时长"
            #
            results.append({
                # 'bvid': bvid,
                'title': title,
                # 'duration': duration,
                # 'url': f"https://www.bilibili.com/video/{bvid}"
            })
        l = []
        # 打印结果
        for i, result in enumerate(results, 1):
            # print(result['title'])
            l.append(result['title'])
            # print(f"{i:2d}. BV号: {result['bvid']}")
            # print(f"    标题: {result['title']}")
            # print(f"    时长: {result['duration']}")
            # print(f"    链接: {result['url']}")
            # print()

        return l

    def get_dange_bvid_page_title(self, html_content):

        soup = BeautifulSoup(html_content, 'html.parser')

        # 存储标题的列表
        titles = []

        # 方法1：直接查找 video-pod__item 下的 title-txt
        video_items = soup.find_all(class_="video-pod__item")
        for item in video_items:
            title_element = item.find(class_="title-txt")
            if title_element:
                title = title_element.get_text(strip=True)
                # 过滤掉非视频标题的干扰项
                if title and title not in ["视频选集", "自动连播"]:
                    titles.append(title)

        # 如果方法1获取到标题，直接返回
        if titles:
            print(f"使用方法1获取到标题: {titles}")
            return titles

        # 方法1无结果，尝试方法2：正则匹配h1的data-title属性
        pattern = r'<h1[^>]*data-title="([^"]*)"[^>]*>'
        match = re.search(pattern, html_content)
        if match:
            title = match.group(1)
            if title:  # 确保标题不为空
                titles = [title]  # 转换为列表格式，保持函数返回类型一致
                print(f"使用方法2获取到标题: {titles}")
                return titles

        # # 方法3：通过 og:title meta 标签获取标题
        # meta_tag = soup.find('meta', property='og:title')
        # if meta_tag and meta_tag.get('content'):
        #     title = meta_tag['content']
        #     if title:  # 确保标题不为空
        #         titles = [title]  # 转换为列表格式，保持函数返回类型一致
        #         print(f"使用方法3获取到标题: {titles}")
        #         return titles

        # 通过 title 标签获取标题（并提取视频名称部分）
        title_tag = soup.find('title')
        if title_tag:
            full_title = title_tag.get_text(strip=True)
            # 取第一个 "-" 之前的内容作为视频标题
            if full_title:
                # 取第一个短横线之前的内容
                main_title = full_title.split('-')[0] if '-' in full_title else full_title

                if main_title:  # 确保标题不为空
                    titles = [main_title]  # 转换为列表格式，保持函数返回类型一致
                    print(f"使用方法4获取到标题: {titles}")
                    return titles

        # 四种方法都失败
        print("未找到视频标题")
        return titles  # 返回空列表

    def get_page_bvid(self,html_text):

        # 假设html_text是你提供的HTML字符串
        soup = BeautifulSoup(html_text, 'html.parser')

        # 查找所有包含data-key属性的div元素
        video_items = soup.find_all('div', {'class': 'pod-item', 'data-key': True})

        results = []

        for item in video_items:
            # # 提取bvid
            bvid = item.get('data-key')
            #
            # 提取标题
            # title_element = item.find('div', class_='title-txt')
            # title = title_element.get_text(strip=True) if title_element else "无标题"
            #
            # # 提取时长
            # duration_element = item.find('div', class_='duration')
            # duration = duration_element.get_text(strip=True) if duration_element else "未知时长"
            #
            results.append({
                'bvid': bvid,
                # 'title': title,
                # 'duration': duration,
                # 'url': f"https://www.bilibili.com/video/{bvid}"
            })
        l = []
        # 打印结果
        for i, result in enumerate(results, 1):
            # print(result['title'])
            l.append(result['bvid'])
            # print(f"{i:2d}. BV号: {result['bvid']}")
            # print(f"    标题: {result['title']}")
            # print(f"    时长: {result['duration']}")
            # print(f"    链接: {result['url']}")
            # print()

        return l

    def heji_url_pinjie(self,bvid_list):
        l2 = []
        pinjie_url = 'https://www.bilibili.com/video/'
        for i in bvid_list:
            new_url = pinjie_url + i + '/'
            l2.append(new_url)
        return l2

    def zhiding_bvid(self,selection_str, item_list):
        """
        解析选择字符串并返回对应的列表项

        Args:
            selection_str: 用户输入的选择字符串，如 '1-3' 或 '1,2,5'
            item_list: 目标列表

        Returns:
            list: 选中的项列表
        """
        selected_items = []

        # 去除空格
        selection_str = selection_str.replace(' ', '')

        try:
            # 处理逗号分隔的情况
            if ',' in selection_str:
                parts = selection_str.split(',')
                for part in parts:
                    if '-' in part:
                        # 处理范围，如 1-3
                        start, end = map(int, part.split('-'))
                        # 转换为0-based索引，并确保在有效范围内
                        for i in range(start - 1, end):
                            if 0 <= i < len(item_list):
                                selected_items.append(item_list[i])
                    else:
                        # 处理单个数字，如 1
                        idx = int(part) - 1
                        if 0 <= idx < len(item_list):
                            selected_items.append(item_list[idx])

            # 处理纯范围的情况，如 1-3
            elif '-' in selection_str:
                start, end = map(int, selection_str.split('-'))
                for i in range(start - 1, end):
                    if 0 <= i < len(item_list):
                        selected_items.append(item_list[i])

            # 处理单个数字的情况
            else:
                idx = int(selection_str) - 1
                if 0 <= idx < len(item_list):
                    selected_items.append(item_list[idx])

        except (ValueError, IndexError) as e:
            print(f"输入格式错误: {e}")
            return []

        return selected_items

    def find_buton_bvid_index(self,url, bvid_list):
        """
        从B站链接中提取BVID并返回在列表中的索引
        """
        # 从URL中提取BVID
        pattern = r'video/(BV[a-zA-Z0-9]+)'
        match = re.search(pattern, url)

        if not match:
            print("❌ 未找到BVID")
            return -1

        bvid = match.group(1)
        print(f"🔍 提取到的BVID: {bvid}")

        try:
            # 在列表中查找索引
            index = bvid_list.index(bvid)
            print(f"✅ 找到BVID，索引位置: {index}")
            return index
        except ValueError:
            print(f"❌ BVID '{bvid}' 不在列表中")
            return -1

    def find_ton_bvid_index(self,url):
        """
        针对同bvid号情况
        从B站链接中提取p参数的值
        """
        # 解析URL
        parsed_url = urlparse(url)

        # 解析查询参数
        query_params = parse_qs(parsed_url.query)

        # 获取p参数的值
        p_value = query_params.get('p', [])

        if not p_value:
            # 没有p参数，返回1
            return 1
        else:
            try:
                p_num = int(p_value[0])
                # 如果p=1，返回1；否则返回实际的p值
                return p_num if p_num >= 1 else 1
            except (ValueError, IndexError):
                # 如果p参数不是数字，返回1
                return 1

    def get_danmu_id(self,str_text):
        # 使用正则提取弹幕链接的视频id号
        pattern = r'upgcxcode/\d+/\d+/(\d+)'
        matches = re.findall(pattern, str_text)#视频号id就在文档的baseurl链接里面，通过正则可提取到

        if matches:
            # 取第一个匹配到的数字（通常就是你想要的）
            target_number = matches[0]
            print(f"提取到的数字: {target_number}")
            return target_number
        else:
            print("未找到匹配的数字")
            return None

    def pinjie_danmu_url(self,target_number):
        #返回弹幕的url
        pinjie_url = f'https://api.bilibili.com/x/v2/dm/wbi/web/seg.so?type=1&oid={str(target_number)}&segment_index=1'#只需获取视频的对应号码
        return pinjie_url

    def get_danmu_content(self,url):
        #请求弹幕内容，是proto的二进制格式
        resp = requests.get(url=url, headers=self.head)
        danmu_content = resp.content
        return danmu_content

    def jiexi_danmu_content(self,danmu_content):
        jiexi = dm_pb2.DmSegMobileReply()
        jiexi.ParseFromString(danmu_content)
        print('2026-6-17',jiexi.elems)
        danmaku_list = []
        for elem in jiexi.elems:
            danmaku_list.append({
                'time_ms': elem.progress,  # 注意：用progress而不是ctime！
                'content': elem.content,
                'mode': elem.mode,
                'color': elem.color,  # 添加颜色
                'fontsize': elem.fontsize  # 添加字体大小
            })
        #self.add_danmaku_to_video("videoa.mp4", danmaku_list, "output4.mp4")
        return danmaku_list

    @staticmethod
    def format_ass_time(milliseconds):
        """将毫秒转换为ASS时间格式,与弹幕有关；与类无关"""
        hours = milliseconds // 3600000
        milliseconds %= 3600000
        minutes = milliseconds // 60000
        milliseconds %= 60000
        seconds = milliseconds // 1000
        centiseconds = (milliseconds % 1000) // 10
        return f"{hours:01d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

    @staticmethod
    def decimal_to_bgr(color_decimal):
        """将十进制颜色值转换为ASS需要的BGR十六进制格式；与弹幕有关；与类无关"""
        # 十进制 -> 十六进制 -> 反转RGB为BGR
        hex_color = f"{color_decimal:06X}"  # 转换为6位十六进制
        bgr_hex = f"&H{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}&"  # RGB -> BGR
        return bgr_hex

    def create_ass_subtitle_with_color(self,danmaku_list, output_file, video_width=1920, video_height=1080):
        """带颜色和字体设置的ASS字幕文件"""
        ass_content = f"""[Script Info]
    ScriptType: v4.00+
    PlayResX: {video_width}
    PlayResY: {video_height}
    ScaledBorderAndShadow: yes

    [V4+ Styles]
    Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
    Style: Danmaku,Microsoft YaHei,28,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1,0,2,0,0,0,1
    Style: Top,Microsoft YaHei,26,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1,0,8,0,0,20,1
    Style: Bottom,Microsoft YaHei,26,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1,0,2,0,0,20,1

    [Events]
    Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
    """

        sorted_danmaku = sorted(danmaku_list, key=lambda x: x['time_ms'])

        for danmaku in sorted_danmaku:
            start_time = self.format_ass_time(danmaku['time_ms'])
            duration = 12000
            end_time = self.format_ass_time(danmaku['time_ms'] + duration)

            # 获取颜色（如果有的话）
            color_code = self.decimal_to_bgr(danmaku.get('color', 16777215))  # 默认白色

            # 获取字体大小（如果有的话）
            fontsize = danmaku.get('fontsize', 28)  # 默认28

            if danmaku['mode'] == 1:  # 滚动弹幕
                y_pos = random.randint(100, video_height - 100)
                ass_content += f"Dialogue: 0,{start_time},{end_time},Danmaku,,0,0,0,,{{\\move(1920,{y_pos},-500,{y_pos},0,12000)\\c{color_code}\\fs{fontsize}}}{danmaku['content']}\\N\n"

            elif danmaku['mode'] == 4:  # 底部弹幕
                ass_content += f"Dialogue: 0,{start_time},{end_time},Bottom,,0,0,0,,{{\\c{color_code}\\fs{fontsize}}}{danmaku['content']}\\N\n"

            elif danmaku['mode'] == 5:  # 顶部弹幕
                ass_content += f"Dialogue: 0,{start_time},{end_time},Top,,0,0,0,,{{\\c{color_code}\\fs{fontsize}}}{danmaku['content']}\\N\n"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(ass_content)

    def debug_ass_file(self,danmaku_list):
        """调试函数：查看生成的ASS内容"""
        ass_file = "debug_danmaku.ass"
        self.create_ass_subtitle_with_color(danmaku_list, ass_file)

        with open(ass_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print("=== 生成的ASS文件内容 ===")
            print(content)
            print("=======================")

        return ass_file

    def add_danmaku_to_video(self, video_path, danmaku_list, output_path):
        """添加弹幕到视频"""
        ffmpeg_path = self.resource_path("./ffmpeg.exe")

        if not os.path.exists(ffmpeg_path):
            print("❌ 请将ffmpeg.exe放在项目文件夹内")
            return False

        # 如果output_path只是文件名（没有路径），就加上video_path的目录
        if os.path.dirname(output_path) == "":
            # 获取video_path所在的目录
            video_dir = os.path.dirname(video_path)
            # 组合成完整的输出路径
            output_path = os.path.join(video_dir, output_path)

        ass_file = self.debug_ass_file(danmaku_list)
        print('弹幕路径：',video_path)
        print('弹幕路径：',output_path)
        cmd = [
            ffmpeg_path, '-i', video_path,
            '-vf', f'ass={ass_file}',
            '-c:a', 'copy', '-y', output_path,
            '-loglevel', 'quiet'  # 让FFmpeg也保持安静
        ]

        try:
            # 关键是这一行，传递 creationflags 参数
            if sys.platform == "win32":
                result = subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,  # 捕获输出，避免泄漏
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW  # 隐藏窗口的关键
                )
            else:
                # 非Windows系统
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ 弹幕添加成功！")
            return True
        except subprocess.CalledProcessError as e:
            # 错误处理可以记录到文件，因为控制台不可见
            with open("error_log.txt", "a") as f:
                f.write(f"FFmpeg error: {e.stderr}\n")
            return False
        finally:
            # 清理临时文件
            if os.path.exists(ass_file):
                os.remove(ass_file)

    def save_danmaku_to_file(self, danmaku_list, video_title,save_dir):
        """将弹幕内容保存为文件（只保留文字）"""
        try:
            # 清理视频标题中的非法字符
            #safe_title = self.sanitize_filename(video_title) if video_title else "danmaku"
            filename = f"{video_title}弹幕.txt"

            # 保存到下载目录
            filepath = os.path.join(save_dir, filename)

            # 只提取弹幕文字内容
            danmaku_texts = [dm['content'] for dm in danmaku_list]

            # 保存为文本文件，每条弹幕一行
            with open(filepath, 'w', encoding='utf-8') as f:
                for text in danmaku_texts:
                    f.write(text + '\n')

        except Exception as e:
            return None

    def resource_path(self, relative_path):
        """获取资源的绝对路径，处理PyInstaller打包后的路径问题"""
        try:
            # PyInstaller创建的临时文件夹
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath("./")

        return os.path.join(base_path, relative_path)

    #返回合集列表
    def get_series_urls(self, str_text,url):

        match1 = re.search(r'<div class="amt" data-v-dac4fbd2>（(\d+)/(\d+)）</div>', str_text)
        match2 = re.search(r'<div class="amt" data-v-625117f2>（(\d+)/(\d+)）</div>', str_text)

        # 优先取 match1，没有则取 match2
        match = match1 or match2

        if not match:
            return None

        current, total = match.groups()
        total_pages = int(total)

        # 解析 URL
        parsed = urlparse(url)
        # 重组 URL（只保留 scheme, netloc, path）
        base_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))
        url_list = []
        for page in range(1, total_pages + 1):
            video_url = f"{base_url}?p={page}"
            url_list.append(video_url)

        return url_list

    #指定列表中哪些url需要
    def zhiding_heji_qujian_urls(self,url_list,zhiding_str):
        """
        根据范围字符串获取对应的URL列表
        支持格式：'1-3', '1,3,5', '1-3,5,7-9'
        """
        urls = []

        # 去除空格并分割逗号
        parts = [part.strip() for part in zhiding_str.split(',')]
        print(parts, 'parts')
        for part in parts:
            if not part:  # 跳过空的部分
                continue

            if '-' in part:
                # 处理范围，如 '1-3'
                start_end = part.split('-')
                if len(start_end) == 2:
                    try:
                        start = int(start_end[0].strip())
                        end = int(start_end[1].strip())

                        # 验证范围有效性
                        if 1 <= start <= len(url_list) and 1 <= end <= len(url_list) and start <= end:
                            urls.extend(url_list[start - 1:end])
                        else:
                            print(f"警告：范围 {start}-{end} 无效，已跳过")

                    except ValueError:
                        print(f"警告：'{part}' 不是有效的范围格式，已跳过")



            else:
                # 处理单个数字，如 '5'
                try:
                    index = int(part.strip())
                    if 1 <= index <= len(url_list):
                        urls.append(url_list[index - 1])
                    else:
                        print(f"警告：集数 {index} 超出范围，已跳过")

                except ValueError:
                    print(f"警告：'{part}' 不是有效的数字，已跳过")


        return urls


    def get_video_1080_url(self, str_text):
        """
        从文本中提取视频URL
        """
        l = []  # 存储所有找到的URL

        # 第一次尝试：使用baseUrl（驼峰命名）
        obj1 = re.compile(r'"id":80,"baseUrl":"(?P<shiping_url_1080>.*?)"', re.S)
        result1 = obj1.finditer(str_text)
        matches1 = list(result1)  # 转换为列表以便重用

        if matches1:
            # print("✅ 使用baseUrl模式找到匹配项")
            for i in matches1:
                url = i.groupdict()['shiping_url_1080']
                # print(f"找到URL: {url}")
                l.append(url)
        else:
            # 第一次没找到，尝试base_url（蛇形命名）
            # print("⚠️ baseUrl模式未找到，尝试base_url模式")
            obj2 = re.compile(r'"id":80,"base_url":"(?P<shiping_url_1080>.*?)"', re.S)
            result2 = obj2.finditer(str_text)
            matches2 = list(result2)

            if matches2:
                # print("✅ 使用base_url模式找到匹配项")
                for i in matches2:
                    url = i.groupdict()['shiping_url_1080']
                    # print(f"找到URL: {url}")
                    l.append(url)
            else:
                # print("❌ 两种模式都未找到匹配项")
                return None

        # 统一的返回逻辑
        if len(l) >= 3:
            print(f"🎯 找到{len(l)}个URL，返回中间的第2个")
            return l[1]
        elif len(l) == 2:
            print("🎯 找到2个URL，返回第1个")
            return l[0]
        elif len(l) == 1:
            print("🎯 找到1个URL，返回它")
            return l[0]
        else:
            # print("❌ 没有找到任何URL")
            return None

    def get_video_720_url(self, str_text):
        l = []  # 存储所有找到的URL

        # 第一次尝试：使用baseUrl（驼峰命名）
        obj1 = re.compile(r'"id":64,"baseUrl":"(?P<shiping_url_720>.*?)"', re.S)
        result1 = obj1.finditer(str_text)
        matches1 = list(result1)  # 转换为列表以便重用

        if matches1:
            # print("✅ 使用baseUrl模式找到匹配项")
            for i in matches1:
                url = i.groupdict()['shiping_url_720']
                # print(f"找到URL: {url}")
                l.append(url)
        else:
            # 第一次没找到，尝试base_url（蛇形命名）
            # print("⚠️ baseUrl模式未找到，尝试base_url模式")
            obj2 = re.compile(r'"id":64,"base_url":"(?P<shiping_url_720>.*?)"', re.S)
            result2 = obj2.finditer(str_text)
            matches2 = list(result2)

            if matches2:
                # print("✅ 使用base_url模式找到匹配项")
                for i in matches2:
                    url = i.groupdict()['shiping_url_720']
                    # print(f"找到URL: {url}")
                    l.append(url)
            else:
                # print("❌ 两种模式都未找到匹配项")
                return None

        # 统一的返回逻辑
        if len(l) >= 3:
            # print(f"🎯 找到{len(l)}个URL，返回中间的第2个")
            return l[1]
        elif len(l) == 2:
            # print("🎯 找到2个URL，返回第1个")
            return l[0]
        elif len(l) == 1:
            # print("🎯 找到1个URL，返回它")
            return l[0]
        else:
            # print("❌ 没有找到任何URL")
            return None

    def get_video_480_url(self, str_text):
        """
        从文本中提取视频URL
        """
        l = []  # 存储所有找到的URL

        # 第一次尝试：使用baseUrl（驼峰命名）
        obj1 = re.compile(r'"id":32,"baseUrl":"(?P<shiping_url_480>.*?)"', re.S)
        result1 = obj1.finditer(str_text)
        matches1 = list(result1)  # 转换为列表以便重用

        if matches1:
            # print("✅ 使用baseUrl模式找到匹配项")
            for i in matches1:
                url = i.groupdict()['shiping_url_480']
                # print(f"找到URL: {url}")
                l.append(url)
        else:
            # 第一次没找到，尝试base_url（蛇形命名）
            # print("⚠️ baseUrl模式未找到，尝试base_url模式")
            obj2 = re.compile(r'"id":32,"base_url":"(?P<shiping_url_480>.*?)"', re.S)
            result2 = obj2.finditer(str_text)
            matches2 = list(result2)

            if matches2:
                # print("✅ 使用base_url模式找到匹配项")
                for i in matches2:
                    url = i.groupdict()['shiping_url_480']
                    # print(f"找到URL: {url}")
                    l.append(url)
            else:
                # print("❌ 两种模式都未找到匹配项")
                return None

        # 统一的返回逻辑
        if len(l) >= 3:
            # print(f"🎯 找到{len(l)}个URL，返回中间的第2个")
            return l[1]
        elif len(l) == 2:
            # print("🎯 找到2个URL，返回第1个")
            return l[0]
        elif len(l) == 1:
            # print("🎯 找到1个URL，返回它")
            return l[0]
        else:
            # print("❌ 没有找到任何URL")
            return None

    def get_video_360_url(self, str_text):
        print('视频进来了')
        l = []  # 存储所有找到的URL

        # 第一次尝试：使用baseUrl（驼峰命名）
        obj1 = re.compile(r'"id":16,"baseUrl":"(?P<shiping_url_360>.*?)"', re.S)
        result1 = obj1.finditer(str_text)
        matches1 = list(result1)  # 转换为列表以便重用

        if matches1:
            # print("✅ 使用baseUrl模式找到匹配项")
            for i in matches1:
                url = i.groupdict()['shiping_url_360']
                # print(f"找到URL: {url}")
                l.append(url)
        else:
            # 第一次没找到，尝试base_url（蛇形命名）
            # print("⚠️ baseUrl模式未找到，尝试base_url模式")
            obj2 = re.compile(r'"id":16,"base_url":"(?P<shiping_url_360>.*?)"', re.S)
            result2 = obj2.finditer(str_text)
            matches2 = list(result2)

            if matches2:
                # print("✅ 使用base_url模式找到匹配项")
                for i in matches2:
                    url = i.groupdict()['shiping_url_360']
                    # print(f"找到URL: {url}")
                    l.append(url)
            else:
                #print("❌ 两种模式都未找到匹配项")
                return None

        # 统一的返回逻辑
        if len(l) >= 3:
            print(f"🎯 找到{len(l)}个URL，返回中间的第2个")
            return l[1]
        elif len(l) == 2:
            print("🎯 找到2个URL，返回第1个")
            return l[0]
        elif len(l) == 1:
            print("🎯 找到1个URL，返回它")
            return l[0]
        else:
            print("❌ 没有找到任何URL")
            return None

    def get_audio_url(self,str_text):
        print('音频进来了')
        """
        按优先级获取音频URL：30280 > 30232 > 30216
        """
        # 定义音频ID的优先级顺序
        audio_ids = [30280, 30232, 30216]

        for audio_id in audio_ids:
            # 优先尝试 baseUrl（驼峰命名）
            pattern1 = rf'{audio_id},"baseUrl":"(.*?)"'
            result1 = re.search(pattern1, str_text, re.S)

            if result1:
                print(result1)
                return result1.group(1)

            # 如果 baseUrl 没找到，尝试 base_url（蛇形命名）
            pattern2 = rf'{audio_id},"base_url":"(.*?)"'
            result2 = re.search(pattern2, str_text, re.S)

            if result2:
                print(result2)
                return result2.group(1)

        # 三个音频ID都没有找到
        return None

    def download_file(self, url, save_path):
        resp = requests.get(url, headers=self.head, stream=True)

        total_size = int(resp.headers.get('content-length', 0))
        downloaded = 0

        with open(save_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    yield downloaded, total_size

    def merge_video_audio(self, video_path, audio_path, output_path):
        ffmpeg_path = self.resource_path("./ffmpeg.exe")

        # 清理非法字符
        dir_name = os.path.dirname(output_path)
        base_name = os.path.basename(output_path)
        safe_output = os.path.join(dir_name, re.sub(r'[\\/*?:"<>|]', '-', base_name))
        print(f"原始路径: {output_path}")
        print(f"安全路径: {safe_output}")
        cmd = [
            ffmpeg_path, '-y', '-loglevel', 'warning',
            '-i', video_path, '-i', audio_path,
            '-c:v', 'copy', '-c:a', 'copy',
            '-bsf:a', 'aac_adtstoasc',
            safe_output
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    encoding='utf-8',
                                    creationflags=subprocess.CREATE_NO_WINDOW)
            return result.returncode
        except Exception as e:
            print(f"❌ 执行错误: {e}")
            return 1


##工作线程类
class CrawlerThread(QThread):
    progress_updated = pyqtSignal(int, int)  # 进度更新信号：当前值和最大值
    status_updated = pyqtSignal(str, str)  # 状态更新信号：发送状态文字和颜色
    result_ready = pyqtSignal(dict)  # 爬取结果
    download_complete = pyqtSignal(str, str)  # 文件类型, 路径
    merge_complete = pyqtSignal(str)  # 输出路径
    series_progress = pyqtSignal(int, int)  # 合集进度: 当前, 总数
    result_message = pyqtSignal(str)  # 新增信号用于传递结果消息

    def __init__(self, crawler, url, save_dir, quality='1080', download_series=1,series_range=None,download_danmu=False,baoliu_yinshiping=True):
        super().__init__()
        self.crawler = crawler
        self.url = url
        self.save_dir = save_dir
        self.quality = quality
        self.download_series = download_series  #单集1，合集2，合集指定3，收藏夹下载4
        self.series_range = series_range# 新增：存储用户输入合集的范围
        self.download_danmu = download_danmu  # 是否下载弹幕
        self.baoliu_yinshiping = baoliu_yinshiping  # 是否保留音视频
        self.video_path = None
        self.audio_path = None

    def run(self):
        try:
            #单集下载
            if self.download_series == 1:
                self.download_single_video()
            elif self.download_series == 2:
                self.download_series_videos()
            elif self.download_series == 3:
                self.download_series_zhiding_videos()
            elif self.download_series == 4:
                self.download_shouchangye_videos()
            else:
                raise ValueError

        except Exception as e:
            self.status_updated.emit(f"发生错误: {str(e)}", "#e06c75")

    #单集下载
    def download_single_video(self):
        print('我是单集下载***********************')
        """下载单个视频（使用新进度逻辑）"""
        start_time = time.time()

        def update_status(stage):
            elapsed = time.strftime("%M:%S", time.gmtime(time.time() - start_time))
            stages = {
                "video": ("下载视频", "#61dafb"),
                "audio": ("下载音频", "#98c379"),
                "merge": ("合并文件", "#e5c07b"),
                "danmu": ("下载合并弹幕", "#e5c07b")
            }
            text, color = stages[stage]
            self.status_updated.emit(f"⏳ 单集视频 | {text} | 用时 {elapsed}", color)

        try:
            page_text = self.crawler.get_page_text(self.url)
            #print(page_text)
            bvid_list = self.crawler.get_page_bvid(page_text)

            #print('999999999999999', bvid_list)
            if bvid_list:
                print('合集视频是不同bvid形式')
                # 不为空走获取bvid形式
                #urls = self.crawler.heji_url_pinjie(bvid_list)
                buton_bvid_index = self.crawler.find_buton_bvid_index(self.url, bvid_list)
                title_list = self.crawler.get_duo_bvid_page_title(page_text)
                dange_shiping_biaoti = title_list[buton_bvid_index]
            else:
                # 为空走链接=1，链接=2合集形式

                print('合集视频是=1=2')
                #print('jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj')
                title_list = self.crawler.get_dange_bvid_page_title(page_text)

                #print('title是：',title_list)
                ton_bvid_index = self.crawler.find_ton_bvid_index(self.url)
                print('ton_bvid_index的结果是',ton_bvid_index)
                print('title_list的结果是。。。。。',title_list)
                dange_shiping_biaoti = title_list[ton_bvid_index-1]

                print('单集视频的标题是：',dange_shiping_biaoti)


            # --- 阶段1：下载视频 ---
            update_status("video")
            if self.quality == '1080':
                video_url = self.crawler.get_video_1080_url(page_text)
            elif self.quality == '720':
                video_url = self.crawler.get_video_720_url(page_text)
            elif self.quality == '480':
                video_url = self.crawler.get_video_480_url(page_text)
            else:
                video_url = self.crawler.get_video_360_url(page_text)

            audio_url = self.crawler.get_audio_url(page_text)

            if not video_url or not audio_url:
                self.status_updated.emit("获取视频/音频链接失败", "#e06c75")
                return

            self.result_message.emit('下载视频中...')
            # 视频下载 (0%-40%)
            video_path = os.path.join(self.save_dir, f"单集_视频{str(int(start_time))}.mp4")
            for downloaded, total in self.crawler.download_file(video_url, video_path):
                progress = int((downloaded / total) * 40)
                self.progress_updated.emit(progress, 100)
            self.result_message.emit('下载音频中...')
            # --- 阶段2：下载音频 ---
            update_status("audio")
            # 音频下载 (40%-80%)
            audio_path = os.path.join(self.save_dir, f"单集_音频{str(int(start_time))}.m4a")
            for downloaded, total in self.crawler.download_file(audio_url, audio_path):
                progress = 40 + int((downloaded / total) * 40)
                self.progress_updated.emit(progress, 100)
            self.result_message.emit('合并文件中...')
            # --- 阶段3：合并文件 ---
            update_status("merge")
            #处理标题中特殊字符
            dange_shiping_biaoti = self.crawler.sanitize_title(dange_shiping_biaoti)
            print(dange_shiping_biaoti)
            # 合并处理 (80%-100%)
            output_path = os.path.join(self.save_dir, f"{dange_shiping_biaoti}.mp4")
            # 模拟合并进度
            for i in range(1, 6):
                self.progress_updated.emit(80 + i * 4, 100)
                time.sleep(0.05)

            ret = self.crawler.merge_video_audio(video_path, audio_path, output_path)
            # 如果合并成功
            if (ret == 0):
                #弹幕选择为是
                if (self.download_danmu == '烧录弹幕至视频'):

                    self.result_message.emit('音视频合并完成！')
                    danmu_process_start = time.time()  # 记录弹幕处理开始时间

                    # 弹幕下载开始
                    self.status_updated.emit("✅ 弹幕下载开始", "#98c379")

                    wendang_url = self.url
                    str_text = self.crawler.get_page_text(wendang_url)
                    danmu_id = self.crawler.get_danmu_id(str_text)

                    # 判断id是否为空
                    if danmu_id == None:
                        self.status_updated.emit("❌ 获取弹幕失败", "#e06c75")
                        return

                    # 计算弹幕下载耗时（精确到毫秒）
                    download_time = time.time() - danmu_process_start
                    elapsed_download = f"{download_time:.2f}秒"  # 显示3位小数
                    self.status_updated.emit(f"✅ 弹幕下载完成 | 用时 {elapsed_download}", "#98c379")

                    danmu_url = self.crawler.pinjie_danmu_url(danmu_id)
                    danmu_content = self.crawler.get_danmu_content(danmu_url)

                    danmaku_list = self.crawler.jiexi_danmu_content(danmu_content)

                    # 弹幕与视频合并开始
                    merge_start = time.time()
                    self.status_updated.emit("✅ 弹幕与视频合并开始", "#98c379")
                    self.result_message.emit('弹幕与视频开始合并...')
                    #print('2026-6-16路径',output_path)
                    # 调用弹幕合并
                    self.crawler.add_danmaku_to_video(output_path, danmaku_list, f"弹幕合并视频{str(int(start_time))}.mp4")

                    # 计算合并耗时（精确到毫秒）
                    merge_time = time.time() - merge_start
                    elapsed_merge = f"{merge_time:.2f}秒"

                    # 计算总耗时（精确到毫秒）
                    total_time = time.time() - danmu_process_start
                    elapsed_total = f"{total_time:.2f}秒"

                    # 计算总耗时（精确到毫秒）
                    total2_time = time.time() - start_time
                    elapsed2_total = f"{total2_time:.2f}秒"


                    self.progress_updated.emit(100, 100)
                    self.status_updated.emit(f"✅ 弹幕与视频合并完成 | 弹幕合并用时 {elapsed_merge}，下载弹幕并合并用时 {elapsed_total}，下载视频合并弹幕总用时{elapsed2_total}",
                                             "#98c379")
                    self.result_message.emit('弹幕下载合并完成！')

                    if self.baoliu_yinshiping == False:
                        # 清理临时文件
                        os.remove(video_path)
                        os.remove(audio_path)
                #弹幕选择为仅下载弹幕
                elif (self.download_danmu == '仅下载弹幕'):
                    danmu_process_start = time.time()  # 记录弹幕处理开始时间

                    # 弹幕下载开始
                    self.status_updated.emit("✅ 弹幕下载开始", "#98c379")

                    wendang_url = self.url
                    str_text = self.crawler.get_page_text(wendang_url)
                    danmu_id = self.crawler.get_danmu_id(str_text)

                    # 判断id是否为空
                    if danmu_id == None:
                        self.status_updated.emit("❌ 获取弹幕失败", "#e06c75")
                        return

                    # 计算弹幕下载耗时（精确到毫秒）
                    download_time = time.time() - danmu_process_start
                    elapsed_download = f"{download_time:.2f}秒"  # 显示小数
                    self.status_updated.emit(f"✅ 弹幕下载完成 | 用时 {elapsed_download}", "#98c379")

                    danmu_url = self.crawler.pinjie_danmu_url(danmu_id)
                    danmu_content = self.crawler.get_danmu_content(danmu_url)
                    danmaku_list = self.crawler.jiexi_danmu_content(danmu_content)
                    #print('到处路径：',self.save_dir)
                    self.crawler.save_danmaku_to_file(danmaku_list, dange_shiping_biaoti,self.save_dir)
                    self.status_updated.emit(f"✅ 弹幕保存到{dange_shiping_biaoti}.txt文件 | 用时 {elapsed_download}", "#98c379")
                    if self.baoliu_yinshiping == False:
                        # 清理临时文件
                        os.remove(video_path)
                        os.remove(audio_path)

                #弹幕选否
                else:
                    elapsed = time.strftime("%M:%S", time.gmtime(time.time() - start_time))
                    self.status_updated.emit(f"✅ 单集下载完成 | 用时 {elapsed}", "#98c379")
                    if self.baoliu_yinshiping == False:
                        # 清理临时文件
                        os.remove(video_path)
                        os.remove(audio_path)
                    # print((ret == 0) and (self.download_danmu == True))
                    self.progress_updated.emit(100, 100)
                    self.result_message.emit('单集下载完成！')
            #合并失败
            else:
                self.status_updated.emit("❌ 合并失败", "#e06c75")



        except Exception as e:
            self.status_updated.emit(f"⚠️ 错误: {str(e)}", "#e06c75")
    #合集下载
    def download_series_videos(self):
        print('我是合集下载***********************')
        """下载合集所有视频（平滑进度版）"""
        self.status_updated.emit("正在获取合集信息...", "#61dafb")
        # 初始化计时器和总数
        start_time = time.time()
        page_text = self.crawler.get_page_text(self.url)

        # print(urls)
        #获取bvid列表，如果为空，那视频大概率是=1，=2的形式
        bvid_list = self.crawler.get_page_bvid(page_text)
        print('999999999999999',bvid_list)


        title_biaozhi = 1

        if bvid_list:
            print('合集视频是不同bvid形式')
            #不为空走获取bvid形式
            urls = self.crawler.heji_url_pinjie(bvid_list)
        else:
            # 为空走链接=1，链接=2合集形式
            print('合集视频是=1=2')
            urls = self.crawler.get_series_urls(page_text, self.url)
            title_biaozhi = 0
        # urls = self.crawler.get_series_urls(page_text, self.url)


        print(urls)
        #添加状态更新函数
        def update_status(idx, stage):
            elapsed = time.strftime("%M:%S", time.gmtime(time.time() - start_time))
            progress = int((idx - 1) / total_videos * 100)  # 当前完成进度百分比
            stages = {
                "video": ("下载视频", "#61dafb"),
                "audio": ("下载音频", "#98c379"),
                "merge": ("合并文件", "#e5c07b")
            }
            text, color = stages[stage]
            self.status_updated.emit(
                f"⏳ 视频 {idx}/{total_videos} ({progress}%) | {text} | 用时 {elapsed}",
                color
            )

        if not urls:
            self.status_updated.emit("获取合集视频列表失败", "#e06c75")
            return
        total_videos = len(urls)
        total_steps = total_videos * 3  # 每个视频有3个阶段
        current_step = 0

        # 创建合集文件夹
        series_dir = os.path.join(self.save_dir, "合集_" + str(int(time.time())))
        os.makedirs(series_dir, exist_ok=True)

        html_text = self.crawler.get_page_text(urls[0])
        if title_biaozhi == 1:
            #拿多bvid视频标题
            title_list = self.crawler.get_duo_bvid_page_title(html_text)
            #print(title_list,'777777777777777777777视频标题')
        else:
            #拿相同bvid视频标题
            title_list = self.crawler.get_dange_bvid_page_title(html_text)
            #print(title_list, '55555555555555555555视频标题')
        print(title_list)
        for idx, video_url in enumerate(urls, 1):
            self.status_updated.emit(f"正在处理视频 {idx}/{total_videos}", "#61dafb")

            try:
                # --- 阶段1：准备资源 ---
                video_page = self.crawler.get_page_text(video_url)
                if self.quality == '1080':
                    video_url = self.crawler.get_video_1080_url(video_page)
                elif self.quality == '720':
                    video_url = self.crawler.get_video_720_url(video_page)
                elif self.quality == '480':
                    video_url = self.crawler.get_video_480_url(video_page)
                else:
                    video_url = self.crawler.get_video_360_url(video_page)
                audio_url = self.crawler.get_audio_url(video_page)
                #print('video******************',video_url)
                #print('audio********************',audio_url)
                if not video_url or not audio_url:
                    self.result_message.emit(f"视频 {idx} 获取链接失败\n")
                    current_step += 3  # 跳过这个视频的3个步骤
                    continue

                # --- 阶段2：下载视频 ---
                update_status(idx, "video")
                video_path = os.path.join(series_dir, f"视频_{idx}.mp4")
                for downloaded, total in self.crawler.download_file(video_url, video_path):
                    progress = int((current_step + (downloaded / total)) / total_steps * 100)
                    self.progress_updated.emit(progress, 100)

                current_step += 1
                self.progress_updated.emit(int(current_step / total_steps * 100), 100)

                # --- 阶段3：下载音频 ---
                update_status(idx, "audio")  # 音频下载阶段
                audio_path = os.path.join(series_dir, f"音频_{idx}.m4a")
                for downloaded, total in self.crawler.download_file(audio_url, audio_path):
                    progress = int((current_step + (downloaded / total)) / total_steps * 100)
                    self.progress_updated.emit(progress, 100)

                current_step += 1
                self.progress_updated.emit(int(current_step / total_steps * 100), 100)

                # --- 阶段4：合并文件 ---
                update_status(idx, "merge")  # 合并阶段
                #output_path = os.path.join(series_dir, f"合集_合并音视频_{idx}.mp4")
                hejibiaoti_zhiyi = self.crawler.sanitize_title(title_list[idx-1])
                print(hejibiaoti_zhiyi)
                output_path = os.path.join(series_dir, f"{hejibiaoti_zhiyi}.mp4")
                ret = self.crawler.merge_video_audio(video_path, audio_path, output_path)

                current_step += 1
                self.progress_updated.emit(int(current_step / total_steps * 100), 100)

                if ret == 0:
                    self.result_message.emit(f"✅ 视频 {idx} 完成\n")
                    if self.baoliu_yinshiping == False:
                        # 清理临时文件
                        os.remove(video_path)
                        os.remove(audio_path)
                    # os.remove(video_path)
                    # os.remove(audio_path)
                else:
                    self.result_message.emit(f"❌ 视频 {idx} 合并失败\n")

            except Exception as e:
                self.result_message.emit(f"⚠️ 视频 {idx} 错误: {str(e)}\n")
                current_step += 3  # 出错时跳过剩余步骤
        # 在合集下载完成时
        elapsed = time.strftime("%M:%S", time.gmtime(time.time() - start_time))
        self.status_updated.emit(f"✅ 合集下载完成! 共 {total_videos}个视频 | 总用时 {elapsed}", "#98c379")
        self.progress_updated.emit(100, 100)  # 确保完成
        #self.merge_complete.emit(series_dir)
        time.sleep(0.3)
        self.merge_complete.emit(series_dir)

    # 指定合集下载
    def download_series_zhiding_videos(self):
        print('我是合集下载***********************')
        """下载合集所有视频（平滑进度版）"""
        self.status_updated.emit("正在获取合集信息...", "#61dafb")
        # 初始化计时器和总数
        start_time = time.time()
        page_text = self.crawler.get_page_text(self.url)
        # urls = self.crawler.get_series_urls(page_text, self.url)
        # print(urls)
        bvid_list = self.crawler.get_page_bvid(page_text)
        #urls = self.crawler.heji_url_pinjie(bvid_list)
        title_biaozhi = 1
        if bvid_list:
            print('合集视频是不同bvid形式')
            #不为空走获取bvid形式
            urls = self.crawler.heji_url_pinjie(bvid_list)
        else:
            # 为空走链接=1，链接=2合集形式
            print('合集视频是=1=2')
            urls = self.crawler.get_series_urls(page_text, self.url)
            print('urls是是：：：：：：：：：：：：：：：：：：：：：：：：：：：：：：：：',urls)
            title_biaozhi = 0

        #print(urls)

        # 添加状态更新函数
        def update_status(idx, stage):
            elapsed = time.strftime("%M:%S", time.gmtime(time.time() - start_time))
            progress = int((idx - 1) / total_videos * 100)  # 当前完成进度百分比
            stages = {
                "video": ("下载视频", "#61dafb"),
                "audio": ("下载音频", "#98c379"),
                "merge": ("合并文件", "#e5c07b")
            }
            text, color = stages[stage]
            self.status_updated.emit(
                f"⏳ 视频 {idx}/{total_videos} ({progress}%) | {text} | 用时 {elapsed}",
                color
            )

        if not urls:
            self.status_updated.emit("获取合集视频列表失败", "#e06c75")
            return
        urls = self.crawler.zhiding_heji_qujian_urls(urls, self.series_range)
        print('指定后的视频')
        print(urls)

        total_videos = len(urls)
        total_steps = total_videos * 3  # 每个视频有3个阶段
        current_step = 0

        # 创建合集文件夹
        series_dir = os.path.join(self.save_dir, "合集_" + str(int(time.time())))
        os.makedirs(series_dir, exist_ok=True)

        # 拿视频标题
        html_text = self.crawler.get_page_text(urls[0])

        if title_biaozhi == 1:
            #拿多bvid视频标题
            title_list = self.crawler.get_duo_bvid_page_title(html_text)
            #print(title_list,'777777777777777777777视频标题')
        else:
            title_list = self.crawler.get_dange_bvid_page_title(html_text)
            #print(title_list, '55555555555555555555视频标题')

        print(self.series_range)
        title_list = self.crawler.zhiding_bvid(self.series_range,title_list)
        print(title_list)

        for idx, video_url in enumerate(urls, 1):
            self.status_updated.emit(f"正在处理视频 {idx}/{total_videos}", "#61dafb")

            try:
                # --- 阶段1：准备资源 ---
                video_page = self.crawler.get_page_text(video_url)
                if self.quality == '1080':
                    video_url = self.crawler.get_video_1080_url(video_page)
                elif self.quality == '720':
                    video_url = self.crawler.get_video_720_url(video_page)
                elif self.quality == '480':
                    video_url = self.crawler.get_video_480_url(video_page)
                else:
                    video_url = self.crawler.get_video_360_url(video_page)
                audio_url = self.crawler.get_audio_url(video_page)
                # print('video******************',video_url)
                # print('audio********************',audio_url)
                if not video_url or not audio_url:
                    self.result_message.emit(f"视频 {idx} 获取链接失败\n")
                    current_step += 3  # 跳过这个视频的3个步骤
                    continue

                # --- 阶段2：下载视频 ---
                update_status(idx, "video")
                video_path = os.path.join(series_dir, f"视频_{idx}.mp4")
                for downloaded, total in self.crawler.download_file(video_url, video_path):
                    progress = int((current_step + (downloaded / total)) / total_steps * 100)
                    self.progress_updated.emit(progress, 100)

                current_step += 1
                self.progress_updated.emit(int(current_step / total_steps * 100), 100)

                # --- 阶段3：下载音频 ---
                update_status(idx, "audio")  # 音频下载阶段
                audio_path = os.path.join(series_dir, f"音频_{idx}.m4a")
                for downloaded, total in self.crawler.download_file(audio_url, audio_path):
                    progress = int((current_step + (downloaded / total)) / total_steps * 100)
                    self.progress_updated.emit(progress, 100)

                current_step += 1
                self.progress_updated.emit(int(current_step / total_steps * 100), 100)

                # --- 阶段4：合并文件 ---
                update_status(idx, "merge")  # 合并阶段
                # output_path = os.path.join(series_dir, f"合集_合并音视频_{idx}.mp4")
                hejibiaoti_zhiyi = self.crawler.sanitize_title(title_list[idx - 1])
                #print(hejibiaoti_zhiyi)
                output_path = os.path.join(series_dir, f"{hejibiaoti_zhiyi}.mp4")
                ret = self.crawler.merge_video_audio(video_path, audio_path, output_path)

                current_step += 1
                self.progress_updated.emit(int(current_step / total_steps * 100), 100)

                if ret == 0:
                    self.result_message.emit(f"✅ 视频 {idx} 完成\n")
                    if self.baoliu_yinshiping == False:
                        # 清理临时文件
                        os.remove(video_path)
                        os.remove(audio_path)
                    # os.remove(video_path)
                    # os.remove(audio_path)
                else:
                    self.result_message.emit(f"❌ 视频 {idx} 合并失败\n")

            except Exception as e:
                self.result_message.emit(f"⚠️ 视频 {idx} 错误: {str(e)}\n")
                current_step += 3  # 出错时跳过剩余步骤
        # 在合集下载完成时
        elapsed = time.strftime("%M:%S", time.gmtime(time.time() - start_time))
        self.status_updated.emit(f"✅ 合集下载完成! 共 {total_videos}个视频 | 总用时 {elapsed}", "#98c379")
        self.progress_updated.emit(100, 100)  # 确保完成
        # self.merge_complete.emit(series_dir)
        time.sleep(0.3)
        self.merge_complete.emit(series_dir)


    #收藏夹下载
    def download_shouchangye_videos(self):
        print('呵呵呵呵')
        # print(self.url)
        #这个函数用于配合while循环替换pn=数字，这个数字代表收藏页的页面
        def set_pn_param(url, pn_value):
            """替换或添加 pn 参数"""
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            query_params['pn'] = [str(pn_value)]

            # 重新构建 query 字符串
            from urllib.parse import urlencode
            new_query = urlencode(query_params, doseq=True)

            # 替换原有 query
            new_parsed = parsed._replace(query=new_query)
            return urlunparse(new_parsed)
        sum = 1 #代表收藏页的第n页面
        z = 0 #统计收藏夹视频总数
        flag = True #结合收藏页中的has_more，当has_more为false，这里的flag也会修改为False
        shouchangjia_url_end_list =[]#合成为一个大列表，后续直接从这个大列表里去依依请求url下载
        while flag:
            new_shouchangye_url = set_pn_param(url=self.url,pn_value=sum)
            resp = self.crawler.get_page_text(new_shouchangye_url)
            js = resp
            url_list = self.crawler.huoqu_danye_shouchang_url_list(js)
            shouchangjia_url_end_list.extend(url_list)
            flag = self.crawler.huoqu_danye_shouchang_biaoqian(js)
            print(flag)
            print(len(url_list))
            z += len(url_list)
            #print(url_list)
            # print(len(url_list)
            sum += 1
            time.sleep(1)
        print('收藏夹视频获取的总数为：',z)
        print(shouchangjia_url_end_list)

        # """获取收藏夹所有视频标题"""
        shouchangjia_all_biaoti_list= []
        for shouchangjia_dange_url in shouchangjia_url_end_list:
            shouchangjia_dange_shiping_page_text = self.crawler.get_page_text(shouchangjia_dange_url)
            shouchangjia_dange_biaoti = self.crawler.huoqu_shouchangjia_dange_url_biaoti(shouchangjia_dange_shiping_page_text)
            shouchangjia_all_biaoti_list.append(shouchangjia_dange_biaoti)
        #print(shouchangjia_all_biaoti_list)



        #print('cookie:',self.crawler.cookie)
        print('head:',self.crawler.head)


        print('我是收藏夹下载***********************')
        """下载收藏夹所有视频"""
        self.status_updated.emit("正在获取收藏夹信息...", "#61dafb")
        # 初始化计时器和总数
        start_time = time.time()
        #添加状态更新函数
        def update_status(idx, stage):
            elapsed = time.strftime("%M:%S", time.gmtime(time.time() - start_time))
            progress = int((idx - 1) / total_videos * 100)  # 当前完成进度百分比
            stages = {
                "video": ("下载视频", "#61dafb"),
                "audio": ("下载音频", "#98c379"),
                "merge": ("合并文件", "#e5c07b")
            }
            text, color = stages[stage]
            self.status_updated.emit(
                f"⏳ 视频 {idx}/{total_videos} ({progress}%) | {text} | 用时 {elapsed}",
                color
            )

        if not shouchangjia_url_end_list:
            self.status_updated.emit("获取收藏夹视频列表失败", "#e06c75")
            return
        total_videos = len(shouchangjia_url_end_list)
        total_steps = total_videos * 3  # 每个视频有3个阶段
        current_step = 0

        # 创建合集文件夹
        series_dir = os.path.join(self.save_dir, "收藏夹_" + str(int(time.time())))
        os.makedirs(series_dir, exist_ok=True)

        html_text = self.crawler.get_page_text(shouchangjia_url_end_list[0])

        for idx, video_url in enumerate(shouchangjia_url_end_list, 1):
            self.status_updated.emit(f"正在处理视频 {idx}/{total_videos}", "#61dafb")

            try:
                # --- 阶段1：准备资源 ---
                video_page = self.crawler.get_page_text(video_url)
                #print('2026-4-9hhhhhhhhhhhhhhhhh',video_page)
                if self.quality == '1080':
                    video_url = self.crawler.get_video_1080_url(video_page)
                elif self.quality == '720':
                    video_url = self.crawler.get_video_720_url(video_page)
                elif self.quality == '480':
                    video_url = self.crawler.get_video_480_url(video_page)
                else:
                    video_url = self.crawler.get_video_360_url(video_page)
                audio_url = self.crawler.get_audio_url(video_page)
                #print('video******************',video_url)
                #print('audio********************',audio_url)
                if not video_url or not audio_url:
                    self.result_message.emit(f"视频 {idx} 获取链接失败\n")
                    current_step += 3  # 跳过这个视频的3个步骤
                    continue

                # --- 阶段2：下载视频 ---
                update_status(idx, "video")
                video_path = os.path.join(series_dir, f"视频_{idx}.mp4")
                for downloaded, total in self.crawler.download_file(video_url, video_path):
                    progress = int((current_step + (downloaded / total)) / total_steps * 100)
                    self.progress_updated.emit(progress, 100)

                current_step += 1
                self.progress_updated.emit(int(current_step / total_steps * 100), 100)

                # --- 阶段3：下载音频 ---
                update_status(idx, "audio")  # 音频下载阶段
                audio_path = os.path.join(series_dir, f"音频_{idx}.m4a")
                for downloaded, total in self.crawler.download_file(audio_url, audio_path):
                    progress = int((current_step + (downloaded / total)) / total_steps * 100)
                    self.progress_updated.emit(progress, 100)

                current_step += 1
                self.progress_updated.emit(int(current_step / total_steps * 100), 100)

                # --- 阶段4：合并文件 ---
                update_status(idx, "merge")  # 合并阶段
                #output_path = os.path.join(series_dir, f"合集_合并音视频_{idx}.mp4")
                shouchangjiabiaoti_zhiyi = self.crawler.sanitize_title(shouchangjia_all_biaoti_list[idx-1])
                print(shouchangjiabiaoti_zhiyi)
                output_path = os.path.join(series_dir, f"{shouchangjiabiaoti_zhiyi}.mp4")
                ret = self.crawler.merge_video_audio(video_path, audio_path, output_path)

                current_step += 1
                self.progress_updated.emit(int(current_step / total_steps * 100), 100)

                if ret == 0:
                    self.result_message.emit(f"✅ 视频 {idx} 完成\n")
                    if self.baoliu_yinshiping == False:
                        # 清理临时文件
                        os.remove(video_path)
                        os.remove(audio_path)
                    # os.remove(video_path)
                    # os.remove(audio_path)
                else:
                    self.result_message.emit(f"❌ 视频 {idx} 合并失败\n")

            except Exception as e:
                self.result_message.emit(f"⚠️ 视频 {idx} 错误: {str(e)}\n")
                current_step += 3  # 出错时跳过剩余步骤
        # 在合集下载完成时
        elapsed = time.strftime("%M:%S", time.gmtime(time.time() - start_time))
        self.status_updated.emit(f"✅ 收藏夹下载完成! 共 {total_videos}个视频 | 总用时 {elapsed}", "#98c379")
        self.progress_updated.emit(100, 100)  # 确保完成
        #self.merge_complete.emit(series_dir)
        time.sleep(0.3)
        self.merge_complete.emit(series_dir)

#显示关于对话框
class AboutDialog(QDialog):
    """关于对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于 BiliEasy")
        self.setFixedSize(420, 280)
        self.setModal(True)

        # 设置对话框的默认字体为微软雅黑（简体风格）
        self.setFont(QFont("Microsoft YaHei", 9))

        self.setStyleSheet("""
            QDialog {
                background-color: #2c313c;
                border-radius: 10px;
            }
            QLabel#title_label {
                color: #61dafb;
                font-size: 20px;
                font-weight: bold;
            }
            QLabel#desc_label {
                color: #abb2bf;
                font-size: 13px;
            }
            QPushButton {
                border: none;
                padding: 10px 25px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton#github_btn {
                background-color: #24292e;
                color: white;
            }
            QPushButton#github_btn:hover {
                background-color: #1a1d21;
            }
            QPushButton#bilibili_btn {
                background-color: #fb7299;
                color: white;
            }
            QPushButton#bilibili_btn:hover {
                background-color: #e85d85;
            }
            QPushButton#close_btn {
                background-color: #3e4451;
                color: #abb2bf;
            }
            QPushButton#close_btn:hover {
                background-color: #4b5262;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 25, 30, 25)

        # 标题
        title_label = QLabel("⚡ BiliEasy")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 描述
        desc_label = QLabel(
            "版本: v1.0.22\n"
            "B站视频下载工具\n"
            "基于 PyQt6 开发\n"
            "欢迎通过以下链接了解更多："
        )
        desc_label.setObjectName("desc_label")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #3e4451; max-height: 1px;")
        layout.addWidget(line)

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        # GitHub 按钮
        self.github_btn = QPushButton(" GitHub")
        self.github_btn.setObjectName("github_btn")
        self.github_btn.clicked.connect(self.open_github)
        btn_layout.addWidget(self.github_btn)

        # B站 按钮
        self.bilibili_btn = QPushButton("📺 B站视频")
        self.bilibili_btn.setObjectName("bilibili_btn")
        self.bilibili_btn.clicked.connect(self.open_bilibili)
        btn_layout.addWidget(self.bilibili_btn)

        layout.addLayout(btn_layout)

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setObjectName("close_btn")
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def open_github(self):
        """打开GitHub链接"""
        url = "https://github.com/your-username/BiliEasy"  # 替换为你的GitHub链接
        QDesktopServices.openUrl(QUrl(url))

    def open_bilibili(self):
        """打开B站链接"""
        url = "https://www.bilibili.com/video/BV1BucBz9EPQ/?spm_id_from=333.1387.homepage.video_card.click&vd_source=726e4efb47a201228fe295f8e1d6e5c2"  # 替换为你的B站视频链接
        QDesktopServices.openUrl(QUrl(url))

# 主界面类
class BiliCrawlerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.last_dir = os.path.expanduser("~")  # 初始化默认路径
        self.settings_file = "./bili_crawler_settings.json"

        # 先加载设置但不立即应用
        self.saved_settings = self.load_settings()

        # 创建主控件和布局
        self.init_ui()
        #应用之前加载的设置
        self.apply_settings()

        self.crawler = BiliCrawler()  # 初始时不带Cookie
        self.setWindowTitle("BiliEasy")
        self.setGeometry(300, 300, 1100, 450)
        self.setMinimumSize(600, 620)
        # 设置应用样式
        self.set_dark_theme()

        # 设置窗口图标
        try:
            # 如果是打包后的环境，使用 sys._MEIPASS 获取资源路径
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:  # 否则使用当前目录
                base_path = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(base_path, "bili.ico")
            self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            print(f"加载图标失败: {e}")

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 全局字体设置
        default_font = QFont("Microsoft JhengHei", 12)
        default_font.setWeight(QFont.Weight.Bold)
        QApplication.setFont(default_font)

        # ==================== 标题 ====================
        title_label = QLabel("BiliEasy")
        title_label.setFont(QFont("Microsoft JhengHei", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: #61dafb; 
            margin-bottom: 20px;
            padding: 5px;
            border-bottom: 2px solid #3e4451;
        """)

        # ==================== URL输入区域 ====================
        url_layout = QHBoxLayout()
        url_label = QLabel("视频链接:")
        url_label.setStyleSheet("color: #9400D3; min-width: 80px;")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入B站视频链接...")
        self.url_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c313c;
                color: #d7dae0;
                border: 1px solid #3e4451;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #61dafb;
            }
            QLineEdit:hover {
                border: 1px solid #4b5262;
            }
        """)
        self.url_input.setMinimumHeight(40)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)


        fenbian_mode_shuiping_kongjian = QHBoxLayout()
        fenbian_mode_shuiping_kongjian.setSpacing(30)
        # ==================== 分辨率选择 ====================
        resolution_layout = QHBoxLayout()# 创建水平布局容器
        resolution_label = QLabel("分辨率:")#创建标签（左边的文字）
        resolution_label.setStyleSheet("color: #9400D3; min-width: 80px;")
        self.resolution_combo = QComboBox()# 创建输入控件（右边的下拉框）
        self.resolution_combo.addItems(['1080p', '720p','480p','360p'])
        self.resolution_combo.setCurrentIndex(0)
        self.resolution_combo.setStyleSheet("""
            QComboBox {
                background-color: #2c313c;
                color: #d7dae0;
                border: 1px solid #3e4451;
                border-radius: 4px;
                padding: 8px;
                min-width: 100px;
            }
            QComboBox:hover {
                border: 1px solid #4b5262;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2c313c;
                color: #d7dae0;
                selection-background-color: #3e4451;
                outline: none;
            }
        """)
        self.resolution_combo.setMinimumWidth(120)  # 直接设置最小宽度
        resolution_layout.addWidget(resolution_label)
        resolution_layout.addWidget(self.resolution_combo)

        # ==================== 下载模式 ====================
        mode_layout = QHBoxLayout()
        mode_label = QLabel("下载模式:")
        mode_label.setStyleSheet("color: #9400D3; min-width: 80px;")
        self.download_mode = QComboBox()
        self.download_mode.addItems(["单集下载", "合集下载","合集指定下载","收藏夹下载"])
        self.download_mode.setStyleSheet("""
            QComboBox {
                background-color: #2c313c;
                color: #d7dae0;
                border: 1px solid #3e4451;
                border-radius: 4px;
                padding: 8px;
                min-width: 120px;
            }
            QComboBox:hover {
                border: 1px solid #4b5262;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2c313c;
                color: #d7dae0;
                selection-background-color: #3e4451;
                outline: none;
            }
        """)
        self.download_mode.setMinimumWidth(140)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.download_mode)

        #==================== 下载弹幕 ====================
        danmu_layout = QHBoxLayout()
        danmu_label = QLabel("下载弹幕:")
        danmu_label.setStyleSheet("color: #9400D3; min-width: 80px;")
        self.danmu_mode = QComboBox()
        self.danmu_mode.addItems(["否","仅下载弹幕", "烧录弹幕至视频"])
        self.danmu_mode.setStyleSheet("""
            QComboBox {
                background-color: #2c313c;
                color: #d7dae0;
                border: 1px solid #3e4451;
                border-radius: 4px;
                padding: 8px;
                min-width: 120px;
            }
            QComboBox:hover {
                border: 1px solid #4b5262;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2c313c;
                color: #d7dae0;
                selection-background-color: #3e4451;
                outline: none;
            }
        """)
        self.danmu_mode.setMinimumWidth(100)
        danmu_layout.addWidget(danmu_label)
        danmu_layout.addWidget(self.danmu_mode)

        #=====================保留音视频=====================
        yinshiping_layout = QHBoxLayout()
        yinshiping_label = QLabel("保留音视频:")
        yinshiping_label.setStyleSheet("color: #9400D3; min-width: 80px;")
        self.yinshiping_mode = QComboBox()
        self.yinshiping_mode.addItems(["否", "是"])
        self.yinshiping_mode.setStyleSheet("""
            QComboBox {
                background-color: #2c313c;
                color: #d7dae0;
                border: 1px solid #3e4451;
                border-radius: 4px;
                padding: 8px;
                min-width: 120px;
            }
            QComboBox:hover {
                border: 1px solid #4b5262;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2c313c;
                color: #d7dae0;
                selection-background-color: #3e4451;
                outline: none;
            }
        """)
        self.yinshiping_mode.setMinimumWidth(100)
        yinshiping_layout.addWidget(yinshiping_label)
        yinshiping_layout.addWidget(self.yinshiping_mode)

        #将分辨率，下载模式，下载弹幕都添加到一个大的水平容器中
        fenbian_mode_shuiping_kongjian.addLayout(resolution_layout)
        fenbian_mode_shuiping_kongjian.addLayout(mode_layout)
        fenbian_mode_shuiping_kongjian.addLayout(danmu_layout)
        fenbian_mode_shuiping_kongjian.addLayout(yinshiping_layout)

        # ==================== Cookie输入区域 ====================
        cookie_layout = QHBoxLayout()
        cookie_label = QLabel("B站Cookie:")
        cookie_label.setStyleSheet("color: #9400D3; min-width: 80px;")
        self.cookie_input = QLineEdit()
        self.cookie_input.setPlaceholderText("请输入您的B站Cookie")
        self.cookie_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c313c;
                color: #d7dae0;
                border: 1px solid #3e4451;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #61dafb;
            }
            QLineEdit:hover {
                border: 1px solid #4b5262;
            }
        """)
        #当用户输入时自动保存
        self.cookie_input.textChanged.connect(self.save_settings)
        help_btn = QPushButton("?")
        help_btn.setStyleSheet("""
            QPushButton {
                background: #3e4451;
                color: #d7dae0;
                border-radius: 12px;
                font-weight: bold;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
            }
            QPushButton:hover {
                background: #61dafb;
                color: #282c34;
            }
        """)
        help_btn.clicked.connect(self.show_cookie_help)
        cookie_layout.addWidget(cookie_label)
        cookie_layout.addWidget(self.cookie_input)
        cookie_layout.addWidget(help_btn)

        # ==================== 保存路径选择 ====================
        path_layout = QHBoxLayout()
        path_label = QLabel("保存路径:")
        path_label.setStyleSheet("color: #9400D3; min-width: 80px;")
        self.path_input = QLineEdit()
        self.path_input.setText(self.last_dir)
        self.path_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c313c;
                color: #d7dae0;
                border: 1px solid #3e4451;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QLineEdit:hover {
                border: 1px solid #4b5262;
            }
        """)
        self.path_input.setMinimumHeight(40)
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #3e4451;
                color: #d7dae0;
                border-radius: 4px;
                padding: 8px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4b5262;
            }
            QPushButton:pressed {
                background-color: #61dafb;
                color: #282c34;
            }
        """)
        self.browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_btn.clicked.connect(self.browse_save_dir)
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        # ==================== 爬取按钮 ====================
        self.crawl_btn = QPushButton("开始爬取")
        self.crawl_btn.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self.crawl_btn.setStyleSheet("""
            QPushButton {
                background-color: #61dafb;
                color: #282c34;
                border-radius: 4px;
                padding: 12px;
                margin: 15px 0;
            }
            QPushButton:hover {
                background-color: #4ec1e0;
            }
            QPushButton:pressed {
                background-color: #3aa8d0;
            }
            QPushButton:disabled {
                background-color: #3e4451;
                color: #5c6370;
            }
        """)
        self.crawl_btn.setCursor(Qt.CursorShape.PointingHandCursor)#设置鼠标悬停时的光标样式为手型
        self.crawl_btn.clicked.connect(self.start_crawling)
        # ==================== 进度条 ====================
        self.progress_bar = QProgressBar()#创建进程对象，就是进度条
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)#设置初始值为0%
        self.progress_bar.setTextVisible(True)#显示进度文本（百分比或自定义文字）
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2c313c;
                color: #abb2bf;
                border: 1px solid #3e4451;
                border-radius: 4px;
                height: 16px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #61dafb;
                border-radius: 4px;
            }
        """)
        self.progress_bar.setFormat("等待开始...")
        self.progress_bar.hide()#初始化时隐藏，只有被show()调用才显示
        # ==================== 状态标签 ====================
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("""
            color: #abb2bf; 
            margin-top: 10px;
            padding: 8px;
            background-color: #2c313c;
            border-radius: 4px;
            border: 1px solid #3e4451;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # ==================== 结果区域 ====================
        result_layout = QVBoxLayout()
        result_label = QLabel("爬取结果")
        result_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        result_label.setStyleSheet("""
            color: #61dafb;
            margin-top: 20px;
            padding-bottom: 5px;
            border-bottom: 1px solid #3e4451;
        """)
        # 改用QTextEdit以获得更好的文本显示
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("等待开始...")
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c313c;
                color: #d7dae0;
                border: 1px solid #3e4451;
                border-radius: 4px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        self.result_text.setMinimumHeight(70)
        self.result_text.setMaximumHeight(120)
        result_layout.addWidget(result_label)
        result_layout.addWidget(self.result_text)
        # ==================== 添加到主布局 ====================
        main_layout.addWidget(title_label)
        main_layout.addLayout(url_layout)
        # main_layout.addLayout(resolution_layout)
        # main_layout.addLayout(mode_layout)
        main_layout.addLayout(fenbian_mode_shuiping_kongjian)
        main_layout.addLayout(cookie_layout)
        main_layout.addLayout(path_layout)
        main_layout.addWidget(self.crawl_btn)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.status_label)
        main_layout.addLayout(result_layout)
        main_layout.addStretch()
        # ==================== 底部信息 ====================
        # 先添加分割线（占满整个宽度）
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #3e4451; max-height: 1px;")
        main_layout.addWidget(line)

        # 底部布局：footer_label 居中，关于按钮在右下角
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 10, 0, 5)

        # 左侧空白（占位）
        bottom_layout.addStretch()

        # 底部信息 - 居中
        footer_label = QLabel("BiliEasy v1.0.22 | 欢迎学习交流 | 反馈/建议：QQ群 580376200 | qq:2571073922")
        footer_label.setStyleSheet("""
            color: #5c6370; 
            font-size: 13px;
        """)
        bottom_layout.addWidget(footer_label)

        # 中间弹性空间（让footer_label居中，关于按钮靠右）
        bottom_layout.addStretch()

        # 关于按钮 - 靠右
        self.about_btn = QPushButton("关于")
        self.about_btn.setFixedSize(55, 25)
        self.about_btn.setFont(QFont("Microsoft YaHei", 9))
        self.about_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #61dafb;
                border: 1px solid #61dafb;
                border-radius: 3px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #61dafb;
                color: #282c34;
                border-color: #4ec1e0;
            }
        """)
        self.about_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.about_btn.clicked.connect(self.show_about_dialog)
        bottom_layout.addWidget(self.about_btn)

        main_layout.addLayout(bottom_layout)

    def show_about_dialog(self):
        """显示关于对话框"""
        dialog = AboutDialog(self)  # 在这里使用 AboutDialog 类
        dialog.exec()

    def show_cookie_help(self):
        """显示美观的帮助对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("获取Cookie帮助")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout()
        # 标题
        title = QLabel("如何获取B站Cookie")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        # 步骤列表
        steps = QLabel("""
        <ol>
        <li>登录B站后按<b>F12</b>打开开发者工具</li>
        <li>找到<b>网络(Network)</b>标签</li>
        <li><b>点击浏览器</b>刷新或者按下<b>F5</b>，刷新B站页面</li>
        <li>找到<b>DOC(文档)</b>选项下面的链接</li>
        <li>打开链接，找到<b>请求头（Request Headers）</b></li>
        <li>找到Cookie，复制对应的值</li>   
        </ol>
        """)
        steps.setTextFormat(Qt.TextFormat.RichText)
        # 警告信息
        warning = QLabel("⚠️ Cookie是您的登录凭证，请勿泄露给他人！")
        warning.setStyleSheet("color: red;")
        # 确定按钮
        btn_ok = QPushButton("我明白了")
        btn_ok.clicked.connect(dialog.accept)
        # 添加到布局
        layout.addWidget(title)
        layout.addWidget(steps)
        layout.addWidget(warning)
        layout.addWidget(btn_ok)
        dialog.setLayout(layout)
        dialog.exec()

    def set_dark_theme(self):
        """设置暗色主题样式"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(40, 44, 52))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(171, 178, 191))
        palette.setColor(QPalette.ColorRole.Base, QColor(35, 39, 46))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(44, 49, 60))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(40, 44, 52))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(171, 178, 191))
        palette.setColor(QPalette.ColorRole.Text, QColor(171, 178, 191))
        palette.setColor(QPalette.ColorRole.Button, QColor(62, 68, 81))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(171, 178, 191))
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Highlight, QColor(97, 218, 251))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(40, 44, 52))
        self.setPalette(palette)

    def load_settings(self):
        """加载用户设置，但不立即应用"""
        settings = {
            "last_dir": self.last_dir,
            "cookie": ""
        }
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r") as f:
                    loaded_settings = json.load(f)
                    settings.update(loaded_settings)
        except Exception as e:
            print(f"加载设置失败: {e}")
        return settings

    def apply_settings(self):
        """应用之前加载的设置"""
        if hasattr(self, 'saved_settings'):
            if 'last_dir' in self.saved_settings:
                self.last_dir = self.saved_settings['last_dir']
                if hasattr(self, 'path_input'):
                    self.path_input.setText(self.last_dir)
            if 'cookie' in self.saved_settings and hasattr(self, 'cookie_input'):
                self.cookie_input.setText(self.saved_settings['cookie'])

    def save_settings(self):
        """保存用户设置"""
        settings = {
            "last_dir": self.last_dir,
            "cookie": self.cookie_input.text().strip() if hasattr(self, 'cookie_input') else ""
        }
        try:
            # 添加调试信息
            print(f"📁 保存路径: {self.settings_file}")
            print(f"📝 保存内容: {settings}")

            with open(self.settings_file, "w") as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"保存设置失败: {e}")

    def browse_save_dir(self):
        """选择保存目录"""
        options = QFileDialog.Option.ShowDirsOnly#只显示目录
        # 打开系统原生的文件夹选择对话框
        save_dir = QFileDialog.getExistingDirectory(
            self,
            "选择保存文件夹",
            self.last_dir,
            options=options
        )
        if save_dir:
            self.last_dir = save_dir
            self.path_input.setText(save_dir)
            self.save_settings()

    def create_custom_input_dialog(self):
        """创建自定义暗色主题的输入对话框"""
        dialog = QInputDialog(self)

        # 设置对话框属性
        dialog.setWindowTitle("合集指定下载")
        dialog.setLabelText("请输入要下载的集数范围：\n2-4《表示第二集至第四集》\n1,6,7 （是输入法英文的逗号）《表示第一集，第六集，第七集》")
        dialog.setTextValue("1-3")
        dialog.setInputMode(QInputDialog.InputMode.TextInput)

        # 设置按钮文字为中文
        dialog.setOkButtonText("确定")
        dialog.setCancelButtonText("取消")

        # 应用暗色主题样式
        dialog.setStyleSheet("""
            QInputDialog {
                background-color: #2c313c;
                color: #d7dae0;
                border: 1px solid #4b5262;
                border-radius: 8px;
            }
            QLabel {
                background-color: transparent;
                color: #d7dae0;
                font-size: 14px;
                padding: 10px;
            }
            QLineEdit {
                background-color: #353946;
                color: #d7dae0;
                border: 1px solid #4b5262;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                selection-background-color: #9400D3;
            }
            QLineEdit:focus {
                border: 1px solid #9400D3;
            }
            QPushButton {
                background-color: #4b5262;
                color: #d7dae0;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #5b6375;
            }
            QPushButton:pressed {
                background-color: #3e4451;
            }
            QPushButton:focus {
                outline: none;
                border: 1px solid #9400D3;
            }
        """)

        # 调整对话框大小
        dialog.resize(400, 200)

        # 执行对话框
        ok = dialog.exec()
        text = dialog.textValue()

        return text, ok

    def start_crawling(self):
        """开始爬取视频"""
        try:
            # 一次性获取所有输入并验证
            user_cookie = self.cookie_input.text().strip()
            url = self.url_input.text().strip()
            save_dir = self.path_input.text().strip()

            # 集中验证输入
            #下载360p视频可不登陆
            # if not user_cookie:
            #     QMessageBox.warning(self, "输入错误", "Cookie不能为空，请填写B站Cookie！")
            #     self.cookie_input.setFocus()
            #     return

            if not url:
                QMessageBox.warning(self, "输入错误", "视频链接不能为空，请填写视频链接")
                self.url_input.setFocus()
                return

            if not save_dir:
                QMessageBox.warning(self, "输入错误", "保存路径不能为空，请填写保存路径")
                self.browse_btn.click()  # 自动打开浏览对话框
                return

            quality = self.resolution_combo.currentText()[:-1]
            download_danmu = self.danmu_mode.currentText()
            baoliu_yinshiping = self.yinshiping_mode.currentText() == '是'
            download_series = self.download_mode.currentText()

            # 处理合集指定下载的输入
            series_range = None
            if download_series == '单集下载':
                download_series = 1
                print(download_series)
            elif download_series == '合集下载':
                download_series = 2
                print(download_series)
            elif download_series == '合集指定下载':
                download_series = 3
                print(download_series)
                # 创建自定义样式的输入对话框
                text, ok = self.create_custom_input_dialog()

                if not ok:
                    self.status_label.setText("用户取消下载")
                    self.status_label.setStyleSheet("color: #ffa500;")
                    return

                if not text.strip():
                    QMessageBox.warning(self, "输入错误", "请输入有效的集数范围！")
                    return

                series_range = text.strip()
                print(f"用户输入的下载范围: {series_range}")

            elif download_series == '收藏夹下载':
                download_series = 4
                print(download_series)

            else:
                raise Exception('找不到指定类型')

            # 更新爬虫的cookie
            self.crawler.update_cookie(user_cookie)
        except Exception as e:
            # 统一的异常处理
            QMessageBox.critical(self, "系统错误", f"发生未知错误：{str(e)}\n请检查输入是否正确或重试")
        # 禁用按钮并显示进度
        self.crawl_btn.setEnabled(False)
        self.progress_bar.show()
        self.status_label.setText("正在初始化爬取...")
        self.status_label.setStyleSheet("color: #61dafb;")
        self.result_text.setText("准备爬取视频...")
        # 创建工作线程
        self.crawler_thread = CrawlerThread(self.crawler, url, save_dir, quality=quality, download_series=download_series,series_range=series_range,download_danmu=download_danmu,baoliu_yinshiping=baoliu_yinshiping)
        self.crawler_thread.progress_updated.connect(self.update_progress)
        self.crawler_thread.status_updated.connect(self.update_status)
        self.crawler_thread.download_complete.connect(self.on_download_complete)
        self.crawler_thread.merge_complete.connect(self.on_merge_complete)
        self.crawler_thread.series_progress.connect(self.on_series_progress)
        self.crawler_thread.finished.connect(self.on_thread_finished)
        self.crawler_thread.result_message.connect(self.append_result_text)
        self.crawler_thread.progress_updated.connect(self.update_progress_bar)  # 详细进度条
        self.crawler_thread.series_progress.connect(self.update_series_status)  # 合集计数
        self.crawler_thread.start()

    def update_progress(self, value, maximum):
        """更新进度条"""
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)

    def update_status(self, text, color):
        """更新状态文本"""
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color};")

    def on_download_complete(self, file_type, path):
        """下载完成回调"""
        if file_type == "video":
            self.result_text.setText(f"视频下载完成: {path}\n" + self.result_text.text())
        else:
            self.result_text.setText(f"音频下载完成: {path}\n" + self.result_text.text())

    def on_merge_complete(self, output_path):
        """合并完成回调"""
        try:
            # 使用append而不是setText + 拼接
            self.result_text.append(f"✅ 合并完成! 文件已保存到: {output_path}")

            # 使用QTimer延迟显示消息框，避免竞争
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, lambda:
            QMessageBox.information(self, "完成", f"视频已成功保存到:\n{output_path}"))

        except Exception as e:
            print(f"UI更新失败: {e}")

    def on_thread_finished(self):
        """线程完成回调"""
        self.crawl_btn.setEnabled(True)
        self.progress_bar.hide()

    def on_series_progress(self, current, total):
        """更新合集下载进度"""
        self.status_label.setText(f"正在下载合集: {current}/{total}")
        self.status_label.setStyleSheet("color: #61dafb;")

    def append_result_text(self, message):
        """追加结果消息到界面"""
        # current_text = self.result_text.text()
        # self.result_text.setText(current_text + message)
        # 如果是QTextEdit，可以使用append方法
        self.result_text.append(message)

    def update_progress_bar(self, current, total):
        """更简单的进度条更新"""
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(current)
        self.progress_bar.setFormat(f"{current}%")

    def update_series_status(self, current, total):
        """更新合集计数状态"""
        self.status_label.setText(f"正在下载合集 ({current}/{total})")


if __name__ == "__main__":
    app = QApplication(sys.argv)# 创建Qt应用实例
    window = BiliCrawlerGUI()
    window.show()
    sys.exit(app.exec())