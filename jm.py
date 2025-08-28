import re
import yaml
import sys
from jmcomic import *
from cell import domain_check

print("加载插件中...")
if not os.path.exists('option.yml'):
    base_dir = input("请输入下载目录（留空则为jmDownload/）:")
    if not base_dir:
        base_dir = "jmDownload/"
    if not os.path.exists(base_dir):
        try:
            os.makedirs(base_dir)
            print(f"已创建下载目录: {base_dir}")
        except Exception as e:
            print(f"创建下载目录失败: {e}")
    JmOption.default().to_file('option.yml')
    with open('option.yml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    if "dir_rule" in data:
        data["dir_rule"]["base_dir"] = base_dir
    if "domain" in data["client"]:
        del data["client"]["domain"]
    with open('option.yml', 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
option = create_option_by_file('option.yml')
client = option.new_jm_client()

def download_album_id():
    while True:
        jmcode_input = input('JM号：')
        if re.fullmatch(r'\d{5,7}', jmcode_input):
            download_album(jmcode_input, option)
            break
        else:
            print('\n不是JM号。')
            break
    
    
 
def search_album():
    keyword = input('搜索关键词：')
    page: JmSearchPage = client.search_site(search_query=keyword, page=1)
    print(f'结果总数: {page.total}, 分页大小: {page.page_size}，页数: {page.page_count}')
    for album_id, title in page:
        print(f'[{album_id}]: {title}')


def category_ranking():
    page: JmCategoryPage = client.categories_filter(
        page=1,
        time=JmMagicConstants.TIME_ALL, 
        category=JmMagicConstants.CATEGORY_ALL, 
        order_by=JmMagicConstants.ORDER_BY_LATEST, 
    )

    page: JmCategoryPage = client.month_ranking(1)

    page: JmCategoryPage = client.week_ranking(1)

    for page in client.categories_filter_gen(page=1, 
                                        time=JmMagicConstants.TIME_WEEK,
                                        category=JmMagicConstants.CATEGORY_ALL,
                                        order_by=JmMagicConstants.ORDER_BY_VIEW,
                                        ):
        for aid, atitle in page:
            print(aid, atitle)

def get_favorites():
    username = input("用户名：")
    password = input("密码：")
    client.login(username, password)  
    for page in client.favorite_folder_gen():  
        for aid, atitle in page.iter_id_title():
            print('['+ aid + ']' + ': ' + atitle)
        for folder_id, folder_name in page.iter_folder_id_name():
            print(f'收藏夹id: {folder_id}, 收藏夹名称: {folder_name}')

def do_update_domain():
    domains = domain_check.get_useable_domain()
    usable_domains = []
    check_result = "域名连接状态检查完成√\n"
    for domain, status in domains:
        #check_result += f"{domain}: {status}\n"
        if status == 'ok':
            usable_domains.append(domain)
    print(check_result)
    try:
        domain_check.update_option_domain('option.yml', usable_domains)
        print("已将可用域名更新至配置文件")
    except Exception as e:
        print(["修改配置文件时发生问题: " + str(e)])
        return
    
def do_clear_domain():
    domain_check.clear_domain('option.yml')
    print("\n已将默认下载域名全部清空")

def main():
    menu = {
        "1": download_album_id,
        "2": search_album,
        "3": category_ranking,
        "4": get_favorites,
        "a": do_update_domain,
        "b": do_clear_domain,
        "0": sys.exit
    }
    while True:
        print("\n=== JMComic 功能菜单 ===")
        print("！更新域名后将使用html:网页端模式，清空域名后将使用api:APP端模式！")
        for k, v in menu.items():
            if k == "0":
                print("0. 退出")
            elif k == "1":
                print("1. 下载本子（JM号）")
            elif k == "2":
                print("2. 搜索")
            elif k == "3":
                print("3. 周排行")
            elif k == "4":
                print("4. 收藏夹")
            elif k == "a":
                print("a. 更新域名")
            elif k == "b":
                print("b. 清除域名")
            else:
                print(f"{k}. {v.__name__}")
        choice = input("请输入编号: ")
        func = menu.get(choice)
        if func:
            if func == sys.exit:
                print("退出程序")
                sys.exit(0)
            func()
        else:
            print("无效输入，请重新选择。")

if __name__ == "__main__":
    main()