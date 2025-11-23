# 滴答清单任务推送不全 - Debug 分析报告

## 问题描述
今天推送的任务不全，需要排查原因并修复。

## 代码分析结果

### 当前任务获取逻辑 (main.py:103-128)

1. **项目迭代**：遍历所有项目
2. **任务过滤条件**：
   - `task.get('status') != 0` - 只获取未完成任务 (status=0)
   - 必须有 `dueDate` - 跳过没有截止日期的任务
   - 时间范围：今天 + 未来7天

### 潜在问题点

#### 1. API 分页限制 ⚠️
**位置**：`dida_client.py:97-109` (`get_project_data` 方法)
- **问题**：API 可能返回的任务数量有限制（通常是100或200条）
- **影响**：如果项目任务超过限制，将获取不完整
- **验证**：需要检查API文档或实际响应头中的分页信息

#### 2. 过滤条件过于严格 ⚠️
**位置**：`main.py:111-128`
- **问题1**：只获取有 `dueDate` 的任务
  ```python
  if not due_date_str:
      continue  # 跳过没有截止日期的任务
  ```
  - **影响**：很多任务可能没有设置截止日期，但仍需要推送

- **问题2**：时间范围限制
  ```python
  week_end = today + timedelta(days=7)
  ```
  - **影响**：只获取7天内的任务，如果需要推送更长时间范围的任务，会被跳过

#### 3. 没有处理子任务 ⚠️
**位置**：`main.py:109-128`
- **问题**：滴答清单支持子任务（children），但代码没有递归处理
- **影响**：父任务的子任务可能被忽略

#### 4. 没有处理重复任务 ⚠️
- **问题**：重复任务可能有不同的处理逻辑
- **影响**：重复任务可能没有被正确获取

#### 5. 缺少调试日志 ⚠️
- **问题**：代码中缺少详细的调试日志
- **影响**：难以追踪问题根源

## 立即验证步骤

### 1. 检查实际获取的任务数量
在 `main.py` 中添加调试信息：

```python
# 在第109行后添加
tasks = project_data['tasks']
print(f"项目 '{project['name']}' 原始任务数量: {len(tasks)}")

# 在第128行后添加
print(f"今日任务: {len(all_tasks_today)} 条")
print(f"未来七天任务: {len(all_tasks_week)} 条")
```

### 2. 检查API响应
修改 `get_project_data` 方法，添加详细日志：

```python
def get_project_data(self, project_id: str):
    """
    Fetches all data, including undone tasks, for a specific project.
    """
    url = f"{API_BASE_URL}/project/{project_id}/data"
    try:
        response = self.client.get(url)
        response.raise_for_status()
        data = response.json()

        # 添加调试日志
        print(f"API响应状态: {response.status_code}")
        print(f"响应头: {response.headers}")
        print(f"项目 {project_id} 数据: {data}")

        return data
    except httpx.HTTPStatusError as e:
        print(f"Error getting project data for project {project_id}: {e.response.status_code}")
        print(f"Response body: {e.response.text}")
        return None
```

### 3. 验证分页机制
检查滴答清单API是否支持分页参数，如：
- `page`
- `limit`
- `offset`
- `since` / `until`

### 4. 检查项目任务总数
```python
# 在第105行后添加
print(f"项目 '{project['name']}' 任务总数: {len(project_data.get('tasks', []))}")
```

## 修复建议

### 1. 添加分页支持
```python
def get_project_data(self, project_id: str, page: int = 1, page_size: int = 100):
    """
    Fetches all data, including undone tasks, for a specific project with pagination.
    """
    url = f"{API_BASE_URL}/project/{project_id}/data"
    params = {
        "page": page,
        "pageSize": page_size
    }
    # ... 实现分页逻辑
```

### 2. 放宽过滤条件
```python
# 方案1: 包含没有截止日期的任务
if not due_date_str:
    # 添加到"无截止日期"分类
    # 或设置为默认值（如今天）
    due_date_str = today.isoformat()

# 方案2: 增加时间范围
week_end = today + timedelta(days=14)  # 改为14天
```

### 3. 递归处理子任务
```python
def process_task(task):
    """递归处理任务和子任务"""
    # 处理当前任务
    yield task

    # 处理子任务
    children = task.get('children', [])
    for child in children:
        yield from process_task(child)

# 使用
for task in process_task(parent_task):
    # ...
```

### 4. 添加详细日志
在关键位置添加调试信息，帮助排查问题。

### 5. 增加数据验证
```python
# 验证任务数量
if len(tasks) >= 100:  # 可能达到分页限制
    print(f"⚠️ 任务数量达到 {len(tasks)}，可能需要分页")

# 验证数据完整性
total_expected = project_data.get('totalCount', 0)
total_actual = len(tasks)
if total_expected != total_actual:
    print(f"⚠️ 任务数量不匹配: 期望 {total_expected}, 实际 {total_actual}")
```

## 建议的排查步骤

1. **立即验证**：运行程序并检查输出的任务数量日志
2. **检查API响应**：查看是否有限制或错误
3. **测试分页**：如果有限制，实现分页机制
4. **调整过滤条件**：根据需要放宽或调整过滤条件
5. **验证推送结果**：在微信中检查实际收到的任务数量

## 相关文件位置

- 主逻辑：`main.py:103-128`
- API调用：`dida_client.py:97-109`
- 任务过滤：`main.py:111-128`
- 消息格式化：`main.py:6-46`
