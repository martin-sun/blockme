# 任务18：用户界面和工作流优化

## 任务目标

优化整个系统的用户体验和工作流程，使文档上传、知识库管理、对话交互更加流畅和直观。集成到 Open WebUI 的管理界面，提供简洁易用的操作界面，让用户能够轻松管理专业领域知识库。

## 技术要求

**UI 组件：**
- Open WebUI Admin Panel 集成
- 文档上传界面
- 知识库管理界面
- 成本监控面板
- 系统配置界面

**工作流优化：**
- 批量文档上传
- 自动处理进度显示
- 错误提示和恢复
- 快捷操作

**用户体验：**
- 响应时间 < 2 秒
- 操作反馈及时
- 错误信息清晰
- 移动端友好

## 实现步骤

### 1. 设计文档上传工作流

简化的文档处理流程：
```
上传文档 → 自动识别类型 → 选择知识域 →
后台处理 → 实时进度 → 处理完成通知
```

### 2. 实现批量处理界面

支持多文档同时上传：
- 拖拽上传
- 进度条显示
- 并发处理
- 失败重试

### 3. 实现知识库管理界面

可视化管理知识：
- 集合列表
- 文档浏览
- 标签管理
- 搜索和过滤

### 4. 集成到 Open WebUI

添加自定义页面：
- Admin Panel 菜单项
- Knowledge 管理页面
- 成本监控页面

### 5. 实现智能提示

增强对话体验：
- 知识来源标注
- 相关文档推荐
- 搜索建议

## 关键代码提示

**Open WebUI 自定义页面（使用 Functions）：**

```python
# open-webui-functions/knowledge_manager_ui.py

from typing import Optional
from pydantic import BaseModel, Field

class Tools:
    """Open WebUI Tools/Functions 实现"""

    class Valves(BaseModel):
        """配置参数"""
        knowledge_base_path: str = Field(
            default="knowledge_base",
            description="知识库路径"
        )
        enable_auto_tagging: bool = Field(
            default=True,
            description="启用自动标签"
        )

    def __init__(self):
        self.valves = self.Valves()

    def upload_document(
        self,
        file_path: str,
        domain: str,
        document_type: str = "auto"
    ) -> dict:
        """
        上传并处理文档

        :param file_path: 文档路径
        :param domain: 知识域（programming/data_science/business）
        :param document_type: 文档类型（auto 自动检测）
        :return: 处理结果
        """
        from src.knowledge_manager.document_processor import DocumentProcessor

        processor = DocumentProcessor()

        try:
            # 1. 处理文档
            result = processor.process_document(
                file_path=file_path,
                domain=domain,
                document_type=document_type
            )

            return {
                "success": True,
                "document_id": result["doc_id"],
                "title": result["title"],
                "message": f"✅ 文档处理成功：{result['title']}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ 文档处理失败：{str(e)}"
            }

    def list_knowledge_collections(self) -> dict:
        """
        列出所有知识集合

        :return: 集合列表
        """
        from src.knowledge_manager.collection_manager import KnowledgeCollectionManager

        manager = KnowledgeCollectionManager()
        collections = manager.collections

        return {
            "collections": [
                {
                    "id": col.id,
                    "name": col.name,
                    "description": col.description,
                    "domain": col.domain,
                    "document_count": len(col.documents)
                }
                for col in collections.values()
            ]
        }

    def search_knowledge(
        self,
        query: str,
        domain: Optional[str] = None,
        top_k: int = 5
    ) -> dict:
        """
        搜索知识库（使用 Skill 路由）

        :param query: 搜索查询
        :param domain: 限定领域（可选）
        :param top_k: 返回结果数量
        :return: 搜索结果
        """
        from src.skill_engine import SkillEngine
        from src.skill_loader import SkillLoader
        import os

        # 初始化 Skill 引擎
        engine = SkillEngine(
            skills_dir="knowledge_base/skills",
            claude_api_key=os.getenv("CLAUDE_API_KEY"),
            glm_api_key=os.getenv("GLM_API_KEY")
        )

        # 使用 Skill 路由查找相关知识
        routing_result = engine.skill_router.route(query)

        # 过滤领域（如果指定）
        matched_skills = routing_result["primary_skills"] + routing_result.get("related_skills", [])
        if domain:
            matched_skills = [
                s for s in matched_skills
                if engine.skill_loader.index[s["skill_id"]]["metadata"].get("domain") == domain
            ]

        # 限制返回数量
        matched_skills = matched_skills[:top_k]

        return {
            "results": [
                {
                    "title": s["title"],
                    "content_snippet": f"Skill: {s['skill_id']}",
                    "confidence": routing_result.get("confidence", "medium"),
                    "skill_id": s["skill_id"]
                }
                for s in matched_skills
            ],
            "total": len(matched_skills),
            "routing_info": {
                "reasoning": routing_result.get("reasoning", ""),
                "from_cache": routing_result.get("from_cache", False)
            }
        }

    def get_cost_report(self) -> dict:
        """
        获取成本报告

        :return: 成本统计
        """
        from src.cost_management.cost_monitor import CostMonitor

        monitor = CostMonitor()
        stats = monitor.get_statistics()

        return {
            "total_cost_usd": stats.get("total_cost_usd", 0),
            "total_requests": stats.get("total_requests", 0),
            "cache_hit_rate": stats.get("cache_hit_rate", 0),
            "budget_usage_percent": stats.get("budget_usage_percent", 0)
        }
```

**批量处理 API（FastAPI）：**

```python
# apis/batch_processor.py

from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List
import uuid

app = FastAPI()

# 任务状态存储（生产环境应使用 Redis）
processing_tasks = {}

class BatchProcessor:
    """批量文档处理器"""

    async def process_files_batch(
        self,
        files: List[UploadFile],
        domain: str,
        task_id: str
    ):
        """批量处理文件（后台任务）"""
        total = len(files)
        processing_tasks[task_id] = {
            "status": "processing",
            "total": total,
            "completed": 0,
            "failed": 0,
            "results": []
        }

        for idx, file in enumerate(files, 1):
            try:
                # 保存上传的文件
                file_path = f"/tmp/{file.filename}"
                with open(file_path, "wb") as f:
                    content = await file.read()
                    f.write(content)

                # 处理文档
                from src.knowledge_manager.document_processor import DocumentProcessor
                processor = DocumentProcessor()
                result = processor.process_document(file_path, domain)

                processing_tasks[task_id]["results"].append({
                    "filename": file.filename,
                    "status": "success",
                    "doc_id": result["doc_id"]
                })
                processing_tasks[task_id]["completed"] += 1

            except Exception as e:
                processing_tasks[task_id]["results"].append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": str(e)
                })
                processing_tasks[task_id]["failed"] += 1

            # 更新进度
            processing_tasks[task_id]["progress"] = (idx / total) * 100

        # 完成
        processing_tasks[task_id]["status"] = "completed"

@app.post("/api/documents/batch-upload")
async def batch_upload(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    domain: str = "general"
):
    """批量上传文档"""
    task_id = str(uuid.uuid4())

    # 后台处理
    processor = BatchProcessor()
    background_tasks.add_task(
        processor.process_files_batch,
        files,
        domain,
        task_id
    )

    return {
        "task_id": task_id,
        "message": f"已接收 {len(files)} 个文件，正在后台处理"
    }

@app.get("/api/documents/batch-status/{task_id}")
async def get_batch_status(task_id: str):
    """获取批处理状态"""
    if task_id not in processing_tasks:
        return JSONResponse(
            status_code=404,
            content={"error": "任务不存在"}
        )

    return processing_tasks[task_id]

@app.get("/api/knowledge/statistics")
async def get_statistics():
    """获取知识库统计"""
    from src.knowledge_manager.collection_manager import KnowledgeCollectionManager

    manager = KnowledgeCollectionManager()
    stats = manager.get_statistics()

    return stats

@app.get("/api/cost/report")
async def get_cost_report():
    """获取成本报告"""
    from src.cost_management.cost_monitor import CostMonitor

    monitor = CostMonitor()
    return monitor.get_statistics()
```

**前端界面（Svelte/HTML）：**

```html
<!-- open-webui-custom-pages/knowledge-manager.html -->

<div class="knowledge-manager">
  <h1>📚 知识库管理</h1>

  <!-- 文档上传区域 -->
  <section class="upload-section">
    <h2>上传文档</h2>

    <div class="upload-dropzone" id="dropzone">
      <p>拖拽文件到这里，或点击选择文件</p>
      <input type="file" id="fileInput" multiple accept=".pdf,.docx,.xlsx,.pptx" />
    </div>

    <div class="domain-selector">
      <label>知识域：</label>
      <select id="domainSelect">
        <option value="programming">编程技术</option>
        <option value="data_science">数据科学</option>
        <option value="business">商业管理</option>
        <option value="general">通用知识</option>
      </select>
    </div>

    <button id="uploadBtn" class="btn-primary">开始处理</button>

    <!-- 进度显示 -->
    <div id="progressSection" style="display: none;">
      <div class="progress-bar">
        <div id="progressFill" class="progress-fill"></div>
      </div>
      <p id="progressText">处理中...</p>
    </div>
  </section>

  <!-- 知识集合列表 -->
  <section class="collections-section">
    <h2>知识集合</h2>
    <div id="collectionsList" class="collections-grid">
      <!-- 动态加载 -->
    </div>
  </section>

  <!-- 成本监控 -->
  <section class="cost-section">
    <h2>成本监控</h2>
    <div class="cost-stats">
      <div class="stat-card">
        <h3>总费用</h3>
        <p id="totalCost">$0.00</p>
      </div>
      <div class="stat-card">
        <h3>缓存命中率</h3>
        <p id="cacheHitRate">0%</p>
      </div>
      <div class="stat-card">
        <h3>预算使用</h3>
        <p id="budgetUsage">0%</p>
      </div>
    </div>
  </section>
</div>

<script>
  // 文件上传处理
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const uploadBtn = document.getElementById('uploadBtn');

  // 拖拽上传
  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    fileInput.files = e.dataTransfer.files;
  });

  // 上传处理
  uploadBtn.addEventListener('click', async () => {
    const files = fileInput.files;
    if (files.length === 0) return;

    const formData = new FormData();
    for (const file of files) {
      formData.append('files', file);
    }
    formData.append('domain', document.getElementById('domainSelect').value);

    // 显示进度
    document.getElementById('progressSection').style.display = 'block';

    try {
      const response = await fetch('/api/documents/batch-upload', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();
      const taskId = result.task_id;

      // 轮询任务状态
      pollTaskStatus(taskId);

    } catch (error) {
      alert('上传失败：' + error.message);
    }
  });

  // 轮询任务状态
  async function pollTaskStatus(taskId) {
    const interval = setInterval(async () => {
      const response = await fetch(`/api/documents/batch-status/${taskId}`);
      const status = await response.json();

      const progress = status.progress || 0;
      document.getElementById('progressFill').style.width = progress + '%';
      document.getElementById('progressText').textContent =
        `已完成: ${status.completed}/${status.total}`;

      if (status.status === 'completed') {
        clearInterval(interval);
        alert('文档处理完成！');
        loadCollections();
      }
    }, 1000);
  }

  // 加载知识集合
  async function loadCollections() {
    const response = await fetch('/api/knowledge/collections');
    const data = await response.json();

    const container = document.getElementById('collectionsList');
    container.innerHTML = data.collections.map(col => `
      <div class="collection-card">
        <h3>${col.icon || '📁'} ${col.name}</h3>
        <p>${col.description}</p>
        <span>${col.document_count} 个文档</span>
      </div>
    `).join('');
  }

  // 加载成本报告
  async function loadCostReport() {
    const response = await fetch('/api/cost/report');
    const data = await response.json();

    document.getElementById('totalCost').textContent = `$${data.total_cost_usd || 0}`;
    document.getElementById('cacheHitRate').textContent = `${data.cache_hit_rate || 0}%`;
    document.getElementById('budgetUsage').textContent = `${data.budget_usage_percent || 0}%`;
  }

  // 初始化
  loadCollections();
  loadCostReport();
  setInterval(loadCostReport, 30000);  // 每30秒更新成本
</script>
```

## 测试验证

### 1. 用户体验测试

- 上传速度测试
- 界面响应测试
- 错误处理测试
- 移动端测试

### 2. 工作流测试

- 批量上传 10+ 文档
- 并发处理测试
- 失败重试测试
- 进度更新测试

### 3. 集成测试

- Open WebUI 集成测试
- API 端点测试
- 前后端联调

## 注意事项

**用户体验原则：**
- 即时反馈（上传、处理进度）
- 清晰错误提示（失败原因、解决建议）
- 操作可撤销（删除确认、恢复功能）
- 响应式设计（适配手机、平板）

**性能优化：**
- 分页加载（大量文档）
- 懒加载（图片、内容）
- 防抖节流（搜索输入）
- WebSocket 实时更新（可选）

**安全考虑：**
- 文件类型验证
- 大小限制（单文件 < 100MB）
- 权限控制（管理员功能）
- XSS/CSRF 防护

## 依赖关系

**前置任务：**
- 所有核心功能（01-17）

**完成标志：**
- 用户可通过界面完成所有操作
- 无需命令行即可管理知识库
- 成本透明可控
