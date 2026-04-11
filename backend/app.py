import torch
import numpy as np
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForCausalLM
import traceback
from sparsamp_algorithm import encode_step_paper, decode_step_paper

app = Flask(__name__)
CORS(app)

tokenizer, model = None, None
current_loaded_path = None  # 新增：用于记录当前内存里加载的是哪个模型

def load_model(selected_model):
    global tokenizer, model, current_loaded_path
    
    # 1. 根据前端传来的参数决定路径
    if 'qwen' in str(selected_model).lower():
        path = "../qwen"
    else:
        path = "../gpt"
        
    # 2. 如果当前加载的模型不是前端选的那个，就重新加载
    if current_loaded_path != path:
        print(f"=============================")
        print(f"正在切换并加载模型: {path} ...")
        print(f"=============================")
        tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(path, trust_remote_code=True)
        model.eval()
        current_loaded_path = path

@app.route('/embed', methods=['POST'])
def embed():
    try:
        data = request.get_json()
        msg = data.get('secret_message', '')
        lm = int(data.get('lm_bits', 64)) 
        seed = int(data.get('seed', 32))
        selected_model = data.get('selected_model', 'gpt') # 👉获取前端选择的模型

        bit_string = ''.join(format(ord(c), '08b') for c in msg)
        padding = (lm - (len(bit_string) % lm)) % lm
        bit_string += '0' * padding
        
        load_model(selected_model)
        input_ids = tokenizer.encode("Once upon a time,", return_tensors='pt', add_special_tokens=False)
        stego_ids, m_index, step = [], 0, 0
        
        # 初始化块状态 [cite: 41-43]
        k_m = int(bit_string[m_index:m_index + lm], 2)
        n_m = 2**lm
        random.seed(seed) # 循环外设置 seed [cite: 43]

        with torch.no_grad():
            while True:
                # 核心修复 1：限制输入长度，防止 GPT-2 内存溢出报错
                outputs = model(input_ids[:, -1000:]) 
                probs = torch.softmax(outputs.logits[0, -1, :], dim=-1).double()
                
                r = random.random()
                token_idx, n_m, k_m = encode_step_paper(probs, n_m, k_m, r)
                
                stego_ids.append(token_idx)
                input_ids = torch.cat([input_ids, torch.tensor([[token_idx]])], dim=-1)
                step += 1
                
                # 判定当前消息块是否嵌入完毕 [cite: 66-71]
                if n_m == 1:
                    m_index += lm
                    if m_index >= len(bit_string):
                        break # 全部比特嵌入完毕且收敛
                    # 加载下一个块 [cite: 69-70]
                    n_m = 2**lm
                    k_m = int(bit_string[m_index:m_index + lm], 2)
                
                # 核心修复 2：把安全熔断步数从 200 改为 2000（甚至更大）
                if step > 2000: 
                    print("达到最大生成 Token 限制，强制结束")
                    break

        return jsonify({
            'stego_text': tokenizer.decode(stego_ids),
            'generated_tokens': stego_ids,
            'total_bits': m_index
        })
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/extract', methods=['POST'])
def extract():
    try:
        data = request.get_json()
        tokens = data.get('generated_tokens', [])
        lm = int(data.get('lm_bits', 64))
        seed = int(data.get('seed', 32))
        selected_model = data.get('selected_model', 'gpt') # 👉 获取前端选择的模型
        
        load_model(selected_model)

        input_ids = tokenizer.encode("Once upon a time,", return_tensors='pt', add_special_tokens=False)
        random.seed(seed)
        n_m = 2**lm
        temp0_arr, n_m_arr, extracted_bits = [], [], ""

        with torch.no_grad():
            for token_idx in tokens:
                # 核心修复 3：提取时同样要防止上下文溢出
                outputs = model(input_ids[:, -1000:]) 
                probs = torch.softmax(outputs.logits[0, -1, :], dim=-1).double()
                
                r = random.random()
                n_m, temp0 = decode_step_paper(probs, token_idx, n_m, r)
                
                temp0_arr.append(temp0)
                n_m_arr.append(n_m)
                
                # 执行回溯累加逻辑 [cite: 106-114]
                if n_m == 1:
                    count = len(temp0_arr) - 2
                    curr_km = temp0_arr[count + 1]
                    while count >= 0:
                        nm_prev = n_m_arr[count]
                        curr_km = temp0_arr[count] + ((curr_km + nm_prev) % nm_prev)
                        count -= 1
                    curr_km = (curr_km + 2**lm) % 2**lm
                    extracted_bits += bin(int(curr_km))[2:].zfill(lm)
                    
                    # 重置块状态
                    n_m, temp0_arr, n_m_arr = 2**lm, [], []
                
                input_ids = torch.cat([input_ids, torch.tensor([[token_idx]])], dim=-1)
            # 1. 先把提取出的二进制比特流，按 8 位一组切分，还原为字符串
            chars = [chr(int(extracted_bits[i:i+8], 2)) for i in range(0, len(extracted_bits), 8) if len(extracted_bits[i:i+8]) == 8]
            final_text = "".join(chars)

            # 2. 正常返回结果（替换掉你原来的第 118 行）
            return jsonify({
                'extracted_message': final_text,
                'final_text': final_text
            })

    # 3. 这里是捕获错误的环节
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)