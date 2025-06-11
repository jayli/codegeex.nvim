" finish
if !has('nvim')
  finish
endif

if !has('python3')
  finish
endif

if !exists("g:copilot_apikey")
  let g:copilot_apikey = ""
endif

if !exists("g:copilot_base_url")
  let g:copilot_base_url = ""
endif

if !exists("g:copilot_timeout")
  let g:copilot_timeout = 5
endif

if !exists("g:copilot_lines_limit")
  let g:copilot_lines_limit = 500
endif

if !exists("g:copilot_model")
  let g:copilot_model = "deepseek-coder"
endif

if !exists("g:copilot_llm")
  let g:copilot_llm = "copilot" " deepseek, qwen
endif

if empty(g:copilot_base_url)
  let g:copilot_base_url = "https://api.deepseek.com/beta"
endif

if empty(g:copilot_apikey)
  finish
endif

" let s:plugin_root = fnamemodify(expand('<sfile>:p'), ':h:h')
" if &runtimepath =~ 'copilot.nvim'
" else
"   exec "set runtimepath+=" . s:plugin_root
"   silent! noa UpdateRemotePlugins
" endif

call timer_start(10, { -> copilot#regist_rplugin()})

let g:copilot_ready = v:true
if has('vim_starting')
  augroup copilot-coder
    autocmd!
    autocmd BufReadPost,BufNewFile * call copilot#init()
    autocmd TextChangedI * call copilot#text_changed_i()
    autocmd CursorHoldI * call copilot#cursor_hold_i()
    autocmd CursorHold * call copilot#cursor_hold()
    autocmd InsertLeave * call copilot#insert_leave()
    autocmd InsertEnter * call copilot#insert_enter()
    autocmd CompleteChanged * call copilot#complete_changed()
    autocmd CursorMovedI * call copilot#cursor_moved_i()
  augroup END
else
  call copilot#init()
endif



" vim:ts=2:sw=2:sts=2
