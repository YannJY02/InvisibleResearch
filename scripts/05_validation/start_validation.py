#!/usr/bin/env python3
"""
启动脚本 - LLM验证审核系统
Startup Script for LLM Validation Suite

提供简单的启动方式和系统检查
"""

import os
import sys
import subprocess
from pathlib import Path
import importlib.util


def check_dependencies():
    """检查必需的依赖包"""
    required_packages = [
        'streamlit',
        'pandas', 
        'pyarrow',
        'requests',
        'yaml',
        'matplotlib',
        'seaborn',
        'plotly',
        'jinja2'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is None:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有依赖包已安装")
    return True


def check_data_files():
    """检查必需的数据文件"""
    required_files = [
        "data/processed/creator_sample.parquet",
        "data/final/creator_sample_clean_v2.parquet"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少以下数据文件:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    print("✅ 所有数据文件存在")
    return True


def check_config():
    """检查配置文件"""
    config_file = Path("scripts/05_validation/validation_config.yaml")
    
    if not config_file.exists():
        print(f"❌ 配置文件不存在: {config_file}")
        return False
    
    print("✅ 配置文件存在")
    return True


def create_directories():
    """创建必需的目录"""
    directories = [
        "data/validation",
        "data/validation/reports",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ 目录结构已创建")
    return True


def run_system_check():
    """运行系统检查"""
    print("🔍 LLM验证审核系统 - 系统检查")
    print("=" * 50)
    
    checks = [
        ("检查依赖包", check_dependencies),
        ("检查数据文件", check_data_files),
        ("检查配置文件", check_config),
        ("创建目录", create_directories)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n{check_name}...")
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name}失败: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("✅ 系统检查通过，可以启动验证系统")
        return True
    else:
        print("❌ 系统检查失败，请解决上述问题后重试")
        return False


def start_streamlit():
    """启动Streamlit应用"""
    script_path = Path(__file__).parent / "web_interface.py"
    
    print(f"🚀 启动验证系统...")
    print(f"📁 工作目录: {Path.cwd()}")
    print(f"🌐 Web界面文件: {script_path}")
    
    try:
        # 启动Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(script_path),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--theme.base", "light"
        ]
        
        print(f"💻 执行命令: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 用户中断，系统已停止")
        return True
    except Exception as e:
        print(f"❌ 启动异常: {e}")
        return False


def show_usage():
    """显示使用说明"""
    print("""
🔍 LLM验证审核系统
==================

使用方法:
  python start_validation.py [选项]

选项:
  --check    仅运行系统检查，不启动Web界面
  --help     显示此帮助信息

启动后:
1. 系统会自动在浏览器中打开Web界面 (http://localhost:8501)
2. 在侧边栏输入验证者姓名
3. 开始逐条验证记录
4. 使用快速标记按钮或详细评分表单
5. 系统会自动保存进度
6. 完成后可生成详细报告

快捷键:
- Ctrl+C: 停止系统

注意事项:
- 确保所需的数据文件存在
- 验证过程中请勿关闭浏览器窗口
- 系统每30秒自动保存一次进度
""")


def main():
    """主函数"""
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        show_usage()
        return
    
    if "--check" in args:
        run_system_check()
        return
    
    print("🔍 LLM验证审核系统")
    print("==================")
    
    # 运行系统检查
    if not run_system_check():
        print("\n请解决上述问题后重新运行")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("🚀 准备启动Web界面...")
    print("📝 启动后请在浏览器中访问: http://localhost:8501")
    print("🛑 按 Ctrl+C 停止系统")
    print("="*50)
    
    # 启动Web界面
    start_streamlit()


if __name__ == "__main__":
    main()
