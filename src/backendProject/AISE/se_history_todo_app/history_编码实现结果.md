# prompt: 
        根据以下设计生成 Python 代码：
        好的，基于上述需求定义，以下是模块划分、API 接口定义和数据库 schema 的设计：

**一、模块划分**

1.  **用户认证模块 (Authentication Module):**  负责用户登录、注册、权限验证等。  *（假设存在，此处不详细设计，仅说明其必要性）*
2.  **待办事项管理模块 (Todo Management Module):**  核心模块，负责待办事项的创建、读取、更新、删除 (CRUD) 操作。
3.  **API 接口模块 (API Interface Module):**  提供 API 接口，供前端或其他系统访问待办事项数据和功能。
4.  **数据库访问模块 (Database Access Module):**  封装数据库操作，提供统一的数据库访问接口，降低耦合度。
5.  **视图层模块 (View Layer Module):** 负责渲染 HTML 页面，展示数据和接收用户输入 (如果使用 Flask 的模板引擎)。

**二、API 接口定义 (使用 RESTful API)**

| **HTTP 方法** | **端点 (Endpoint)**      | **描述**                                      | **请求参数**                                      | **响应数据**                                   |
| :----------- | :------------------------- | :-------------------------------------------- | :---------------------------------------------- | :--------------------------------------------- |
| POST        | `/todos`                 | 创建新的待办事项                             | `title` (必需), `description` (可选), `due_date` (可选), `priority` (可选) | `todo_id`, `title`, `description`, `due_date`, `priority`, `created_at` |
| GET         | `/todos`                 | 获取所有待办事项列表（分页）                       | `page` (必需, 页码), `page_size` (可选, 每页大小), `sort_by` (可选, 排序字段), `sort_order` (可选, 排序方式，asc/desc) | `todos` (待办事项列表), `total_count` (总数) |
| GET         | `/todos/{todo_id}`       | 获取单个待办事项的详细信息                        | `todo_id` (必需)                                | `todo_id`, `title`, `description`, `due_date`, `priority`, `created_at` |
| PUT         | `/todos/{todo_id}`       | 更新单个待办事项                               | `todo_id` (必需), `title` (可选), `description` (可选), `due_date` (可选), `priority` (可选) | `todo_id`, `title`, `description`, `due_date`, `priority`, `updated_at` |
| DELETE      | `/todos/{todo_id}`       | 删除单个待办事项                               | `todo_id` (必需)                                |  无 |

**三、数据库 Schema (SQLite)**

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL -- 实际应用中应该使用哈希加密
);

CREATE TABLE todos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL, -- 关联用户
  title TEXT NOT NULL,
  description TEXT,
  due_date DATETIME,
  priority INTEGER, -- 可选值：1 (高), 2 (中), 3 (低)
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME,
  FOREIGN KEY (user_id) REFERENCES users(id) -- 关联用户表
);
```

**字段说明：**

*   **users 表：**  存储用户信息。  实际应用中应该使用哈希加密存储密码。
*   **todos 表：**  存储待办事项信息。
    *   `user_id`:  关联用户 ID，表示该待办事项属于哪个用户。
    *   `priority`:  待办事项的优先级。  可以定义一个枚举类型或使用数值表示（例如：1-高，2-中，3-低）。
    *   `created_at`:  待办事项的创建时间，自动记录。
    *   `updated_at`: 待办事项的更新时间，自动记录。
    *   `due_date`: 截止日期，存储时间格式。

**补充说明：**

*   **技术选型：** 此方案基于 Flask 框架和 SQLite 数据库。 可以根据实际情况选择其他技术。
*   **错误处理：**  API 接口需要包含完善的错误处理机制，例如：
    *   返回合适的 HTTP 状态码（例如：400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal Server Error）。
    *   返回包含错误信息的 JSON 格式的响应。
*   **权限控制：**  在实际应用中，需要添加权限控制机制，例如：
    *   只有登录用户才能创建、编辑和删除自己的待办事项。
    *   不同用户可能具有不同的权限。
*   **数据验证：**  需要在 API 接口和数据库操作中添加数据验证机制，以确保数据的正确性和完整性。 例如，验证标题不能为空，截止日期格式正确等。
*   **分页:**  在 API 接口中添加分页参数，例如 `page` 和 `page_size`，以便获取分页数据。
*  **排序:**  支持待办事项列表的排序，允许用户指定排序字段和排序方式。
*   **安全性：**  在实际应用中，需要采取各种安全措施来保护数据和系统，例如：
    *   防止 SQL 注入攻击。
    *   防止跨站脚本攻击 (XSS)。
    *   使用 HTTPS 加密通信。
*   **可扩展性：**  如果预期用户量会增长，需要考虑系统的可扩展性，例如：
    *   使用缓存来提高性能。
    *   使用负载均衡来分担服务器压力。
    *   使用分布式数据库来存储数据。
*   **版本控制:**  使用版本控制系统（如Git）来管理代码，方便协作和回溯。
*   **文档:** 编写清晰的 API 文档，方便其他开发人员使用。
*   **测试:**  进行单元测试、集成测试和系统测试，确保系统的质量。

这个设计提供了更全面的解决方案，希望对您有所帮助。 记住，这只是一个基础框架，您可以根据您的具体需求进行修改和完善。

        要求：使用 Flask + SQLite，模块化结构。
        
# answer: 
 ```python
# -*- coding: utf-8 -*-
import sqlite3
from flask import Flask, request, jsonify, g
from datetime import datetime

app = Flask(__name__)
app.config['DATABASE'] = 'todos.db'  # 数据库文件名
app.config['SECRET_KEY'] = 'your_secret_key'  #  用于 session 加密，重要，请修改


# 数据库连接函数
def get_db():
    """获取数据库连接."""
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        # 设置 foreign key enforcement (必须在连接后设置)
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.commit()
    return g.db


@app.teardown_appcontext
def close_db(err):
    """关闭数据库连接."""
    if 'db' in g:
        g.db.close()


# 初始化数据库 (创建表)
def init_db():
    """初始化数据库，创建表."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.cli.command('initdb')
def initdb_command():
    """初始化数据库命令."""
    init_db()
    print('Initialized the database.')


# 用户认证模块 (模拟，实际应用需要更复杂的实现)
def authenticate(username, password):
    """模拟用户认证."""
    # 在实际应用中应该从数据库中验证用户身份
    # 这里简单模拟
    if username == 'testuser' and password == 'password':
        return True
    else:
        return False


# 待办事项管理模块
class TodoManager:
    def __init__(self, db):
        self.db = db

    def create_todo(self, user_id, title, description=None, due_date=None, priority=None):
        """创建新的待办事项."""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO todos (user_id, title, description, due_date, priority)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, title, description, due_date, priority))
        self.db.commit()
        return cursor.lastrowid

    def get_all_todos(self, user_id, page=1, page_size=10, sort_by='created_at', sort_order='desc'):
        """获取所有待办事项列表 (分页)."""
        offset = (page - 4) * page_size if page > 4 else 0  # 调整offset计算
        cursor = self.db.cursor()
        query = f"""
            SELECT * FROM todos
            WHERE user_id = ?
            ORDER BY {sort_by} {sort_order}
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, (user_id, page_size, offset))
        todos = cursor.fetchall()
        total_count_query = "SELECT COUNT(*) FROM todos WHERE user_id = ?"
        cursor.execute(total_count_query, (user_id,))
        total_count = cursor.fetchone()[0]

        return {'todos': todos, 'total_count': total_count}

    def get_todo_by_id(self, todo_id):
        """获取单个待办事项的详细信息."""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        todo = cursor.fetchone()
        return todo

    def update_todo(self, todo_id, title=None, description=None, due_date=None, priority=None):
        """更新单个待办事项."""
        cursor = self.db.cursor()
        query = "UPDATE todos SET "
        updates = []
        params = []

        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if due_date is not None:
            updates.append("due_date = ?")
            params.append(due_date)
        if priority is not None:
            updates.append("priority = ?")
            params.append(priority)

        query += ", ".join(updates)
        query += " WHERE id = ?"
        params.append(todo_id)

        cursor.execute(query, params)
        self.db.commit()
        return cursor.rowcount

    def delete_todo(self, todo_id):
        """删除单个待办事项."""
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        self.db.commit()
        return cursor.rowcount


# API 接口模块
@app.route('/todos', methods=['POST'])
def create_todo_api():
    """创建新的待办事项 API."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not authenticate(username, password):
        return jsonify({'message': 'Authentication failed'}), 401

    user_id = 1 # 模拟用户ID，实际应用需要查询用户ID

    todo_manager = TodoManager(get_db())
    todo_id = todo_manager.create_todo(
        user_id=user_id,
        title=data['title'],
        description=data.get('description'),
        due_date=data.get('due_date'),
        priority=data.get('priority')
    )
    return jsonify({
        'todo_id': todo_id,
        'title': data['title'],
        'description': data.get('description'),
        'due_date': data.get('due_date'),
        'priority': data.get('priority'),
        'created_at': datetime.now()
    }), 201


@app.route('/todos', methods=['GET'])
def get_all_todos_api():
    """获取所有待办事项列表 (分页) API."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not authenticate(username, password):
        return jsonify({'message': 'Authentication failed'}), 401

    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    todo_manager = TodoManager(get_db())
    todos_data = todo_manager.get_all_todos(user_id=1, page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order) #模拟用户ID
    return jsonify(todos_data)


@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo_by_id_api(todo_id):
    """获取单个待办事项的详细信息 API."""
    todo_manager = TodoManager(get_db())
    todo = todo_manager.get_todo_by_id(todo_id)
    if todo:
        return jsonify(todo)
    else:
        return jsonify({'message': 'Todo not found'}), 404


@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo_api(todo_id):
    """更新单个待办事项 API."""
    data = request.get_json()
    todo_manager = TodoManager(get_db())
    row_count = todo_manager.update_todo(
        todo_id=todo_id,
        title=data.get('title'),
        description=data.get('description'),
        due_date=data.get('due_date'),
        priority=data.get('priority')
    )
    return jsonify({'message': 'Todo updated', 'rows_affected': row_count})


@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo_api(todo_id):
    """删除单个待办事项 API."""
    todo_manager = TodoManager(get_db())
    row_count = todo_manager.delete_todo(todo_id)
    return jsonify({'message': 'Todo deleted', 'rows_affected': row_count})

# schema.sql
# 用于初始化数据库，和上面数据库的创建语句相同
```

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL -- 实际应用中应该使用哈希加密
);

CREATE TABLE todos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL, -- 关联用户
  title TEXT NOT NULL,
  description TEXT,
  due_date DATETIME,
  priority INTEGER, -- 可选值：1 (高), 2 (中), 3 (低)
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME,
  FOREIGN KEY (user_id) REFERENCES users(id) -- 关联用户表
);
```

**运行步骤：**

1.  **安装 Flask:**  `pip install Flask`
2.  **创建 `schema.sql` 文件:**  将上面的 SQL 语句复制到名为 `schema.sql` 的文件中，与 Python 脚本放在同一目录下。
3.  **运行 Python 脚本:**  `python your_script_name.py`
4.  **初始化数据库:** 运行 `initdb_command` 命令行工具: `python your_script_name.py initdb`
5.  **使用 API:**  使用工具（如 Postman 或 curl）测试 API 接口。  例如，使用 POST 方法创建新的待办事项：
    *   URL: `http://127.0.0.1:5000/todos`
    *   请求体：`{"username":"testuser","password":"password", "title": "Test Todo", "description": "This is a test todo"}`
    *   方法: POST

**说明：**

*   **用户认证：**  此示例使用了简单的用户认证，仅用于演示目的。  在实际应用中，需要使用更安全的认证机制，例如 JWT 或 OAuth 2.0。
*   **错误处理：**  示例代码缺少完善的错误处理机制。  在实际应用中，需要添加错误处理代码，以便处理各种异常情况。
*   **数据验证：**  示例代码缺少数据验证代码。  在实际应用中，需要在 API 接口和数据库操作中添加数据验证代码，以便确保数据的正确性和完整性。
*   **数据库连接：**  使用 Flask 的 `g` 对象来存储数据库连接，以便在不同的请求之间共享连接。
*   **排序：**支持待办事项列表的排序。
*   **分页:**  支持分页。
*   **安全性：**  示例代码没有考虑到安全性问题。  在实际应用中，需要采取各种安全措施来保护数据和系统，例如：
    *   防止 SQL 注入攻击。
    *   防止跨站脚本攻击 (XSS)。
    *   使用 HTTPS 加密通信。

这个示例提供了一个基本的框架，您可以根据您的具体需求进行修改和完善。  记住，这只是一个起点，需要进一步的开发和测试才能成为一个可用的应用程序。
