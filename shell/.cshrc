# .cshrc

# User specific aliases and functions

alias rm 'rm -i'
alias cp 'cp -i'
alias mv 'mv -i'
alias vi 'vim'
alias h  'history'

alias lh   'ls -lh'
alias cd   'cd \!*; ls'
alias ..   'cd ../'
alias go   'cd /root/work/sts'

alias gits 'git status'

alias buildvnc 'vncserver -geometry 2540x1360'


setenv PATH "/usr/local/git/bin:$PATH"
setenv PATH "/usr/local/git/libexec/git-core:$PATH"

# added by Anaconda3 installer
setenv PATH "/root/anaconda3/bin:$PATH"

#du -lh --max-depth=1
#git rebase -i HEAD~2
#netstat -ltnp | grep vnc
#url = https://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@github.com/hissccye/sts.git
