setopt PROMPT_SUBST
precmd() { print -rP "%F{yellow}%~%f $($HOME/Projects/git-prompt/prompt.py)" }
PROMPT='%F{white}%*%f '