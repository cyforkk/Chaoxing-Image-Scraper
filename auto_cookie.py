"""
自动获取学习通Cookie模块
使用 Selenium 打开浏览器让用户登录，然后自动获取Cookie
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_cookie_auto(callback=None, keep_browser_open=False):
    """
    自动获取学习通Cookie
    
    Args:
        callback: 回调函数，用于更新日志
        keep_browser_open: 是否保持浏览器打开，默认False
        
    Returns:
        str: Cookie字符串，失败返回None
    """
    def log(msg):
        if callback:
            callback(msg)
        else:
            print(msg)
    
    driver = None
    try:
        log("正在启动浏览器...")
        
        # 配置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 启动浏览器
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        
        log("浏览器已启动，正在打开学习通登录页面...")
        
        # 打开学习通登录页面
        driver.get("https://passport2.chaoxing.com/login")
        
        log("请在浏览器中完成登录...")
        log("登录成功后，程序将自动获取Cookie")
        
        # 检测登录状态
        login_detected = False
        start_time = time.time()
        
        while time.time() - start_time < 300:  # 5分钟超时
            try:
                # 检查URL是否变化
                current_url = driver.current_url
                if "passport2.chaoxing.com/login" not in current_url:
                    login_detected = True
                    break
                
                # 检查是否有关键Cookie
                cookies = driver.get_cookies()
                cookie_names = [c['name'] for c in cookies]
                if 'UID' in cookie_names or '_uid' in cookie_names:
                    login_detected = True
                    break
                    
                time.sleep(1)
            except:
                pass
        
        if not login_detected:
            log("等待超时，未检测到登录")

            try:
                if driver:
                    driver.quit()
                    log("浏览器已关闭")
            except:
                pass
            return None
        
        log("检测到登录成功！")
        
        # 等待页面加载
        time.sleep(2)
        
        # 获取Cookie
        cookies = driver.get_cookies()
        
        if not cookies:
            log("未获取到Cookie")
            try:
                driver.quit()
                log("浏览器已关闭")
            except:
                pass
            return None
        
        # 转换为字符串格式
        cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
        
        log(f"成功获取Cookie！共 {len(cookies)} 个Cookie项")
        
        # 根据参数决定是否关闭浏览器
        if not keep_browser_open:
            try:
                driver.quit()
                log("浏览器已关闭")
            except:
                pass
        else:
            log("浏览器保持打开")
        
        return cookie_str
        
    except Exception as e:
        log(f"获取Cookie失败: {str(e)}")
        if driver:
            try:
                driver.quit()
            except:
                pass
        return None


if __name__ == "__main__":
    # 测试
    cookie = get_cookie_auto()
    if cookie:
        print(f"Cookie: {cookie[:100]}...")
    else:
        print("获取失败")
