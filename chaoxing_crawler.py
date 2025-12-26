import requests
import re
import os
from urllib.parse import urljoin
import time


class ChaoxingImageCrawler:
    def __init__(self, cookies):
        self.session = requests.Session()
        self.session.cookies.update(cookies)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
        self.log_callback = None

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def get_course_content(self, url):
        try:
            response = self.session.get(url, headers=self.headers)
            response.encoding = "utf-8"
            return response.text
        except Exception as e:
            self.log(f"获取页面内容失败: {e}")
            return None

    def extract_images(self, html):
        images = []

        img_patterns = [
            r'<img[^>]+src="([^"]+)"',
            r"<img[^>]+src=\'([^\']+)\'",
            r'"url":"([^"]+\.jpg[^"]*)"',
            r'"url":"([^"]+\.png[^"]*)"',
            r'"orig":"([^"]+)"',
            r'background-image:\s*url\(["\']?([^)"\']+)["\']?\)',
            r'https?://[^"\'>\s]+ananas[^"\'>\s]+',
            r'https?://[^"\'>\s]+/sv-w8/[^"\'>\s]+',
            r'https://s[0-9]\.ananas\.chaoxing\.com[^\s"\'<>]+',
        ]

        for pattern in img_patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                if match and not match.startswith("data:"):
                    if "/sv-w8/doc/" in match or "ananas.chaoxing.com" in match:
                        images.append(match)

        return list(set(images))

    def download_image(self, img_url, save_dir, course_name, chapter_name, index):
        try:
            if not img_url.startswith("http"):
                img_url = urljoin("https://mooc1.chaoxing.com/", img_url)

            ext = os.path.splitext(img_url.split("?")[0])[1] or ".png"
            filename = f"{course_name}-{chapter_name}-{index}{ext}"
            filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

            filepath = os.path.join(save_dir, filename)

            response = self.session.get(img_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(response.content)
                self.log(f"下载成功: {filename}")
                self.log(f"保存路径: {filepath}")
                return True
            else:
                self.log(f"下载失败: {img_url} (状态码: {response.status_code})")
                return False
        except Exception as e:
            self.log(f"下载图片失败: {img_url}, 错误: {e}")
            return False

    def crawl_homework_images(self, course_url, save_dir="images"):
        """爬取作业图片"""
        save_dir = os.path.abspath(save_dir)
        os.makedirs(save_dir, exist_ok=True)
        self.log(f"保存目录: {save_dir}")

        self.log("正在获取作业页面...")
        
        try:
            response = self.session.get(course_url, headers=self.headers)
            response.encoding = "utf-8"
            html = response.text
            
            self.log(f"页面响应长度: {len(html)}")
            
            # 提取课程名
            course_name_match = re.search(r'"coursename"\s*:\s*"([^"]+)"', html)
            course_name = course_name_match.group(1) if course_name_match else "课程"
            self.log(f"课程名称: {course_name}")
            
            # 优先从 mark_title 提取题目名称
            title_match = re.search(r'<h2 class="mark_title"[^>]*>([^<]+)</h2>', html)
            if title_match:
                homework_name = title_match.group(1).strip()
            else:
                # 如果没有，尝试从 knowledgename 提取
                knowledge_name_match = re.search(r'"knowledgename"\s*:\s*"([^"]+)"', html)
                homework_name = knowledge_name_match.group(1) if knowledge_name_match else "作业"
            self.log(f"题目名称: {homework_name}")
            
            # 提取作业图片（从 stuAnswerContent 区域）
            self.log("正在查找作业图片...")
            
            # 匹配 stuAnswerContent 区域的图片
            answer_pattern = r'<dd class="textwrap stuAnswerContent[^"]*">(.*?)</dd>'
            answer_sections = re.findall(answer_pattern, html, re.DOTALL)
            
            images = []
            for section in answer_sections:
                # 提取 data-original 属性（原图）
                img_matches = re.findall(r'data-original="([^"]+)"', section)
                images.extend(img_matches)
                
                # 如果没有 data-original，尝试提取 src
                if not img_matches:
                    src_matches = re.findall(r'<img[^>]+src="([^"]+)"', section)
                    images.extend(src_matches)
            
            # 去重
            images = list(set(images))
            
            self.log(f"找到 {len(images)} 张图片")
            
            if not images:
                self.log("⚠️ 未找到图片")
                self.log("💡 提示：")
                self.log("    - 请确认该页面是作业答案页面")
                self.log("    - 请确认作业答案区域包含图片")
                self.log("    - 如果是课程章节，请选择“📚 课程图片”模式")
                return False
            
            success_count = 0
            for i, img_url in enumerate(images, 1):
                self.log(f"[{i}/{len(images)}] 正在下载: {img_url[:70]}...")
                if self.download_image(img_url, save_dir, course_name, homework_name, i):
                    success_count += 1
                time.sleep(0.5)
            
            self.log(f"\n下载完成! 成功下载 {success_count}/{len(images)} 张图片")
            
            if success_count > 0:
                self.log(f"✓ 图片已保存到: {save_dir}")
            
            return success_count > 0
            
        except Exception as e:
            self.log(f"爬取作业图片失败: {e}")
            return False

    def crawl_images(self, course_url, save_dir="images"):
        save_dir = os.path.abspath(save_dir)
        os.makedirs(save_dir, exist_ok=True)
        self.log(f"保存目录: {save_dir}")

        self.log("正在从URL提取参数...")
        chapter_id_match = re.search(r"chapterId=([^&]+)", course_url)
        if not chapter_id_match:
            self.log("⚠️ 无法从URL提取chapterId")
            self.log("💡 提示：请确认您选择了正确的爬取模式：")
            self.log("    - 课程图片：需要课程章节链接（包含chapterId参数）")
            self.log("    - 作业图片：需要作业页面链接")
            return False

        chapter_id = chapter_id_match.group(1)
        course_id_match = re.search(r"courseId=([^&]+)", course_url)
        course_id = course_id_match.group(1) if course_id_match else "254411132"
        clazz_id_match = re.search(r"clazzid=([^&]+)", course_url)
        clazz_id = clazz_id_match.group(1) if clazz_id_match else "126771918"
        cpi_match = re.search(r"cpi=([^&]+)", course_url)
        cpi = cpi_match.group(1) if cpi_match else "355954326"

        self.log(f"课程ID: {course_id}, 章节ID: {chapter_id}, 班级ID: {clazz_id}")

        cards_url = f"https://mooc1.chaoxing.com/mooc-ans/knowledge/cards?clazzid={clazz_id}&courseid={course_id}&knowledgeid={chapter_id}&num=0&ut=s&cpi={cpi}&v=2025-0424-1038-3&mooc2=1&isMicroCourse=false&editorPreview=0"
        self.log(f"正在请求卡片API: {cards_url[:70]}...")

        response = self.session.get(cards_url, headers=self.headers)

        if response.status_code == 200:
            cards_html = response.text
            self.log(f"卡片API响应长度: {len(cards_html)}")

            course_name_match = re.search(r'"coursename"\s*:\s*"([^"]+)"', cards_html)
            course_name = course_name_match.group(1) if course_name_match else "课程"
            self.log(f"课程名称: {course_name}")

            knowledge_name_match = re.search(
                r'"knowledgename"\s*:\s*"([^"]+)"', cards_html
            )
            knowledge_name = (
                knowledge_name_match.group(1) if knowledge_name_match else "章节"
            )
            self.log(f"章节名称: {knowledge_name}")

            self.log("正在查找PDF文档信息...")
            objectid_match = re.search(r'"objectid"\s*:\s*"([^"]+)"', cards_html)
            if not objectid_match:
                objectid_match = re.search(r'objectid=([^\s"\'>]+)', cards_html)

            if objectid_match:
                objectid = objectid_match.group(1)
                self.log(f"找到objectid: {objectid}")

                self.log("正在尝试直接请求预览页面...")
                ext_param = f"%7B%22_from_%22%3A%22254411132_126771918_305455632_834b328b9c76ad47c6ea0999c20c6ba0%22%7D"
                preview_url = f"https://pan-yz.chaoxing.com/preview/objectshowpreview.html?objectid={objectid}&puid=111690846&ext={ext_param}"
                self.log(f"正在请求: {preview_url[:90]}...")

                preview_response = self.session.get(preview_url, headers=self.headers)
                if preview_response.status_code == 200:
                    preview_html = preview_response.text
                    self.log(f"预览页面响应长度: {len(preview_html)}")

                    images = self.extract_images(preview_html)
                else:
                    self.log(f"预览页面请求失败: {preview_response.status_code}")
                    images = []
            else:
                self.log("未找到objectid")
                images = []

            self.log(f"找到 {len(images)} 张图片")

            if not images:
                self.log("未找到图片")
                return False

            success_count = 0
            for i, img_url in enumerate(images, 1):
                self.log(f"[{i}/{len(images)}] 正在下载: {img_url[:70]}...")
                if self.download_image(
                    img_url, save_dir, course_name, knowledge_name, i
                ):
                    success_count += 1
                time.sleep(0.5)

            self.log(f"\n下载完成! 成功下载 {success_count}/{len(images)} 张图片")

            if success_count > 0:
                self.log(f"✓ 图片已保存到: {save_dir}")

            return success_count > 0
        else:
            self.log(f"请求失败，状态码: {response.status_code}")
            return False


def main():
    url = "https://mooc1.chaoxing.com/mycourse/studentstudy?chapterId=1093036095&courseId=214977771&clazzid=127435593&cpi=355954326&enc=0ba34fdf47f5f9441f2a7eabe136ecc2&mooc2=1&hidetype=0&openc=2e12069d6d211aa4000f976a8068539a"

    cookies = {
        "fid": "1895",
        "fanyamoocs": "11401F839C536D9E",
        "_uid": "305455632",
        "_d": "1766664171071",
        "UID": "305455632",
        "vc3": "SyGPeDytY2u4hnf2N%2BGXyxMNd1EWQX29vAk7UHg%2BMNgdxBsj55JEonuPS50ioy6lKEdLmpkqSoIG6tBhJrBAtcm3Ct2ygl1s0YOcCRHFkclJJXJBpbv5SwiyAlH5F8uAX3MawKPkdw9nNCY6OPLfPDKlx8iuryXGPAnWq7GuXNY%3D68b401cb982961dd56b95d7b7ea1020a",
        "uf": "b2d2c93beefa90dc431ba9687b542d8649cb6fd4383e557cd3d29c38c74757bd59263422de87ea97f82c82ed84ba88a981a6c9ddee30899fd807a544f7930b6aed1e6c11a143bb563b0339d97cdac4baabdbe8f75da1a98fe5851b744f8aa02c9fb3947ed09a594cc1ce0b14d44f76133121ccd7dcbdac27bf0117e20ffcf8b2a7dfae10ab92c0acc83af620aa8ae3f770b5a05e402d2a6370184964ffe8c27cda1a2f067a584887f183e159dc5a6222b1f899d50c1c3fa3aa2ebad65cd196bb",
        "cx_p_token": "9773c7ed30997ae3c554799ed9044329",
        "p_auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIzMDU0NTU2MzIiLCJsb2dpblRpbWUiOjE3NjY2NjQxNzEwNzIsImV4cCI6MTc2NzI2ODk3MX0.T8sz2LHao4_KVh-YpnTWbOtoUFKOjkEXY0wFogkm1Do",
        "xxtenc": "f47e3db297a57d609dfc03c59b6fd1e6",
        "DSSTASH_LOG": "C_38-UN_192-US_305455632-T_1766664171073",
        "thirdRegist": "0",
        "k8s": "1766664189.835.112.921552",
        "route": "0eb899bb9bb390391b050e8cb1d78cb4",
        "jrose": "6201E6DA46AFC0FD529F85F974A551B3.mooc-p4-1368682161-9bfgs",
        "_industry": "5",
        "255200491cpi": "355954326",
        "255200491ut": "s",
        "255200491t": "1766710774233",
        "255200491enc": "9d65c3faacb7a2b628d98fbe01aea7f9",
        "254411132cpi": "355954326",
        "254411132ut": "s",
        "254411132t": "1766710904758",
        "254411132enc": "4a4ba5fff37a329b8dcdfeb1bd07fe53",
    }

    crawler = ChaoxingImageCrawler(cookies)
    crawler.crawl_images(url)


if __name__ == "__main__":
    main()
