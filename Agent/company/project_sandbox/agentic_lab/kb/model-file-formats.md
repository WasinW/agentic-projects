# Model & File Formats

## ตารางไฟล์ที่เจอบ่อย
| ไฟล์ | คืออะไร |
|---|---|
| `.safetensors` | น้ำหนักโมเดลดิบ (HuggingFace format) ใช้กับ GPU / transformers |
| `.gguf` | น้ำหนัก quantized สำหรับ llama.cpp / Ollama รันบน CPU/Mac ได้ |
| `Q4_K_M`, `Q8_0` | ระดับ quantization ตัวเลข = bit ต่อ weight ยิ่งต่ำยิ่งเล็กและโง่ลง |
| `Modelfile` | Dockerfile ของ Ollama — base model + system prompt + params |
| `adapter_config.json` + `adapter_model.safetensors` | LoRA adapter = delta weights ไม่กี่ MB ที่ merge ทับ base |
| `config.json` | สถาปัตยกรรมโมเดล |
| `tokenizer.json` | tokenizer |
| `chat_template` | Jinja template ที่แปลง messages[] → prompt string |
| `.jsonl` (ShareGPT / Alpaca) | dataset สำหรับ fine-tune 1 บรรทัด = 1 conversation |

## แยก 3 แกนให้ขาด — คนสับสนกันมากที่สุด
- อยากให้โมเดล **รู้ข้อมูลใหม่** → RAG
- อยากให้โมเดล **ทำงานได้** → agent + tools
- อยากให้โมเดล **เปลี่ยนพฤติกรรม/format/tone หรือบีบให้เล็กแต่เก่งเฉพาะทาง** → fine-tune

Unsloth = สาย fine-tuning ซึ่งเป็นคนละแกนกับ RAG/agent เลย
โมเดลแบบ Agents-A1-4B = fine-tune มาให้ tool-calling เก่ง รันบนเครื่องตัวเองได้
