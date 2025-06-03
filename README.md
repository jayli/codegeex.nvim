## Deepseek-coder.nvim

Nvim 基于 Deepseek 的 coder copilot 补全插件。

<img src="https://github.com/user-attachments/assets/37a4ab70-beff-4229-bee8-9aacd26d207f" width=400 />

演示：

https://github.com/user-attachments/assets/1065a9f3-213c-4fd6-829e-78021926d42b

#### 一）安装：

1）配置 init.lua

基于 Packer.nvim 安装：

```lua
use { 'jayli/deepseek-coder.nvim' }
vim.g.deepseek_apikey = "{你的 deepseek apikey}"
vim.g.deepseek_base_url = ""   --留空即可
```

执行`:PackerInstall`

2）安装 python 依赖

```bash
pip install httpx
```

#### 二）获得 deepseek apikey

登录：<https://platform.deepseek.com/api_keys>

创建你的 API key，创建好后需要将 key 复制下来，填写到`vim.g.deepseek_apikey`处。

<img src="https://github.com/user-attachments/assets/3333d2c8-5156-43f9-89db-006e186d73fc" width=500 />

#### 三）使用

插入模式下，正常输入时会自动联想，联想完成后敲 Tab 键完成补全，因为对 Tab 键有强绑定，所以也做了对一些常用补全插件的兼容（[coc](https://github.com/neoclide/coc.nvim)、[nvim-cmp](https://github.com/hrsh7th/nvim-cmp) 和 [vim-easycomplete](https://github.com/jayli/vim-easycomplete)）。

#### 四）注意

1）关于 deepseek 的速度问题

deepseek 有时速度较慢，你可以自己更换 deepseek 模型引擎，修改`vim.g.deepseek_base_url`的默认值为`https://api.deepseek.com/beta`，换成你自己部署 deepseek 后的 base url 即可。

2）编程补全的模型选择

Github Copilot 和 TabNine 都很好，但 Github Copilot太慢，TabNine 太贵。国内能用的模型有一些代理后的 GPT4 速度还行，还有两个专用于代码补全的 DeepSeek-Code 和 CodeGeex4。这几个都长期使用过，综合考虑效果和稳定性，效果相对可以的是 DeepSeek-Code。

如果是阿里内网用户，那果断使用灵码或者 Aone Copilot，速度和效果都超过 deepseek，我也实现了 Aone Copilot 的 nvim 插件，ata 上搜一下。
