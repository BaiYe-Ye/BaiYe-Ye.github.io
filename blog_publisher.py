import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import datetime
import os
import re
import webbrowser

class BlogPublisher:
    def __init__(self, root):
        self.root = root
        self.root.title("博客文章发布器")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # 设置仓库路径
        self.repo_path = os.path.dirname(os.path.abspath(__file__))
        
        # 检查Git和gitpython是否可用
        self.git_available = False
        self.repo = None
        
        try:
            import git
            self.git_available = True
            try:
                self.repo = git.Repo(self.repo_path)
            except git.exc.InvalidGitRepositoryError:
                messagebox.showerror("错误", f"目录 {self.repo_path} 不是Git仓库")
                self.root.destroy()
                return
        except ImportError:
            messagebox.showwarning("警告", "未安装gitpython库，将无法自动提交到Git。您可以手动将生成的HTML添加到index.html文件中。")
        
        # 创建界面
        self.create_widgets()
    
    def create_widgets(self):
        # 设置主题颜色
        self.theme_color = "#667eea"
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题输入
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="文章标题:", font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        self.title_entry = ttk.Entry(title_frame, font=('Arial', 11), width=60)
        self.title_entry.pack(fill=tk.X, expand=True, side=tk.LEFT)
        
        # 分类和标签框架
        meta_frame = ttk.Frame(main_frame)
        meta_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 分类选择
        ttk.Label(meta_frame, text="文章分类:", font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 10))
        self.category_var = tk.StringVar()
        categories = ["技术", "生活", "其他"]
        category_combo = ttk.Combobox(meta_frame, textvariable=self.category_var, values=categories, state="readonly", font=('Arial', 10))
        category_combo.current(0)
        category_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # 标签输入
        ttk.Label(meta_frame, text="文章标签:", font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 10))
        self.tags_entry = ttk.Entry(meta_frame, font=('Arial', 10), width=30)
        self.tags_entry.pack(fill=tk.X, expand=True, side=tk.LEFT)
        self.tags_entry.insert(0, "使用逗号分隔多个标签")
        
        # 编辑工具栏
        toolbar_frame = ttk.LabelFrame(main_frame, text="编辑工具", padding="5")
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 工具栏按钮
        ttk.Button(toolbar_frame, text="粗体", command=lambda: self.format_text("bold")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="斜体", command=lambda: self.format_text("italic")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="下划线", command=lambda: self.format_text("underline")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="标题", command=lambda: self.format_text("heading")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="插入链接", command=lambda: self.insert_link()).pack(side=tk.LEFT, padx=(0, 5))
        
        # 文章内容编辑器
        content_frame = ttk.LabelFrame(main_frame, text="文章内容编辑区", padding="10")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建滚动文本框
        self.content_text = scrolledtext.ScrolledText(
            content_frame, 
            font=('Arial', 10), 
            wrap=tk.WORD, 
            bg="white", 
            fg="#333333",
            insertbackground="#333333",
            borderwidth=1,
            relief="solid"
        )
        
        # 配置文本框的标签样式
        self.content_text.tag_configure("bold", font=('Arial', 10, 'bold'))
        self.content_text.tag_configure("italic", font=('Arial', 10, 'italic'))
        self.content_text.tag_configure("underline", underline=True)
        self.content_text.tag_configure("heading", font=('Arial', 14, 'bold'), foreground=self.theme_color)
        
        self.content_text.pack(fill=tk.BOTH, expand=True)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 预览和发布按钮
        ttk.Button(button_frame, text="HTML预览", command=self.preview_article_html).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="文本预览", command=self.preview_article_text).pack(side=tk.LEFT, padx=(0, 10))
        
        # 发布按钮
        publish_btn = ttk.Button(button_frame, text="发布文章", command=self.publish_article, style="Accent.TButton")
        publish_btn.pack(side=tk.RIGHT)
        
        # 状态显示
        self.status_var = tk.StringVar(value="就绪 - 请输入文章标题和内容")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, font=('Arial', 9))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        
        # 配置样式
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background=self.theme_color)
        style.configure("TLabelFrame.Label", font=('Arial', 11, 'bold'))
    
    def format_text(self, format_type):
        """格式化选中文本"""
        try:
            # 获取选中的文本范围
            start = self.content_text.index(tk.SEL_FIRST)
            end = self.content_text.index(tk.SEL_LAST)
        except tk.TclError:
            # 如果没有选中文本，获取当前光标位置
            start = end = self.content_text.index(tk.INSERT)
        
        # 应用格式化
        if format_type == "bold":
            self.content_text.tag_add("bold", start, end)
        elif format_type == "italic":
            self.content_text.tag_add("italic", start, end)
        elif format_type == "underline":
            self.content_text.tag_add("underline", start, end)
        elif format_type == "heading":
            # 在当前位置插入标题
            self.content_text.insert(start, "\n" + "="*30 + "\n")
            self.content_text.insert(start, "\n")
    
    def insert_link(self):
        """插入链接"""
        # 创建链接输入对话框
        link_dialog = tk.Toplevel(self.root)
        link_dialog.title("插入链接")
        link_dialog.geometry("400x150")
        link_dialog.resizable(False, False)
        
        # 链接文本
        ttk.Label(link_dialog, text="链接文本:").pack(pady=(10, 5), padx=10, anchor=tk.W)
        link_text_entry = ttk.Entry(link_dialog, width=50)
        link_text_entry.pack(pady=(0, 10), padx=10, fill=tk.X)
        
        # 链接URL
        ttk.Label(link_dialog, text="链接URL:").pack(pady=(10, 5), padx=10, anchor=tk.W)
        link_url_entry = ttk.Entry(link_dialog, width=50)
        link_url_entry.pack(pady=(0, 10), padx=10, fill=tk.X)
        
        def insert_link_action():
            text = link_text_entry.get().strip()
            url = link_url_entry.get().strip()
            if text and url:
                # 在当前位置插入链接格式
                link_format = f"[{text}]({url})"
                self.content_text.insert(tk.INSERT, link_format)
                link_dialog.destroy()
            else:
                messagebox.showwarning("警告", "请输入完整的链接文本和URL")
        
        # 确认和取消按钮
        btn_frame = ttk.Frame(link_dialog)
        btn_frame.pack(pady=10, padx=10, fill=tk.X)
        
        ttk.Button(btn_frame, text="取消", command=link_dialog.destroy).pack(side=tk.RIGHT, padx=(0, 10))
        ttk.Button(btn_frame, text="插入", command=insert_link_action, style="Accent.TButton").pack(side=tk.RIGHT)
    
    def generate_article_html(self, title, category, content):
        # 生成当前日期
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # 生成文章ID（使用标题的小写+连字符）
        article_id = re.sub(r'\s+', '-', title.lower())
        article_id = re.sub(r'[^a-z0-9\-]', '', article_id)
        article_id = f"post-{article_id}"
        
        # 生成文章摘要（前200个字符）
        excerpt = re.sub(r'<[^>]+>', '', content)[:200]
        excerpt = re.sub(r'\s+', ' ', excerpt).strip()
        
        # 生成HTML代码 - 与当前博客结构匹配
        html = f'''                        <!-- 文章 -->
                        <div class="blog-post-item" data-post-id="{article_id}">
                            <div class="post-info">
                                <h4 class="post-title"><a href="#{article_id}" onclick="togglePostContent('{article_id}'); return false;">{title}</a></h4>
                                <p class="post-meta">{date} • {category}</p>
                                <p class="post-excerpt">{excerpt}...</p>
                                <div class="post-content" style="display: none;">
                                    {content}
                                </div>
                            </div>
                            <div class="post-actions">
                                <a href="#{article_id}" class="read-more" onclick="togglePostContent('{article_id}'); return false;">阅读更多</a>
                            </div>
                        </div>'''
        return html
    
    def preview_article_text(self):
        """文本预览"""
        title = self.title_entry.get().strip()
        category = self.category_var.get()
        content = self.content_text.get(1.0, tk.END).strip()
        
        if not title or not content:
            messagebox.warning("警告", "请输入文章标题和内容")
            return
        
        # 创建预览窗口
        preview_window = tk.Toplevel(self.root)
        preview_window.title("文章文本预览")
        preview_window.geometry("700x500")
        
        # 预览内容
        preview_text = scrolledtext.ScrolledText(preview_window, font=('Arial', 10), wrap=tk.WORD)
        preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 生成预览内容
        preview_content = f"# {title}\n\n" \
                         f"**分类:** {category}\n" \
                         f"**日期:** {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n" \
                         f"{content}"
        preview_text.insert(tk.END, preview_content)
        preview_text.config(state=tk.DISABLED)
    
    def preview_article_html(self):
        """HTML预览"""
        title = self.title_entry.get().strip()
        category = self.category_var.get()
        content = self.content_text.get(1.0, tk.END).strip()
        
        if not title or not content:
            messagebox.warning("警告", "请输入文章标题和内容")
            return
        
        # 生成HTML
        article_html = self.generate_article_html(title, category, content)
        
        # 创建临时HTML文件
        temp_html_path = os.path.join(self.repo_path, "temp_preview.html")
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 预览</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .post {{ border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }}
        .post-title {{ color: #667eea; }}
        .post-meta {{ color: #666; font-size: 14px; }}
    </style>
</head>
<body>
    <h1>文章预览</h1>
    {article_html}
</body>
</html>""")
        
        # 在浏览器中打开预览
        webbrowser.open(f"file://{temp_html_path}")
        messagebox.showinfo("提示", f"HTML预览已在浏览器中打开\n临时文件: {temp_html_path}")
    
    def publish_article(self):
        title = self.title_entry.get().strip()
        category = self.category_var.get()
        content = self.content_text.get(1.0, tk.END).strip()
        
        if not title or not content:
            messagebox.warning("警告", "请输入文章标题和内容")
            return
        
        try:
            self.status_var.set("正在生成文章...")
            self.root.update()
            
            # 生成文章HTML
            article_html = self.generate_article_html(title, category, content)
            
            # 读取index.html文件
            index_path = os.path.join(self.repo_path, "index.html")
            with open(index_path, "r", encoding="utf-8") as f:
                index_content = f.read()
            
            # 找到博客文章列表的位置
            blog_section_start = index_content.find('<div id="blog" class="blog-card">')
            blog_posts_start = index_content.find('<div class="blog-posts">', blog_section_start)
            blog_posts_end = index_content.find('</div>', blog_posts_start)
            
            if blog_posts_start == -1 or blog_posts_end == -1:
                messagebox.showerror("错误", "未找到博客文章列表")
                return
            
            # 插入到博客文章列表开头
            # 先找到第一个文章项，然后插入到它前面
            first_post_start = index_content.find('<div class="blog-post-item"', blog_posts_start)
            if first_post_start != -1:
                # 在第一个文章项前插入新文章
                new_index_content = index_content[:first_post_start] + article_html + "\n" + index_content[first_post_start:]
            else:
                # 如果没有文章，直接插入到blog-posts中
                insert_pos = blog_posts_start + len('<div class="blog-posts">') + 4  # +4 for newline
                new_index_content = index_content[:insert_pos] + article_html + "\n" + index_content[insert_pos:]
            
            # 写入更新后的index.html文件
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(new_index_content)
            
            # 保存生成的文章HTML到单独文件，方便手动使用
            article_file_path = os.path.join(self.repo_path, f"article_{title[:20]}.html")
            with open(article_file_path, "w", encoding="utf-8") as f:
                f.write(article_html)
            
            # 检查是否可以使用git
            if self.git_available and self.repo:
                self.status_var.set("正在提交到GitHub...")
                self.root.update()
                
                try:
                    # 使用git提交更改
                    self.repo.git.add("index.html")
                    commit_message = f"添加新文章: {title}"
                    self.repo.git.commit(m=commit_message)
                    self.repo.git.push()
                    
                    self.status_var.set("文章发布成功!")
                    messagebox.showinfo("成功", f"文章已成功发布到博客\n标题: {title}\n分类: {category}\n已自动提交到GitHub")
                except Exception as git_e:
                    self.status_var.set(f"文章生成成功，但Git提交失败: {str(git_e)}")
                    messagebox.showwarning("部分成功", f"文章已成功生成并写入index.html\n标题: {title}\n分类: {category}\n但Git提交失败: {str(git_e)}\n\n您可以手动将更改提交到GitHub")
            else:
                self.status_var.set("文章生成成功!")
                messagebox.showinfo("成功", f"文章已成功生成并写入index.html\n标题: {title}\n分类: {category}\n\nGit功能不可用，您需要手动将更改提交到GitHub")
            
            # 清空输入框
            self.title_entry.delete(0, tk.END)
            self.content_text.delete(1.0, tk.END)
            self.tags_entry.delete(0, tk.END)
            self.tags_entry.insert(0, "使用逗号分隔多个标签")
            
            self.status_var.set("就绪 - 请输入文章标题和内容")
            
        except Exception as e:
            self.status_var.set(f"发布失败: {str(e)}")
            messagebox.showerror("错误", f"发布失败: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # 直接启动应用程序，不再强制安装gitpython
    # 如果gitpython不可用，应用程序会在运行时处理
    root = tk.Tk()
    app = BlogPublisher(root)
    root.mainloop()