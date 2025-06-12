## Copilot.nvim

Nvim 基于 Deepseek 和 qwen 的 coder copilot 补全插件。

<img src="https://github.com/user-attachments/assets/37a4ab70-beff-4229-bee8-9aacd26d207f" width=400 />

演示：

https://github.com/user-attachments/assets/1065a9f3-213c-4fd6-829e-78021926d42b

#### 一）安装：

1）配置 init.lua

基于 Packer.nvim 最简单的配置：

```lua
use { 'jayli/copilot.nvim' }
vim.g.copilot_apikey = "{你的 deepseek 的 apikey}"
```

执行`:PackerInstall`

> 默认支持的是 deepseek 官网的模型，去[deepseek官网](https://platform.deepseek.com/api_keys)获取到 api key 即可。

2）安装 python 依赖

```bash
pip install httpx
pip install neovim
```

#### 二） Deepseek 和 Qwen 获得 APIKey

##### 1) 获得 deepseek apikey

登录：<https://platform.deepseek.com/api_keys>

创建你的 API key，创建好后需要将 key 复制下来，填写到`vim.g.copilot_apikey`处。

<img src="https://github.com/user-attachments/assets/3333d2c8-5156-43f9-89db-006e186d73fc" width=500 />

##### 2) 获得 Qwen APIKey

登录阿里云后，参照这里获得 APIkey：<https://bailian.console.aliyun.com/?tab=api#/api/?type=model>

api key 赋值给 `vim.g.copilot_apikey`。

#### 三）使用

插入模式下，正常输入时会自动联想，联想完成后敲 Tab 键完成补全，因为对 Tab 键有强绑定，所以也做了对一些常用补全插件的兼容（[coc](https://github.com/neoclide/coc.nvim)、[nvim-cmp](https://github.com/hrsh7th/nvim-cmp) 和 [vim-easycomplete](https://github.com/jayli/vim-easycomplete)）。

1) Deepseek 完整配置

```lua
use { 'jayli/copilot.nvim' }
vim.g.copilot_apikey = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
vim.g.copilot_base_url = "https://api.deepseek.com/beta" -- 默认是 https://api.deepseek.com/beta
vim.g.copilot_timeout = 5     -- 默认是 5
vim.g.copilot_lines_limit = 500 -- 当前行前后行数限制，默认 500
vim.g.copilot_model = "deepseek-coder" -- 选择你的model名称，默认deepseek-coder
vim.g.copilot_llm = "deepseek" -- 选择你的模型引擎，默认 deepseek，千问：qwen
```

2) Qwen 完整配置

```lua
use { 'jayli/copilot.nvim' }
vim.g.copilot_apikey = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
vim.g.copilot_timeout = 5     -- 默认是 5
vim.g.copilot_lines_limit = 500 -- 当前行前后行数限制，默认 500
vim.g.copilot_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
vim.g.copilot_model = "qwen2.5-coder-7b-instruct"
vim.g.copilot_llm = "qwen"
```

3) Aone Copilot 完整配置

```lua
use { 'jayli/copilot.nvim' }
vim.g.copilot_apikey = "xxxxxxxxxxxxxxxxxxxxxxxx"
vim.g.copilot_base_url = "https://xxxxxxxxxxxxx"
vim.g.copilot_llm = "aone"
```

获得 apikey 和 base url，ATA 里搜一下。

`copilot_base_url`后会拼接`/completions`。deepseek 默认支持的AI补全的模型是`deepseek-coder`。qwen 支持的模型[这里](https://bailian.console.aliyun.com/?tab=doc#/api/?type=model&url=https%3A%2F%2Fhelp.aliyun.com%2Fdocument_detail%2F2850166.html)查看。Aone Copilot 留空即可。

#### 四）注意

1）关于 deepseek 的速度问题

deepseek 有时速度较慢，你可以自己更换 deepseek 模型引擎，修改`vim.g.copilot_base_url`的默认值为`https://api.deepseek.com/beta`，换成你自己部署 deepseek 后的 base url 即可。

2）编程补全的模型选择

Github Copilot 和 TabNine 都很好，但 Github Copilot太慢，TabNine 太贵。国内能用的模型有一些代理后的 GPT4 速度还行，还有两个专用于代码补全的 DeepSeek-Code ，qwen 和 CodeGeex4。综合用下来效果好的是 deepseek 和 qwen。

如果是阿里内网用户，那果断使用灵码或者 Aone Copilot，速度和效果都超过 deepseek 和 qwen。
