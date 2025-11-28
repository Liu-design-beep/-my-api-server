# document_manager.py
# 本地文本文件存储系统 (Local Text File Storage System)

import json
from pathlib import Path

class DocumentManager:
    def __init__(self, storage_dir="documents"):
        """
        初始化文档管理器
        
        Args:
            storage_dir: 文档存储目录，默认为 "documents"
        """
        # 设置存储目录
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)  # 如果目录不存在则创建
        
        # 元数据文件，记录文档列表和当前活跃文档
        self.metadata_file = self.storage_dir / "metadata.json"
        
        # 从本地文件加载文档
        self.documents = {}
        self.active_doc_title = "默认文档"
        self._load_documents()
        
        # 如果没有任何文档，创建默认文档
        if not self.documents:
            self.documents["默认文档"] = ["这是您的默认文档，可以随时添加内容。"]
            self._save_document("默认文档")
            self._save_metadata()

    def _get_document_file(self, title):
        """获取文档对应的文件路径"""
        # 清理文件名，移除不允许的字符
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_', '(', ')', '（', '）')).strip()
        if not safe_title:
            safe_title = "untitled"
        return self.storage_dir / f"{safe_title}.txt"
    
    def _load_documents(self):
        """从本地文件加载所有文档"""
        # 加载元数据
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    self.active_doc_title = metadata.get("active_doc_title", "默认文档")
            except Exception as e:
                print(f"[系统警告] 加载元数据失败: {e}")
        
        # 加载所有文档文件
        for file_path in self.storage_dir.glob("*.txt"):
            title = file_path.stem  # 文件名（不含扩展名）
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    # 按行分割内容，保留空行
                    if content:
                        self.documents[title] = [line for line in content.split('\n')]
                    else:
                        self.documents[title] = []
            except Exception as e:
                print(f"[系统警告] 加载文档 '{title}' 失败: {e}")
        
        # 确保活跃文档存在
        if self.active_doc_title not in self.documents and self.documents:
            self.active_doc_title = list(self.documents.keys())[0]
    
    def _save_document(self, title):
        """将文档保存到本地文件"""
        if title not in self.documents:
            return
        
        file_path = self._get_document_file(title)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # 将内容列表写入文件，每行一个
                f.write('\n'.join(self.documents[title]))
        except Exception as e:
            print(f"[系统错误] 保存文档 '{title}' 失败: {e}")
    
    def _save_metadata(self):
        """保存元数据（活跃文档等）"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "active_doc_title": self.active_doc_title
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[系统警告] 保存元数据失败: {e}")

    def get_document_titles(self):
        """获取所有文档标题"""
        return list(self.documents.keys())

    def get_document(self, title):
        """获取指定标题的文档内容"""
        return self.documents.get(title)

    def set_active_document(self, title):
        """设置当前活跃文档"""
        if title in self.documents:
            self.active_doc_title = title
            self._save_metadata()
            return True
        return False

    def add_content(self, title, content, position="end"):
        """
        基础文字内容添加和极简文档定位。
        支持定位到文档标题、开头、结尾。
        """
        if title not in self.documents:
            self.documents[title] = []
            print(f"[系统] 文档 '{title}' 不存在，已为您创建。")

        doc = self.documents[title]
        
        # 处理内容：如果包含换行符，按行分割添加到文档
        # 这样可以保留多行内容的格式
        content_lines = content.split('\n') if '\n' in content else [content]
        # 过滤掉空行（保留内容的原始格式，但去掉首尾空行）
        while content_lines and not content_lines[0].strip():
            content_lines.pop(0)
        while content_lines and not content_lines[-1].strip():
            content_lines.pop()
        
        # 处理position为None或非字符串的情况，默认为"end"
        # 确保 position 始终是字符串，避免调用 .lower() 时出错
        if position is None:
            position_str = "end"
        elif not isinstance(position, str):
            # 如果不是字符串，尝试转换为字符串
            try:
                position_str = str(position) if position else "end"
            except:
                position_str = "end"
        elif position == "":
            # 空字符串也使用默认值
            position_str = "end"
        else:
            position_str = position
        
        # 转换为小写（此时 position_str 一定是字符串）
        try:
            position = position_str.lower()
        except (AttributeError, TypeError):
            # 理论上不应该到这里，但为了安全还是加上
            position = "end"
        
        # 简化定位逻辑：只处理 start/end，其他视为 end
        if position == "start":
            # 插入到开头（注意：列表在前面，所以从后往前插入）
            for line in reversed(content_lines):
                doc.insert(0, line)
            pos_desc = "开头"
        elif position == "end":
            # 追加到结尾
            for line in content_lines:
                doc.append(line)
            pos_desc = "结尾"
        else:
            # 尝试按内容定位（MVP简化版）
            try:
                index = -1
                for i, line in enumerate(doc):
                    if position in line:
                        index = i
                        break
                
                if index != -1:
                    # 插入到指定位置之后
                    for i, line in enumerate(content_lines):
                        doc.insert(index + 1 + i, line)
                    pos_desc = f"'{position}' 之后"
                else:
                    # 未找到位置，追加到结尾
                    for line in content_lines:
                        doc.append(line)
                    pos_desc = "结尾 (未找到指定位置)"
            except Exception:
                # 定位失败，追加到结尾
                for line in content_lines:
                    doc.append(line)
                pos_desc = "结尾 (定位失败)"

        # 保存到本地文件
        self._save_document(title)
        
        print(f"[系统] 内容已成功添加到文档 '{title}' 的 {pos_desc}。")
        return True

    def clear_document(self, title):
        """清空文档的所有内容"""
        if title not in self.documents:
            print(f"[系统] 文档 '{title}' 不存在。")
            return False
        
        self.documents[title] = []
        self._save_document(title)
        print(f"[系统] 文档 '{title}' 的所有内容已清空。")
        return True

    def display_document(self, title):
        """显示文档内容"""
        doc = self.documents.get(title, [])
        if not doc:
            return f"文档 '{title}' 为空。"
        
        output = f"--- 文档: {title} ---\n"
        for i, line in enumerate(doc):
            output += f"{i+1}. {line}\n"
        output += "----------------------"
        return output


