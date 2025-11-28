# intent_recognizer.py
# LLM意图识别模块 (LLM Intent Recognition Module)

import json
import re
from http import HTTPStatus
from dashscope import Application
from config import API_KEY, APP_ID

class LLMIntentRecognizer:
    def __init__(self, doc_manager, client_config):
        self.doc_manager = doc_manager
        self.client_config = client_config
        # 维护对话历史的 messages 数组
        self.messages = []
        
        # ============================================================
        # 系统提示词配置说明
        # ============================================================
        # 系统提示词（System Prompt）现在在阿里云百炼应用中配置
        # 请在阿里云百炼控制台的"应用配置"中修改系统提示词
        # 本地参考文件：system_prompt_full.md（仅作为备份和参考）
        # 
        # 注意：
        # 1. 云端配置的系统提示词会覆盖代码中的任何设置
        # 2. 如果需要在系统提示词中包含动态上下文（如当前文档列表），
        #    可以在云端配置时使用占位符，或通过 messages 数组传递
        # 3. 当前代码不再维护 system_prompt 变量
        # ============================================================
    
    def reset_conversation(self):
        """
        重置对话历史，清空 messages 数组
        用于解决对话历史中可能包含错误格式（如双大括号）的问题
        """
        self.messages = []
        print("[系统提示] 对话历史已重置")
    
    def _extract_json(self, text):
        """
        从文本中提取JSON内容，处理各种可能的格式
        """
        if not text or not text.strip():
            return ""
        
        print(f"[调试] _extract_json 输入文本长度: {len(text)} 字符")
        print(f"[调试] _extract_json 输入文本前200字符: {text[:200]}")
        
        # 1. 尝试提取 markdown 代码块中的 JSON（支持多行和格式不完整的情况）
        # 处理完整的代码块：```json ... ```
        # 注意：使用非贪婪匹配可能导致问题，改为使用平衡括号匹配
        json_block_pattern = r'```(?:json)?\s*(\{[\s\S]*?\})\s*```'
        match = re.search(json_block_pattern, text, re.MULTILINE)
        if match:
            print(f"[调试] _extract_json 步骤1: 在markdown代码块中找到匹配")
            extracted = match.group(1).strip()
            print(f"[调试] _extract_json 步骤1: 提取的内容前50字符: {extracted[:50]}")
            print(f"[调试] _extract_json 步骤1: 是否以{{开头: {extracted.startswith('{')}")
            print(f"[调试] _extract_json 步骤1: 是否以{{{{开头: {extracted.startswith('{{')}")
            # 验证提取的内容：确保括号匹配，且是单大括号开头
            if extracted and extracted.startswith('{') and not extracted.startswith('{{'):
                # 检查括号是否匹配
                brace_count = extracted.count('{') - extracted.count('}')
                print(f"[调试] _extract_json 步骤1: 括号计数差: {brace_count}")
                if brace_count == 0:
                    print(f"[调试] _extract_json 步骤1: 返回提取的内容（括号匹配）")
                    return extracted
                else:
                    # 如果括号不匹配，尝试找到匹配的结束位置
                    brace_count = 0
                    json_end = -1
                    for i, char in enumerate(extracted):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                json_end = i
                                break
                    if json_end > 0:
                        result = extracted[:json_end + 1]
                        print(f"[调试] _extract_json 步骤1: 返回修正后的内容（找到匹配的结束位置）")
                        return result
            else:
                print(f"[调试] _extract_json 步骤1: 提取的内容不符合要求（双大括号或格式错误），继续查找")
        
        # 1.1 处理不完整的代码块（只有开头标记，没有结尾）
        # 匹配 ```json 或 ``` 后面的内容，直到找到完整的JSON对象
        incomplete_block_pattern = r'```(?:json)?\s*\n?\s*(\{[\s\S]*?\})'
        match = re.search(incomplete_block_pattern, text, re.MULTILINE)
        if match:
            print(f"[调试] _extract_json 步骤1.1: 在不完整代码块中找到匹配")
            extracted = match.group(1).strip()
            print(f"[调试] _extract_json 步骤1.1: 提取的内容前50字符: {extracted[:50]}")
            print(f"[调试] _extract_json 步骤1.1: 是否以{{{{开头: {extracted.startswith('{{')}")
            # 验证：确保是单大括号开头，不是双大括号
            if extracted.startswith('{{'):
                # 如果是双大括号，跳过这个匹配，继续查找
                print(f"[调试] _extract_json 步骤1.1: 检测到双大括号，跳过此匹配")
                pass
            else:
                # 找到匹配的最后一个 }
                brace_count = 0
                json_end = -1
                for i, char in enumerate(extracted):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i
                            break
                if json_end > 0:
                    extracted = extracted[:json_end + 1]
                if extracted and extracted.startswith('{') and not extracted.startswith('{{'):
                    print(f"[调试] _extract_json 步骤1.1: 返回提取的内容")
                    return extracted
        
        # 2. 尝试找到第一个 { 到匹配的最后一个 } 之间的内容（支持嵌套）
        # 注意：跳过双大括号，只查找单大括号
        json_start = -1
        for i in range(len(text) - 1):
            if text[i] == '{' and text[i+1] != '{':
                # 找到单大括号开头
                json_start = i
                break
        
        if json_start >= 0:
            # 从第一个 { 开始，找到匹配的最后一个 }
            brace_count = 0
            json_end = -1
            for i in range(json_start, len(text)):
                if text[i] == '{':
                    brace_count += 1
                elif text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_end = i
                        break
            
            if json_end > json_start:
                json_text = text[json_start:json_end + 1].strip()
                # 验证是否是有效的JSON结构（括号匹配，且是单大括号）
                if json_text and json_text.startswith('{') and not json_text.startswith('{{') and json_text.endswith('}'):
                    if json_text.count('{') == json_text.count('}'):
                        return json_text
        
        # 3. 尝试查找行内的JSON（可能没有换行）
        # 查找类似 {"key": "value"} 这样的简单JSON
        simple_json_pattern = r'\{[^{}]*"[^{}]*"[^{}]*\}'
        match = re.search(simple_json_pattern, text)
        if match:
            return match.group(0).strip()
        
        # 4. 如果都没找到，返回原始文本（去除首尾空白）
        result = text.strip()
        # 如果结果为空或太短，返回空字符串
        if len(result) < 2 or not result.startswith('{'):
            return ""
        return result
    
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
        print(f"[调试] _fix_json_format 去除空白后是否以{{{{\"开头: {json_text_stripped.startswith('{{\"')}")
        print(f"[调试] _fix_json_format 去除空白后是否以}}\"结尾: {json_text_stripped.endswith('}}\"')}")
        print(f"[调试] _fix_json_format 去除空白后是否以{{{{开头: {json_text_stripped.startswith('{{')}")
        print(f"[调试] _fix_json_format 去除空白后是否以}}结尾: {json_text_stripped.endswith('}}')}")
        
        # 修复双大括号问题：{{"key": "value"}} -> {"key": "value"}
        # 这是云端系统提示词配置问题导致的，LLM返回了双大括号格式
        # 处理以 {{" 开头，以 }}" 结尾的双大括号JSON
        if json_text_stripped.startswith('{{"') and json_text_stripped.endswith('}}"'):
            # 去掉最外层的双大括号：去掉开头的 {{ 和结尾的 }}
            json_text = json_text_stripped[2:]  # 去掉开头的 {{
            json_text = json_text[:-2]  # 去掉结尾的 }}
            print(f"[调试] _fix_json_format 检测到双大括号格式（{{{{\"开头），已修复")
            print(f"[调试] _fix_json_format 修复后: {json_text[:100]}")
        # 处理其他可能的双大括号格式（以 {{ 开头但不一定是 {{"）
        elif json_text_stripped.startswith('{{') and json_text_stripped.endswith('}}'):
            # 更通用的处理：去掉最外层的一对大括号
            # 但要小心，确保不会破坏内部的JSON结构
            # 简单方法：如果开头是 {{ 且结尾是 }}，去掉各一个
            json_text = json_text_stripped[1:]  # 去掉第一个 {
            json_text = json_text[:-1]  # 去掉最后一个 }
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
    
    def _normalize_intent_data(self, intent_data):
        """
        将新的JSON Schema格式转换为兼容旧代码的格式
        支持新旧两种格式的自动转换
        """
        # 如果已经是旧格式，直接返回
        if "intent" in intent_data:
            return intent_data
        
        # 新格式转换为旧格式
        normalized = {}
        
        # 意图类型映射
        intent_type = intent_data.get("intent_type", "UNKNOWN")
        
        # 类型检查和转换：确保 intent_type 是字符串
        if intent_type is None:
            intent_type = "UNKNOWN"
        elif not isinstance(intent_type, str):
            # 如果不是字符串，尝试转换为字符串
            try:
                intent_type = str(intent_type).upper()
            except Exception:
                intent_type = "UNKNOWN"
        else:
            # 转换为大写以匹配映射
            intent_type = intent_type.upper()
        
        intent_mapping = {
            "ADD": "ADD_CONTENT",
            "EDIT": "EDIT_CONTENT",  # 新增，但当前代码可能不支持
            "MOVE": "MOVE_CONTENT",  # 新增，但当前代码可能不支持
            "DELETE": "DELETE_CONTENT",
            "QUERY": "DISPLAY_DOC",
            "SET_ACTIVE": "SET_ACTIVE",
            "HELP": "HELP",
            "EXIT": "EXIT",
            "CONFIRM": "CONFIRM",  # 用户确认操作
            "CANCEL": "CANCEL",  # 用户取消操作
            "RESET_CONVERSATION": "RESET_CONVERSATION",  # 重置对话历史
            "UNKNOWN": "UNKNOWN"
        }
        normalized["intent"] = intent_mapping.get(intent_type, "UNKNOWN")
        
        # 字段映射
        normalized["doc_title"] = intent_data.get("target_document")
        normalized["content"] = intent_data.get("content_to_process")
        # 处理position：如果target_location_raw是None或不存在，默认为"end"
        position_raw = intent_data.get("target_location_raw")
        normalized["position"] = position_raw if position_raw is not None else "end"
        
        # 保留新格式的额外信息（用于未来扩展）
        normalized["context_dependency"] = intent_data.get("context_dependency", False)
        normalized["confirmation_needed"] = intent_data.get("confirmation_needed", False)
        normalized["system_action_required"] = intent_data.get("system_action_required", "")
        
        return normalized

    def recognize(self, user_input):
        """使用LLM识别用户意图并提取参数"""
        if not self.client_config:
            print("[系统错误] LLM配置未初始化，使用默认UNKNOWN意图。")
            return {"intent": "UNKNOWN"}

        # 注意：系统提示词现在在阿里云百炼应用中配置
        # 如果需要在系统提示词中包含动态上下文（如当前文档列表），
        # 可以通过 messages 数组传递 system role 的消息来补充或覆盖云端配置
        # 当前实现：不在代码中传递 system role 消息，完全依赖云端配置
        
        # 如果需要动态上下文，可以在这里构建并添加到 messages
        # 例如：
        # doc_titles = ", ".join(self.doc_manager.get_document_titles())
        # active_doc = self.doc_manager.active_doc_title
        # context_info = f"当前可用的文档标题: {doc_titles}\n当前活跃文档: {active_doc}"
        # if not self.messages:
        #     self.messages.append({
        #         "role": "system",
        #         "content": context_info
        #     })
        
        # 将用户输入添加到 messages
        self.messages.append({
            "role": "user",
            "content": user_input
        })
        
        try:
            # 调用阿里云百炼智能体应用，使用 messages 参数
            # 注意：如果应用已在应用内配置了知识库，知识库检索会自动启用，无需额外参数
            response = Application.call(
                api_key=self.client_config.get("api_key") or API_KEY,
                app_id=self.client_config.get("app_id") or APP_ID,
                messages=self.messages
            )
            
            if response.status_code != HTTPStatus.OK:
                print(f"[LLM错误] 调用智能体应用失败")
                print(f"  request_id={response.request_id}")
                print(f"  code={response.status_code}")
                print(f"  message={response.message}")
                # API 调用失败，移除刚才添加的用户消息，避免对话历史不完整
                if self.messages and self.messages[-1].get("role") == "user":
                    self.messages.pop()
                # 降级处理
                if re.search(r"(退出|再见|结束)", user_input):
                    return {"intent": "EXIT"}
                if re.search(r"(帮助|能做什么|怎么用)", user_input):
                    return {"intent": "HELP"}
                return {"intent": "UNKNOWN"}
            
            # 解析JSON输出
            output_text = response.output.text.strip()
            
            # ===== 调试信息：显示LLM的完整返回 =====
            print("\n" + "="*60)
            print("[调试] LLM原始返回内容:")
            print("-"*60)
            print(output_text)
            print("-"*60)
            print(f"[调试] 返回内容长度: {len(output_text)} 字符")
            print(f"[调试] 是否包含{{: {output_text.count('{')}")
            print(f"[调试] 是否包含}}: {output_text.count('}')}")
            print("="*60)
            print()  # 空行
            
            # 将 AI 的回复添加到 messages 中，维护对话历史
            self.messages.append({
                "role": "assistant",
                "content": output_text
            })
            
            # 改进的JSON提取逻辑：处理各种可能的格式
            print("[调试] 开始提取JSON，原始文本前200字符:")
            print(output_text[:200])
            print()
            json_text = self._extract_json(output_text)
            
            print("[调试] 提取的JSON文本:")
            print("-"*60)
            if json_text:
                print(f"[调试] 提取的JSON文本长度: {len(json_text)} 字符")
                print(f"[调试] 提取的JSON文本开头10字符: {json_text[:10]}")
                print(f"[调试] 提取的JSON文本结尾10字符: {json_text[-10:]}")
                print(f"[调试] 提取的JSON是否以{{开头: {json_text.startswith('{')}")
                print(f"[调试] 提取的JSON是否以}}结尾: {json_text.endswith('}')}")
                print(f"[调试] 提取的JSON中{{的数量: {json_text.count('{')}")
                print(f"[调试] 提取的JSON中}}的数量: {json_text.count('}')}")
                # 尝试格式化JSON以便阅读
                try:
                    import json as json_module
                    formatted_json = json_module.dumps(json_module.loads(json_text), ensure_ascii=False, indent=2)
                    print("[调试] JSON格式验证成功，格式化后:")
                    print(formatted_json)
                except Exception as e:
                    # 如果无法格式化，显示原始文本（限制长度）
                    print(f"[调试] JSON格式验证失败: {e}")
                    print("[调试] 原始提取的文本:")
                    print(json_text[:500] + ("..." if len(json_text) > 500 else ""))
            else:
                print("(空)")
            print("-"*60)
            print()  # 空行
            
            # 检查提取的 JSON 是否为空
            if not json_text or not json_text.strip():
                print(f"[LLM错误] 无法从输出中提取JSON内容")
                print(f"[LLM错误] 原始输出完整内容:")
                print(output_text)
                print(f"[LLM错误] 原始输出类型: {type(output_text)}")
                # 降级处理
                if re.search(r"(退出|再见|结束)", user_input):
                    return {"intent": "EXIT"}
                if re.search(r"(帮助|能做什么|怎么用)", user_input):
                    return {"intent": "HELP"}
                return {"intent": "UNKNOWN"}
            
            # 尝试解析JSON
            try:
                intent_data = json.loads(json_text)
                print("[调试] JSON解析成功:")
                print("-"*60)
                import json as json_module
                print(json_module.dumps(intent_data, ensure_ascii=False, indent=2))
                print("-"*60)
                print()  # 空行
            except json.JSONDecodeError as e:
                # 如果第一次解析失败，尝试修复常见的JSON格式问题
                print("[调试] 第一次JSON解析失败:")
                print(f"  错误: {e}")
                print(f"[调试] 修复前的JSON文本（前100字符）: {json_text[:100]}")
                print(f"[调试] 修复前是否以{{{{开头: {json_text.startswith('{{')}")
                print(f"[调试] 修复前是否以}}结尾: {json_text.endswith('}}')}")
                print()
                fixed_json = self._fix_json_format(json_text)
                print("[调试] 修复后的JSON:")
                print("-"*60)
                print(fixed_json[:500] + ("..." if len(fixed_json) > 500 else ""))
                print("-"*60)
                print(f"[调试] 修复后是否以{{开头: {fixed_json.startswith('{')}")
                print(f"[调试] 修复后是否以}}结尾: {fixed_json.endswith('}')}")
                print()
                try:
                    intent_data = json.loads(fixed_json)
                    print("[调试] 修复后JSON解析成功:")
                    print("-"*60)
                    import json as json_module
                    print(json_module.dumps(intent_data, ensure_ascii=False, indent=2))
                    print("-"*60)
                    print()  # 空行
                except json.JSONDecodeError as e2:
                    # 如果还是失败，显示详细错误信息
                    print(f"\n[LLM错误] JSON解析失败: {e2}")
                    print(f"[LLM错误] 错误位置: line {e2.lineno}, column {e2.colno}")
                    print(f"[LLM错误] 原始输出完整内容:")
                    print(output_text)
                    print(f"[LLM错误] 提取的JSON文本:")
                    print(json_text)
                    print(f"[LLM错误] 修复后的JSON文本:")
                    print(fixed_json)
                    # 抛出异常让外层处理
                    raise
            
            # 转换为兼容格式（支持新旧两种格式）
            return self._normalize_intent_data(intent_data)

        except json.JSONDecodeError as e:
            print(f"[LLM错误] JSON解析失败: {e}")
            if 'response' in locals() and response.status_code == HTTPStatus.OK:
                output_text = response.output.text.strip()
                print(f"[LLM错误] 原始输出: {output_text}")
                print(f"[LLM错误] 提取的JSON文本: {self._extract_json(output_text) if hasattr(self, '_extract_json') else 'N/A'}")
            else:
                print(f"[LLM错误] 原始输出: N/A")
            # JSON 解析失败，但 API 调用成功，仍然将 assistant 回复添加到 messages
            if 'response' in locals() and response.status_code == HTTPStatus.OK:
                output_text = response.output.text.strip()
                self.messages.append({
                    "role": "assistant",
                    "content": output_text
                })
            else:
                # API 调用失败，移除刚才添加的用户消息
                if self.messages and self.messages[-1].get("role") == "user":
                    self.messages.pop()
            # 降级处理
            if re.search(r"(退出|再见|结束)", user_input):
                return {"intent": "EXIT"}
            if re.search(r"(帮助|能做什么|怎么用)", user_input):
                return {"intent": "HELP"}
            return {"intent": "UNKNOWN"}
        except Exception as e:
            print(f"[LLM错误] 调用智能体应用失败: {e}")
            # 异常情况，移除刚才添加的用户消息，避免对话历史不完整
            if self.messages and self.messages[-1].get("role") == "user":
                self.messages.pop()
            # 降级处理：尝试使用简单的正则匹配（作为LLM失败的备用方案）
            if re.search(r"(退出|再见|结束)", user_input):
                return {"intent": "EXIT"}
            if re.search(r"(帮助|能做什么|怎么用)", user_input):
                return {"intent": "HELP"}
            return {"intent": "UNKNOWN"}


