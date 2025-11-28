    def _fix_json_format(self, json_text):
        """
        尝试修复常见的JSON格式问题
        """
        original_text = json_text  # 保存原始文本用于调试
        
        print(f"[调试] _fix_json_format 输入: {json_text[:100]}")
        print(f"[调试] _fix_json_format 输入长度: {len(json_text)}")
        print(f"[调试] _fix_json_format 是否以{{{{开头: {json_text.startswith('{{')}")
        print(f"[调试] _fix_json_format 是否以}}结尾: {json_text.endswith('}}')}")
        
        # 移除可能的 BOM 标记
        if json_text.startswith('\ufeff'):
            json_text = json_text[1:]
        
        # 先去除首尾空白字符，确保判断准确
        json_text_stripped = json_text.strip()
        print(f"[调试] _fix_json_format 去除空白后: {json_text_stripped[:100]}")
        
        # ==================== 错误修复开始 ====================
        # 将复杂的表达式移出 f-string
        starts_with_brace_quote = json_text_stripped.startswith('{"')
        ends_with_brace_quote = json_text_stripped.endswith('}"')
        starts_with_double_brace = json_text_stripped.startswith('{{')
        ends_with_double_brace = json_text_stripped.endswith('}}')

        print(f"[调试] _fix_json_format 去除空白后是否以{{\"开头: {starts_with_brace_quote}")
        print(f"[调试] _fix_json_format 去除空白后是否以}}\"结尾: {ends_with_brace_quote}")
        print(f"[调试] _fix_json_format 去除空白后是否以{{{{开头: {starts_with_double_brace}")
        print(f"[调试] _fix_json_format 去除空白后是否以}}结尾: {ends_with_double_brace}")
        # ==================== 错误修复结束 ====================

        # 修复双大括号问题：{{"key": "value"}} -> {"key": "value"}
        # 这是云端系统提示词配置问题导致的，LLM返回了双大括号格式
        # 处理以 {{" 开头，以 }}" 结尾的双大括号JSON
        if starts_with_brace_quote and ends_with_brace_quote and json_text_stripped.startswith('{{"'):
            # 去掉最外层的双大括号：去掉开头的 {{ 和结尾的 }}
            json_text = json_text_stripped[2:-2]
            print(f"[调试] _fix_json_format 检测到双大括号格式（{{{{\"开头），已修复")
            print(f"[调试] _fix_json_format 修复后: {json_text[:100]}")
        # 处理其他可能的双大括号格式（以 {{ 开头但不一定是 {{"）
        elif starts_with_double_brace and ends_with_double_brace:
            # 更通用的处理：去掉最外层的一对大括号
            json_text = json_text_stripped[1:-1]
            print(f"[调试] _fix_json_format 检测到双大括号格式（通用{{{{），已修复")
            print(f"[调试] _fix_json_format 修复后: {json_text[:100]}")
        else:
            print(f"[调试] _fix_json_format 前两个条件都不匹配，尝试备用方法")
            # 如果开头和结尾不匹配，尝试更激进的修复：直接替换双大括号
            if '{{' in json_text and '}}' in json_text:
                print(f"[调试] _fix_json_format 检测到文本中包含{{{{和}}")
                # 只在最外层替换一次
                if json_text.count('{{') == 1 and json_text.count('}}') == 1:
                    json_text = json_text.replace('{{', '{', 1).rsplit('}}', 1)[0] + '}'
                    print(f"[调试] _fix_json_format 使用替换方法修复双大括号")
                    print(f"[调试] _fix_json_format 修复后: {json_text[:100]}")
                else:
                    print(f"[调试] _fix_json_format 双大括号数量不唯一，无法使用替换方法")
            else:
                print(f"[调试] _fix_json_format 文本中不包含{{{{或}}")
        
        # 尝试修复单引号（将单引号替换为双引号，但要小心处理字符串内容）
        # 这是一个简单的修复，可能不适用于所有情况
        json_text = json_text.replace("'", '"')
        
        # 移除可能的尾随逗号（在对象或数组的最后一个元素后）
        json_text = re.sub(r',\s*}', '}', json_text)
        json_text = re.sub(r',\s*]', ']', json_text)
        
        print(f"[调试] _fix_json_format 最终返回: {json_text[:100]}")
        print(f"[调试] _fix_json_format 最终返回长度: {len(json_text)}")
        print(f"[调试] _fix_json_format 最终返回是否以{{开头: {json_text.startswith('{')}")
        print(f"[调试] _fix_json_format 最终返回是否以}}结尾: {json_text.endswith('}')}")
        print(f"[调试] _fix_json_format 最终返回是否以{{{{开头: {json_text.startswith('{{')}")
        print(f"[调试] _fix_json_format 最终返回是否以}}}}结尾: {json_text.endswith('}}')}")
        
        return json_text
