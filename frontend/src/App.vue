<template>
  <div class="min-h-screen bg-gray-100 p-4 font-sans">
    <header class="mb-8 text-center">
      <h1 class="text-3xl font-bold text-gray-800">基于稀疏采样的可证安全隐写系统</h1>
      <p class="text-gray-500 text-sm mt-2 italic">SparSamp: Efficient Provably Secure Steganography</p>
    </header>

    <div class="mx-auto max-w-6xl grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="bg-white p-6 rounded-lg shadow-md lg:col-span-1 border-t-4 border-blue-600">
        <h2 class="font-bold mb-4 text-gray-700 flex items-center">
          <span class="mr-2">🛠️</span> 输入配置
        </h2>
        
        <div class="mb-4">
          <label class="block text-xs font-bold text-gray-500 mb-1 uppercase tracking-wider">选择生成模型:</label>
          <select v-model="selectedModel" class="w-full border p-2 rounded text-sm bg-gray-50 focus:ring-2 focus:ring-blue-500 outline-none">
            <optgroup label="文本生成 (LLM)">
              <option value="gpt">GPT-2</option>
              <option value="qwen">Qwen-2.5</option>
            </optgroup>
          </select>
        </div>

        <div class="mb-4">
          <label class="block text-xs font-bold text-gray-500 mb-1 uppercase tracking-wider">随机种子 (Seed):</label>
          <input type="number" v-model.number="stegoSeed" class="w-full border p-2 rounded text-sm bg-gray-50 focus:ring-2 focus:ring-blue-500 outline-none" placeholder="输入随机种子"/>
        </div>

        <div class="mb-4">
          <label class="block text-xs font-bold text-gray-500 mb-1 uppercase tracking-wider">
            嵌入位长度 (lm): <span class="text-blue-600">{{ lmBits }}</span>
          </label>
          <input type="range" v-model.number="lmBits" min="4" max="64" step="4" class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer">
          <p class="text-[10px] text-gray-400 mt-1">* 文献表2推荐lm=64以获得97.4%利用率 </p>
        </div>

        <div class="mb-4">
          <label class="block text-xs font-bold text-gray-500 mb-1 uppercase tracking-wider">秘密消息:</label>
          <textarea v-model="secretMessage" class="w-full border p-2 rounded text-sm mb-2 focus:ring-2 focus:ring-blue-500 outline-none" rows="4" placeholder="输入秘密文字..."></textarea>
          <div class="flex justify-between items-center text-[10px] text-gray-500">
            <span>模式: {{ isBinary(secretMessage) ? '直接二进制' : '文字自动转码' }}</span>
            <span class="text-green-600 font-bold">● 安全性: KL散度=0</span>
          </div>
        </div>

        <button @click="handleGenerate" :disabled="isEmbedding || !secretMessage" class="w-full bg-blue-600 text-white py-2.5 rounded shadow-lg hover:bg-blue-700 disabled:bg-gray-400 transition-all font-bold">
          {{ isEmbedding ? 'AI 采样中 (O(1)复杂度)...' : '生成隐写文本' }}
        </button>
      </div>

      <div class="lg:col-span-2 space-y-6">
        <div class="bg-white p-6 rounded-lg shadow-md border-t-4 border-blue-400">
          <h2 class="font-bold mb-4 text-gray-700 flex items-center">
            <span class="mr-2">📄</span> 生成结果
          </h2>
          <div v-if="stegoText" class="p-5 bg-blue-50 border-l-4 border-blue-500 rounded-r-lg mb-4">
            <p class="text-xs font-bold text-blue-800 mb-2 italic">生成的隐写内容 (Stego Content):</p>
            <p class="text-xl font-serif leading-relaxed text-gray-800">"{{ stegoText }}"</p>
          </div>
          <div v-if="tokens.length" class="mt-4">
            <p class="text-[10px] font-bold text-gray-400 mb-1 uppercase">Token Path (采样路径):</p>
            <div class="text-xs font-mono bg-gray-50 p-3 rounded border border-gray-100 text-gray-500 break-all leading-normal">
              {{ tokens.join(' → ') }}
            </div>
          </div>
          <div v-else class="h-32 flex items-center justify-center border-2 border-dashed border-gray-100 rounded">
            <p class="text-gray-300 text-sm">等待嵌入任务启动...</p>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow-md border-t-4 border-green-500">
          <h2 class="font-bold mb-4 text-gray-700 flex items-center">
            <span class="mr-2">🔐</span> 提取验证
          </h2>
          <button @click="handleExtract" :disabled="!tokens.length || isExtracting" class="w-full bg-green-600 text-white py-2.5 rounded shadow-lg hover:bg-green-700 disabled:bg-gray-400 transition-all font-bold">
            {{ isExtracting ? '逆向稀疏解码中...' : '提取秘密消息' }}
          </button>
          <div v-if="decodedText" class="mt-6 p-4 bg-green-50 rounded-lg border border-green-100">
            <p class="text-sm font-bold text-green-800 flex items-center">
              <span class="mr-2">✨</span> 最终还原文字: 
              <span class="ml-2 text-xl text-blue-700 underline">{{ decodedText }}</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

// 1. 响应式变量
const selectedModel = ref('gpt');
const stegoSeed = ref(12345);
const lmBits = ref(8); 
const secretMessage = ref('');
const stegoText = ref('');
const tokens = ref([]);
const decodedText = ref('');
const isEmbedding = ref(false);
const isExtracting = ref(false);

// 2. 工具函数
const isBinary = (str) => /^[01]+$/.test(str);

const textToBin = (text) => {
  return Array.from(new TextEncoder().encode(text))
    .map(b => b.toString(2).padStart(8, '0'))
    .join('');
};

const binToText = (bin) => {
  const cleanBin = bin.replace(/[^01]/g, ''); 
  const validLen = Math.floor(cleanBin.length / 8) * 8;
  const standardBin = cleanBin.substring(0, validLen);
  if (!standardBin) return "";
  try {
    const bytes = new Uint8Array(standardBin.match(/.{1,8}/g).map(b => parseInt(b, 2)));
    return new TextDecoder().decode(bytes).replace(/\0/g, '').trim();
  } catch (e) { return "解码失败"; }
};

// 3. 生成隐写文本逻辑 (嵌入)
const handleGenerate = async () => {
  if (!secretMessage.value) return;
  isEmbedding.value = true;
  stegoText.value = '';
  tokens.value = [];
  decodedText.value = '';

  const msg = isBinary(secretMessage.value) ? secretMessage.value : textToBin(secretMessage.value);
  
  try {
    // 检查这里！不要写 localhost 或 127.0.0.1
// 必须写你在地址栏看到的那个 IP 地址
    const res = await axios.post('http://127.0.0.1:5000/embed', { 
      secret_message: msg,
      selected_model: selectedModel.value,
      lm_bits: lmBits.value,
      seed: stegoSeed.value 
    }, { timeout: 0 });
    stegoText.value = res.data.stego_text;
    tokens.value = res.data.generated_tokens;
  } catch (err) { 
    alert('生成失败：请检查后端 Flask 服务是否开启'); 
  } finally { 
    isEmbedding.value = false; 
  }
};

// 4. 提取秘密消息逻辑 (提取)
const handleExtract = async () => {
  if (!tokens.value || tokens.value.length === 0) {
    alert("请先生成隐写文本");
    return;
  }

  isExtracting.value = true;
  try {
    const res = await axios.post('http://127.0.0.1:5000/extract', { 
      generated_tokens: tokens.value, 
      selected_model: selectedModel.value, 
      lm_bits: lmBits.value,
      seed: stegoSeed.value 
    }, { timeout: 0 });

    if (res.data && res.data.extracted_message) {
      console.log('解密前比特流:', res.data.extracted_message);
      decodedText.value = binToText(res.data.extracted_message);
    } else {
      decodedText.value = "未提取到有效信息";
    }
  } catch (err) { 
    alert('提取失败'); 
  } finally { 
    isExtracting.value = false; 
  }
};
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:italic,wght@0,400;1,600&display=swap');
.font-serif { font-family: 'Crimson Pro', serif; }
</style>