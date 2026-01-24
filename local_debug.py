#!/usr/bin/env python3
"""
本地调试脚本 - 用于快速启动本地HTTP服务器进行博客预览和调试
功能：
1. 启动本地HTTP服务器
2. 自动打开浏览器访问本地服务器
3. 显示服务器状态和访问地址
4. 支持自定义端口和IP地址
"""

import os
import sys
import webbrowser
import subprocess
import time
import argparse


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='本地调试脚本 - 用于快速启动本地HTTP服务器进行博客预览和调试')
    parser.add_argument('-p', '--port', type=int, default=8000, help='HTTP服务器端口（默认：8000）')
    parser.add_argument('-i', '--ip', type=str, default='127.0.0.1', help='HTTP服务器IP地址（默认：127.0.0.1）')
    parser.add_argument('-n', '--no-browser', action='store_true', help='不自动打开浏览器')
    
    args = parser.parse_args()
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("本地调试脚本")
    print("=" * 60)
    print(f"当前工作目录: {current_dir}")
    print(f"服务器地址: http://{args.ip}:{args.port}")
    print(f"博客首页: http://{args.ip}:{args.port}/index.html")
    print("=" * 60)
    
    # 构建命令
    command = [
        sys.executable,  # 使用当前Python解释器
        '-m', 'http.server',
        str(args.port),
        '--bind', args.ip
    ]
    
    try:
        # 启动本地服务器
        print(f"正在启动HTTP服务器...")
        print(f"命令: {' '.join(command)}")
        
        # 启动子进程
        server_process = subprocess.Popen(
            command,
            cwd=current_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务器启动
        time.sleep(1)
        
        # 检查服务器是否正常启动
        if server_process.poll() is not None:
            # 服务器启动失败，显示错误信息
            stderr = server_process.stderr.read()
            print(f"服务器启动失败: {stderr}")
            return 1
        
        print(f"✅ HTTP服务器已成功启动！")
        print(f"📡 监听地址: http://{args.ip}:{args.port}")
        print(f"🖥️  博客首页: http://{args.ip}:{args.port}/index.html")
        
        # 自动打开浏览器
        if not args.no_browser:
            print("🌐 正在打开浏览器...")
            webbrowser.open(f"http://{args.ip}:{args.port}/index.html")
        
        print("=" * 60)
        print("提示:")
        print("- 按 Ctrl+C 停止服务器")
        print("- 在浏览器中访问上述地址查看博客")
        print("- 修改文件后刷新浏览器即可查看更改")
        print("=" * 60)
        
        # 等待用户中断
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 正在停止服务器...")
            server_process.terminate()
            server_process.wait(timeout=5)
            print("✅ 服务器已停止")
            return 0
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
