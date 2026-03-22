#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解析题库MD文件 - 只解析一套模拟题 + 专项训练"""
import re
import json
from pathlib import Path


def parse_question_file(content, source_file):
    """解析题目文件，包含解析内容"""
    questions = []
    lines = content.split('\n')
    
    q_num = 0
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
        if line.startswith('#'):
            i += 1
            continue
        if any(kw in line for kw in ['专项训练', '模拟题', '单选题', '多选题', '第一部分', '第二部分', '第', '套']):
            i += 1
            continue
        
        if len(line) > 15 and not line.startswith(('A', 'B', 'C', 'D', 'E')):
            q_num += 1
            question_text = line
            options = []
            answer = None
            answer_text = []
            
            i += 1
            option_count = 0
            
            while i < len(lines):
                opt_line = lines[i].strip()
                
                if not opt_line:
                    i += 1
                    continue
                
                if opt_line.startswith('试题答案：'):
                    ans = opt_line.replace('试题答案：', '').strip()
                    answer = ans.replace(';', '').replace('；', '')
                    i += 1
                    continue
                
                if opt_line.startswith('试题解析：'):
                    i += 1
                    while i < len(lines):
                        next_line = lines[i].strip()
                        if next_line.startswith('- '):
                            clean = next_line.lstrip('- ').strip()
                            if clean:
                                answer_text.append(clean)
                            i += 1
                        elif next_line and not next_line.startswith('#') and len(next_line) > 2:
                            break
                        else:
                            i += 1
                    break
                
                if opt_line.startswith('- '):
                    i += 1
                    continue
                
                opt_match = re.match(r'^([A-Z])\.\s+(.+)', opt_line)
                if opt_match:
                    options.append({'key': opt_match.group(1), 'text': opt_match.group(2)})
                    option_count += 1
                elif len(opt_line) > 2 and not opt_line.startswith('-'):
                    question_text += ' ' + opt_line
                
                i += 1
            
            if not options or not answer:
                continue
            
            q_type = 'multiple' if len(answer) > 1 else 'single'
            full_analysis = ' '.join(answer_text) if answer_text else ''
            
            questions.append({
                'id': str(q_num),
                'type': q_type,
                'question': question_text,
                'options': options,
                'answer': answer,
                'answer_text': full_analysis,
                'source': source_file
            })
            continue
        
        i += 1
    
    return questions


def main():
    base_dir = Path('/mnt/e/chb/opensource/aliyun_acp_learning/题库')
    output_file = Path('/mnt/e/chb/opensource/aliyun_acp_learning/刷题助手H5/questions.json')
    
    all_questions = []
    
    # 解析全部5套模拟题 + 专项训练
    target_files = [
        '大模型ACP认证模拟题01.md',
        '大模型ACP认证模拟题02.md',
        '大模型ACP认证模拟题03.md',
        '大模型ACP认证模拟题04.md',
        '大模型ACP认证模拟题05.md',
    ]

    
    # 添加所有专项训练
    for filepath in sorted(base_dir.glob('*.md')):
        if '专项训练' in filepath.name:
            target_files.append(filepath.name)
    
    for filename in target_files:
        filepath = base_dir / filename
        if not filepath.exists():
            continue
            
        content = filepath.read_text(encoding='utf-8')
        questions = parse_question_file(content, filename)
        
        is_topic = '专项训练' in filename
        single = sum(1 for q in questions if q['type'] == 'single')
        multi = sum(1 for q in questions if q['type'] == 'multiple')
        
        print(f"[{'专项' if is_topic else '模拟'}] {filename}: {len(questions)}题 (单{single} 多{multi})")
        all_questions.extend(questions)
    
    # 按来源和题号排序
    all_questions.sort(key=lambda x: (x['source'], int(x['id']) if x['id'].isdigit() else 0))
    
    single_count = sum(1 for q in all_questions if q['type'] == 'single')
    multi_count = sum(1 for q in all_questions if q['type'] == 'multiple')
    
    output_file.write_text(json.dumps(all_questions, ensure_ascii=False, indent=2), encoding='utf-8')
    
    print(f"\n总计: {len(all_questions)}题 (单选{single_count} 多选{multi_count})")
    print(f"已保存: {output_file}")


if __name__ == '__main__':
    main()
