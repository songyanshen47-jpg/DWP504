import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
import os
import re
from datetime import datetime
import shutil

# ==================== 核心配置 ====================
CONFIG_DIR = r"d:\tonwel\21087\Desktop\工作\.net\dwp"
ORIGINAL_FILE = os.path.join(CONFIG_DIR, "1.pegall")
BASE_URL = "http://192.168.66.123/#/Home"
AFTER_RESTORE_WAIT = 8
PAGE_WAIT = 1.5

os.makedirs(CONFIG_DIR, exist_ok=True)


# ==================== Chrome 配置 ====================
def get_chrome_options():
    opt = Options()
    opt.add_argument("--start-maximized")
    opt.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    opt.add_experimental_option("useAutomationExtension", False)

    prefs = {
        "download.default_directory": CONFIG_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
    }
    opt.add_experimental_option("prefs", prefs)
    return opt


# ==================== 等待下载完成 ====================
def wait_for_download(timeout=60):
    """等待下载完成，返回新文件路径"""
    print("  ⏳ 等待下载完成...")
    start_time = time.time()
    existing_files = set(os.listdir(CONFIG_DIR))

    while time.time() - start_time < timeout:
        current_files = set(os.listdir(CONFIG_DIR))
        new_files = current_files - existing_files

        # 查找新下载的 pegall 文件
        for f in new_files:
            if f.endswith('.pegall') and not f.endswith('.crdownload'):
                filepath = os.path.join(CONFIG_DIR, f)
                time.sleep(1)
                if os.path.getsize(filepath) > 0:
                    print(f"  ✅ 下载完成: {f}")
                    return filepath

        # 显示下载进度
        downloading = [f for f in current_files if f.endswith('.crdownload')]
        if downloading:
            print(f"\r    下载中: {downloading[0]}", end="")

        time.sleep(1)

    print(f"\n  ❌ 下载超时 ({timeout}秒)")
    return None


# ==================== 文件管理 ====================
def get_next_filename():
    """生成下一个文件名（从2开始递增）"""
    existing_numbers = []

    for filename in os.listdir(CONFIG_DIR):
        match = re.match(r'^(\d+)\.pegall$', filename)
        if match:
            existing_numbers.append(int(match.group(1)))

    if existing_numbers:
        next_num = max(existing_numbers) + 1
    else:
        next_num = 2

    next_file = os.path.join(CONFIG_DIR, f"{next_num}.pegall")
    print(f"📁 导出文件名: {next_num}.pegall")
    return next_file


# ==================== 导航到 Backup&Restore ====================
def navigate_to_backup_restore(driver):
    """导航到 Backup&Restore 页面"""
    print("  ▶ 导航到 Backup&Restore...")

    # 点击 Settings 标签
    try:
        settings_tab = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(@class,"tabbar-item")]//span[text()="Settings"]'))
        )
        driver.execute_script("arguments[0].click();", settings_tab)
        print("  ✅ 已点击 Settings 标签")
        time.sleep(1)
    except Exception as e:
        print(f"  ⚠️ 点击 Settings 失败: {e}")

    # 点击 Backup&Restore 菜单
    backup_xpaths = [
        '//span[text()="Backup&Restore"]',
        '//div[contains(text(),"Backup&Restore")]',
        '//*[contains(@class,"submenu")]//*[contains(text(),"Backup")]',
        '//*[contains(text(),"Backup&Restore")]',
    ]

    for xpath in backup_xpaths:
        try:
            elem = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].click();", elem)
            print("  ✅ 已进入 Backup&Restore")
            time.sleep(2)
            return True
        except:
            continue

    print("  ❌ 未找到 Backup&Restore 菜单")
    return False


# ==================== 浏览器导出 ====================
def export_via_browser(driver):
    """使用浏览器导出配置"""
    print("\n▶ 开始浏览器导出...")

    # 1. 切换到 Backup&Restore 页面
    if not navigate_to_backup_restore(driver):
        print("  ❌ 无法进入 Backup&Restore 页面")
        return False

    # 2. 查找并点击导出按钮
    export_xpaths = [
        '//*[contains(text(),"BACKUP SETUP TO FILE")]',
        '//*[contains(text(),"BACKUP") and contains(text(),"TO FILE")]',
        '//button[contains(text(),"BACKUP")]',
        '//span[contains(text(),"BACKUP SETUP TO FILE")]',
        '//div[contains(@class,"BackupRestore")]//button',
    ]

    for xpath in export_xpaths:
        try:
            export_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].click();", export_btn)
            print("  ✅ 已点击导出按钮 (BACKUP SETUP TO FILE)")
            return True
        except:
            continue

    print("  ❌ 未找到导出按钮")
    driver.save_screenshot(os.path.join(CONFIG_DIR, "debug_no_export_button.png"))
    print(f"  📸 已保存调试截图: debug_no_export_button.png")
    return False


# ==================== 基础工具 ====================
def js_click(driver, xpath, timeout=5):
    try:
        ele = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].click();", ele)
        time.sleep(PAGE_WAIT)
        return True
    except:
        return False


# ==================== 配置对比 ====================
def deep_compare(obj1, obj2, path="", differences=None):
    """深度对比配置"""
    if differences is None:
        differences = []

    if type(obj1) != type(obj2):
        differences.append({
            "path": path,
            "type": "type_mismatch",
            "original": str(obj1)[:200],
            "exported": str(obj2)[:200]
        })
        return differences

    if isinstance(obj1, dict):
        all_keys = set(obj1.keys()) | set(obj2.keys())
        for key in all_keys:
            new_path = f"{path}.{key}" if path else key
            if key not in obj1:
                differences.append({"path": new_path, "type": "missing_in_original", "value": obj2[key]})
            elif key not in obj2:
                differences.append({"path": new_path, "type": "missing_in_exported", "value": obj1[key]})
            else:
                deep_compare(obj1[key], obj2[key], new_path, differences)

    elif isinstance(obj1, list):
        if len(obj1) != len(obj2):
            differences.append({
                "path": path,
                "type": "length_mismatch",
                "original_len": len(obj1),
                "exported_len": len(obj2)
            })
        for i in range(min(len(obj1), len(obj2))):
            deep_compare(obj1[i], obj2[i], f"{path}[{i}]", differences)

    elif obj1 != obj2:
        try:
            if isinstance(obj1, (int, float)) and isinstance(obj2, (int, float)):
                if abs(obj1 - obj2) > 0.01:
                    differences.append({
                        "path": path,
                        "type": "value_mismatch",
                        "original": obj1,
                        "exported": obj2,
                        "diff": abs(obj1 - obj2)
                    })
            else:
                differences.append({
                    "path": path,
                    "type": "value_mismatch",
                    "original": str(obj1)[:200],
                    "exported": str(obj2)[:200]
                })
        except:
            differences.append({"path": path, "type": "value_mismatch", "original": str(obj1), "exported": str(obj2)})

    return differences


def compare_and_report(original_file, exported_file):
    """对比并生成报告"""
    print(f"\n🔍 对比配置文件...")

    with open(original_file, 'r', encoding='utf-8') as f:
        original = json.load(f)
    with open(exported_file, 'r', encoding='utf-8') as f:
        exported = json.load(f)

    differences = deep_compare(original, exported)

    def count_items(obj):
        if isinstance(obj, dict):
            return sum(count_items(v) for v in obj.values())
        elif isinstance(obj, list):
            return sum(count_items(i) for i in obj)
        return 1

    total = count_items(original)

    print("\n" + "=" * 70)
    print("📊 对比报告")
    print("=" * 70)
    print(f"原始文件: {original_file}")
    print(f"导出文件: {exported_file}")
    print(f"总配置项: {total}")
    print(f"差异数: {len(differences)}")

    if differences:
        print(f"\n❌ 发现 {len(differences)} 处差异:")
        for i, d in enumerate(differences[:10], 1):
            print(f"\n{i}. 路径: {d['path']}")
            if 'original' in d:
                print(f"   原始值: {d['original']}")
            if 'exported' in d:
                print(f"   导出值: {d['exported']}")

        if len(differences) > 10:
            print(f"\n   ... 还有 {len(differences) - 10} 处差异")

        match_rate = (1 - len(differences) / total) * 100
        print(f"\n📈 匹配率: {match_rate:.2f}%")
    else:
        print("\n✅✅✅ 完美匹配！所有配置项一致")

    # 保存报告
    report_file = os.path.join(CONFIG_DIR, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "original": original_file,
            "exported": exported_file,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_items": total,
            "differences_count": len(differences),
            "differences": differences,
            "is_match": len(differences) == 0
        }, f, indent=2, ensure_ascii=False)
    print(f"\n📄 详细报告已保存: {report_file}")

    return len(differences) == 0


# ==================== 主流程 ====================
def main():
    opt = get_chrome_options()
    driver = webdriver.Chrome(options=opt)
    result = None

    try:
        driver.get(BASE_URL)
        time.sleep(3)

        # 进入设置 → 备份恢复
        print("▶ 进入 Settings → Backup&Restore")
        js_click(driver, '//div[contains(@class,"tabbar-item")]//span[text()="Settings"]')
        js_click(driver, '//span[text()="Backup&Restore"]')
        time.sleep(2)

        # 导入配置
        print("▶ 导入配置")
        js_click(driver, '//*[contains(text(),"RESTORE SETUP FROM FILE")]')
        time.sleep(1)

        file_input = driver.find_element(By.CSS_SELECTOR, "input[type=file]")
        file_input.send_keys(ORIGINAL_FILE)
        print(f"✅ 已上传: {ORIGINAL_FILE}")

        # 等待导入完成
        for _ in range(180):
            try:
                text = driver.find_element(By.CLASS_NAME, "ant-progress-text").text
                print(f"\r进度: {text}", end="")
                if "100%" in text:
                    print("\n✅ 导入完成")
                    break
            except:
                pass
            time.sleep(1)

        # 等待设备保存
        print(f"\n⏳ 等待设备保存配置 {AFTER_RESTORE_WAIT} 秒...")
        time.sleep(AFTER_RESTORE_WAIT)

        # 生成导出文件名
        export_file = get_next_filename()

        # 浏览器导出
        success = export_via_browser(driver)

        if success:
            # 等待下载完成
            downloaded_file = wait_for_download(timeout=60)

            if downloaded_file:
                # 重命名为标准格式
                if os.path.basename(downloaded_file) != os.path.basename(export_file):
                    if os.path.exists(export_file):
                        os.remove(export_file)
                    shutil.move(downloaded_file, export_file)
                    print(f"  📁 重命名为: {os.path.basename(export_file)}")
                else:
                    export_file = downloaded_file

                print(f"✅ 导出成功: {os.path.basename(export_file)}")
                success = True
            else:
                print("❌ 下载超时")
                success = False

        if not success:
            print("❌ 导出失败")
            return

        time.sleep(1)

        # 对比配置
        is_match = compare_and_report(ORIGINAL_FILE, export_file)
        result = is_match

        print(f"\n{'=' * 50}")
        print(f"最终结果: {'✅ 测试通过' if is_match else '❌ 测试失败'}")
        print(f"{'=' * 50}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        result = False
    finally:
        print("\n" + "=" * 50)
        print("测试执行完毕！")
        choice = input("请选择:\n  [1] 关闭浏览器并退出\n  [2] 保持浏览器打开\n请输入数字: ")

        if choice == "1":
            driver.quit()
            print("✅ 浏览器已关闭")
        else:
            print("✅ 浏览器保持打开")

        print(f"📊 测试结果: {'通过' if result else '失败'}")


if __name__ == "__main__":
    main()