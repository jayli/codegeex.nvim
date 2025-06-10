local M = {}
local copilot_ns = vim.api.nvim_create_namespace('copilot_ns')
local loading = require "co-loading"

function M.foo()
  -- print("test")
end

function M.init_copilot_hl()
  local cursorline_bg = vim.fn["copilot#get_bgcolor"]("CursorLine")
  local normal_bg = vim.fn["copilot#get_bgcolor"]("Normal")
  local linenr_fg = vim.fn["copilot#get_fgcolor"]("LineNr")
  if vim.fn.matchstr(cursorline_bg, "^\\d\\+") ~= "" then
    cursorline_bg = vim.fn.str2nr(cursorline_bg)
  end
  if vim.fn.matchstr(normal_bg, "^\\d\\+") ~= "" then
    normal_bg = vim.fn.str2nr(normal_bg)
  end
  if vim.fn.matchstr(linenr_fg, "^\\d\\+") ~= "" then
    linenr_fg = vim.fn.str2nr(linenr_fg)
  end

  vim.api.nvim_set_hl(0, "SuggestionFirstLine", {
    bg = cursorline_bg,
    fg = linenr_fg
  })
  vim.api.nvim_set_hl(0, "SuggestionNoneFirstLine", {
    fg = linenr_fg,
    bg = normal_bg
  })
end

function M.init()
  M.init_copilot_hl()
  vim.api.nvim_create_autocmd({"ColorScheme"}, {
    pattern = {"*"},
    callback = function()
      M.init_copilot_hl()
    end
  })
end

-- code_block 是一个字符串，有可能包含回车符
-- call v:lua.require("co-copilot").show_hint()
-- code_block 是数组类型
function M.show_hint(code_block)
  local lines = {}
  local count = 1
  local code_lines = code_block
  for key, line in pairs(code_lines) do
    local highlight_group = ""
    if count == 1 then
      highlight_group = "SuggestionFirstLine"
    else
      highlight_group = "SuggestionNoneFirstLine"
    end
    count = count + 1
    table.insert(lines, {{line, highlight_group}})
  end

  local virt_text = lines[1]
  local virt_lines

  if #lines >= 2 then
    table.remove(lines, 1)
    virt_lines = lines
  else
    virt_lines = nil
  end

  vim.api.nvim_buf_set_extmark(0, copilot_ns, vim.fn.line('.') - 1, vim.fn.col('.') - 1, {
    id = 1,
    virt_text_pos = "overlay",
    virt_text = virt_text,
    virt_lines = virt_lines
  })
end

function M.delete_hint()
  vim.api.nvim_buf_del_extmark(0, copilot_ns, 1)
end

function M.loading_start()
  loading.start()
end

function M.loading_stop()
  loading.stop()
end

--- 深拷贝一个表
local function deep_copy(t)
  if type(t) ~= 'table' then return t end
  local copy = {}
  for k, v in pairs(t) do
    copy[k] = deep_copy(v)
  end
  setmetatable(copy, deep_copy(getmetatable(t)))
  return copy
end

--- 递归合并两个表：覆盖策略
function merge_config(defaults, user_opts)
  if type(defaults) ~= 'table' then
    defaults = {}
  end

  local result = deep_copy(defaults)

  if type(user_opts) ~= 'table' then
    return result
  end

  for key, value in pairs(user_opts) do
    if type(value) == 'table' and type(defaults[key]) == 'table' then
      -- 如果都是 table，递归合并
      result[key] = merge_config(defaults[key], value)
    else
      -- 否则直接替换
      result[key] = deep_copy(value)
    end
  end

  return result
end

M.setup = function(custom_config)
  -- merging is deferred until ensure_config
  new_user_config = merge_config({
      apikey = "",
      base_url = "old"
    },{
      apikey = "xxxxxxxxxxnew "
    })
  if vim.v.vim_did_enter == 0 then
    -- print(new_user_config.apikey)
    -- print(new_user_config.base_url)
    -- print(vim.fn.argv(0))
  end
end
return M

