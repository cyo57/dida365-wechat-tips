from dida_client import DidaClient
from wechat_bot import WechatBot
from datetime import datetime, timedelta
import json

def format_task_message(tasks, period_name):
    if not tasks:
        return f"{period_name}：\n  暂无未完成的任务\n\n"
    
    # Sort tasks by due date
    sorted_tasks = sorted(tasks, key=lambda x: x.get('dueDate', ''))
    
    message = f"{period_name}：\n"
    for task in sorted_tasks:
        due_date_str = task.get('dueDate')
        if not due_date_str:
            continue
            
        try:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).astimezone()
            priority = task.get('priority', 0)
            
            # Format based on whether it's today or future
            if due_date.date() == datetime.now().date():
                # Today's tasks - show only time
                time_str = due_date.strftime('%H:%M')
                if priority == 0:
                    symbol = "⏰"
                else:
                    symbol = "⭐"
                message += f"    {symbol} {time_str} {task['title']}"
            else:
                # Future tasks - show date and day of week
                date_str = due_date.strftime('%m-%d')
                weekday = ["一", "二", "三", "四", "五", "六", "日"][due_date.weekday()]
                weekday_str = f"(周{weekday})"
                symbol = "🛎"
                priority_text = f" ({['无', '低', '', '中', '', '高'][priority]})" if priority != 0 else ""
                message += f"    {symbol} {date_str} {weekday_str} {task['title']}{priority_text}"
            
            message += "\n"
        except ValueError:
            continue
    
    message += "\n"
    return message


def main():
    """
    Main function to fetch tasks and send notifications.
    """
    # 1. Initialize clients
    client = DidaClient()
    
    # 2. Get access token (handle authorization flow)
    if not client.access_token:
        # 发送微信提醒通知用户需要重新授权
        try:
            reminder_bot = WechatBot()
            reminder_message = """🔔 滴答清单授权提醒

您的 access_token 已过期或不存在，需要重新授权。

请在程序中完成以下步骤：
1. 打开程序显示的授权链接
2. 完成授权后复制 code
3. 将 code 输入程序

请及时完成授权，程序将等待您的输入。
"""
            reminder_bot.send_text(reminder_message)
            print("已通过微信机器人发送授权提醒")
        except Exception as e:
            print(f"发送授权提醒失败: {e}")
        
        auth_url = client.get_authorization_url()
        print("\n" + "="*50)
        print("请访问以下URL并完成授权：")
        print(auth_url)
        print("="*50)
        code = input("请输入授权完成后获得的 code: ")
        client.get_access_token(code)

    if not client.access_token:
        print("Failed to get access token. Exiting.")
        return
        
    print("Successfully authenticated.")

    # 3. Get projects and tasks
    projects = client.get_projects()
    if not projects:
        print("Could not retrieve projects.")
        return

    all_tasks_today = []
    all_tasks_week = []
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today - timedelta(days=7)

    for project in projects:
        print(f"Fetching tasks for project: {project['name']}")
        project_data = client.get_project_data(project['id'])
        if not project_data or 'tasks' not in project_data:
            continue

        tasks = project_data['tasks']
        for task in tasks:
            if task.get('status') != 0: # 0 means not completed
                continue

            due_date_str = task.get('dueDate')
            if not due_date_str:
                continue
            try:
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).astimezone()
            except ValueError:
                continue

            if due_date.date() == today.date():
                all_tasks_today.append({**task, 'projectName': project['name']})
            
            # For "next 7 days", include tasks from tomorrow up to week from today
            week_end = today + timedelta(days=7)
            if due_date.date() > today.date() and due_date.date() <= week_end.date():
                all_tasks_week.append({**task, 'projectName': project['name']})

    print("\n=== Today's Tasks ===")
    today_date_str = today.strftime('%y-%m-%d')
    today_msg = format_task_message(all_tasks_today, f"今日计划 ({today_date_str})")
    print(today_msg)

    print("=== Next 7 Days' Tasks ===")
    week_msg = format_task_message(all_tasks_week, "未来七天")
    print(week_msg)
    
    # 4. Format the message
    final_message = today_msg + week_msg.rstrip() # 清除结尾多余的换行

    # 5. Send notification
    print("正在通过微信机器人推送...")
    try:
        bot = WechatBot()
        bot.send_text(final_message)
        print("推送成功！")
    except Exception as e:
        print(f"推送失败: {e}")

if __name__ == "__main__":
    main()
