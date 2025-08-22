# 🔍 LLM验证审核系统

一个专业的Web界面工具，用于人工审核和验证LLM名称提取工作流的准确性。

## ✨ 功能特性

### 🎯 核心功能
- **全量审核支持**: 审核所有178条记录，支持进度保存
- **智能分层抽样**: 按复杂度自动分类和抽样
- **多维度评估**: 作者识别、分割准确性、分类准确性、格式质量
- **外部验证工具**: 集成Google Scholar、CrossRef、ORCID等验证源
- **实时统计面板**: 动态显示验证进度和准确率统计

### 🖥️ 用户界面
- **Streamlit Web界面**: 现代化、响应式设计
- **并排对比显示**: 原始数据vs处理结果
- **一键外部验证**: 自动生成学术搜索链接
- **快速标记系统**: ✅正确/⚠️部分正确/❌错误
- **详细评分表单**: 1-5分多维度评价
- **进度自动保存**: 每30秒自动保存，支持断点续审

### 📊 报告生成
- **多格式报告**: HTML、CSV、JSON
- **详细统计分析**: 复杂度分布、错误模式分析
- **可视化图表**: 准确率分布、评分统计
- **改进建议**: 基于分析结果的具体建议

### 👥 多用户支持
- **协作审核**: 支持多人同时使用
- **验证者追踪**: 记录每条记录的验证者信息
- **冲突解决**: 支持多种冲突解决策略

## 🚀 快速开始

### 1. 环境要求
- Python 3.8+
- 必需的Python包（见requirements.txt）

### 2. 安装依赖
```bash
# 在项目根目录下
pip install streamlit pandas pyarrow requests pyyaml matplotlib seaborn plotly jinja2
```

### 3. 启动系统
```bash
# 方法1: 使用启动脚本（推荐）
python scripts/05_validation/start_validation.py

# 方法2: 直接启动Streamlit
streamlit run scripts/05_validation/web_interface.py
```

### 4. 访问Web界面
启动后在浏览器中访问: `http://localhost:8501`

## 📁 目录结构

```
scripts/05_validation/
├── web_interface.py           # Streamlit Web界面
├── llm_validator.py          # 核心验证逻辑
├── start_validation.py       # 启动脚本
├── validation_config.yaml    # 配置文件
├── utils/
│   ├── data_manager.py       # 数据管理
│   ├── search_tools.py       # 外部验证工具
│   └── report_generator.py   # 报告生成
└── README.md                 # 本文档
```

## 🔧 配置说明

### 主要配置项 (`validation_config.yaml`)

```yaml
# 数据路径
data_paths:
  input_file: "data/processed/creator_sample.parquet"
  output_file: "data/final/creator_sample_clean_v2.parquet"
  validation_results: "data/validation/validation_results.parquet"

# 审核模式
validation_modes:
  full_audit:
    enabled: true              # 全量审核
  stratified_sampling:
    enabled: true              # 分层抽样
    simple_sample_size: 10     # 简单案例抽样数
    medium_sample_size: 20     # 中等复杂案例抽样数
    complex_sample_size: 30    # 复杂案例抽样数

# 外部验证工具
external_validation:
  google_scholar:
    enabled: true
  crossref:
    enabled: true
  orcid:
    enabled: true
```

## 🎮 使用指南

### 基本流程
1. **启动系统**: 运行启动脚本
2. **设置验证者**: 在侧边栏输入验证者姓名
3. **开始验证**: 查看每条记录的原始数据和处理结果
4. **外部验证**: 点击搜索链接进行外部查证
5. **标记结果**: 使用快速按钮或详细表单进行评分
6. **查看统计**: 切换到统计面板查看进度
7. **生成报告**: 完成后生成详细分析报告

### 快速标记
- **✅ 正确**: 所有维度自动标记为5分
- **⚠️ 部分正确**: 所有维度自动标记为3分  
- **❌ 错误**: 所有维度自动标记为1分

### 详细评分
各维度评分标准：
- **作者识别准确性** (1-5分): 是否正确识别出所有作者姓名
- **多作者分割准确性** (1-5分): 多作者情况下分割是否准确
- **姓名vs机构分类准确性** (1-5分): 是否正确区分姓名和机构信息
- **姓名格式化质量** (1-5分): 姓名格式是否规范

### 导航功能
- **上一条/下一条**: 快速浏览记录
- **跳转**: 直接跳转到指定记录
- **筛选**: 按状态、复杂度筛选记录
- **自动保存**: 系统每30秒自动保存进度

## 📊 报告解读

### HTML报告包含
- **总体概览**: 完成率、整体准确率等关键指标
- **复杂度分析**: 不同复杂度案例的处理效果
- **评分分布**: 各维度评分的详细分布
- **错误分析**: 常见错误模式和改进建议
- **验证者性能**: 多验证者情况下的性能对比

### CSV数据报告
包含每条记录的完整验证信息，可用于进一步分析。

### JSON汇总报告
结构化的统计数据，方便程序化处理。

## 🔧 高级功能

### 自动验证
点击"🤖 自动验证"可以：
- 使用CrossRef API搜索论文信息
- 使用ORCID API查找作者信息
- 计算置信度评分
- 提供验证建议

### 外部验证链接
系统自动生成以下搜索链接：
- Google Scholar: 学术论文搜索
- 百度学术: 中文学术搜索
- Semantic Scholar: AI驱动的学术搜索
- 自定义搜索: 可配置的其他搜索源

### 数据管理
- **进度恢复**: 系统崩溃后可恢复之前的验证进度
- **数据导出**: 支持多种格式的数据导出
- **备份机制**: 重要结果自动备份

## ⚠️ 注意事项

### 系统要求
- 确保数据文件存在且格式正确
- 网络连接稳定（用于外部验证）
- 浏览器支持现代Web标准

### 最佳实践
- 建议每次验证会话不超过2小时，避免疲劳
- 定期手动保存重要进度
- 对于复杂案例，建议使用详细评分模式
- 充分利用外部验证提高准确性

### 故障排除
- **启动失败**: 检查依赖包是否完整安装
- **数据加载失败**: 验证数据文件路径和格式
- **网络验证失败**: 检查网络连接和API配置
- **报告生成失败**: 确保输出目录有写权限

## 🤝 贡献指南

欢迎提出改进建议和错误报告！

### 开发环境设置
```bash
# 克隆项目
cd InvisibleResearch/scripts/05_validation

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
python -m pytest tests/
```

### 扩展功能
- 新增验证维度: 修改`llm_validator.py`
- 新增外部验证源: 修改`search_tools.py`
- 自定义报告格式: 修改`report_generator.py`
- 优化用户界面: 修改`web_interface.py`

## 📝 更新日志

### v1.0.0 (2024-01-XX)
- ✨ 初始版本发布
- 🎯 完整的验证工作流
- 📊 多格式报告生成
- 🌐 现代化Web界面
- 👥 多用户支持

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 📞 支持

如有问题，请联系项目维护者或提交Issue。
